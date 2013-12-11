from . import _

import os
from string import atoi

from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Console import Console
from Components.config import config, ConfigSelection, getConfigListEntry
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from HddMount import CheckMountDir, GetDeviceFromList, GetDevices, mountdevice


class MountSetup(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["Setup"]
		self.setTitle(_("HDD mount configuration"))
		self.Console = Console()
		self.list = []
		self.swapdevice = []
		self.device = GetDevices()
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Ok"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.Cancel,
				"ok": self.Ok,
				"green": self.Ok,
				"red": self.Cancel
			}, -2)
		self.Console.ePopen("sfdisk -l /dev/sd? | grep swap", self.CheckSwap)
		ConfigListScreen.__init__(self, self.list, session=session)

	def CheckSwap(self, result, retval, extra_args):
		if self.device:
			for line in result.splitlines():
				if line and line[:4] == "/dev":
					swap = GetDeviceFromList(self.device, line[5:9])
					if swap in self.device:
						self.device.remove(swap)
						self.swapdevice.append(swap)
		mounts = CheckMountDir(self.device)
		self.hdd = mounts[0]
		self.MountOnHdd = ConfigSelection(default = self.hdd, \
			choices = [("nothing", _("nothing"))] + self.device)
		self.movie = mounts[1]
		self.MountOnMovie = ConfigSelection(default = self.movie, \
			choices = [("nothing", _("nothing"))] + self.device)
		self.swap = "no"
		try:
			with open("/proc/swaps", "r") as f:
				for line in f.readlines():
					if line[:19] == "/media/hdd/swapfile":
						self.swap = str(os.path.getsize("/media/hdd/swapfile") / 1024)
					else:
						for device in self.swapdevice:
							if device[:4] == line[5:9]:
								self.swap = device
			f.close()
		except IOError, ex:
			print "[HddManager] Failed to open /proc/swaps", ex
		self.MountOnHdd.addNotifier(self.CreateList, initial_call = False)
		self.CreateList()

	def CreateList(self, configEntry = None):
		if self.device and self.MountOnHdd.value != "nothing":
			self.SwapFile = ConfigSelection(default = self.swap, \
				choices = [("no", _("no")), ("65536", _("64MB")), 
				("131072", _("128MB")), ("262144", _("256MB")), 
				("524288", _("512MB"))] + self.swapdevice)
		else:
			if self.MountOnHdd.value == "nothing" \
				and not self.swap[:2] == "sd":
				defaultswap = "no"
			else:
				defaultswap = self.swap
			self.SwapFile = ConfigSelection(default = defaultswap, \
				choices = [("no", _("no"))] + self.swapdevice)
		self.list = []
		self.list.append(getConfigListEntry(_("Mount all on receiver startup"),
			config.plugins.HddMount.MountOnStart))
		self.list.append(getConfigListEntry(_("Mount on /media/hdd"),
			self.MountOnHdd))
		self.list.append(getConfigListEntry(_("Mount on /media/hdd/movie"),
			self.MountOnMovie))
		self.list.append(getConfigListEntry(_("Enable swap on receiver startup"),
			config.plugins.HddMount.SwapOnStart))
		self.list.append(getConfigListEntry(_("Enable swapfile"),
			self.SwapFile))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def Ok(self):
		if self.list:
			config.plugins.HddMount.MountOnHdd.value = self.MountOnHdd.value
			if self.MountOnHdd.value != self.hdd:
				if self.hdd != "nothing":
					self.Console.ePopen("umount /media/hdd")
				if self.MountOnHdd.value != "nothing":
					mountdevice.Mount("/dev/" + self.MountOnHdd.value[:4], \
						"/media/hdd")
			config.plugins.HddMount.MountOnMovie.value = self.MountOnMovie.value
			if self.MountOnMovie.value != self.movie:
				if self.movie != "nothing":
					self.Console.ePopen("umount /media/hdd/movie")
				if self.MountOnMovie.value != "nothing":
					mountdevice.Mount("/dev/" + self.MountOnMovie.value[:4], \
						"/media/hdd/movie")
			config.plugins.HddMount.SwapFile.value = self.SwapFile.value
			if self.SwapFile.value != self.swap:
				if self.swap[:2] == "sd":
					self.Console.ePopen("swapoff /dev/%s" % self.swap[:4])
				elif self.swap != "no":
					self.Console.ePopen("swapoff /media/hdd/swapfile")
					self.Console.ePopen("rm -f /media/hdd/swapfile")
				if self.SwapFile.value != "no":
					if not self.SwapFile.value[:2] == "sd":
						msg = _("Please wait, is currently to created a swap file.\nIt will take some time.")
						self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
					self.CreateSwapFile()
			config.plugins.HddMount.save()
			self.close()

	def CreateSwapFile(self):
		if self.SwapFile.value[:2] == "sd":
			Console().ePopen("swapon /dev/%s" % self.SwapFile.value[:4])
		else:
			Console().ePopen("dd if=/dev/zero of=/media/hdd/swapfile bs=1024 count=%s" \
				% atoi(self.SwapFile.value), self.MakeSwapFile)

	def MakeSwapFile(self, result, retval, extra_args):
		Console().ePopen("mkswap /media/hdd/swapfile", self.EnableSwapFile)

	def EnableSwapFile(self, result, retval, extra_args):
		Console().ePopen("swapon /media/hdd/swapfile")
		if self.mbox:
			self.mbox.close()

	def Cancel(self):
		ConfigListScreen.keyCancel(self)

