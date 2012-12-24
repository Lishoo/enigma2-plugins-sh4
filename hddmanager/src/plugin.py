from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Console import Console
from Components.config import config, ConfigSelection, ConfigSubsection, \
	ConfigText, ConfigYesNo, getConfigListEntry
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from os import mkdir, path
from string import atoi

config.plugins.HddMount = ConfigSubsection()
config.plugins.HddMount.MountOnStart = ConfigYesNo(default = False)
config.plugins.HddMount.MountOnHdd = ConfigText(default = "nothing")
config.plugins.HddMount.MountOnMovie = ConfigText(default = "nothing")
config.plugins.HddMount.SwapOnStart = ConfigYesNo(default = False)
config.plugins.HddMount.SwapFile = ConfigText(default = "no")

def GetDevices():
	device = []
	try:
		f = open("/proc/partitions", "r")
		for line in f.readlines():
			parts = line.strip().split()
			if parts and parts[3][-4:-2] == "sd":
				size = int(parts[2])
				if (size / 1024 / 1024) > 1:
					des = str(size / 1024 / 1024) + "GB"
				else:
					des = str(size / 1024) + "MB"
				device.append(parts[3] + "  " + des)
		f.close()
	except:
		print "[HddManager] ERROR in read /proc/partitions"
	return device

def CreateMountDir(list):
	dir = ""
	for line in list[1:].split("/"):
		dir += "/" + line
		if not path.exists(dir):
			try:
				mkdir(dir)
				print "[HddManager] mkdir", dir
			except:
				print "[HddManager] ERROR mkdir", dir

def CheckMountDir(device):
	hdd = "nothing"
	movie = "nothing"
	from Components.Harddisk import getProcMounts
	mounts = getProcMounts()
	for line in mounts:
		if line[1][-3:] == "hdd":
			hdd = GetDeviceFromList(device, line[0][5:])
		elif line[1][-5:] == "movie":
			movie = GetDeviceFromList(device, line[0][5:])
	return hdd, movie

def GetDeviceFromList(list, device):
	for line in list:
		if line.startswith(device):
			return line

