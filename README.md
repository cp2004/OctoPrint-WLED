# OctoPrint WLED Integration

### This plugin is still under development, not recommended you install it yet!

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
  - Print success
  - Print failed
  - Print paused
- Highly configurable settings
- Easy to use UI
- ... and more!

**This project is under early development, please be patient as bugs are fixed and features are added!**

## Setup

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
