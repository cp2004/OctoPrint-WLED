/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (function() { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./octoprint_wled/static/src/wled.js":
/*!*******************************************!*\
  !*** ./octoprint_wled/static/src/wled.js ***!
  \*******************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var nanoid__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! nanoid */ \"./node_modules/nanoid/index.dev.js\");\n/*\n * View model for OctoPrint WLED Plugin\n *\n * Author: Charlie Powell\n * License: AGPLv3\n */\n\nvar ko = window.ko;\nvar OctoPrint = window.OctoPrint;\nvar $ = window.$;\nvar OCTOPRINT_VIEWMODELS = window.OCTOPRINT_VIEWMODELS;\n$(function () {\n  console.log('hi');\n\n  function WLEDViewModel(parameters) {\n    var self = this;\n    var allEventNames = ['idle', 'disconnected', 'started', 'failed', 'success', 'paused'];\n    var allProgressNames = ['print'];\n    self.settingsViewModel = parameters[0];\n    self.lights_on = ko.observable(true);\n\n    self.createEffectObservables = function () {\n      var u_id = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 0;\n      var effect = {};\n      effect.unique_id = ko.observable(u_id);\n      effect.id = ko.observable(0);\n      effect.brightness = ko.observable(200);\n      effect.color_primary = ko.observable('#ffffff');\n      effect.color_secondary = ko.observable('#000000');\n      effect.color_tertiary = ko.observable('#000000');\n      effect.effect = ko.observable('Solid');\n      effect.intensity = ko.observable(127);\n      effect.speed = ko.observable(127);\n      effect.override_on = ko.observable(false);\n      return effect;\n    };\n\n    self.createProgressObservables = function () {\n      var uid = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 0;\n      return {\n        unique_id: ko.observable(uid),\n        id: ko.observable(0),\n        brightness: ko.observable(200),\n        color_primary: ko.observable('#ffffff'),\n        color_secondary: ko.observable('#000000'),\n        override_on: ko.observable(false)\n      };\n    };\n\n    self.setEditingObservables = function (effect, data) {\n      effect.editing(data);\n    };\n\n    self.setEffectsFromSettings = function () {\n      var settings = self.settingsViewModel.settings.plugins.wled;\n      allEventNames.forEach(function (name) {\n        self.effects[name].enabled(settings.effects[name].enabled());\n        self.effects[name].segments([]);\n        settings.effects[name].settings().forEach(function (segment, index) {\n          var observables = self.createEffectObservables();\n          observables.unique_id(settings.effects[name].settings()[index].unique_id());\n          observables.id(settings.effects[name].settings()[index].id());\n          observables.brightness(settings.effects[name].settings()[index].brightness());\n          observables.color_primary(settings.effects[name].settings()[index].color_primary());\n          observables.color_secondary(settings.effects[name].settings()[index].color_secondary());\n          observables.color_tertiary(settings.effects[name].settings()[index].color_tertiary());\n          observables.effect(settings.effects[name].settings()[index].effect());\n          observables.speed(settings.effects[name].settings()[index].speed());\n          observables.override_on(settings.effects[name].settings()[index].override_on());\n          self.effects[name].segments.push(observables);\n        });\n      });\n      allProgressNames.forEach(function (name) {\n        self.progress[name].enabled(settings.progress[name].enabled());\n        self.progress[name].segments([]);\n        settings.progress[name].settings().forEach(function (segment, index) {\n          var observables = self.createProgressObservables();\n          observables.unique_id(settings.progress[name].settings()[index].unique_id());\n          observables.id(settings.progress[name].settings()[index].id());\n          observables.brightness(settings.progress[name].settings()[index].brightness());\n          observables.color_primary(settings.progress[name].settings()[index].color_primary());\n          observables.color_secondary(settings.progress[name].settings()[index].color_secondary());\n          observables.override_on(settings.progress[name].settings()[index].override_on());\n          self.progress[name].segments.push(observables);\n        });\n      });\n    };\n\n    self.effects = function () {\n      var effects = {};\n      allEventNames.forEach(function (eventName) {\n        effects[eventName] = function () {\n          var eventEffect = {};\n          eventEffect.enabled = ko.observable();\n          eventEffect.segments = ko.observableArray([]);\n          eventEffect.editing = ko.observable(self.createEffectObservables());\n          return eventEffect;\n        }();\n      });\n      return effects;\n    }();\n\n    self.progress = function () {\n      var progress = {};\n      allProgressNames.forEach(function (name) {\n        progress[name] = {\n          enabled: ko.observable(),\n          segments: ko.observableArray([]),\n          editing: ko.observable(self.createProgressObservables())\n        };\n      });\n      return progress;\n    }();\n\n    self.addEffect = function (name) {\n      var uid = (0,nanoid__WEBPACK_IMPORTED_MODULE_0__.nanoid)(8); // Probability of collisions @ 1/hr is 271 years. AKA unlikely\n\n      var newEffect = self.createEffectObservables(uid);\n      self.effects[name].segments.push(newEffect);\n      self.editEffect(name, newEffect);\n    };\n\n    self.addProgressEffect = function (name) {\n      var uid = (0,nanoid__WEBPACK_IMPORTED_MODULE_0__.nanoid)(8);\n      var newEffect = self.createProgressObservables(uid);\n      self.progress[name].segments.push(newEffect);\n      self.editProgressEffect(name, newEffect);\n    };\n\n    self.editEffect = function (name, data) {\n      // name: effect type (eg. 'idle')\n      // data: object for editing effect\n      var effect = self.effects[name];\n      effect.editing(data);\n      self.showEditModal(name);\n    };\n\n    self.editProgressEffect = function (name, data) {\n      var effect = self.progress[name];\n      effect.editing(data);\n      self.showEditModal(name, 'Progress');\n    };\n\n    self.deleteEffect = function (name, data) {\n      self.effects[name].segments.remove(data);\n    };\n\n    self.deleteProgressEffect = function (name, data) {\n      self.progress[name].segments.remove(data);\n    };\n\n    self.showEditModal = function (name, type) {\n      var dialogType = type || '';\n      $('#WLED' + name + dialogType + 'EditModal').modal('show');\n    };\n\n    self.hideEditModal = function (name, type) {\n      var dialogType = type || '';\n      $('#WLED' + name + dialogType + 'EditModal').modal('hide');\n    }; // Generic state bindings\n\n\n    self.requestInProgress = ko.observable(false); // Test connection observables & logic\n\n    self.testConnectionStatus = ko.observable();\n    self.testConnectionOK = ko.observable(false);\n    self.testConnectionError = ko.observable();\n    self.testInProgress = ko.observable();\n\n    self.testConnection = function () {\n      var config = {\n        host: self.settingsViewModel.settings.plugins.wled.connection.host(),\n        password: self.settingsViewModel.settings.plugins.wled.connection.password(),\n        port: self.settingsViewModel.settings.plugins.wled.connection.port(),\n        request_timeout: self.settingsViewModel.settings.plugins.wled.connection.request_timeout(),\n        tls: self.settingsViewModel.settings.plugins.wled.connection.tls(),\n        username: self.settingsViewModel.settings.plugins.wled.connection.username(),\n        auth: self.settingsViewModel.settings.plugins.wled.connection.auth()\n      };\n      self.testInProgress(true);\n      self.testConnectionOK(true);\n      self.testConnectionStatus('');\n      self.testConnectionError('');\n      OctoPrint.simpleApiCommand('wled', 'test', {\n        config: config\n      });\n    };\n\n    self.fromTestResponse = function (response) {\n      self.testInProgress(false);\n\n      if (response.success) {\n        self.testConnectionOK(true);\n        self.testConnectionStatus(response.message);\n        self.testConnectionError('');\n      } else {\n        self.testConnectionOK(false);\n        self.testConnectionStatus(response.error);\n        self.testConnectionError(response.exception);\n      }\n    };\n\n    self.toggle_lights = function () {\n      OctoPrint.simpleApiCommand('wled', self.lights_on() ? 'lights_off' : 'lights_on').done(function (response) {\n        self.lights_on(response.lights_on);\n      });\n    }; // API GET response handler\n    // Response is displayed in connection status section of settings\n\n\n    self.statusConnected = ko.observable(false);\n    self.statusConnectionError = ko.observable();\n    self.statusConnectionHost = ko.observable();\n    self.statusConnectionPort = ko.observable();\n    self.statusConnectionVersion = ko.observable();\n    self.availableEffects = ko.observableArray();\n\n    self.fromGetResponse = function (response) {\n      if (response.connected) {\n        self.statusConnected(true);\n        self.statusConnectionHost(response.connection_info.host);\n        self.statusConnectionPort(response.connection_info.port);\n        self.statusConnectionVersion(response.connection_info.version);\n        self.availableEffects(self.listEffects(response.effects));\n      } else {\n        self.statusConnected(false);\n        self.statusConnectionError(response.error + ': ' + response.exception);\n      }\n\n      self.requestInProgress(false);\n    };\n\n    self.listEffects = function (effects) {\n      // parses effects from WLED data to simple list\n      var effectList = [];\n      effects.forEach(function (effect) {\n        effectList.push(effect.name);\n      });\n      return effectList;\n    }; // Viewmodel callbacks\n\n\n    self.onAfterBinding = self.onEventSettingsUpdated = function () {\n      self.setEffectsFromSettings();\n      self.requestInProgress(true);\n      OctoPrint.simpleApiGet('wled').done(function (response) {\n        self.lights_on(response.lights_on);\n      });\n    };\n\n    self.onDataUpdaterPluginMessage = function (plugin, data) {\n      if (plugin !== 'wled') {\n        return;\n      }\n\n      if (data.type === 'api_get') {\n        self.fromGetResponse(data.content);\n      } else if (data.type === 'api_post_test') {\n        self.fromTestResponse(data.content);\n      }\n    };\n\n    self.onSettingsBeforeSave = function () {\n      allEventNames.forEach(function (name) {\n        self.settingsViewModel.settings.plugins.wled.effects[name].settings(self.effects[name].segments());\n        self.settingsViewModel.settings.plugins.wled.effects[name].enabled(self.effects[name].enabled());\n      });\n      allProgressNames.forEach(function (name) {\n        self.settingsViewModel.settings.plugins.wled.progress[name].settings(self.progress[name].segments());\n        self.settingsViewModel.settings.plugins.wled.progress[name].enabled(self.progress[name].enabled());\n      });\n    };\n  }\n\n  OCTOPRINT_VIEWMODELS.push({\n    construct: WLEDViewModel,\n    dependencies: ['settingsViewModel'],\n    elements: ['#settings_plugin_wled', '#navbar_plugin_wled']\n  });\n});\n\n//# sourceURL=webpack://octoprint-wled/./octoprint_wled/static/src/wled.js?");

/***/ }),

