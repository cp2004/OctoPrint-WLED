/*
 * View model for OctoPrint WLED Plugin
 *
 * Author: Charlie Powell
 * License: AGPLv3
 */
import { nanoid } from 'nanoid'

const ko = window.ko
const OctoPrint = window.OctoPrint
const $ = window.$
const OCTOPRINT_VIEWMODELS = window.OCTOPRINT_VIEWMODELS

$(function () {
  function WLEDViewModel (parameters) {
    const self = this

    const allEventNames = [
      'idle',
      'disconnected',
      'started',
      'failed',
      'success',
      'paused'
    ]

    const allProgressNames = [
      'print',
      'heating',
      'cooling'
    ]

    self.settingsViewModel = parameters[0]

    self.lights_on = ko.observable(true)

    self.createEffectObservables = (u_id = 0) => ({
      unique_id: ko.observable(u_id),
      id: ko.observable(0),
      brightness: ko.observable(200),
      color_primary: ko.observable('#ffffff'),
      color_secondary: ko.observable('#000000'),
      color_tertiary: ko.observable('#000000'),
      effect: ko.observable('Solid'),
      intensity: ko.observable(127),
      speed: ko.observable(127),
      override_on: ko.observable(false)
    })

    self.createProgressObservables = (uid = 0) => ({
      unique_id: ko.observable(uid),
      id: ko.observable(0),
      brightness: ko.observable(200),
      color_primary: ko.observable('#ffffff'),
      color_secondary: ko.observable('#000000'),
      override_on: ko.observable(false)
    })

    self.setEditingObservables = (effect, data) => {
      effect.editing(data)
    }

    self.setEffectsFromSettings = () => {
      const settings = self.settingsViewModel.settings.plugins.wled
      allEventNames.forEach((name) => {
        self.effects[name].enabled(settings.effects[name].enabled())
        self.effects[name].segments([])
        settings.effects[name].settings().forEach((segment, index) => {
          const observables = self.createEffectObservables()
          observables.unique_id(
            settings.effects[name].settings()[index].unique_id()
          )
          observables.id(settings.effects[name].settings()[index].id())
          observables.brightness(
            settings.effects[name].settings()[index].brightness()
          )
          observables.color_primary(
            settings.effects[name].settings()[index].color_primary()
          )
          observables.color_secondary(
            settings.effects[name].settings()[index].color_secondary()
          )
          observables.color_tertiary(
            settings.effects[name].settings()[index].color_tertiary()
          )
          observables.effect(settings.effects[name].settings()[index].effect())
          observables.speed(settings.effects[name].settings()[index].speed())
          observables.intensity(settings.effects[name].settings()[index].intensity())
          observables.override_on(
            settings.effects[name].settings()[index].override_on()
          )
          self.effects[name].segments.push(observables)
        })
      })
      allProgressNames.forEach(name => {
        self.progress[name].enabled(settings.progress[name].enabled())
        self.progress[name].segments([])
        settings.progress[name].settings().forEach((segment, index) => {
          const observables = self.createProgressObservables()
          observables.unique_id(settings.progress[name].settings()[index].unique_id())
          observables.id(settings.progress[name].settings()[index].id())
          observables.brightness(
            settings.progress[name].settings()[index].brightness()
          )
          observables.color_primary(
            settings.progress[name].settings()[index].color_primary()
          )
          observables.color_secondary(
            settings.progress[name].settings()[index].color_secondary()
          )
          observables.override_on(
            settings.progress[name].settings()[index].override_on()
          )
          self.progress[name].segments.push(observables)
        })
      })
    }

    self.effects = (() => {
      const effects = {}
      allEventNames.forEach((eventName) => {
        effects[eventName] = {
          enabled: ko.observable(),
          segments: ko.observableArray([]),
          editing: ko.observable(self.createEffectObservables())
        }
      })
      return effects
    })()

    self.progress = (() => {
      const progress = {}
      allProgressNames.forEach((name) => {
        progress[name] = {
          enabled: ko.observable(),
          segments: ko.observableArray([]),
          editing: ko.observable(self.createProgressObservables())
        }
      })
      return progress
    })()

    self.addEffect = (name) => {
      const uid = nanoid(8) // Probability of collisions @ 1/hr is 271 years. AKA unlikely
      const newEffect = self.createEffectObservables(uid)
      self.effects[name].segments.push(newEffect)
      self.editEffect(name, newEffect)
    }

    self.addProgressEffect = (name) => {
      const uid = nanoid(8)
      const newEffect = self.createProgressObservables(uid)
      self.progress[name].segments.push(newEffect)
      self.editProgressEffect(name, newEffect)
    }

    self.editEffect = (name, data) => {
      // name: effect type (eg. 'idle')
      // data: object for editing effect
      const effect = self.effects[name]
      effect.editing(data)
      self.showEditModal(name)
    }

    self.editProgressEffect = (name, data) => {
      const effect = self.progress[name]
      effect.editing(data)
      self.showEditModal(name, 'Progress')
    }

    self.deleteEffect = (name, data) => {
      self.effects[name].segments.remove(data)
    }

    self.deleteProgressEffect = (name, data) => {
      self.progress[name].segments.remove(data)
    }

    self.showEditModal = (name, type) => {
      const dialogType = type || ''
      $('#WLED' + name + dialogType + 'EditModal').modal('show')
    }

    self.hideEditModal = (name, type) => {
      const dialogType = type || ''
      $('#WLED' + name + dialogType + 'EditModal').modal('hide')
    }

    // Generic state bindings
    self.requestInProgress = ko.observable(false)

    // Test connection observables & logic
    self.testConnectionStatus = ko.observable()
    self.testConnectionOK = ko.observable(false)
    self.testConnectionError = ko.observable()
    self.testInProgress = ko.observable()

    self.testConnection = () => {
      self.testInProgress(true)
      self.testConnectionOK(true)
      self.testConnectionStatus('')
      self.testConnectionError('')
      OctoPrint.simpleApiCommand('wled', 'test', {
        config: ko.toJS(self.settingsViewModel.settings.plugins.wled.connection)
      })
    }

    self.fromTestResponse = (response) => {
      self.testInProgress(false)
      if (response.success) {
        self.testConnectionOK(true)
        self.testConnectionStatus(response.message)
        self.testConnectionError('')
      } else {
        self.testConnectionOK(false)
        self.testConnectionStatus(response.error)
        self.testConnectionError(response.exception)
      }
    }

    self.toggle_lights = () => {
      OctoPrint.simpleApiCommand(
        'wled',
        self.lights_on() ? 'lights_off' : 'lights_on'
      ).done((response) => {
        self.lights_on(response.lights_on)
      })
    }

    // API GET response handler
    // Response is displayed in connection status section of settings
    self.statusConnected = ko.observable(false)
    self.statusConnectionError = ko.observable()
    self.statusConnectionHost = ko.observable()
    self.statusConnectionPort = ko.observable()
    self.statusConnectionVersion = ko.observable()
    self.availableEffects = ko.observableArray()

    self.fromGetResponse = (response) => {
      if (response.connected) {
        self.statusConnected(true)
        self.statusConnectionHost(response.connection_info.host)
        self.statusConnectionPort(response.connection_info.port)
        self.statusConnectionVersion(response.connection_info.version)
        self.availableEffects(self.listEffects(response.effects))
      } else {
        self.statusConnected(false)
        self.statusConnectionError(response.error + ': ' + response.exception)
      }
      self.requestInProgress(false)
    }

    self.listEffects = (effects) => effects.map(effect => effect.name)

    // Viewmodel callbacks
    self.onAfterBinding = self.onEventSettingsUpdated = () => {
      self.setEffectsFromSettings()
      self.requestInProgress(true)
      OctoPrint.simpleApiGet('wled').done(function (response) {
        self.lights_on(response.lights_on)
      })
    }

    self.onDataUpdaterPluginMessage = (plugin, data) => {
      if (plugin !== 'wled') {
        return
      }

      if (data.type === 'api_get') {
        self.fromGetResponse(data.content)
      } else if (data.type === 'api_post_test') {
        self.fromTestResponse(data.content)
      }
    }

    self.onSettingsBeforeSave = () => {
      allEventNames.forEach((name) => {
        self.settingsViewModel.settings.plugins.wled.effects[name].settings(
          self.effects[name].segments()
        )
        self.settingsViewModel.settings.plugins.wled.effects[name].enabled(
          self.effects[name].enabled()
        )
      })
      allProgressNames.forEach((name) => {
        self.settingsViewModel.settings.plugins.wled.progress[name].settings(
          self.progress[name].segments()
        )
        self.settingsViewModel.settings.plugins.wled.progress[name].enabled(
          self.progress[name].enabled()
        )
      })
    }
  }
  OCTOPRINT_VIEWMODELS.push({
    construct: WLEDViewModel,
    name: 'WLEDViewModel', // Required because webpack in production inlines it, and it has no name
    dependencies: ['settingsViewModel'],
    elements: ['#settings_plugin_wled', '#navbar_plugin_wled']
  })
})
