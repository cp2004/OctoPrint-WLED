# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, Optional

import octoprint.plugin

from octoprint_wled.wled import WLED
from octoprint_wled.wled.exceptions import (
    WLEDConnectionError,
    WLEDConnectionTimeoutError,
    WLEDEmptyResponseError,
    WLEDError,
)


class WLEDComm:
    def __init__(
        self,
        plugin: octoprint.plugin.OctoPrintPlugin,
        settings: octoprint.plugin.PluginSettings,
    ):
        self.plugin: octoprint.plugin.OctoPrintPlugin = plugin
        self._settings: octoprint.plugin.PluginSettings = settings
        self._logger: logging.Logger = logging.getLogger("octoprint.plugins.wled.comm")

        self.host: str = self._settings.get(["connection", "host"])
        self.password: str = self._settings.get(["connection", "password"])
        self.port: int = self._settings.get_int(["connection", "port"])
        self.request_timeout: int = self._settings.get_int(
            ["connection", "request_timeout"]
        )
        self.tls: bool = self._settings.get_boolean(["connection", "tls"])
        self.username: str = self._settings.get(["connection", "username"])
        self._user_agent: str = f"OctoPrintWLED/{self.plugin._plugin_version}"

        self.wled: Optional[WLED] = None
