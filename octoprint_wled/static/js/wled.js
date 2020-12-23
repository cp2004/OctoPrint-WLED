/*
 * View model for OctoPrint WLED Plugin
 *
 * Author: Charlie Powell
 * License: AGPLv3
 */
$(function() {
    function WLEDViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0]

        // Generic state bindings
        self.requestInProgress = ko.observable(false)

        // Test connection observables & logic
        self.testConnectionStatus = ko.observable()
        self.testConnectionOK = ko.observable(false)
        self.testConnectionError = ko.observable()
        self.testInProgress = ko.observable()

        self.testConnection = function (){
            let config = {
                host: self.settingsViewModel.settings.plugins.wled.connection.host(),
                password: self.settingsViewModel.settings.plugins.wled.connection.password(),
                port: self.settingsViewModel.settings.plugins.wled.connection.port(),
                request_timeout: self.settingsViewModel.settings.plugins.wled.connection.request_timeout(),
                tls: self.settingsViewModel.settings.plugins.wled.connection.tls(),
                username: self.settingsViewModel.settings.plugins.wled.connection.username(),
                auth: self.settingsViewModel.settings.plugins.wled.connection.auth(),
            }
            self.testInProgress(true)
            self.testConnectionOK(true)
            self.testConnectionStatus("")
            self.testConnectionError("")
            OctoPrint.simpleApiCommand("wled", "test", {config: config}).done(function(response){
                self.testInProgress(false)
                if (response.success){
                    self.testConnectionOK(true)
                    self.testConnectionStatus(response.message)
                    self.testConnectionError("")
                } else {
                    self.testConnectionOK(false)
                    self.testConnectionStatus(response.error)
                    self.testConnectionError(response.exception)
                }
            })
        }

        // API GET response handler
        // Response is displayed in connection status section of settings
        self.statusConnected = ko.observable(false)
        self.statusConnectionError = ko.observable()
        self.statusConnectionHost = ko.observable()
        self.statusConnectionPort = ko.observable()
        self.statusConnectionVersion = ko.observable()

        self.fromResponse = function (response){
            if (response.connected){
                self.statusConnected(true)
                self.statusConnectionHost(response.connection_info.host)
                self.statusConnectionPort(response.connection_info.port)
                self.statusConnectionVersion(response.connection_info.version)
            } else {
                self.statusConnected(false)
                self.statusConnectionError(
                    response.error + ": " + response.exception
                )
            }
            self.requestInProgress(false)
        }

        // Viewmodel callbacks
        self.onAfterBinding = self.onEventSettingsUpdated = function (){
            self.requestInProgress(true)
            OctoPrint.simpleApiGet("wled").done(self.fromResponse)
        }
    }
    OCTOPRINT_VIEWMODELS.push({
        construct: WLEDViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_wled"]
    });
});
