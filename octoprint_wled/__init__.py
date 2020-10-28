# -*- coding: utf-8 -*-
from __future__ import absolute_import

import octoprint.plugin

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions


class WledPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
):

    # SettingsPlugin mixin
    def get_settings_defaults(self):
        return {}

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
__plugin_pythoncompat__ = ">=2.7,<4"  # python 2 and 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = WledPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
