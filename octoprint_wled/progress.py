import copy
import logging
from typing import Optional

import octoprint_wled
from octoprint_wled.util import hex_to_rgb


class PluginProgressHandler:
    def __init__(self, plugin):
        self.plugin = plugin  # type: octoprint_wled.WLEDPlugin
        self._logger: logging.Logger = logging.getLogger(
            "octoprint.plugins.wled.progress"
        )

        self.last_print_progress: Optional[int] = None

    def on_print_progress(self, value: int):
        self.set_progress(value, "print")

    def on_heating_progress(self, value: int):
        self.set_progress(value, "heating")

    def on_cooling_progress(self, value: int):
        self.set_progress(value, "cooling")

    def set_progress(self, value: int, progress_type: str):
        # Check WLED is setup & ready
        if not self.plugin.wled:
            return

        # Grab settings
        # noinspection PyProtectedMember
        enabled = self.plugin._settings.get_boolean(
            ["progress", progress_type, "enabled"]
        )
        # noinspection PyProtectedMember
        effect_settings = self.plugin._settings.get(
            ["progress", progress_type, "settings"]
        )
        lights_on = copy.copy(self.plugin.lights_on)
        turn_lights_on = False

        if not enabled:
            self._logger.debug(f"Progress {progress_type} not enabled, not running")

        if not effect_settings:
            self._logger.warning(
                f"Progress {progress_type} enabled but no settings found, check config"
            )

        for segment in effect_settings:
            if segment["override_on"]:
                turn_lights_on = True

            self._logger.debug(
                f"Setting {progress_type} progress to segment {segment['id']}"
            )
            # Try and set the effect to WLED
            self.plugin.runner.wled_call(
                self.plugin.wled.segment,
                kwargs={
                    "segment_id": int(segment["id"]),
                    "brightness": int(segment["brightness"]),
                    "color_primary": hex_to_rgb(segment["color_primary"]),
                    "color_secondary": hex_to_rgb(segment["color_secondary"]),
                    "effect": "Percent",
                    "intensity": int(value),
                    "on": lights_on,
                },
            )

        if turn_lights_on:
            self.plugin.activate_lights()