/***/ "./node_modules/nanoid/index.dev.js":
/*!******************************************!*\
  !*** ./node_modules/nanoid/index.dev.js ***!
  \******************************************/
/***/ (function(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"nanoid\": function() { return /* binding */ nanoid; },\n/* harmony export */   \"customAlphabet\": function() { return /* binding */ customAlphabet; },\n/* harmony export */   \"customRandom\": function() { return /* binding */ customRandom; },\n/* harmony export */   \"urlAlphabet\": function() { return /* reexport safe */ _url_alphabet_index_js__WEBPACK_IMPORTED_MODULE_0__.urlAlphabet; },\n/* harmony export */   \"random\": function() { return /* binding */ random; }\n/* harmony export */ });\n/* harmony import */ var _url_alphabet_index_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./url-alphabet/index.js */ \"./node_modules/nanoid/url-alphabet/index.js\");\n// This file replaces `index.js` in bundlers like webpack or Rollup,\n// according to `browser` config in `package.json`.\n\n\n\nif (true) {\n  // All bundlers will remove this block in the production bundle.\n  if (\n    typeof navigator !== 'undefined' &&\n    navigator.product === 'ReactNative' &&\n    typeof crypto === 'undefined'\n  ) {\n    throw new Error(\n      'React Native does not have a built-in secure random generator. ' +\n        'If you don’t need unpredictable IDs use `nanoid/non-secure`. ' +\n        'For secure IDs, import `react-native-get-random-values` ' +\n        'before Nano ID.'\n    )\n  }\n  if (typeof msCrypto !== 'undefined' && typeof crypto === 'undefined') {\n    throw new Error(\n      'Import file with `if (!window.crypto) window.crypto = window.msCrypto`' +\n        ' before importing Nano ID to fix IE 11 support'\n    )\n  }\n  if (typeof crypto === 'undefined') {\n    throw new Error(\n      'Your browser does not have secure random generator. ' +\n        'If you don’t need unpredictable IDs, you can use nanoid/non-secure.'\n    )\n  }\n}\n\nlet random = bytes => crypto.getRandomValues(new Uint8Array(bytes))\n\nlet customRandom = (alphabet, size, getRandom) => {\n  // First, a bitmask is necessary to generate the ID. The bitmask makes bytes\n  // values closer to the alphabet size. The bitmask calculates the closest\n  // `2^31 - 1` number, which exceeds the alphabet size.\n  // For example, the bitmask for the alphabet size 30 is 31 (00011111).\n  // `Math.clz32` is not used, because it is not available in browsers.\n  let mask = (2 << (Math.log(alphabet.length - 1) / Math.LN2)) - 1\n  // Though, the bitmask solution is not perfect since the bytes exceeding\n  // the alphabet size are refused. Therefore, to reliably generate the ID,\n  // the random bytes redundancy has to be satisfied.\n\n  // Note: every hardware random generator call is performance expensive,\n  // because the system call for entropy collection takes a lot of time.\n  // So, to avoid additional system calls, extra bytes are requested in advance.\n\n  // Next, a step determines how many random bytes to generate.\n  // The number of random bytes gets decided upon the ID size, mask,\n  // alphabet size, and magic number 1.6 (using 1.6 peaks at performance\n  // according to benchmarks).\n\n  // `-~f => Math.ceil(f)` if f is a float\n  // `-~i => i + 1` if i is an integer\n  let step = -~((1.6 * mask * size) / alphabet.length)\n\n  return () => {\n    let id = ''\n    while (true) {\n      let bytes = getRandom(step)\n      // A compact alternative for `for (var i = 0; i < step; i++)`.\n      let j = step\n      while (j--) {\n        // Adding `|| ''` refuses a random byte that exceeds the alphabet size.\n        id += alphabet[bytes[j] & mask] || ''\n        if (id.length === size) return id\n      }\n    }\n  }\n}\n\nlet customAlphabet = (alphabet, size) => customRandom(alphabet, size, random)\n\nlet nanoid = (size = 21) => {\n  let id = ''\n  let bytes = crypto.getRandomValues(new Uint8Array(size))\n\n  // A compact alternative for `for (var i = 0; i < step; i++)`.\n  while (size--) {\n    // It is incorrect to use bytes exceeding the alphabet size.\n    // The following mask reduces the random byte in the 0-255 value\n    // range to the 0-63 value range. Therefore, adding hacks, such\n    // as empty string fallback or magic numbers, is unneccessary because\n    // the bitmask trims bytes down to the alphabet size.\n    let byte = bytes[size] & 63\n    if (byte < 36) {\n      // `0-9a-z`\n      id += byte.toString(36)\n    } else if (byte < 62) {\n      // `A-Z`\n      id += (byte - 26).toString(36).toUpperCase()\n    } else if (byte < 63) {\n      id += '_'\n    } else {\n      id += '-'\n    }\n  }\n  return id\n}\n\n\n\n\n//# sourceURL=webpack://octoprint-wled/./node_modules/nanoid/index.dev.js?");

/***/ }),

/***/ "./node_modules/nanoid/url-alphabet/index.js":
/*!***************************************************!*\
  !*** ./node_modules/nanoid/url-alphabet/index.js ***!
  \***************************************************/
/***/ (function(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"urlAlphabet\": function() { return /* binding */ urlAlphabet; }\n/* harmony export */ });\n// This alphabet uses `A-Za-z0-9_-` symbols. The genetic algorithm helped\n// optimize the gzip compression for this alphabet.\nlet urlAlphabet =\n  'ModuleSymbhasOwnPr-0123456789ABCDEFGHNRVfgctiUvz_KqYTJkLxpZXIjQW'\n\n\n\n\n//# sourceURL=webpack://octoprint-wled/./node_modules/nanoid/url-alphabet/index.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	!function() {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = function(exports, definition) {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	!function() {
/******/ 		__webpack_require__.o = function(obj, prop) { return Object.prototype.hasOwnProperty.call(obj, prop); }
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	!function() {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = function(exports) {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	}();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = __webpack_require__("./octoprint_wled/static/src/wled.js");
/******/ 	
/******/ })()
;