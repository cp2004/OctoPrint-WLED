import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import octoprint.plugin

from octoprint_wled import _version, api, constants, events, progress, runner
from octoprint_wled.util import calculate_heating_progress, get_wled_params
from octoprint_wled.wled import WLED

__version__ = _version.get_versions()["version"]


class WLEDPlugin(
    octoprint.plugin.ShutdownPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.ProgressPlugin,
):
    def __init__(self):
        super().__init__()
        self.wled: Optional[WLED] = None
        self.api: Optional[api.PluginAPI] = None
        self.events: Optional[events.PluginEventHandler] = None
        self.runner: Optional[runner.WLEDRunner] = None
        self.progress: Optional[progress.PluginProgressHandler] = None
        self.lights_on: bool = True

        self._logger: logging.Logger

        # Heating & cooling detection flags
        self.heating: bool = False
        self.cooling: bool = False
        self.target_temperature: Dict[str, int] = {"tool": 0, "bed": 0}
        self.current_heater_heating: Optional[str] = None
        self.tool_to_target: int = 0

        self.current_progress: int = 0

    def initialize(self) -> None:
        # Called after all injections complete, startup of plugin
        # These sub-modules depend on the rest of the plugin to be initialized.
        self.init_wled()
        self.api = api.PluginAPI(self)
        self.events = events.PluginEventHandler(self)
        self.runner = runner.WLEDRunner(self)
        self.progress = progress.PluginProgressHandler(self)

    def init_wled(self) -> None:
        if self._settings.get(["connection", "host"]):
            # host is defined, we can try connecting
            self.wled = WLED(**get_wled_params(self._settings))
        else:
            self.wled = None

    def activate_lights(self) -> None:
        self._logger.info("Turning WLED lights on")
        try:
            self.runner.wled_call(self.wled.master, kwargs={"on": True})
        except Exception as e:
            self._logger.error("Error while turning WLED lights on")
            self._logger.exception(repr(e))

        # Notify the UI
        # WARNING: this still occurs even if there was an error above - it prevents crucial blocking
        # in the gcode & temperatures received hooks. Which is bad, which is why this is not sync.
        self.send_message("lights", {"on": True})
        self.lights_on = True

    def deactivate_lights(self) -> None:
        self._logger.info("Turning WLED lights off")
        # TODO async?
        response = self.runner.wled_call(
            self.wled.master, kwargs={"on": False}, block=True
        )
        if response:
            # Notify the UI, if we got this far there was no issue
            self.send_message("lights", {"on": False})
            self.lights_on = False

    # Gcode tracking hook
    def process_gcode_queue(
        self,
        comm,
        phase,
        cmd: str,
        cmd_type,
        gcode: str,
        subcode=None,
        tags=None,
        *args,
        **kwargs,
    ):
        if gcode in constants.BLOCKING_TEMP_GCODES.keys():
            self.heating = True
            self.cooling = False  # can't do both at the same time...
            self.current_heater_heating = constants.BLOCKING_TEMP_GCODES[gcode]

        else:
            if self.heating:
                # Currently heating, now stopping
                self.heating = False
                if self._printer.is_printing():
                    self.progress.return_to_print_progress()

    def temperatures_received(
        self,
        comm,
        parsed_temps: Dict[str, Tuple[float, Union[float, None]]],
        *args,
        **kwargs,
    ):
        tool_key = self._settings.get(["progress", "heating", "tool_key"])

        # Find the tool target temperature
        try:
            tool_target = parsed_temps[f"T{tool_key}"][1]
        except KeyError:
            # Tool number was invalid, stick to whatever saved previously
            tool_target = self.target_temperature["tool"]

        # We don't always get the target when the printer is heating, instead None
        if tool_target is None or tool_target <= 0:
            tool_target = self.target_temperature["tool"]

        # Find the bed target temperature
        try:
            bed_target = parsed_temps["B"][1]
        except KeyError:
            # Bed doesn't exist? Probably won't need bed temp
            bed_target = self.target_temperature["tool"]

        if bed_target is None or bed_target <= 0:
            bed_target = self.target_temperature["bed"]

        # Save these for later, so that they can be used on the next round for the above
        self.target_temperature["tool"] = tool_target
        self.target_temperature["bed"] = bed_target

        if self.heating:
            if self.current_heater_heating == "tool":
                heater = f"T{tool_key}"
            else:
                heater = "B"
            try:
                current = parsed_temps[heater][0]
            except KeyError:
                self._logger.warning(
                    f"{heater} not found, can't show progress - check config"
                )
                self.heating = False
                # self.process_previous_event()
                return parsed_temps

            value = calculate_heating_progress(
                current, self.target_temperature[self.current_heater_heating]
            )
            self._logger.debug(f"Heating, progress {value}%")
            if self._settings.get(["progress", "heating", self.current_heater_heating]):
                self.progress.on_heating_progress(value)

        elif self.cooling:
            bed_or_tool = self._settings.get(["progress", "cooling", "bed_or_tool"])
            if bed_or_tool == "tool":
                heater = "T{}".format(
                    self._settings.get(["progress", "heating", "tool_key"])
                )
            else:
                heater = "B"

            current = parsed_temps[heater][0]

            if current < self._settings.get_int(["progress", "cooling", "threshold"]):
                self.cooling = False
                # Run PRINT_DONE again, instead of when it actually happened.
                self.events.update_effect("success")
                return parsed_temps

            value = calculate_heating_progress(
                current, self.target_temperature[bed_or_tool]
            )

            self._logger.debug(f"Cooling, progress {value}%")
            self.progress.on_cooling_progress(value)

        # MUST always return parsed_temps
        return parsed_temps

    # @ command handling - commands defined in constants.py
    def process_at_command(
        self, comm, phase, cmd: str, parameters: str, tags=None, *args, **kwargs
    ):
        if cmd != constants.AT_WLED or not self._settings.get_boolean(
            ["features", "atcommand"]
        ):
            return

        cmd = cmd.upper()
        parameters = parameters.upper()

        if parameters == constants.AT_PARAM_ON:
            self.activate_lights()
        elif parameters == constants.AT_PARAM_OFF:
            self.deactivate_lights()

    # SimpleApiPlugin
    def get_api_commands(self) -> Dict[str, List[Optional[str]]]:
        return self.api.get_api_commands()

    def on_api_command(self, command, data):
        return self.api.on_api_command(command, data)

    def on_api_get(self, request):
        return self.api.on_api_get(request)

    # UI Notifier
    def send_message(self, msg_type: str, msg_content: dict):
        self._plugin_manager.send_plugin_message(
            "wled", {"type": msg_type, "content": msg_content}
        )

    # Event handling
    def on_event(self, event, payload):
        self.events.on_event(event, payload)

    # Print Progress handling
    def on_print_progress(self, storage, path, progress_value):
        self.progress.on_print_progress(progress_value)

    # Shutdown handling
    def on_shutdown(self):
        self.runner.kill()

    # SettingsPlugin
    def get_settings_defaults(self) -> Dict[str, Any]:
        return {
            "connection": {
                "host": "",
                "auth": False,
                "username": None,
                "password": "",
                "port": 80,
                "request_timeout": 2,
                "tls": False,
                "verify_ssl": True,
            },
            "effects": {
                "idle": {"enabled": True, "settings": []},
                "disconnected": {
                    "enabled": True,
                    "settings": [
                        {
                            "brightness": 200,
                            "color_primary": "#000000",
                            "color_secondary": "#000000",
                            "color_tertiary": "#000000",
                            "effect": "Rainbow",
                            "id": 0,
                            "intensity": 127,
                            "override_on": False,
                            "speed": 127,
                            "unique_id": "CcU-Mih1",
                        }
                    ],
                },
                "failed": {
                    "enabled": True,
                    "settings": [
                        {
                            "brightness": 200,
                            "color_primary": "#00ff2a",
                            "color_secondary": "#000000",
                            "color_tertiary": "#000000",
                            "effect": "Wipe",
                            "id": 0,
                            "intensity": 127,
                            "override_on": False,
                            "speed": 127,
                            "unique_id": "21pW5WCy",
                        }
                    ],
                },
                "started": {
                    "enabled": False,
                    "settings": [
                        {
                            "brightness": 200,
                            "color_primary": "#ffffff",
                            "color_secondary": "#000000",
                            "color_tertiary": "#000000",
                            "effect": "Solid",
                            "id": 0,
                            "intensity": 127,
                            "override_on": False,
                            "speed": 127,
                            "unique_id": "5N8Sa14y",
                        }
                    ],
                },
                "success": {
                    "enabled": True,
                    "settings": [
                        {
                            "brightness": 200,
                            "color_primary": "#1adb00",
                            "color_secondary": "#000000",
                            "color_tertiary": "#000000",
                            "effect": "Washing Machine",
                            "id": 0,
                            "intensity": 127,
                            "override_on": False,
                            "speed": 127,
                            "unique_id": "POL9wP_Y",
                        }
                    ],
                },
                "paused": {
                    "enabled": True,
                    "settings": [
                        {
                            "brightness": 200,
                            "color_primary": "#3e33e1",
                            "color_secondary": "#000000",
                            "color_tertiary": "#1fdaff",
                            "effect": "Sinelon Dual",
                            "id": 0,
                            "intensity": 127,
                            "override_on": False,
                            "speed": "45",
                            "unique_id": "WtKQwSu0",
                        }
                    ],
                },
                # example settings entry, per segment
                # {
                #   "unique_id": 0              # UNIQUE internal ID of this segment. So it can be edited easily
                #   "id": 0,                    # Segment ID
                #   "brightness": 100,          # Segment brightness
                #   "color_primary": #ff0000,   # Effect colour 1
                #   "color_secondary": #00ff00  # Effect colour 2
                #   "color_tertiary": #0000ff,  # Effect colour 3
                #   "effect": "Solid",          # Effect name
                #   "intensity": 100,           # Effect intensity
                #   "speed": 100                # Effect speed
                #   "override_on": True         # Always turn the LEDs on
                # }
                # These should be created by the UI in this way, using the effect editor.
                # It is *not* recommended that you configure these manually, it will probably go wrong.
                # TO ADD ANYTHING TO THIS LIST a settings migration should be configured. See TP-Link Smartplug plugin
                # for inspiration :)
            },
            "progress": {
                "print": {
                    "enabled": True,
                    "settings": [
                        {
                            "brightness": 200,
                            "color_primary": "#00ff59",
                            "color_secondary": "#bb2525",
                            "id": 0,
                            "override_on": False,
                            "unique_id": "yqvg8h0c",
                        }
                    ],
                },
                "heating": {
                    "enabled": True,
                    "settings": [
                        {
                            "brightness": 200,
                            "color_primary": "#bb2525",
                            "color_secondary": "#0083f5",
                            "id": 0,
                            "override_on": False,
                            "unique_id": "sduhc3fh",
                        }
                    ],
                    "tool": True,
                    "bed": True,
                    "tool_key": "0",
                },
                "cooling": {
                    "enabled": True,
                    "settings": [
                        {
                            "brightness": 200,
                            "color_primary": "#bb2525",
                            "color_secondary": "#0083f5",
                            "id": 0,
                            "override_on": False,
                            "unique_id": "argrsh53",
                        }
                    ],
                    "bed_or_tool": "tool",
                    "tool_key": "0",
                    "threshold": "40",
                }
                # Progress effects have a similar layout to the above, HOWEVER without:
                # * color_tertiary
                # * effect
                # * speed
                # * intensity (controlled by progress value)
            },
            "development": False,
            "features": {
                "atcommand": True,
            },
        }

    def get_settings_version(self):
        return 1

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.init_wled()
        self.events.restart()

    # AssetPlugin
    def get_assets(self) -> Dict[str, List[str]]:
        if self._settings.get_boolean(["development"]):
            js = ["src/wled.js"]
        else:
            js = ["dist/wled.js"]

        return {
            "js": js,
            "css": ["dist/wled.css"],
        }

    # TemplatePlugin
    def get_template_vars(self):
        return {
            "version": self._plugin_version,
        }

    # Software Update hook
    def get_update_information(self) -> dict:
        return {
            "wled": {
                "displayName": "WLED Connection",
                "displayVersion": self._plugin_version,
                # version check: github repository
                "type": "github_release",
                "user": "cp2004",
                "repo": "OctoPrint-WLED",
                "current": self._plugin_version,
                "stable_branch": {
                    "name": "Stable",
                    "branch": "main",
                    "comittish": ["main"],
                },
                "prerelease_branches": [
                    {
                        "name": "Release Candidate",
                        "branch": "pre-release",
                        "comittish": ["pre-release", "main"],
                    }
                ],
                # update method: pip
                "pip": "https://github.com/cp2004/OctoPrint-WLED/releases/download/{target_version}/release.zip",
            }
        }


__plugin_name__ = "WLED Connection"
__plugin_version__ = __version__
__plugin_pythoncompat__ = ">=3.6,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = WLEDPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.process_gcode_queue,
        "octoprint.comm.protocol.temperatures.received": __plugin_implementation__.temperatures_received,
        "octoprint.comm.protocol.atcommand.queuing": __plugin_implementation__.process_at_command,
    }
