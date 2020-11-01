# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import asyncio

import octoprint.plugin

from octoprint_wled.wled import WLED

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions


class WLEDPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
):
    wled = None

    def on_after_startup(self):
        self.wled = WLED("192.168.0.91", user_agent=f"OctoPrintWLED/{__plugin_version__}")
        device = self.wled.update()
        self._logger.info(f"Connection to WLED {device.info.version} successful")

    # SettingsPlugin mixin
    def get_settings_defaults(self):
        return {
            "address": None,
        }

    # AssetPlugin mixin
    def get_assets(self):
        return {
            "js": ["js/wled.js"],
            "css": ["css/wled.css"],
            "less": ["less/wled.less"],
        }

    # Software Update hook
    def get_update_information(self):
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
