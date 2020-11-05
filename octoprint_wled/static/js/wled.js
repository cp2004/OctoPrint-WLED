/*
 * View model for WLED
 *
 * Author: Charlie Powell
 * License: AGPLv3
 */
$(function() {
    function WLEDViewModel(parameters) {
        var self = this;

        self.settings = parameters[0]

        self.connectionStatus = ko.observable()
        self.architecture = ko.observable()
        self.numLEDs = ko.observable()
        self.version = ko.observable()
        self.wifi_bssid = ko.observable()
        self.wifi_channel = ko.observable()
        self.wifi_rssi = ko.observable()
        self.wifi_signal = ko.observable()

        self.onAllBound = self.onEventSettingsUpdated = function () {
            self.request_wled_data()
        }

        self.update_info = function (data) {
            console.log(data)
            if (data.errors){
                new PNotify({
                    'title': "WLED Error",
                    'text': data.errors,
                    'type': "error",
                    'hide': true,
                })
            }
            if (data.info){
                self.architecture(data.info.architecture)
                self.numLEDs(data.info.leds.count)
                self.version(data.info.version)
                self.wifi_bssid(data.info.wifi.bssid)
                self.wifi_channel(data.info.wifi.channel)
                self.wifi_rssi(data.info.wifi.rssi)
                self.wifi_signal(data.info.wifi.signal)
            }
        }


        self.request_wled_data = function (){
            OctoPrint.simpleApiGet("wled").done(self.update_info)
        }

        /* Settings handling */
        self.connection_host = ko.observable()
        self.connection_password = ko.observable()
        self.connection_port = ko.observable()
        self.connection_request_timeout = ko.observable()
        self.connection_tls = ko.observable()
        self.connection_username = ko.observable()
        self.connection_verify_ssl = ko.observable()

        self.onBeforeBinding = function () {
            console.log(self.settings.settings.plugins.wled)
            self.connection_host(self.settings.settings.plugins.wled.connection.host())
            self.connection_password(self.settings.settings.plugins.wled.connection.password())
            self.connection_port(self.settings.settings.plugins.wled.connection.port())
            self.connection_request_timeout(self.settings.settings.plugins.wled.connection.request_timeout())
            self.connection_tls(self.settings.settings.plugins.wled.connection.tls())
            self.connection_username(self.settings.settings.plugins.wled.connection.username())
            self.connection_verify_ssl(self.settings.settings.plugins.wled.connection.verify_ssl())
        }


        self.onSettingsBeforeSave = function (){
            self.settings.settings.plugins.wled.connection.host(self.connection_host())
            self.settings.settings.plugins.wled.connection.password(self.connection_password())
            self.settings.settings.plugins.wled.connection.port(self.connection_port())
            self.settings.settings.plugins.wled.connection.request_timeout(self.connection_request_timeout())
            self.settings.settings.plugins.wled.connection.tls(self.connection_tls())
            self.settings.settings.plugins.wled.connection.username(self.connection_username())
            self.settings.settings.plugins.wled.connection.verify_ssl(self.connection_verify_ssl())
        }
    }
    OCTOPRINT_VIEWMODELS.push({
        construct: WLEDViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_wled"]
    });
});
