# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import threading
from typing import Any, Iterable, Mapping

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


def start_thread(
    function: Any,
    args: Iterable = (),
    kwargs: Mapping[str, Any] = None,
    name: str = "WLED worker thread",
) -> threading.Thread:
    if kwargs is None:
        kwargs = {}
    t = threading.Thread(target=function, name=name, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
    return t
