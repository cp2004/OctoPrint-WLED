# OctoPrint WLED Integration

### This plugin is still under development, while it works it is incomplete. 
### If you want to see what is coming soon, have a look at the [the TODO issue](https://github.com/cp2004/OctoPrint-WLED/issues/2)

[WLED](https://github.com/Aircoookie/WLED) is an awesome project, [OctoPrint](https://octoprint.org)
is yet another awesome project. What could be better than an OctoPrint plugin for connecting the two?

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

    https://github.com/cp2004/OctoPrint-WLED/archive/main.zip

## Configuration

Configuration can be performed in the OctoPrint UI, under Settings > WLED Integration.

Pictures coming soon 😉!

## Credits

This plugin wouldn't be possible without the great work of [@frenck](https://github.com/frenck)'s
[python-wled](https://github.com/frenck/python-wled) Python module that I was able to use. It has been slightly modified
to work better within an OctoPrint plugin, but it is a great module to work with. Thank you!

[View the python-wled license](https://github.com/cp2004/OctoPrint-WLED/blob/main/octoprint_wled/wled/LICENSE.md)
