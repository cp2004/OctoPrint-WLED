---
layout: plugin

id: wled
title: WLED Connection
description: WLED is an awesome project, as is OctoPrint. What could be better than a plugin linking the two?
author: Charlie Powell
license: AGPLv3

# TODO
date: 2021-04-14

homepage: https://github.com/cp2004/OctoPrint-WLED
source: https://github.com/cp2004/OctoPrint-WLED
archive: https://github.com/cp2004/OctoPrint-WLED/releases/latest/download/release.zip

# Set this to true if your plugin uses the dependency_links setup parameter to include
# library versions not yet published on PyPi. SHOULD ONLY BE USED IF THERE IS NO OTHER OPTION!
#follow_dependency_links: false

tags:
  - wled
  - led
  - wireless
  - IoT
  - rgb led
  - status

# TODO
screenshots:
  - url: url of a screenshot, /assets/img/...
    alt: alt-text of a screenshot
    caption: caption of a screenshot
  - url: url of another screenshot, /assets/img/...
    alt: alt-text of another screenshot
    caption: caption of another screenshot
  - ...

# TODO
featuredimage: url of a featured image for your plugin, /assets/img/...


compatibility:
  octoprint:
    - 1.5.0
  python: ">=3.6,<4"

---

This plugin allows you to configure a WLED device to connect to OctoPrint, and the LEDs can react to different events
to display the status of your prints with ease!

Inspired by my other plugin, [OctoPrint WS281x LED Status](https://github.com/cp2004/OctoPrint-WS281x_LED_Status), it
aims to provide a similar experience of high configurability with ease of use.

#### Current features:

- Reacting to printer states including:
  - Idle
  - Disconnected
  - Print started
  - Print success
  - Print failed
  - Print paused
- Highly configurable settings
- Easy to use UI
- ... and more!

**This project is under early development, please be patient as bugs are fixed and features are added!**

## Setup

### Compatibility

This plugin will only install on Python 3 systems. For a guide to upgrading (it's easy!), please see the
[blog post (octoprint.org)](https://octoprint.org/blog/2020/09/10/upgrade-to-py3/).

In addition, I can also only guarantee compatibility with OctoPrint 1.5.0 and newer. The icons definitely won't work in
older versions. Please update!

### Install

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/cp2004/OctoPrint-WLED/releases/latest/download/release.zip

## Configuration

Configuration can be performed in the OctoPrint UI, under Settings > WLED Integration.

Pictures coming soon 😉!

## Credits

This plugin wouldn't be possible without the great work from [@frenck](https://github.com/frenck) with the
[python-wled](https://github.com/frenck/python-wled) Python module that I was able to use. It has been slightly modified
to work better within an OctoPrint plugin, but it is a great module to work with. Thank you!

*[View the OctoPrint-WLED license](https://github.com/cp2004/OctoPrint-WLED/blob/main/LICENSE.md)*

*[View the python-wled license](https://github.com/cp2004/OctoPrint-WLED/blob/main/octoprint_wled/wled/LICENSE.md)*
