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

        self.connectionStatus = ko.observable()
        self.connectionOK = ko.observable(false)
        self.connectionError = ko.observable()
        self.testInProgress = ko.observable()

        self.testConnection = function (){
            let config = {
                host: self.settingsViewModel.settings.plugins.wled.connection.host(),
                password: self.settingsViewModel.settings.plugins.wled.connection.password(),
                port: self.settingsViewModel.settings.plugins.wled.connection.port(),
                request_timeout: self.settingsViewModel.settings.plugins.wled.connection.request_timeout(),
                tls: self.settingsViewModel.settings.plugins.wled.connection.tls(),
                username: self.settingsViewModel.settings.plugins.wled.connection.username(),
                auth: self.settingsViewModel.settins.plugins.wled.auth(),
            }
            self.testInProgress(true)
            self.connectionOK(true)
            self.connectionStatus("")
            self.connectionError("")
            OctoPrint.simpleApiCommand("wled", "test", {config: config}).done(function(response){
                self.testInProgress(false)
                if (response.success){
                    self.connectionOK(true)
                    self.connectionStatus(response.message)
                    self.connectionError("")
                } else {
                    self.connectionOK(false)
                    self.connectionStatus(response.error)
                    self.connectionError(response.exception)
                }
            })
        }
    }
    OCTOPRINT_VIEWMODELS.push({
        construct: WLEDViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_wled"]
    });
});
