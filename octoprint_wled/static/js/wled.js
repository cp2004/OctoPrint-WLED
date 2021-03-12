/*
 * View model for OctoPrint WLED Plugin
 *
 * Author: Charlie Powell
 * License: AGPLv3
 */
$(function () {
    function WLEDViewModel(parameters) {
        var self = this;

        self.allEventNames = ["idle", "disconnected", "started", "failed", "success", "paused"]

        self.settingsViewModel = parameters[0];

        self.createEffectObservables = function (u_id = 0) {
            let effect = {};
            effect.unique_id = ko.observable(u_id);
            effect.id = ko.observable(0);
            effect.brightness = ko.observable(200);
            effect.color_primary = ko.observable("#ffffff");
            effect.color_secondary = ko.observable("#000000");
            effect.color_tertiary = ko.observable("#000000");
            effect.effect = ko.observable("Solid");
            effect.intensity = ko.observable(127);
            effect.speed = ko.observable(127);
            effect.override_on = ko.observable(true);
            return effect;
        };

        self.setDefaultEffectObservables = function (object, uid) {
            object().id(0);
            object().brightness(200);
            object().color_primary("#ffffff");
            object().color_secondary("#000000");
            object().color_secondary("#000000");
            object().effect("Solid");
            object().intensity(127);
            object().speed(127);
            object().override_on(true);
        };

        self.setEditingObservables = function (effect, data) {
            effect.editing(data);
        };

        self.setEffectsFromSettings = function () {
            let plugin_settings = self.settingsViewModel.settings.plugins.wled;
            _.forEach(
                self.allEventNames,
                function (name) {
                    self.effects[name].enabled(
                        plugin_settings.effects[name].enabled()
                    );
                    self.effects[name].segments([]);
                    for (let segment in plugin_settings.effects[
                        name
                    ].settings()) {
                        let effect_observables = self.createEffectObservables();
                        effect_observables.unique_id(
                            plugin_settings.effects[name]
                                .settings()
                                [segment].unique_id()
                        );
                        effect_observables.id(
                            plugin_settings.effects[name]
                                .settings()
                                [segment].id()
                        );
                        effect_observables.brightness(
                            plugin_settings.effects[name]
                                .settings()
                                [segment].brightness()
                        );
                        effect_observables.color_primary(
                            plugin_settings.effects[name]
                                .settings()
                                [segment].color_primary()
                        );
                        effect_observables.color_secondary(
                            plugin_settings.effects[name]
                                .settings()
                                [segment].color_secondary()
                        );
                        effect_observables.color_tertiary(
                            plugin_settings.effects[name]
                                .settings()
                                [segment].color_tertiary()
                        );
                        effect_observables.effect(
                            plugin_settings.effects[name]
                                .settings()
                                [segment].effect()
                        );
                        effect_observables.speed(
                            plugin_settings.effects[name]
                                .settings()
                                [segment].speed()
                        );
                        effect_observables.override_on(
                            plugin_settings.effects[name]
                                .settings()
                                [segment].override_on()
                        );
                        self.effects[name].segments.push(effect_observables);
                    }
                }
            );
        };

        self.effects = (function () {
            let effects = {};

            _.forEach(
                self.allEventNames,
                function (eventName) {
                    effects[eventName] = (function () {
                        let eventEffect = {};
                        eventEffect.enabled = ko.observable();
                        eventEffect.segments = ko.observableArray([]);
                        eventEffect.editing = ko.observable(self.createEffectObservables());
                        return eventEffect;
                    })();
                }
            )

            return effects;
        })();
        console.log(self.effects);

        self.addEffect = function (name) {
            let uid = self.new_uid(name);
            let new_effect = self.createEffectObservables(uid);
            self.effects[name].segments.push(new_effect);
            self.editEffect(name, new_effect);
        };

        self.new_uid = function (name) {
            let highest_uid = 0;
            _.forEach(self.effects[name].segments(), function (segment) {
                if (segment.unique_id() > highest_uid) {
                    highest_uid = segment.unique_id();
                }
            });
            return highest_uid + 1;
        };

        self.editEffect = function (name, data) {
            // name: effect type (eg. 'idle')
            // data: object for editing effect
            let effect = self.effects[name];
            self.setEditingObservables(effect, data);
            self.showEditModal(name);
        };

        self.saveEdit = function (name, data) {
            let effect = self.effects[name];
            let segment_unique_id = data.unique_id();
            for (let segment in self.effects[name].segments()) {
                if (
                    self.effects[name].segments()[segment].unique_id() ===
                    segment_unique_id
                ) {
                    self.effects[name].segments()[segment] = data;
                }
            }
            self.hideEditModal(name);
        };

        self.deleteEffect = function (name, data) {
            self.effects[name].segments.remove(data);
        };

        self.showEditModal = function (name) {
            $("#WLED" + name + "EditModal").modal("show");
        };

        self.hideEditModal = function (name) {
            $("#WLED" + name + "EditModal").modal("hide");
        };

        // Generic state bindings
        self.requestInProgress = ko.observable(false);

        // Test connection observables & logic
        self.testConnectionStatus = ko.observable();
        self.testConnectionOK = ko.observable(false);
        self.testConnectionError = ko.observable();
        self.testInProgress = ko.observable();

        self.testConnection = function () {
            let config = {
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

        self.fromTestResponse = function (response) {
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

        // API GET response handler
        // Response is displayed in connection status section of settings
        self.statusConnected = ko.observable(false);
        self.statusConnectionError = ko.observable();
        self.statusConnectionHost = ko.observable();
        self.statusConnectionPort = ko.observable();
        self.statusConnectionVersion = ko.observable();
        self.availableEffects = ko.observableArray();

        self.fromGetResponse = function (response) {
            console.log(response);
            if (response.connected) {
                self.statusConnected(true);
                self.statusConnectionHost(response.connection_info.host);
                self.statusConnectionPort(response.connection_info.port);
                self.statusConnectionVersion(response.connection_info.version);
                self.availableEffects(self.listEffects(response.effects));
                console.log(self.availableEffects());
            } else {
                self.statusConnected(false);
                self.statusConnectionError(
                    response.error + ": " + response.exception
                );
            }
            self.requestInProgress(false);
        };

        self.listEffects = function (effects) {
            // parses effects from WLED data to simple list
            let effect_list = [];
            _.forEach(effects, function (effect) {
                effect_list.push(effect.name);
            });
            console.log(effect_list);
            return effect_list;
        };

        // Viewmodel callbacks
        self.onAfterBinding = self.onEventSettingsUpdated = function () {
            self.setEffectsFromSettings();
            self.requestInProgress(true);
            OctoPrint.simpleApiGet("wled");
        };

        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin !== "wled") {
                return;
            }

            if (data.type === "api_get") {
                self.fromGetResponse(data.content);
            } else if (data.type === "api_post_test") {
                self.fromTestResponse(data.content);
            }
        };

        self.onSettingsBeforeSave = function () {
            _.forEach(
                ["idle", "disconnected", "started", "failed", "success", "paused"],
                function (name) {
                    self.settingsViewModel.settings.plugins.wled.effects[
                        name
                    ].settings(self.effects[name].segments());
                    self.settingsViewModel.settings.plugins.wled.effects[
                        name
                    ].enabled(self.effects[name].enabled());
                }
            );
        };

        self.toggle_flashlight = function () {
            OctoPrint.simpleApiCommand(
                "wled",
                "toggle_flashlight"
            ).done(update_light_status);
        };
    }
    OCTOPRINT_VIEWMODELS.push({
        construct: WLEDViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_wled"],
    });
});
