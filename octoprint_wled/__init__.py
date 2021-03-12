# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from typing import Any, Dict, List, Optional

import octoprint.plugin

from octoprint_wled import _version, api, events
from octoprint_wled.util import get_wled_params
from octoprint_wled.wled import WLED

__version__ = _version.get_versions()["version"]


class WLEDPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.EventHandlerPlugin,
):
    wled: Optional[WLED]
    api: Optional[api.PluginAPI]
    events: Optional[events.PluginEventHandler]
    lights_on: bool = True

    def initialize(self) -> None:
        # Called after all injections complete, startup of plugin
        self.init_wled()
        self.api = api.PluginAPI(self)
        self.events = events.PluginEventHandler(self)

    def init_wled(self) -> None:
        if self._settings.get(["connection", "host"]):
            # host is defined, we can try connecting
            self.wled = WLED(**get_wled_params(self._settings))
        else:
            self.wled = None

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

    # SettingsPlugin
    def get_settings_defaults(self) -> Dict[str, Any]:
        return {
            "connection": {
                "host": "",
                "auth": False,
                "username": None,
                "password": "",
                "port": 80,
                "request_timeout": 8,
                "tls": False,
                "verify_ssl": True,
            },
            "effects": {
                "idle": {"enabled": True, "settings": []},
                "disconnected": {"enabled": False, "settings": []},
                "failed": {"enabled": False, "settings": []},
                "started": {"enabled": False, "settings": []},
                "success": {"enabled": False, "settings": []},
                "paused": {"enabled": False, "settings": []},
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
                # TO ADD ANYTHING TO THIS LIST a settings migration must be configured. See TPLINK smartplug plugin
                # for inspiration :)
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
        return {
            "js": ["js/wled.js"],
            "css": ["css/wled.css"],
        }

    # Software Update hook
    def get_update_information(self) -> dict:
        return {
            "wled": {
                "displayName": "WLED Integration",
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
                "pip": "https://github.com/cp2004/OctoPrint-WLED/archive/{target_version}.zip",
            }
        }

    # Template plugin
    def get_template_configs(self):
        return [
            {"type": "generic", "custom_bindings": True},
        ]

__plugin_name__ = "WLED Integration"
__plugin_version__ = __version__
__plugin_pythoncompat__ = ">=3.6,<4"  # python 3.6+


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = WLEDPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
