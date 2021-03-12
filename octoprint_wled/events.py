# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import copy
import logging
from typing import Any, Dict, Optional

from octoprint.events import Events

import octoprint_wled
from octoprint_wled.util import hex_to_rgb, start_thread
from octoprint_wled.wled.exceptions import (
    WLEDConnectionError,
    WLEDConnectionTimeoutError,
    WLEDEmptyResponseError,
    WLEDError,
)


class PluginEventHandler:
    def __init__(self, plugin):
        self.plugin = plugin  # type: octoprint_wled.WLEDPlugin
        self._logger: logging.Logger = logging.getLogger(
            "octoprint.plugins.wled.events"
        )

        self.event_to_effect: Dict[str, str] = {
            Events.CONNECTED: "idle",
            Events.DISCONNECTED: "disconnected",
            Events.PRINT_STARTED: "started",
            Events.PRINT_FAILED: "failed",
            Events.PRINT_DONE: "success",
            Events.PRINT_PAUSED: "paused",
        }

        self.last_event: Optional[str] = None

    def on_event(self, event, payload) -> None:
        if event in self.event_to_effect.keys():
            self.last_event = event
            start_thread(
                self.update_effect, kwargs={"effect": self.event_to_effect[event]}
            )

    def update_effect(self, effect) -> None:
        """
        Updates the effect running on the specified segment in WLED
        :param effect: name of the effect to run, internal identifier (not WLED)
        :return: None
        """
        # Check WLED is setup & ready
        if not self.plugin.wled:
            return

        # Grab the settings
        # noinspection PyProtectedMember
        effect_enabled = self.plugin._settings.get_boolean(
            ["effects", effect, "enabled"]
        )
        effect_settings = self.plugin._settings.get(["effects", effect, "settings"])
        lights_on = copy.copy(self.plugin.lights_on)

        if not effect_enabled:
            self._logger.debug("Effect not enabled, not running")
            return
        if not effect_settings:
            self._logger.warning(
                "Effect enabled but no settings could be found, check config"
            )
            return

        # Loop through segments, set the brightness, report any problems
        for segment in effect_settings:
            if segment["override_on"]:
                lights_on = True

            try:
                # Set the effect on WLED
                self._logger.debug(
                    f"setting {segment['effect']} to segment {segment['id']}"
                )
                self.plugin.wled.segment(
                    segment_id=int(segment["id"]),
                    brightness=int(segment["brightness"]),
                    color_primary=hex_to_rgb(segment["color_primary"]),
                    color_secondary=hex_to_rgb(segment["color_secondary"]),
                    color_tertiary=hex_to_rgb(segment["color_tertiary"]),
                    effect=segment["effect"],
                    intensity=int(segment["intensity"]),
                    speed=int(segment["speed"]),
                    on=lights_on,
                )
                response = {}
            except (
                WLEDEmptyResponseError,
                WLEDConnectionError,
                WLEDConnectionTimeoutError,
            ) as exception:
                # Known exception, reported to frontend on the websocket
                error = f"Error setting {segment['effect']} to segment {segment['id']}"
                self._logger.error(error),
                self._logger.error(repr(exception))
                response = {
                    "success": False,
                    "error": error,
                    "exception": repr(exception),
                }
            except Exception as exception:
                # Something else wrong... Needs handling to report to user.
                error = (
                    f"Unexpected error setting {segment['effect']} to segment {segment['id']}, "
                    f"consult the log for details."
                )
                self._logger.error(error)
                self._logger.exception(exception)
                response = {"success": False, "error": error, "exception": ""}

            if response:
                # Update the UI if necessary
                self.plugin.send_message("event_update_effect", response)

    def restart(self) -> None:
        """
        Process the last event again, called when settings are changed
        :return: None
        """
        self.on_event(self.last_event, {})
