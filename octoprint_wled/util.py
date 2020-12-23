# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import octoprint.plugin


def get_wled_params(settings: octoprint.plugin.PluginSettings):
    return {
        "host": settings.get(["connection", "host"]),
        "port": settings.get_int(["connection", "port"]),
        "request_timeout": settings.get_int(["connection", "request_timeout"]),
        "tls": settings.get(["connection", "tls"]),
        # username/password only if auth is configured
        "username": settings.get(["connection", "username"])
        if settings.get_boolean(["connection", "auth"])
        else None,
        "password": settings.get(["connection", "password"])
        if settings.get_boolean(["connection", "auth"])
        else None,
    }
