from . import _

from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo
from Plugins.Plugin import PluginDescriptor

from time import sleep

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
			from HddMount import CheckMountDir, GetDevices, mountdevice
			device = GetDevices()
			if not device:
				sleep(5)
				device = GetDevices()
			mounts = CheckMountDir(device)
			MountOnHdd = config.plugins.HddMount.MountOnHdd.value
			if MountOnHdd != "nothing" and MountOnHdd in device and \
				mounts[0] == "nothing":
				mountdevice.Mount("/dev/" + MountOnHdd[:4], "/media/hdd")
			MountOnMovie = config.plugins.HddMount.MountOnMovie.value
			if MountOnMovie != "nothing" and MountOnMovie in device and \
				mounts[1] == "nothing":
				mountdevice.Mount("/dev/" + MountOnMovie[:4], "/media/hdd/movie")
		if config.plugins.HddMount.SwapOnStart.value:
			SwapFile = config.plugins.HddMount.SwapFile.value
			if SwapFile != "no":
				from Components.Console import Console
				import os
				if SwapFile[:2] == "sd":
					Console().ePopen("swapon /dev/%s" % SwapFile[:4])
				elif os.path.exists("/media/hdd/swapfile"):
					Console().ePopen("swapon /media/hdd/swapfile")
				else:
					sleep(5)
					if os.path.exists("/media/hdd/swapfile"):
						Console().ePopen("swapon /media/hdd/swapfile")

def Plugins(**kwargs):
	return [PluginDescriptor(name =_("HDD mount manager"),
		description =_("Plugin to manage mounting and swapfile."),
		where = [PluginDescriptor.WHERE_PLUGINMENU,
		PluginDescriptor.WHERE_EXTENSIONSMENU], needsRestart = False, fnc = main),
		PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART,
		needsRestart = False, fnc = OnStart)]

