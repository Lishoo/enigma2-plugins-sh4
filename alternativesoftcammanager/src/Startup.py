from enigma import eTimer
from Components.config import config
from Components.Console import Console

from Softcam import getcamcmd


class StartCamOnStart:
	def __init__(self):
		print "[Alternative SoftCam Manager] StartCamOnStart init"
		self.Console = Console()
		self.Timer = eTimer()
		self.Timer.timeout.get().append(self.__camnotrun)

	def start(self):
		self.Timer.start(2000, False)

	def __camnotrun(self):
		self.Timer.stop()
		self.Console.ePopen("ps", self.checkprocess)

	def checkprocess(self, result, retval, extra_args):
		processes = result.lower()
		camlist = ["oscam", "mgcamd", "wicard", "camd3", "mcas", "cccam",
			"gbox", "mpcs", "mbox", "newcs", "vizcam", "rucam"]
		camlist.insert(0, config.plugins.AltSoftcam.actcam.value)
		camnot = True
		for cam in camlist:
			if cam in processes:
				print "[Alternative SoftCam Manager] CAM START ERROR! Already in processes:", cam
				camnot = False
				break
		if camnot:
			cmd = getcamcmd(config.plugins.AltSoftcam.actcam.value)
			print "[Alternative SoftCam Manager]", cmd
			Console().ePopen(cmd)

startcamonstart = StartCamOnStart()

