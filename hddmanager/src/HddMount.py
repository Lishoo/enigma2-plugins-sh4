import os
from time import sleep
from Components.Console import Console


def GetDevices():
	device = []
	try:
		with open("/proc/partitions", "r") as f:
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

def __ReadMounts():
	try:
		with open("/proc/mounts", "r") as f:
			result = [line.strip().split(' ') for line in f]
			for item in result:
				item[1] = item[1].replace('\\040', ' ')
		f.close()
	except IOError, ex:
		print "[HddManager] Failed to open /proc/mounts", ex
		result = ""
	return result

def CheckMountDir(device):
	hdd = "nothing"
	movie = "nothing"
	for line in __ReadMounts():
		if line[1][-3:] == "hdd":
			hdd = GetDeviceFromList(device, line[0][5:])
		elif line[1][-5:] == "movie":
			movie = GetDeviceFromList(device, line[0][5:])
	return hdd, movie

def GetDeviceFromList(list, device):
	for line in list:
		if line[:len(device)] == device:
			return line

def MountHddOnStart(MountOnHdd, MountOnMovie, enableswap):
	device = GetDevices()
	if not device:
		print "[HddManager] not found devices"
		sleep(5)
		device = GetDevices()
	mounts = CheckMountDir(device)
	if MountOnHdd != "nothing" and MountOnHdd in device and \
		mounts[0] == "nothing":
		enableswap == False
		mountdevice.Mount("/dev/" + MountOnHdd[:4], "/media/hdd", enableswap)
	if MountOnMovie != "nothing" and MountOnMovie in device and \
		mounts[1] == "nothing":
		mountdevice.Mount("/dev/" + MountOnMovie[:4], "/media/hdd/movie")
	if enableswap:
		mountdevice.EnableSwap()

class MountDevice:
	def __init__(self):
		self.Console = Console()

	def Mount(self, device, dirpath, enableswap = False):
		dir = ""
		self.enableswap = enableswap
		for line in dirpath[1:].split("/"):
			dir += "/" + line
			if not os.path.exists(dir):
				try:
					os.mkdir(dir)
					print "[HddManager] mkdir", dir
				except:
					print "[HddManager] Failed to mkdir", dir
		if os.path.exists("/bin/ntfs-3g"):
			self.Console.ePopen("sfdisk -l /dev/sd? | grep NTFS",
				self.__CheckNtfs, [device, dirpath])
		else:
			self.__StartMount("mount " + device + " " + dirpath)

	def __CheckNtfs(self, result, retval, extra_args):
		(device, dirpath) = extra_args
		cmd = "mount "
		for line in result.splitlines():
			if line and line[:9] == device:
				for line in __ReadMounts():
					if device in line[0]:
						self.Console.ePopen("umount -f " + device)
						break
				cmd = "ntfs-3g "
		cmd += device + " " + dirpath
		self.__StartMount(cmd)

	def __StartMount(self, cmd):
		if self.enableswap:
			self.enableswap = False
			self.Console.ePopen(cmd, self.EnableSwap)
		else:
			self.Console.ePopen(cmd)

	def EnableSwap(self, result=None, retval=None, extra_args=None):
		if os.path.exists("/media/hdd/swapfile"):
			Console().ePopen("swapon /media/hdd/swapfile")
		else:
			print "[HddManager] not found /media/hdd/swapfile"
			sleep(5)
			if os.path.exists("/media/hdd/swapfile"):
				Console().ePopen("swapon /media/hdd/swapfile")
			else:
				print "[HddManager] not found /media/hdd/swapfile"
				self.enableswap = True

mountdevice = MountDevice()

