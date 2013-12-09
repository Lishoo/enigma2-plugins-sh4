from . import _

from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo
from Plugins.Plugin import PluginDescriptor

config.plugins.HddMount = ConfigSubsection()
config.plugins.HddMount.MountOnStart = ConfigYesNo(default = False)
config.plugins.HddMount.MountOnHdd = ConfigText(default = "nothing")
config.plugins.HddMount.MountOnMovie = ConfigText(default = "nothing")
config.plugins.HddMount.SwapOnStart = ConfigYesNo(default = False)
config.plugins.HddMount.SwapFile = ConfigText(default = "no")

def main(session, **kwargs):
	from Manager import MountSetup
	session.open(MountSetup)

EnigmaStart = False

def OnStart(reason, **kwargs):
	global EnigmaStart
	if reason == 0 and EnigmaStart == False: # Enigma start and not use reloadPlugins
		EnigmaStart = True
		enableswap = False
		if config.plugins.HddMount.SwapOnStart.value:
			from Components.Console import Console
			SwapFile = config.plugins.HddMount.SwapFile.value
			if SwapFile != "no":
				if SwapFile[:2] == "sd":
					Console().ePopen("swapon /dev/%s" % SwapFile[:4])
				else:
					enableswap = True
		if config.plugins.HddMount.MountOnStart.value:
			from HddMount import MountHddOnStart
			MountHddOnStart(config.plugins.HddMount.MountOnHdd.value,
				config.plugins.HddMount.MountOnMovie.value, enableswap)
		elif enableswap:
			import os
			if os.path.exists("/media/hdd/swapfile"):
				Console().ePopen("swapon /media/hdd/swapfile")

def Plugins(**kwargs):
	return [PluginDescriptor(name =_("HDD mount manager"),
		description =_("Plugin to manage mounting and swapfile."),
		where = [PluginDescriptor.WHERE_PLUGINMENU,
		PluginDescriptor.WHERE_EXTENSIONSMENU], needsRestart = False, fnc = main),
		PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART,
		needsRestart = False, fnc = OnStart)]

