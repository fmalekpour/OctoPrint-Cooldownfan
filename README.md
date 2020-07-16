# OctoPrint-Cooldownfan

At the end of printing, I had to wait a long time for hotbed to cool down in order to remove the print. So I attached two large fan to top of the printer, connected them to a relay module and signalled it from GPIO on Raspberry Pi. This plugin controlls the relay module and turns ON the fan for defined amount of time at the end of printing.

<img src="/screenshots/gpio-cooldownfan_bb.jpg?raw=true" width="500px">

<img src="/fmalekpour/OctoPrint-Cooldownfan/raw/master/screenshots/fan.jpg" width="500px">


## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/fmalekpour/OctoPrint-Cooldownfan/archive/master.zip



## Configuration

In web interface, install the plugin and reload if necessary, then click on GPIO Shutdown, you will have:

- Pin Cooldown: Which Raspberry Pi GPIO pin (BCM Mode) your cooldown fan relay or mosfet is attached to.
- Run time: When printing finished, run the external cooldown fan for this amount of time.
- Normal State: State of the GPIO pin when fan is OFF.

In configuration screen, there are two buttons (Fan ON and Fan OFF) to test the fan functionality.

<img src="https://github.com/fmalekpour/OctoPrint-Cooldownfan/blob/master/screenshots/cool-down-fan-config-screen.jpg?raw=true" width="500px">

You can find the GPIO pin number assignments at [Raspberry Pi GPIO Pinout](https://www.raspberrypi.org/documentation/usage/gpio/).


#### Support me

This plugin was developed in my spare time.
If you find it useful and like it [Buy me a beer](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WHCDYE3DCBW2Y&source=url), cheers :)

