from __future__ import annotations

import json
import logging
from typing import Any, Dict, Mapping, Optional, Tuple, Union

import backoff
import requests
from packaging import version
from yarl import URL

from .__version__ import __version__
from .exceptions import (
    WLEDConnectionError,
    WLEDConnectionTimeoutError,
    WLEDEmptyResponseError,
    WLEDError,
)
from .models import Device


class WLED:
    """Main class for handling connections with WLED"""

    _device: Device | None = None
    _supports_si_request: bool | None = None

    def __init__(
        self,
        host: str,
        base_path: str = "/json",
        password: str = None,
        port: int = 80,
        request_timeout: float = 8.0,
        session: requests.session = None,
        tls: bool = False,
        username: str = None,
        verify_ssl: bool = True,
        user_agent: str = None,
    ):
        self._session = session
        self._close_session = False

        self.base_path = base_path
        self.host = host
        self.password = password
        self.port = port
        self.socketaddr = None
        self.request_timeout = request_timeout
        self.tls = tls
        self.username = username
        self.verify_ssl = verify_ssl
        self.user_agent = user_agent

        if user_agent is None:
            self.user_agent = f"PythonWLED/{__version__}"

        if self.base_path[-1] != "/":
            self.base_path += "/"

    @backoff.on_exception(
        backoff.expo,
        WLEDConnectionError,
        max_tries=3,
        logger=logging.getLogger("octoprint.plugins.wled.wled"),
    )
    def _request(
        self,
        uri: str = "",
        method: str = "GET",
        data: Any | None = None,
        json_data: dict | None = None,
        params: Mapping[str, str] | None = None,
    ) -> Any:
        """Handle a request to a WLED device"""
        scheme = "https" if self.tls else "http"
        url = URL.build(
            scheme=scheme, host=self.host, port=self.port, path=self.base_path
        ).join(URL(uri))

        auth = None
        if self.username and self.password:
            auth = requests.auth.HTTPBasicAuth(
                self.username, self.password
            )  # TODO test this, not sure if it works the same way as aiohttp

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
        }

        if self._session is None:
            self._session = requests.session()
            self._close_session = True

        # If updating the state, always request for a state response
        if method == "POST" and uri == "state" and json_data is not None:
            json_data["v"] = True

        try:
            response = self._session.request(
                method,
                url,
                auth=auth,
                data=data,
                json=json_data,
                params=params,
                headers=headers,
                verify=self.verify_ssl,
                timeout=self.request_timeout,
            )
        except requests.exceptions.Timeout as exception:
            raise WLEDConnectionTimeoutError(
                f"Timeout occured while connecting to WLED device at {self.host}"
            ) from exception
        except requests.exceptions.ConnectionError as exception:
            raise WLEDConnectionError(
                f"Error occured while communicating with WLED device at {self.host}"
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if (response.status_code // 100) in [4, 5]:
            contents = response.content
            response.close()

            if content_type == "application/json":
                raise WLEDError(
                    response.status_code, json.loads(contents.decode("utf8"))
                )
            raise WLEDError(response.status_code, {"message": contents.decode("utf8")})

        if "application/json" in content_type:
            data = response.json()
            if (
                method == "POST"
                and uri == "state"
                and self._device is not None
                and json_data is not None
            ):
                self._device.update_from_dict(data={"state": data})
            return data

        return response.text

    @backoff.on_exception(
        backoff.expo,
        WLEDEmptyResponseError,
        max_tries=3,
        logger=logging.getLogger("octoprint.plugins.wled.wled"),
    )
    def update(self, full_update: bool = False) -> Device:
        """Get all information about the device in a single call."""
        if self._device is None or full_update:
            data = self._request()
            if not data:
                raise WLEDEmptyResponseError(
                    f"WLED device at {self.host} returned an empty API"
                    f" response on full update"
                )
            self._device = Device(data)

            try:
                version.Version(self._device.info.version)
                self._supports_si_request = version.parse(
                    self._device.info.version
                ) >= version.parse("0.10.0")
            except version.InvalidVersion:
                # Could be a manual build one? Lets poll for it
                try:
                    self._request("si")
                    self._supports_si_request = True
                except WLEDError:
                    self._supports_si_request = False

            return self._device

        # Handle legacy state and update in separate requests
        if not self._supports_si_request:
            info = self._request("info")
            if not info:
                raise WLEDEmptyResponseError(
                    f"WLED device at {self.host} returned an empty API"
                    f" response on info update"
                )

            state = self._request("state")
            if not state:
                raise WLEDEmptyResponseError(
                    f"WLED device {self.host} returned an empty API"
                    f" response on state update"
                )
            self._device.update_from_dict({"info": info, "state": state})
            return self._device

        state_info = self._request("si")
        if not state_info:
            raise WLEDEmptyResponseError(
                f"WLED device at {self.host} returned an empty API"
                " response on state & info update"
            )
        self._device.update_from_dict(state_info)
        return self._device

    def master(
        self,
        *,
        brightness: int | None = None,
        on: bool | None = None,
        transition: int | None = None,
    ):
        """Change master state of a WLED Light device."""
        state: dict[str, bool | int] = {}

        if brightness is not None:
            state["bri"] = brightness

        if on is not None:
            state["on"] = on

        if transition is not None:
            state["tt"] = transition

        self._request("state", method="POST", json_data=state)

    def segment(
        self,
        segment_id: int,
        *,
        brightness: int | None = None,
        clones: int | None = None,
        color_primary: None | (tuple[int, int, int, int] | tuple[int, int, int]) = None,
        color_secondary: None
        | (tuple[int, int, int, int] | tuple[int, int, int]) = None,
        color_tertiary: None
        | (tuple[int, int, int, int] | tuple[int, int, int]) = None,
        effect: int | str | None = None,
        intensity: int | None = None,
        length: int | None = None,
        on: bool | None = None,
        palette: int | str | None = None,
        reverse: bool | None = None,
        selected: bool | None = None,
        speed: int | None = None,
        start: int | None = None,
        stop: int | None = None,
        transition: int | None = None,
    ) -> None:
        """Change state of a WLED Light segment."""
        if self._device is None:
            self.update()

        if self._device is None:
            raise WLEDError("Unable to communicate with WLED to get the current state")

        state = {}
        segment = {
            "bri": brightness,
            "cln": clones,
            "fx": effect,
            "ix": intensity,
            "len": length,
            "on": on,
            "pal": palette,
            "rev": reverse,
            "sel": selected,
            "start": start,
            "stop": stop,
            "sx": speed,
        }

        # > WLED 0.10.0, does not support segment control on/bri.
        # Luckily, the same release introduced si requests.
        # Therefore, we can use that capability check to decide.
        if not self._supports_si_request:
            # This device does not support on/bri in the segment
            del segment["on"]
            del segment["bri"]
            state = {
                "bri": brightness,
                "on": on,
            }

        # Find effect if it was based on a name
        if effect is not None and isinstance(effect, str):
            segment["fx"] = next(
                (
                    item.effect_id
                    for item in self._device.effects
                    if item.name.lower() == effect.lower()
                ),
                None,
            )

        # Find palette if it was based on a name
        if palette is not None and isinstance(palette, str):
            segment["pal"] = next(
                (
                    item.palette_id
                    for item in self._device.palettes
                    if item.name.lower() == palette.lower()
                ),
            )

        # Filter out not set values
        state = {k: v for k, v in state.items() if v is not None}
        segment = {k: v for k, v in segment.items() if v is not None}

        # Determine color set
        colors = []
        if color_primary is not None:
            colors.append(color_primary)
        elif color_secondary is not None or color_tertiary is not None:
            colors.append(self._device.state.segments[segment_id].color_primary)

        if color_secondary is not None:
            colors.append(color_secondary)
        elif color_tertiary is not None:
            colors.append(self._device.state.segments[segment_id].color_secondary)

        if color_tertiary is not None:
            colors.append(color_tertiary)

        if colors:
            segment["col"] = colors  # type: ignore

        if segment:
            segment["id"] = segment_id
            state["seg"] = [segment]  # type: ignore

        if transition is not None:
            state["tt"] = transition

        self._request("state", method="POST", json_data=state)

    def transition(self, transition: int) -> None:
        """Set the default transition time for manual control."""
        self._request("state", method="POST", json_data={"transition": transition})

    def preset(self, preset: int) -> None:
        """Set a preset on a WLED device."""
        self._request("state", method="POST", json_data={"ps": preset})

    def playlist(self, playlist: int) -> None:
        """Set a running playlist on a WLED device."""
        self._request("state", method="POST", json_data={"pl": playlist})

    def sync(self, *, send: bool | None = None, receive: bool | None = None) -> None:
        """Set the sync status of the WLED device."""
        sync = {"send": send, "recv": receive}
        sync = {k: v for k, v in sync.items() if v is not None}
        self._request("state", method="POST", json_data={"udpn": sync})

    def nightlight(
        self,
        *,
        duration: int | None = None,
        fade: bool | None = None,
        on: bool | None = None,
        target_brightness: int | None = None,
    ) -> None:
        """Control the nightlight function of a WLED device."""
        nightlight = {
            "dur": duration,
            "fade": fade,
            "on": on,
            "tbri": target_brightness,
        }

        # Filter out not set values
        nightlight = {k: v for k, v in nightlight.items() if v is not None}

        state: dict[str, Any] = {"nl": nightlight}
        if on:
            state["on"] = True

        self._request("state", method="POST", json_data=state)

    def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            self._session.close()

    @property
    def device(self) -> Device:
        return self._device

    def __enter__(self) -> WLED:
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
