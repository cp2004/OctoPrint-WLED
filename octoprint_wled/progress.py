import copy
import logging
from typing import Optional

import octoprint_wled
from octoprint_wled.util import hex_to_rgb
from octoprint_wled.wled.exceptions import (
    WLEDConnectionError,
    WLEDConnectionTimeoutError,
    WLEDEmptyResponseError,
)


class PluginProgressHandler:
    def __init__(self, plugin):
        self.plugin = plugin  # type: octoprint_wled.WLEDPlugin
        self._logger: logging.Logger = logging.getLogger(
            "octoprint.plugins.wled.progress"
        )

        self.last_print_progress: Optional[int] = None

    def on_print_progress(self, value):
        # Check WLED is setup & ready
        if not self.plugin.wled:
            return

        # Grab the settings
        # noinspection PyProtectedMember
        progress_enabled = self.plugin._settings.get_boolean(
            ["progress", "print", "enabled"]
        )
        # noinspection PyProtectedMember
        effect_settings = self.plugin._settings.get(["progress", "print", "settings"])
        lights_on = copy.copy(self.plugin.lights_on)
        turn_lights_on = False

        if not progress_enabled:
            self._logger.debug("Progress not enabled, not running")
            return

        if not effect_settings:
            self._logger.warning("Progress enabled but no settings found, chck config")
            return

        for segment in effect_settings:
            if segment["override_on"]:
                turn_lights_on = True

            self._logger.debug(f"Setting print progress to segment {segment['id']}")

            try:
                # Try and set the effect to WLED
                self.plugin.wled.segment(
                    segment_id=int(segment["id"]),
                    brightness=int(segment["brightness"]),
                    color_primary=hex_to_rgb(segment["color_primary"]),
                    color_secondary=hex_to_rgb(segment["color_secondary"]),
                    # color_tertiary=hex_to_rgb(segment["color_tertiary"]),  # Irrelevant to percent effect
                    effect="Percent",
                    intensity=int(value),
                    # speed=int(segment["speed"])   # Don't mess with speed here, pointless
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

        if turn_lights_on:
            self.plugin.activate_lights()
