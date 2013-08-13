from . import _
import Softcam

from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry
from Components.Console import Console
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.List import List
from Components.ScrollLabel import ScrollLabel
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap

from enigma import eTimer
from os import path, listdir


class AltCamManager(Screen):
	skin = """
		<screen position="center,center" size="630,370" title="SoftCam manager">
			<eLabel position="5,0" size="620,2" backgroundColor="#aaaaaa" />
			<widget source="list" render="Listbox" position="10,15" size="340,300" \
				scrollbarMode="showOnDemand">
				<convert type="TemplatedMultiContent">
					{
						"template": [MultiContentEntryPixmapAlphaTest(pos=(5, 5), \
								size=(51, 40), png=1), 
							MultiContentEntryText(pos=(65, 10), size=(275, 40), font=0, \
								flags=RT_HALIGN_LEFT, text=0), 
							MultiContentEntryText(pos=(5, 25), size=(51, 16), font=1, \
								flags=RT_HALIGN_CENTER, text=2),],
						"fonts": [gFont("Regular", 26), gFont("Regular", 12)],
						"itemHeight": 50
					}
				</convert>
			</widget>
			<eLabel halign="center" position="390,10" size="210,35" font="Regular;20" \
				text="Ecm info" transparent="1" />
			<widget name="status" position="360,50" size="320,300" font="Regular;16" \
				halign="left" noWrap="1" />
			<eLabel position="12,358" size="148,2" backgroundColor="#00ff2525" />
			<eLabel position="165,358" size="148,2" backgroundColor="#00389416" />
			<eLabel position="318,358" size="148,2" backgroundColor="#00baa329" />
			<eLabel position="471,358" size="148,2" backgroundColor="#006565ff" />
			<widget name="key_red" position="12,328" zPosition="2" size="148,30" \
				valign="center" halign="center" font="Regular;22" transparent="1" />
			<widget name="key_green" position="165,328" zPosition="2" size="148,30" \
				valign="center" halign="center" font="Regular;22" transparent="1" />
			<widget name="key_yellow" position="318,328" zPosition="2" size="148,30" \
				valign="center" halign="center" font="Regular;22" transparent="1" />
			<widget name="key_blue" position="471,328" zPosition="2" size="148,30" \
				valign="center" halign="center" font="Regular;22" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("SoftCam manager"))
		self.Console = Console()
		self["key_red"] = Label(_("Stop"))
		self["key_green"] = Label(_("Start"))
		self["key_yellow"] = Label(_("Restart"))
		self["key_blue"] = Label(_("Setup"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.start,
				"red": self.stop,
				"yellow": self.restart,
				"blue": self.setup
			}, -1)
		self["status"] = ScrollLabel()
		self["list"] = List([])
		Softcam.checkconfigdir()
		self.actcam = config.plugins.AltSoftcam.actcam.value
		self.softcamlist = []
		self.finish = True
		self.camstartcmd = ""
		self.actcampng = LoadPixmap(path=resolveFilename(SCOPE_PLUGINS,
			"Extensions/AlternativeSoftCamManager/images/actcam.png"))
		self.defcampng = LoadPixmap(path=resolveFilename(SCOPE_PLUGINS,
			"Extensions/AlternativeSoftCamManager/images/defcam.png"))
		self.stoppingTimer = eTimer()
		self.stoppingTimer.timeout.get().append(self.stopping)
		self.closestopTimer = eTimer()
		self.closestopTimer.timeout.get().append(self.closestop)
		self.startcreateinfo()
		self.Timer = eTimer()
		self.Timer.callback.append(self.listecminfo)
		self.Timer.start(1000*4, False)

	def startcreateinfo(self):
		self.camdir = config.plugins.AltSoftcam.camdir.value
		self.createinfo()

	def createinfo(self):
		self.iscam = False
		self.finish = False
		self.startcreatecamlist()
		self.listecminfo()

	def listecminfo(self):
		listecm = ""
		try:
			ecmfiles = open("/tmp/ecm.info", "r")
			for line in ecmfiles:
				while len(line) > 32:
					linebreak = line.rfind(' ', 0, 32)
					if linebreak == -1:
						linebreak = 32
					listecm += line[:linebreak] + "\n"
					line = line[linebreak+1:]
				listecm += line
			self["status"].setText(listecm)
			ecmfiles.close()
		except:
			self["status"].setText("")

	def startcreatecamlist(self):
		self.camliststart()

	def camliststart(self):
		if path.exists(self.camdir):
			self.softcamlist = listdir(self.camdir)
			if self.softcamlist:
				self.iscam = True
				self.Console.ePopen("chmod 755 %s/*" % self.camdir)
				if self.actcam != "none" and Softcam.getcamscript(self.actcam):
					self.createcamlist()
				else:
					self.Console.ePopen("pidof %s" % self.actcam, self.camactive)
		else:
			if path.exists("/usr/bin/cam") and not self.iscam and self.camdir != "/usr/bin/cam":
				self.iscam = True
				self.camdir = "/usr/bin/cam"
				config.plugins.AltSoftcam.camdir.value = self.camdir
				self.startcreatecamlist()
			elif camdir != "/var/emu":
				self.iscam = False
				self.camdir = "/var/emu"
				config.plugins.AltSoftcam.camdir.value = self.camdir
				self.startcreatecamlist()
			else:
				self.iscam = False
				self.finish = True

	def camactive(self, result, retval, extra_args):
		if result.strip():
			self.createcamlist()
		else:
			self.actcam = "none"
			for line in self.softcamlist:
				Console().ePopen("pidof %s" % line, self.camactivefromlist, line)
			Console().ePopen("echo 1", self.camactivefromlist, "none")

	def camactivefromlist(self, result, retval, extra_args):
		if result.strip():
			self.actcam = extra_args
			self.createcamlist()
		else:
			self.finish = True

	def createcamlist(self):
		self.list = []
		try:
			if self.actcam != "none":
				self.list.append((self.actcam, self.actcampng, self.checkcam(self.actcam)))
			for line in self.softcamlist:
				if line != self.actcam:
					self.list.append((line, self.defcampng, self.checkcam(line)))
			self["list"].setList(self.list)
		except:
			self.actcam = "none"
			self.softcamlist = []
		self.finish = True

	def checkcam (self, cam):
		cam = cam.lower()
		if Softcam.getcamscript(cam):
			return "Script"
		elif "oscam" in cam:
			return "Oscam"
		elif "mgcamd" in cam:
			return "Mgcamd"
		elif "wicard" in cam:
			return "Wicard"
		elif "camd3" in cam:
			return "Camd3"
		elif "mcas" in cam:
			return "Mcas"
		elif "cccam" in cam:
			return "CCcam"
		elif "gbox" in cam:
			return "Gbox"
		elif "ufs910camd" in cam:
			return "Ufs910"
		elif "incubuscamd" in cam:
			return "Incubus"
		elif "mpcs" in cam:
			return "Mpcs"
		elif "mbox" in cam:
			return "Mbox"
		elif "newcs" in cam:
			return "Newcs"
		elif "vizcam" in cam:
			return "Vizcam"
		elif "sh4cam" in cam:
			return "Sh4CAM"
		elif "rucam" in cam:
			return "Rucam"
		else:
			return cam[0:6]

	def start(self):
		if self.iscam and self.finish:
			self.camstart = self["list"].getCurrent()[0]
			if self.camstart != self.actcam:
				print "[Alternative SoftCam Manager] Start SoftCam"
				self.camstartcmd = Softcam.getcamcmd(self.camstart)
				msg = _("Starting %s") % self.camstart
				self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
				self.stoppingTimer.start(100, False)

	def stop(self):
		if self.iscam and self.actcam != "none" and self.finish:
			Softcam.stopcam(self.actcam)
			msg  = _("Stopping %s") % self.actcam
			self.actcam = "none"
			self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			self.closestopTimer.start(1000, False)

	def closestop(self):
		self.closestopTimer.stop()
		self.mbox.close()
		self.createinfo()

	def restart(self):
		if self.iscam and self.actcam != "none" and self.finish:
			print "[Alternative SoftCam Manager] restart SoftCam"
			self.camstart = self.actcam
			if self.camstartcmd == "":
				self.camstartcmd = Softcam.getcamcmd(self.camstart)
			msg = _("Restarting %s") % self.actcam
			self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			self.stoppingTimer.start(100, False)

	def stopping(self):
		self.stoppingTimer.stop()
		Softcam.stopcam(self.actcam)
		self.actcam = self.camstart
		service = self.session.nav.getCurrentlyPlayingServiceReference()
		if service:
			self.session.nav.stopService()
		self.Console.ePopen(self.camstartcmd)
		print "[Alternative SoftCam Manager] ", self.camstartcmd
		if self.mbox:
			self.mbox.close()
		if service:
			self.session.nav.playService(service)
		self.createinfo()

	def ok(self):
		if self.iscam and self.finish:
			if self["list"].getCurrent()[0] != self.actcam:
				self.start()
			else:
				self.restart()

	def cancel(self):
		if self.finish:
			if config.plugins.AltSoftcam.actcam.value != self.actcam:
				config.plugins.AltSoftcam.actcam.value = self.actcam
			config.plugins.AltSoftcam.save()
			self.close()
		else: # if list setting not completed as they should
			self.cancelTimer = eTimer()
			self.cancelTimer.timeout.get().append(self.setfinish)
			self.cancelTimer.start(1000*4, False)

	def setfinish(self):			
		self.cancelTimer.stop()
		self.finish = True

	def setup(self):
		if self.finish:
			self.session.openWithCallback(self.startcreateinfo, ConfigEdit)


class ConfigEdit(Screen, ConfigListScreen):
	skin = """
		<screen name="ConfigEdit" position="center,center" size="500,200" \
			title="SoftCam path configuration">
			<eLabel position="5,0" size="490,2" backgroundColor="#aaaaaa" />
			<widget name="config" position="30,20" size="460,50" zPosition="1" \
				scrollbarMode="showOnDemand" />
			<eLabel position="85,180" size="166,2" backgroundColor="#00ff2525" />
			<eLabel position="255,180" size="166,2" backgroundColor="#00389416" />
			<widget name="key_red" position="85,150" zPosition="2" size="170,30" \
				valign="center" halign="center" font="Regular;22" transparent="1" />
			<widget name="key_green" position="255,150" zPosition="2" size="170,30" \
				valign="center" halign="center" font="Regular;22" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("SoftCam path configuration"))
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Ok"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"red": self.cancel,
				"ok": self.ok,
				"green": self.ok,
			}, -2)
		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session)
		self.camconfig = config.plugins.AltSoftcam.camconfig
		self.camdir = config.plugins.AltSoftcam.camdir
		self.list.append(getConfigListEntry(_("SoftCam config directory"), self.camconfig))
		self.list.append(getConfigListEntry(_("SoftCam directory"), self.camdir))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def ok(self):
		msg = [ ]
		if not path.exists(self.camconfig.value):
			msg.append("%s " % self.camconfig.value)
		if not path.exists(self.camdir.value):
			msg.append("%s " % self.camdir.value)
		if msg == [ ]:
			if self.camconfig.value.endswith("/"):
				self.camconfig.value = self.camconfig.value[:-1]
			if self.camdir.value.endswith("/"):
				self.camdir.value = self.camdir.value[:-1]
			config.plugins.AltSoftcam.camconfig = self.camconfig
			config.plugins.AltSoftcam.camdir = self.camdir
			config.plugins.AltSoftcam.save()
			self.close()
		else:
			self.mbox = self.session.open(MessageBox,
				_("Directory %s does not exist!\nPlease set the correct directory path!")
				% msg, MessageBox.TYPE_INFO, timeout = 5)

	def cancel(self, answer = None):
		if answer is None:
			if self["config"].isChanged():
				self.session.openWithCallback(self.cancel, MessageBox,
					_("Really close without saving settings?"))
			else:
				self.close()
		elif answer:
			for x in self["config"].list:
				x[1].cancel()
			self.close()

