# coding=utf-8
from __future__ import absolute_import

import os
import sys


import octoprint.plugin
from octoprint.events import Events
import RPi.GPIO as GPIO
from time import sleep
from flask import jsonify
from octoprint.util import ResettableTimer
import flask

class CooldownfanPlugin(
						octoprint.plugin.StartupPlugin,
						octoprint.plugin.ShutdownPlugin,
						octoprint.plugin.EventHandlerPlugin,
						octoprint.plugin.TemplatePlugin,
						octoprint.plugin.SettingsPlugin,
						octoprint.plugin.SimpleApiPlugin,
						octoprint.plugin.AssetPlugin
						):

	def initialize(self):
		self.activated = 0
		self.last_cooldown_pin = -1
		self.turnOffTimer = None
		self.fanStatus = ""
		self._logger.info("Running RPi.GPIO version '{0}'".format(GPIO.VERSION))
		if GPIO.VERSION < "0.6":       # Need at least 0.6 for edge detection
			raise Exception("RPi.GPIO must be greater than 0.6")
		GPIO.setwarnings(False)        # Disable GPIO warnings

	def on_after_startup(self):
		self._logger.info("CooldownFan Plugin Starting...")
		self._setup_sensor()

	@property
	def pin_cooldown(self):
		return int(self._settings.get(["pin_cooldown"]))

	@property
	def run_time(self):
		return int(self._settings.get(["run_time"]))

	@property
	def normal_state(self):
		return int(self._settings.get(["normal_state"]))

	@property
	def fan_status(self):
		return self.fanStatus

	def get_template_configs(self):
		return [dict(type="settings", custom_bindings=True)]

	def _setup_sensor(self):
		self.cleanup_last_channel(self.last_cooldown_pin)
		self.last_cooldown_pin = self.pin_cooldown

		if self.cooldown_pin_enabled():
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(self.pin_cooldown, GPIO.OUT, initial=self.get_off_state())
			GPIO.output(self.pin_cooldown, self.get_off_state())


	def cleanup_last_channel(self, channel):
		if channel!=-1:
			try:
				GPIO.remove_event_detect(channel)
			except:
				pass
			try:
				GPIO.cleanup(channel)
			except:
				pass


	def get_settings_defaults(self):
		return dict(
			pin_cooldown	= -1,   # Default is no pin
			run_time		= 600,	# Default 5 minutes running time
			normal_state	= 0		# Normal (OFF) state is LOW
		)

	def on_settings_save(self, data):
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		self._setup_sensor()

	def cooldown_pin_enabled(self):
		return self.pin_cooldown != -1
	
	def on_event(self, event, payload):
		if event == Events.PRINT_DONE:
			self.startCoolingDown()
		elif event == Events.PRINT_STARTED:
			self.turnOffCoolingFan()
    
	def startCoolingDown(self):
		self.fanStatus = "Start cooling fan on GPIO {} for {} seconds!".format(self.pin_cooldown, self.run_time)
		self._logger.info(self.fanStatus)
		self.disableFanTimer()
		if self.cooldown_pin_enabled():
			GPIO.output(self.pin_cooldown, self.get_on_state())
			self.turnOffTimer = ResettableTimer(self.get_valid_time_seconds(), self.turnOffCoolingFan)
			self.turnOffTimer.start()

	def turnOffCoolingFan(self):
		self.fanStatus = "Fan turned off"
		self.disableFanTimer()
		if self.cooldown_pin_enabled():
			GPIO.output(self.pin_cooldown, self.get_off_state())
		
	def disableFanTimer(self):
		if self.turnOffTimer!=None:
			self.turnOffTimer.cancel()
		self.turnOffTimer=None

	def get_valid_time_seconds(self):
		t = self.run_time
		if t<5:
			return 5
		else:
			return t
	
	def get_off_state(self):
		if self.normal_state==0:
			return GPIO.LOW
		return GPIO.HIGH

	def get_on_state(self):
		if self.normal_state==0:
			return GPIO.HIGH
		return GPIO.LOW

	##~~ simpleApiPlugin
	def get_api_commands(self):
		return dict(fan_on=["pin","time","normal"],fan_off=["pin","time","normal"],pull_status=["rnd"])

	def on_api_command(self, command, data):
		if command == "fan_on":
			try:
				selected_pin = int(data.get("pin"))
				selected_time = int(data.get("time"))
				selected_normal = int(data.get("normal"))
				self._settings.set(["pin_cooldown"],selected_pin)
				self._settings.set(["run_time"],selected_time)
				self._settings.set(["normal_state"],selected_normal)
				self._setup_sensor()
				self.startCoolingDown()
				return flask.jsonify(dict(status="y",fanStatus=self.fanStatus)), 200
			except ValueError:
				return flask.jsonify(dict(status="n",fanStatus=self.fanStatus)), 200

		elif command == "fan_off":
			try:
				selected_pin = int(data.get("pin"))
				selected_time = int(data.get("time"))
				selected_normal = int(data.get("normal"))
				self._settings.set(["pin_cooldown"],selected_pin)
				self._settings.set(["run_time"],selected_time)
				self._settings.set(["normal_state"],selected_normal)
				self.turnOffCoolingFan()
				return flask.jsonify(dict(status="y",fanStatus=self.fanStatus)), 200
			except ValueError:
				return flask.jsonify(dict(status="n",fanStatus=self.fanStatus)), 200
		elif command == "pull_status":
				return flask.jsonify(dict(status="y",fanStatus=self.fanStatus)), 200

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/cooldownfan.js"],
			css=["css/cooldownfan.css"],
			less=["less/cooldownfan.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			cooldownfan=dict(
				displayName="Cooldown Fan",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="fmalekpour",
				repo="OctoPrint-Cooldownfan",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/fmalekpour/OctoPrint-Cooldownfan/archive/{target_version}.zip"
			)
		)


__plugin_name__ = "Cooldown Fan"

__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = CooldownfanPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

