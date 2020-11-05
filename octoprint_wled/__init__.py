# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import threading
from typing import Any, Dict, List, Mapping, Optional

import octoprint.plugin
from flask import jsonify

from octoprint_wled.wled import WLED
from octoprint_wled.wled.exceptions import (
    WLEDConnectionError,
    WLEDConnectionTimeoutError,
    WLEDEmptyResponseError,
    WLEDError,
)

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions


class WLEDPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SimpleApiPlugin,
):
    def __init__(self):
        super(WLEDPlugin, self).__init__()
        self.config_needed: bool = False
        self.config_valid: bool = True
        self.wled: Optional[WLED] = None
        self.error: bool = False  # This will let the user know on next refresh that
        self.errors: List[str] = []

    def on_after_startup(self) -> None:
        if not self._settings.get(["configured"]):
            # Not configured yet, no point trying to connect
            self.config_needed = True

            return

        if not self._settings.get(["connection", "host"]):
            # Address is empty: don't connect, TODO throw warning?
            self.config_valid = False
            self._logger.info("No address, not connecting.")
            return
        t = threading.Thread(target=self.connect, name="WLED Startup connection")
        t.daemon = True
        t.start()

    def connect(self) -> WLED:
        if not self.wled:
            self.wled = WLED(
                host=self._settings.get(["connection", "host"]),
                password=self._settings.get(["connection", "password"]),
                port=self._settings.get_int(["connection", "port"]),
                request_timeout=self._settings.get_int(
                    ["connection", "request_timeout"], min=0
                ),
                tls=self._settings.get_boolean(["connection", "tls"]),
                username=self._settings.get(["connection", "username"]),
                verify_ssl=self._settings.get(["connection", "verify_ssl"]),
                user_agent=f"OctoPrintWLED/{self._plugin_version}",
            )
        try:
            device = self.wled.update()
            self._logger.info(f"Connection to WLED {device.info.version} successful")
        except (
            WLEDEmptyResponseError,
            WLEDConnectionError,
            WLEDConnectionTimeoutError,
        ) as exception:
            self._logger.error(f"Error connecting to WLED, {exception}")
            self.log_error(exception)

        return self.wled

    def restart_wled(self) -> None:
        if self.test_configured():
            self.wled = None
            t = threading.Thread(target=self.connect, name="WLED Connect")
            t.daemon = True
            t.start()
        else:
            self.log_error("No hostname is configured, no connection can be made")

    def test_configured(self) -> bool:
        if self._settings.get(["connection", "host"]):
            self._settings.set_boolean(["configured"], True)
        else:
            self._settings.set_boolean(["configured"], False)

        return self._settings.get_boolean(["configured"])

    def get_device_info(self) -> Any:
        if self.wled:
            return self.wled.device.info
        else:
            return None

    def log_error(self, exception: [str, BaseException]):
        self.error = True
        self.errors.append(repr(exception))

    # SimpleAPIPlugin
    def on_api_get(self, request):
        data = {"info": self.get_device_info()}
        if self.error:
            data.update(errors=self.errors)

        return jsonify(data)

    # SettingsPlugin
    def get_settings_defaults(self) -> dict:
        return {
            "configured": False,
            "connection": {
                "host": "",
                "password": "",
                "port": 80,
                "request_timeout": 8,
                "tls": False,
                "username": None,
                "verify_ssl": True,
            },
        }

    def on_settings_save(self, data):
        old_connection_settings = self._settings.get(["connection"])

        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        new_connection_settings = self._settings.get(["connection"])

        if new_connection_settings != old_connection_settings:
            self.restart_wled()

    # AssetPlugin
    def get_assets(self) -> dict:
        return {
            "js": ["js/wled.js"],
            "css": ["css/wled.css"],
            "less": ["less/wled.less"],
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
