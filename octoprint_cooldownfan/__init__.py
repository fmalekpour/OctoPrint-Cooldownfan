# coding=utf-8
from __future__ import absolute_import

import os
import sys


import octoprint.plugin
from octoprint.events import Events
import RPi.GPIO as GPIO
from time import sleep
from flask import jsonify

class CooldownfanPlugin(
						octoprint.plugin.StartupPlugin,
						octoprint.plugin.ShutdownPlugin,
						octoprint.plugin.EventHandlerPlugin,
						octoprint.plugin.TemplatePlugin,
						octoprint.plugin.SettingsPlugin
						):

	def initialize(self):
		self.activated = 0
		self.last_cooldown_pin = -1
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

	def get_template_configs(self):
		return [dict(type="settings", custom_bindings=False)]

	def _setup_sensor(self):
		self.cleanup_last_channel(self.last_cooldown_pin)
		self.last_cooldown_pin = self.pin_cooldown

		if self.cooldown_pin_enabled():
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(self.pin_cooldown, GPIO.OUT, initial=GPIO.LOW)
			GPIO.output(self.pin_cooldown, GPIO.LOW)


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
		)

	def on_settings_save(self, data):
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		self._setup_sensor()

	def cooldown_pin_enabled(self):
		return self.pin_cooldown != -1
	


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

