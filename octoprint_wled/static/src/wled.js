/*
 * View model for OctoPrint WLED Plugin
 *
 * Author: Charlie Powell
 * License: AGPLv3
 */
const ko = window.ko;
const OctoPrint = window.OctoPrint;

$(function () {
    function WLEDViewModel(parameters) {
        const self = this;

        const allEventNames = [
            "idle",
            "disconnected",
            "started",
            "failed",
            "success",
            "paused",
        ];

        self.settingsViewModel = parameters[0];

        self.lights_on = ko.observable(true);

        self.createEffectObservables = (u_id = 0) => {
            const effect = {};
            effect.unique_id = ko.observable(u_id);
            effect.id = ko.observable(0);
            effect.brightness = ko.observable(200);
            effect.color_primary = ko.observable("#ffffff");
            effect.color_secondary = ko.observable("#000000");
            effect.color_tertiary = ko.observable("#000000");
            effect.effect = ko.observable("Solid");
            effect.intensity = ko.observable(127);
            effect.speed = ko.observable(127);
            effect.override_on = ko.observable(false);
            return effect;
        };

        self.setEditingObservables = (effect, data) => {
            effect.editing(data);
        };

        self.setEffectsFromSettings = () => {
            const settings = self.settingsViewModel.settings.plugins.wled;
            allEventNames.forEach((name) => {
                self.effects[name].enabled(settings.effects[name].enabled());
                self.effects[name].segments([]);
                settings.effects[name].settings().forEach((segment, index) => {
                    let observables = self.createEffectObservables();
                    observables.unique_id(
                        settings.effects[name].settings()[index].unique_id()
                    );
                    observables.id(
                        settings.effects[name].settings()[index].id()
                    );
                    observables.brightness(
                        settings.effects[name].settings()[index].brightness()
                    );
                    observables.color_primary(
                        settings.effects[name].settings()[index].color_primary()
                    );
                    observables.color_secondary(
                        settings.effects[name]
                            .settings()
                            [index].color_secondary()
                    );
                    observables.color_tertiary(
                        settings.effects[name]
                            .settings()
                            [index].color_tertiary()
                    );
                    observables.effect(
                        settings.effects[name].settings()[index].effect()
                    );
                    observables.speed(
                        settings.effects[name].settings()[index].speed()
                    );
                    observables.override_on(
                        settings.effects[name].settings()[index].override_on()
                    );
                    self.effects[name].segments.push(observables);
                });
            });
        };

        self.effects = (() => {
            const effects = {};
            allEventNames.forEach((eventName) => {
                effects[eventName] = (function () {
                    const eventEffect = {};
                    eventEffect.enabled = ko.observable();
                    eventEffect.segments = ko.observableArray([]);
                    eventEffect.editing = ko.observable(
                        self.createEffectObservables()
                    );
                    return eventEffect;
                })();
            });
            return effects;
        })();

        self.addEffect = (name) => {
            const uid = self.new_uid(name);
            const new_effect = self.createEffectObservables(uid);
            self.effects[name].segments.push(new_effect);
            self.editEffect(name, new_effect);
        };

        self.new_uid = (name) => {
            let highest_uid = 0;
            _.forEach(self.effects[name].segments(), function (segment) {
                if (segment.unique_id() > highest_uid) {
                    highest_uid = segment.unique_id();
                }
            });
            return highest_uid + 1;
        };

        self.editEffect = (name, data) => {
            // name: effect type (eg. 'idle')
            // data: object for editing effect
            const effect = self.effects[name];
            self.setEditingObservables(effect, data);
            self.showEditModal(name);
        };

        self.deleteEffect = (name, data) => {
            self.effects[name].segments.remove(data);
        };

        self.showEditModal = (name) => {
            $("#WLED" + name + "EditModal").modal("show");
        };

        self.hideEditModal = (name) => {
            $("#WLED" + name + "EditModal").modal("hide");
        };

        // Generic state bindings
        self.requestInProgress = ko.observable(false);

        // Test connection observables & logic
        self.testConnectionStatus = ko.observable();
        self.testConnectionOK = ko.observable(false);
        self.testConnectionError = ko.observable();
        self.testInProgress = ko.observable();

        self.testConnection = () => {
            const config = {
                host: self.settingsViewModel.settings.plugins.wled.connection.host(),
                password: self.settingsViewModel.settings.plugins.wled.connection.password(),
                port: self.settingsViewModel.settings.plugins.wled.connection.port(),
                request_timeout: self.settingsViewModel.settings.plugins.wled.connection.request_timeout(),
                tls: self.settingsViewModel.settings.plugins.wled.connection.tls(),
                username: self.settingsViewModel.settings.plugins.wled.connection.username(),
                auth: self.settingsViewModel.settings.plugins.wled.connection.auth(),
            };
            self.testInProgress(true);
            self.testConnectionOK(true);
            self.testConnectionStatus("");
            self.testConnectionError("");
            OctoPrint.simpleApiCommand("wled", "test", { config: config });
        };

        self.fromTestResponse = (response) => {
            self.testInProgress(false);
            if (response.success) {
                self.testConnectionOK(true);
                self.testConnectionStatus(response.message);
                self.testConnectionError("");
            } else {
                self.testConnectionOK(false);
                self.testConnectionStatus(response.error);
                self.testConnectionError(response.exception);
            }
        };

        self.toggle_lights = () => {
            OctoPrint.simpleApiCommand(
                "wled",
                self.lights_on() ? "lights_off" : "lights_on"
            ).done((response) => {
                self.lights_on(response.lights_on);
            });
        };

        // API GET response handler
        // Response is displayed in connection status section of settings
        self.statusConnected = ko.observable(false);
        self.statusConnectionError = ko.observable();
        self.statusConnectionHost = ko.observable();
        self.statusConnectionPort = ko.observable();
        self.statusConnectionVersion = ko.observable();
        self.availableEffects = ko.observableArray();

        self.fromGetResponse = (response) => {
            if (response.connected) {
                self.statusConnected(true);
                self.statusConnectionHost(response.connection_info.host);
                self.statusConnectionPort(response.connection_info.port);
                self.statusConnectionVersion(response.connection_info.version);
                self.availableEffects(self.listEffects(response.effects));
            } else {
                self.statusConnected(false);
                self.statusConnectionError(
                    response.error + ": " + response.exception
                );
            }
            self.requestInProgress(false);
        };

        self.listEffects = (effects) => {
            // parses effects from WLED data to simple list
            const effect_list = [];
            _.forEach(effects, function (effect) {
                effect_list.push(effect.name);
            });
            return effect_list;
        };

        // Viewmodel callbacks
        self.onAfterBinding = self.onEventSettingsUpdated = () => {
            self.setEffectsFromSettings();
            self.requestInProgress(true);
            OctoPrint.simpleApiGet("wled").done(function (response) {
                self.lights_on(response.lights_on);
            });
        };

        self.onDataUpdaterPluginMessage = (plugin, data) => {
            if (plugin !== "wled") {
                return;
            }

            if (data.type === "api_get") {
                self.fromGetResponse(data.content);
            } else if (data.type === "api_post_test") {
                self.fromTestResponse(data.content);
            }
        };

        self.onSettingsBeforeSave = () => {
            allEventNames.forEach((name) => {
                self.settingsViewModel.settings.plugins.wled.effects[
                    name
                ].settings(self.effects[name].segments());
                self.settingsViewModel.settings.plugins.wled.effects[
                    name
                ].enabled(self.effects[name].enabled());
            });
        };
    }
    OCTOPRINT_VIEWMODELS.push({
        construct: WLEDViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_wled", "#navbar_plugin_wled"],
    });
});
