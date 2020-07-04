/*
 * View model for OctoPrint-Cooldownfan
 *
 * Author: Farhad Malekpour
 * License: AGPLv3
 */
$(function() {
    function CooldownfanViewModel(parameters) {
		var self = this;
		
		self.settingsViewModel = parameters[0];
		self.testResult = ko.observable(null);
		self.pullInterval = 0;

        self.cooldownFanON = function () {
			self.cooldownFanSwitch('fan_on');
		}

        self.cooldownFanOFF = function () {
			self.cooldownFanSwitch('fan_off');
		}

        self.cooldownFanSwitch = function (commnand) {
            $.ajax({
                    url: "/api/plugin/cooldownfan",
                    type: "post",
                    dataType: "json",
                    contentType: "application/json",
                    headers: {"X-Api-Key": UI_API_KEY},
                    data: JSON.stringify({
                        "command": commnand,
                        "pin": $("#pinCooldown").val(),
                        "time": $("#runTime").val(),
                        "normal": $("#normalState").val(),
                    }),
                    error: function () {
                        self.testResult("There was an error :(");
                    },
                    success: function (result) {
						self.testResult(result.fanStatus);
                    }
                }
            );
		}

		self.pullTick = function(th){
            $.ajax({
				url: "/api/plugin/cooldownfan",
				type: "post",
				dataType: "json",
				contentType: "application/json",
				headers: {"X-Api-Key": UI_API_KEY},
				data: JSON.stringify({
					"command": "pull_status",
					"rnd": Math.random(),
				}),
				error: function () {
					th.testResult("- - -");
				},
				success: function (result) {
					th.testResult(result.fanStatus);
				}
			}
		);
	}

		self.startPullingStatus = function(){
			self.pullInterval = setInterval(self.pullTick, 2000, self);
		}

		self.stopPullingStatus = function(){
			if(self.pullInterval)
			{
				clearInterval(self.pullInterval);
				self.pullInterval = 0;
			}
		}

        self.onSettingsShown = function () {
			self.testResult("");
			self.stopPullingStatus();
			self.startPullingStatus();
		}

		self.onSettingsHidden = function() {
			self.stopPullingStatus();
		}
    }


	OCTOPRINT_VIEWMODELS.push({
		construct: CooldownfanViewModel,
		dependencies: [ "settingsViewModel" ],
		// Elements to bind to, e.g. #settings_plugin_cooldownfan, #tab_plugin_cooldownfan, ...
		elements: [ "#settings_plugin_cooldownfan" ]
	});
	
});
