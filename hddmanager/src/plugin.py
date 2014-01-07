from . import _

from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo
from Plugins.Plugin import PluginDescriptor

from HddMount import MountHddOnStart

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
			SwapFile = config.plugins.HddMount.SwapFile.value
			if SwapFile != "no":
				if SwapFile[:2] == "sd":
					from Components.Console import Console
					Console().ePopen("swapon /dev/%s" % SwapFile[:4])
				else:
					enableswap = True
		if config.plugins.HddMount.MountOnStart.value:
			print "[HddManager] MountOnStart"
			MountHddOnStart(config.plugins.HddMount.MountOnHdd.value,
				config.plugins.HddMount.MountOnMovie.value, enableswap)
		elif enableswap:
			MountHddOnStart("nothing", "nothing", enableswap)

def Plugins(**kwargs):
	return [PluginDescriptor(name =_("HDD mount manager"),
		description =_("Plugin to manage mounting and swapfile."),
		where = [PluginDescriptor.WHERE_PLUGINMENU,
		PluginDescriptor.WHERE_EXTENSIONSMENU], needsRestart = False, fnc = main),
		PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART,
		needsRestart = False, fnc = OnStart)]