class MountSetup(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["Setup"]
		self.setTitle(_("HDD mount configuration"))
		self.CreateSetup()
		self.list = []
		ConfigListScreen.__init__(self, self.list, session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Ok"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.Cancel,
				"ok": self.Ok,
				"green": self.Ok,
				"red": self.Cancel,
			}, -2)

	def CreateSetup(self):
		self.device = GetDevices()
		self.Console = Console()
		self.Console.ePopen("sfdisk -l /dev/sd? | grep swap", self.CheckSwap)

	def CheckSwap(self, result, retval, extra_args):
		if self.device:
			for line in result.splitlines():
				if line and line.startswith("/dev"):
					swap = GetDeviceFromList(self.device, line[5:9])
					if swap in self.device:
						self.device.remove(swap)
		self.CreateList()

	def CreateList(self):
		self.MountOnStart = ConfigYesNo(default = \
			config.plugins.HddMount.MountOnStart.value)
		mounts = CheckMountDir(self.device)
		self.hdd = mounts[0]
		self.MountOnHdd = ConfigSelection(default = self.hdd, \
			choices = [("nothing", _("nothing"))] + self.device)
		self.movie = mounts[1]
		self.MountOnMovie = ConfigSelection (default = self.movie, \
			choices = [("nothing", _("nothing"))] + self.device)
		self.SwapOnStart = ConfigYesNo(default = \
			config.plugins.HddMount.SwapOnStart.value)
		self.swap = "no"
		if self.hdd != "nothing" and path.exists("/media/hdd/swapfile"):
			try:
				f = open("/proc/swaps", "r")
				for line in f.readlines():
					if line.startswith("/media/hdd/swapfile"):
						self.swap = str(path.getsize("/media/hdd/swapfile") / 1024)
				f.close()
			except:
				print "[HddManager] ERROR in read /proc/swaps"
		if self.device:
			self.SwapFile = ConfigSelection(default = self.swap, \
				choices = [("no", _("no")), ("65536", _("64MB")), 
				("131072", _("128MB")), ("262144", _("256MB")), ("524288", _("512MB"))])
		else:
			self.SwapFile = ConfigSelection(default = self.swap, \
				choices = [("no", _("no"))])
		self.list = []
		self.list.append(getConfigListEntry(_("Mount all on receiver startup"),
			self.MountOnStart))
		self.list.append(getConfigListEntry(_("Mount on /media/hdd"),
			self.MountOnHdd))
		self.list.append(getConfigListEntry(_("Mount on /media/hdd/movie"),
			self.MountOnMovie))
		self.list.append(getConfigListEntry(_("Enable swap on receiver startup"),
			self.SwapOnStart))
		self.list.append(getConfigListEntry(_("Enable swapfile on /media/hdd"),
			self.SwapFile))
		self["config"].list = self.list

	def Ok(self):
		config.plugins.HddMount.MountOnStart.value = self.MountOnStart.value
		config.plugins.HddMount.MountOnHdd.value = self.MountOnHdd.value
		if self.MountOnHdd.value != self.hdd:
			if self.hdd != "nothing":
				self.Console.ePopen("umount /media/hdd")
			if self.MountOnHdd.value != "nothing":
				CreateMountDir("/media/hdd")
				print self.MountOnHdd.value
				self.Console.ePopen("mount /dev/%s /media/hdd" % \
					self.MountOnHdd.value[:4])
		config.plugins.HddMount.MountOnMovie.value = self.MountOnMovie.value
		if self.MountOnMovie.value != self.movie:
			if self.movie != "nothing":
				self.Console.ePopen("umount /media/hdd/movie")
			if self.MountOnMovie.value != "nothing":
				CreateMountDir("/media/hdd/movie")
				self.Console.ePopen("mount /dev/%s /media/hdd/movie" % \
					self.MountOnMovie.value[:4])
		config.plugins.HddMount.SwapOnStart.value = self.SwapOnStart.value
		config.plugins.HddMount.SwapFile.value = self.SwapFile.value
		if self.SwapFile.value != self.swap:
			if self.SwapFile.value != "no":
				msg = _("Please wait, is currently to created a swap file.\nIt will take some time.")
				self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			if self.swap != "no":
				self.Console.ePopen("swapoff /media/hdd/swapfile", \
					self.DeleteSwapFile, self.SwapFile.value)
			elif self.SwapFile.value != "no":
				self.CreateSwapFile()
		config.plugins.HddMount.save()
		self.close()

	def DeleteSwapFile(self, result, retval, extra_args):
		if extra_args != "no":
			self.CreateSwapFile()
		else:
			Console().ePopen("rm -f /media/hdd/swapfile")

	def CreateSwapFile(self):
		Console().ePopen("dd if=/dev/zero of=/media/hdd/swapfile bs=1024 count=%s" \
			% atoi(self.SwapFile.value), self.MakeSwapFile)

	def MakeSwapFile(self, result, retval, extra_args):
		Console().ePopen("mkswap /media/hdd/swapfile", self.EnableSwapFile)

	def EnableSwapFile(self, result, retval, extra_args):
		Console().ePopen("swapon /media/hdd/swapfile")
		self.mbox.close()

	def Cancel(self):
		ConfigListScreen.keyCancel(self)

def main(session, **kwargs):
	session.open(MountSetup)

def OnStart(reason, **kwargs):
	if reason == 0: # Enigma start
		if config.plugins.HddMount.MountOnStart.value:
			device = GetDevices()
			mounts = CheckMountDir(device)
			MountOnHdd = config.plugins.HddMount.MountOnHdd.value
			if MountOnHdd != "nothing" and MountOnHdd in device \
				and mounts[0] == "nothing":
				CreateMountDir("/media/hdd")
				Console().ePopen("mount /dev/%s /media/hdd" % MountOnHdd[:4])
			MountOnMovie = config.plugins.HddMount.MountOnMovie.value
			if MountOnMovie != "nothing" and MountOnMovie in device \
				and mounts[1] == "nothing":
				CreateMountDir("/media/hdd/movie")
				Console().ePopen("mount /dev/%s /media/hdd/movie" % MountOnMovie[:4])
		if config.plugins.HddMount.SwapOnStart.value \
			and config.plugins.HddMount.SwapFile.value != "no" \
			and path.exists("/media/hdd/swapfile"):
				Console().ePopen("swapon /media/hdd/swapfile")

def Plugins(**kwargs):
	return [PluginDescriptor(name=_("HDD mount manager"),
		description=_("Plugin to manage mounting and swapfile."),
		where = [PluginDescriptor.WHERE_PLUGINMENU,
		PluginDescriptor.WHERE_EXTENSIONSMENU], needsRestart = False, fnc=main),
	PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART,
		needsRestart = False, fnc = OnStart)]
