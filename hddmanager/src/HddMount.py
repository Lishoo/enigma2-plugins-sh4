from Components.config import config
from Components.Console import Console

from time import sleep

import os


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
	except IOError, ex:
		print "[HddManager] Failed to open /proc/partitions", ex
	return device

def ReadMounts():
	result = ""
	try:
		f = open("/proc/mounts", "r")
		result = [line.strip().split(' ') for line in f]
		f.close()
	except IOError, ex:
		print "[HddManager] Failed to open /proc/mounts", ex
	for item in result:
		item[1] = item[1].replace('\\040', ' ')
	return result

def CheckMountDir(device):
	hdd = "nothing"
	movie = "nothing"
	for line in ReadMounts():
		if line[1][-3:] == "hdd":
			hdd = GetDeviceFromList(device, line[0][5:])
		elif line[1][-5:] == "movie":
			movie = GetDeviceFromList(device, line[0][5:])
	return hdd, movie

def GetDeviceFromList(list, device):
	for line in list:
		if line[:len(device)] == device:
			return line

def MountOnStart():
	if config.plugins.HddMount.MountOnStart.value:
		device = GetDevices()
		if not device:
			sleep(3)
			device = GetDevices()
		mounts = CheckMountDir(device)
		MountOnHdd = config.plugins.HddMount.MountOnHdd.value
		if MountOnHdd != "nothing" and MountOnHdd in device \
			and mounts[0] == "nothing":
			mountdevice.Mount("/dev/" + MountOnHdd[:4], "/media/hdd")
		MountOnMovie = config.plugins.HddMount.MountOnMovie.value
		if MountOnMovie != "nothing" and MountOnMovie in device \
			and mounts[1] == "nothing":
			mountdevice.Mount("/dev/" + MountOnMovie[:4], "/media/hdd/movie")
	if config.plugins.HddMount.SwapOnStart.value \
		and config.plugins.HddMount.SwapFile.value != "no":
		SwapFile = config.plugins.HddMount.SwapFile.value
		if SwapFile != "no":
			if SwapFile[:2] == "sd":
				Console().ePopen("swapon /dev/%s" % SwapFile[:4])
			elif os.path.exists("/media/hdd/swapfile"):
				Console().ePopen("swapon /media/hdd/swapfile")
			else:
				sleep(5)
				if os.path.exists("/media/hdd/swapfile"):
					Console().ePopen("swapon /media/hdd/swapfile")

class MountDevice:
	def __init__(self):
		self.Console = Console()

	def Mount(self, device, dirpath):
		dir = ""
		for line in dirpath[1:].split("/"):
			dir += "/" + line
			if not os.path.exists(dir):
				try:
					os.mkdir(dir)
					print "[HddManager] mkdir", dir
				except:
					print "[HddManager] Failed to mkdir", dir
		if os.path.exists("/bin/ntfs-3g"):
			self.Console.ePopen("sfdisk -l /dev/sd? | grep NTFS", self.CheckNtfs, [device, dirpath])
		else:
			self.StartMount("mount " + device + " " + dirpath)

	def CheckNtfs(self, result, retval, extra_args):
		(device, dirpath) = extra_args
		cmd = "mount "
		for line in result.splitlines():
			if line and line[:9] == device:
				for line in ReadMounts():
					if device in line[0]:
						self.Console.ePopen("umount -f " + device)
						break
				cmd = "ntfs-3g "
		cmd += device + " " + dirpath
		self.StartMount(cmd)

	def StartMount(self, cmd):
		self.Console.ePopen(cmd)
		print "[HddManager]", cmd

mountdevice = MountDevice()

