"""
Synchronous Python Client for WLED
Based on the library by Franck Nijhof https://github.com/frenck/python-wled
Ported for use in OctoPrint without async functions
"""

from .models import (
    Device,
    Effect,
    Info,
    Leds,
    Nightlight,
    Palette,
    Segment,
    State,
    Sync,
)
from .wled import WLED, WLEDConnectionError, WLEDError  # noqa
