# -*- coding: utf-8 -*-

import logging

import flask

from octoprint_wled.wled import WLED
from octoprint_wled.wled.exceptions import (
    WLEDConnectionError,
    WLEDConnectionTimeoutError,
    WLEDEmptyResponseError,
    WLEDError,
)

CMD_TEST = "test"


class PluginAPI:
    def __init__(self, plugin):
        self.plugin = plugin
        self._settings = plugin._settings
        self._logger = logging.getLogger("octoprint.plugins.wled.api")

    @staticmethod
    def get_api_commands():
        return {CMD_TEST: ["config"]}

    def on_api_command(self, command, data):
        if command == CMD_TEST:
            return self.test_wled(data)

    def on_api_get(self, request):
        wled = self.plugin.wled
        if wled:
            if not wled.device:
                try:
                    wled.update()
                except (
                    WLEDEmptyResponseError,
                    WLEDConnectionError,
                    WLEDConnectionTimeoutError,
                ) as exception:
                    error = f"Error connecting to WLED at {wled.host}"
                    self._logger.error(error)
                    self._logger.error(repr(exception))
                    return flask.jsonify(
                        {
                            "connected": False,
                            "error": error,
                            "exception": repr(exception),
                        }
                    )
                except Exception as e:
                    error = f"Unknown error connecting to WLED at {wled.host}, consult the log for details."
                    self._logger.error(error)
                    self._logger.error(repr(e))
                    return flask.jsonify(
                        {
                            "connected": False,
                            "error": error,
                            "exception": repr(e),
                        }
                    )

            response = {
                "connected": True,
                "effects": wled.device.effects,
                "connection_info": {
                    "version": wled.device.info.version,
                    "host": wled.host,
                    "port": wled.port,
                },
            }
        else:
            # No wled class, probably not configured yet
            response = {
                "connected": False,
                "error": "No hostname has been configured",
                "exception": "",
            }

        return flask.jsonify(response)

    def test_wled(self, data):
        """
        Tests if the WLED device is reachable from OctoPrint
        by making a single request to the JSON API
        :param data: request data, from the plugin API
        :return: flask.Response: JSON response to the API
        """
        self._logger.info("Testing connection with WLED")
        config = data["config"]
        if not config.get("auth"):
            config["password"] = None
            config["username"] = None
        with WLED(
            host=config.get("host"),
            password=config.get("password", None),
            port=int(config.get("port", 80)),
            request_timeout=float(config.get("request_timeout", 8.0)),
            tls=config.get("tls", False),
            verify_ssl=config.get("verify_ssl", True),
            username=config.get("username", None),
            user_agent=f"OctoPrintWLED/{self.plugin._plugin_version}",
        ) as wled:
            try:
                device = wled.update()
                version = device.info.version
                response = {
                    "success": True,
                    "message": f"Connection to WLED {version} at {config.get('host')} successful",
                }
            except (
                WLEDEmptyResponseError,
                WLEDConnectionError,
                WLEDConnectionTimeoutError,
            ) as exception:
                error = f"Error connecting to WLED at {config.get('host')}"
                self._logger.error(error)
                self._logger.error(repr(exception))
                response = {
                    "success": False,
                    "error": error,
                    "exception": repr(exception),
                }

        return flask.jsonify(response)
