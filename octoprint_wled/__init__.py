# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import threading
from typing import Any, Dict, List, Mapping, Optional, Union

import octoprint.plugin
from flask import jsonify

from octoprint_wled import _version, api, comm
from octoprint_wled.comm import WLEDComm

__version__ = _version.get_versions()["version"]


class WLEDPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SimpleApiPlugin,
):
    def __init__(self):
        super(WLEDPlugin, self).__init__()
        self.wled_comm: Optional[WLEDComm] = None
        self.api: Optional[api.PluginAPI] = None

    def initialize(self) -> None:
        # Called after all injections complete, startup of plugin
        # Watch initialisation order, for dependency tracking
        self.init_wled()
        # API depends on wled_comm, initialised above
        self.api = api.PluginAPI(self)

    def init_wled(self) -> None:
        if self._settings.get(["connection", "host"]):
            # host is defined, we can try connecting
            self.wled_comm = WLEDComm(self, self._settings)

    # SimpleApiPlugin
    def get_api_commands(self) -> Dict[str, List[Optional[str]]]:
        return self.api.get_api_commands()

    def on_api_command(self, command, data):
        return self.api.on_api_command(command, data)

    def on_api_get(self, request):
        return self.api.on_api_get(request)

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
        }

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
