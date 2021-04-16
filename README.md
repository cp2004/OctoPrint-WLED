# OctoPrint WLED Integration

[WLED](https://github.com/Aircoookie/WLED) is an awesome project, as is [OctoPrint](https://octoprint.org).
What could be better than an OctoPrint plugin for connecting the two?

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
- Displaying printing progress
- Highly configurable settings
- Easy to use UI
- ... and more!

**This project is still under development, please be patient as bugs are fixed and features are added!**

## Setup

### Compatibility

This plugin will only install on Python 3 systems. For a guide to upgrading (it's easy!), please see my
[blog post (octoprint.org)](https://octoprint.org/blog/2020/09/10/upgrade-to-py3/).

In addition, I can also only guarantee compatibility with OctoPrint 1.5.0 and newer.

### Install

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/cp2004/OctoPrint-WLED/releases/latest/download/release.zip

### Warning about installing from source

**If you install the plugin by downloading the source code from GitHub directly, it *will not work*.**

This is because the frontend code is built as part of the release process. For details of building this see below.

## Configuration

Configuration can be performed in the OctoPrint UI, under Settings > WLED Integration.


## Contributing

Contributions are welcome, full contributing guidelines are coming soon.

If you are feeling like contributing a new feature, feel free to open an issue so we can discuss!

To setup the node environment for frontend stuff:

* Install: `npm install`
* Watch JS development mode: `npm run dev`
* Watch CSS development mode: `npm run dev-css`
* Build both assets in release mode: `npm run release`

These files *should not* be checked in, they are built on release automatically by a GitHub action.

## Credits

This plugin wouldn't be possible without the great work from [@frenck](https://github.com/frenck) with the
[python-wled](https://github.com/frenck/python-wled) Python module that I was able to use. It has been slightly modified
to work better within an OctoPrint plugin, but it is a great module to work with. Thank you!

*[View the OctoPrint-WLED license](https://github.com/cp2004/OctoPrint-WLED/blob/main/LICENSE.md)*

*[View the python-wled license](https://github.com/cp2004/OctoPrint-WLED/blob/main/octoprint_wled/wled/LICENSE.md)*
