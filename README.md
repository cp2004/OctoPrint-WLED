# OctoPrint WLED Integration

[![GitHub issues](https://img.shields.io/github/issues/cp2004/OctoPrint-WLED?style=flat-square)](https://github.com/cp2004/OctoPrint-WLED/issues)
[![GitHub branch checks state](https://img.shields.io/github/checks-status/cp2004/OctoPrint-WLED/main?style=flat-square)](https://github.com/cp2004/OctoPrint-WLED/actions)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/cp2004/OctoPrint-WLED?label=latest%20release&sort=semver&style=flat-square)](https://github.com/cp2004/OctoPrint-WLED/releases)
[![GitHub release installs (latest by date)](https://img.shields.io/github/downloads/cp2004/OctoPrint-WLED/latest/total?label=Installs%40latest&style=flat-square)](https://github.com/cp2004/OctoPrint-WLED/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/cp2004/OctoPrint-WLED?style=flat-square)](https://github.com/cp2004/OctoPrint-WLED/releases)
[![GitHub Repo stars](https://img.shields.io/github/stars/cp2004/OctoPrint-WLED?style=flat-square)](https://github.com/cp2004/OctoPrint-WLED/stargazers)
[![GitHub](https://img.shields.io/github/license/cp2004/OctoPrint-WLED?style=flat-square)](https://github.com/cp2004/OctoPrint-WLED/blob/main/LICENSE.md)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/cp2004?style=flat-square)](https://github.com/sponsors/cp2004)

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
- Displaying printing, heating & cooling progress
- Controlling the lights using @ commands
- Highly configurable settings and an easy to use UI
- ... and more!

## Setup

### Compatibility

This plugin will only install on Python 3 systems. For a guide to upgrading (it's easy!), please see my
[blog post (octoprint.org)](https://octoprint.org/blog/2020/09/10/upgrade-to-py3/).

In addition, I can only guarantee compatibility with OctoPrint 1.5.0 and newer.

### Install

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/cp2004/OctoPrint-WLED/releases/latest/download/release.zip

### Warning about installing from source

**If you install the plugin by downloading the source code from GitHub directly, it *will not work*.**

This is because the frontend code is built as part of the release process. For details of building this see below.

## Configuration

Configuration can be performed in the OctoPrint UI, under Settings > WLED Integration.

## Sponsors

- [@KenLucke](https://github.com/KenLucke)
- [@iFrostizz](https://github.com/iFrostizz)
- [@CmdrCody51](https://github.com/CmdrCody51)

As well as 5 others supporting me regularly through [GitHub Sponsors](https://github.com/sponsors/cp2004)!

## Supporting my efforts

I created this project in my spare time, so if you have found it useful or enjoyed using it then please consider [supporting it's development!](https://github.com/sponsors/cp2004). You can sponsor monthly or one time, for any amount you choose.

## Credits

This plugin wouldn't be possible without the great work from [@frenck](https://github.com/frenck) with the
[python-wled](https://github.com/frenck/python-wled) Python module that I was able to use. It has been slightly modified
to work better within an OctoPrint plugin, but it is a great module to work with. Thank you!

*[View the OctoPrint-WLED license](https://github.com/cp2004/OctoPrint-WLED/blob/main/LICENSE.md)*

*[View the python-wled license](https://github.com/cp2004/OctoPrint-WLED/blob/main/octoprint_wled/wled/LICENSE.md)*
