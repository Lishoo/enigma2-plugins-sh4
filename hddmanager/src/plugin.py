from . import _

from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo
from Plugins.Plugin import PluginDescriptor

from HddMount import MountHddOnStart, MountSwapOnStart

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
		if config.plugins.HddMount.MountOnStart.value:
			MountHddOnStart(config.plugins.HddMount.MountOnHdd.value,
				config.plugins.HddMount.MountOnMovie.value)
		if config.plugins.HddMount.SwapOnStart.value:
			MountSwapOnStart(config.plugins.HddMount.SwapFile.value)

def Plugins(**kwargs):
	return [PluginDescriptor(name =_("HDD mount manager"),
		description =_("Plugin to manage mounting and swapfile."),
		where = [PluginDescriptor.WHERE_PLUGINMENU,
		PluginDescriptor.WHERE_EXTENSIONSMENU], needsRestart = False, fnc = main),
	PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART,
		needsRestart = False, fnc = OnStart)]

