# -*- coding: utf-8 -*-

import logging
import threading
from typing import Dict, List, Optional

import flask

import octoprint_wled
from octoprint_wled import util
from octoprint_wled.wled import WLED
from octoprint_wled.wled.exceptions import (
    WLEDConnectionError,
    WLEDConnectionTimeoutError,
    WLEDEmptyResponseError,
    WLEDError,
)

CMD_TEST = "test"
CMD_TOGGLE_FLASHLIGHT = "toggle_flashlight"


class PluginAPI:
    def __init__(self, plugin):
        self.plugin = plugin  # type: octoprint_wled.WLEDPlugin
        # noinspection PyProtectedMember
        self._settings = plugin._settings
        self._logger: logging.Logger = logging.getLogger("octoprint.plugins.wled.api")

        # This API is asynchronous
        # All methods return after creating a thread, then send a message
        # on the websocket later. This prevents long running WLED API calls from
        # blocking the API/frontend.
        # If this thread exists, then the response is 'in progress'
        self.get_thread: Optional[threading.Thread] = None
        self.post_test_thread: Optional[threading.Thread] = None

    @staticmethod
    def get_api_commands() -> Dict[str, List[str]]:
        return {CMD_TEST: ["config"]}

    def on_api_command(self, command, data):
        if command == CMD_TEST:
            if self.post_test_thread and self.post_test_thread.is_alive():
                return flask.jsonify({"status": "in_progress"})
            self.post_test_thread = util.start_thread(
                self.test_wled, kwargs={"data": data}, name="WLED Test thread"
            )
            return flask.jsonify({"status": "started"})
        if command == CMD_TOGGLE_FLASHLIGHT:
            for segmentIndex in range(self.plugin.wled.device.state.segments.count):
                self.plugin.wled.segment(
                    segment_id=segmentIndex,
                    brightness=255,
                    color_primary=(255, 255, 255),
                    color_secondary=(0, 0, 0),
                    color_tertiary=(0, 0, 0),
                    effect="solid",
                    intensity=255,
                    on=True,
                )

    def on_api_get(self, request):
        if self.get_thread and self.get_thread.is_alive():
            return flask.jsonify({"status": "in_progress"})

        self.get_thread = util.start_thread(
            self.get_wled_status,
            kwargs={"request": request},
            name="WLED GET request thread",
        )
        return flask.jsonify({"status": "started"})

    def get_wled_status(self, request) -> None:
        wled = self.plugin.wled
        if wled:
            if not wled.device:
                try:
                    wled.update()
                except (
                    WLEDEmptyResponseError,
                    WLEDConnectionError,
                    WLEDConnectionTimeoutError,
                ) as exception:
                    error = f"Error connecting to WLED at {wled.host}"
                    self._logger.error(error)
                    self._logger.error(repr(exception))
                    self.plugin.send_message(
                        "api_get",
                        {
                            "connected": False,
                            "error": error,
                            "exception": repr(exception),
                        },
                    )
                    return
                except Exception as e:
                    error = f"Unknown error connecting to WLED at {wled.host}, consult the log for details."
                    self._logger.error(error)
                    self._logger.error(repr(e))
                    self.plugin.send_message(
                        "api_get",
                        {
                            "connected": False,
                            "error": error,
                            "exception": repr(e),
                        },
                    )
                    return

            response = {
                "connected": True,
                "effects": util.effects_to_dict(wled.device.effects),
                "connection_info": {
                    "version": wled.device.info.version,
                    "host": wled.host,
                    "port": wled.port,
                },
            }
        else:
            # No wled class, probably not configured yet
            response = {
                "connected": False,
                "error": "No hostname has been configured",
                "exception": "",
            }

        self.plugin.send_message("api_get", response)

    def test_wled(self, data) -> None:
        """
        Tests if the WLED device is reachable from OctoPrint
        by making a single request to the JSON API
        :param data: request data, from the plugin API
        :return: flask.Response: JSON response to the API
        """
        self._logger.info("Testing connection with WLED")
        config = data["config"]
        if not config.get("auth"):
            config["password"] = None
            config["username"] = None
        with WLED(
            host=config.get("host"),
            password=config.get("password", None),
            port=int(config.get("port", 80)),
            request_timeout=float(config.get("request_timeout", 8.0)),
            tls=config.get("tls", False),
            verify_ssl=config.get("verify_ssl", True),
            username=config.get("username", None),
            user_agent=f"OctoPrintWLED/{self.plugin._plugin_version}",
        ) as wled:
            try:
                device = wled.update()
                version = device.info.version
                response = {
                    "success": True,
                    "message": f"Connection to WLED {version} at {config.get('host')} successful",
                }
            except (
                WLEDEmptyResponseError,
                WLEDConnectionError,
                WLEDConnectionTimeoutError,
            ) as exception:
                error = f"Error connecting to WLED at {config.get('host')}"
                self._logger.error(error)
                self._logger.error(repr(exception))
                response = {
                    "success": False,
                    "error": error,
                    "exception": repr(exception),
                }

        self.plugin.send_message("api_post_test", response)
