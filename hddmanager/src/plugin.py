from . import _

from Components.config import config, ConfigSubsection, \
	ConfigText, ConfigYesNo
from Plugins.Plugin import PluginDescriptor

import HddMount, Manager


config.plugins.HddMount = ConfigSubsection()
config.plugins.HddMount.MountOnStart = ConfigYesNo(default = False)
config.plugins.HddMount.MountOnHdd = ConfigText(default = "nothing")
config.plugins.HddMount.MountOnMovie = ConfigText(default = "nothing")
config.plugins.HddMount.SwapOnStart = ConfigYesNo(default = False)
config.plugins.HddMount.SwapFile = ConfigText(default = "no")

def main(session, **kwargs):
	session.open(Manager.MountSetup)

EnigmaStart = False

def OnStart(reason, **kwargs):
	global EnigmaStart
	if reason == 0 and EnigmaStart == False: # Enigma start and not use reloadPlugins
		EnigmaStart = True
		HddMount.MountOnStart()

def Plugins(**kwargs):
	return [PluginDescriptor(name =_("HDD mount manager"),
		description =_("Plugin to manage mounting and swapfile."),
		where = [PluginDescriptor.WHERE_PLUGINMENU,
		PluginDescriptor.WHERE_EXTENSIONSMENU], needsRestart = False, fnc = main),
	PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART,
		needsRestart = False, fnc = OnStart)]

