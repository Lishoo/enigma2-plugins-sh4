#by Taapat taapat@gmail.com
#code and desing examples from 2boom plugins:
#		Easy Pnel for Pli http://gisclub.tv/index.php?topic=5075.0
#		newcamd.list switcher http://gisclub.tv/index.php?topic=4772.0
#openpli SoftcamSetup http://openpli.git.sourceforge.net/git/gitweb.cgi?p=openpli/enigma2-plugins;a=tree;f=PLi/SoftcamSetup/
from Components.ActionMap import ActionMap
from Components.config import config, ConfigSubsection, ConfigText, getConfigListEntry
from Components.Console import Console
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.List import List
from Components.ScrollLabel import ScrollLabel
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from Plugins.Plugin import PluginDescriptor
from enigma import eTimer
import os

config.plugins.AltSoftcam = ConfigSubsection()
config.plugins.AltSoftcam.actcam = ConfigText(default = "none")
config.plugins.AltSoftcam.camconfig = ConfigText(default = "/var/keys", visible_width = 100, fixed_size = False)
config.plugins.AltSoftcam.camdir = ConfigText(default = "/var/emu", visible_width = 100, fixed_size = False)
AltSoftcamConfigError = False
if not os.path.isdir(config.plugins.AltSoftcam.camconfig.value):
	config.plugins.AltSoftcam.camconfig.value = "none"
	AltSoftcamConfigError = True
if not os.path.isdir(config.plugins.AltSoftcam.camdir.value):
	config.plugins.AltSoftcam.camdir.value = "none"
	AltSoftcamConfigError = True

def getcamcmd(cam):
	if cam.lower().find("oscam") != -1:
		result = config.plugins.AltSoftcam.camdir.value + "/" + cam + " -bc " + config.plugins.AltSoftcam.camconfig.value + "/"
	elif cam.lower().find("wicard") != -1:
		result = config.plugins.AltSoftcam.camdir.value + "/" + cam + " -d -c " + config.plugins.AltSoftcam.camconfig.value + "/wicardd.conf"
	elif cam.lower().find("camd3") != -1:
		result = config.plugins.AltSoftcam.camdir.value + "/" + cam + " " + config.plugins.AltSoftcam.camconfig.value + "/camd3.config"
	elif cam.lower().find("mbox") != -1:
		result = config.plugins.AltSoftcam.camdir.value + "/" + cam + " " + config.plugins.AltSoftcam.camconfig.value + "/mbox.cfg"
	elif cam.lower().find("mpcs") != -1:
		result = config.plugins.AltSoftcam.camdir.value + "/" + cam + " -c " + config.plugins.AltSoftcam.camconfig.value
	elif cam.lower().find("newcs") != -1:
		result = config.plugins.AltSoftcam.camdir.value + "/" + cam + " -C " + config.plugins.AltSoftcam.camconfig.value + "/newcs.conf"
	elif cam.lower().find("vizcam") != -1:
		result = config.plugins.AltSoftcam.camdir.value + "/" + cam + " -b -c " + config.plugins.AltSoftcam.camconfig.value + "/"
	elif cam.lower().find("rucam") != -1:
		result = config.plugins.AltSoftcam.camdir.value + "/" + cam + " -b"
	else:
		result = config.plugins.AltSoftcam.camdir.value + "/" + cam
	return result

class AltCamManager(Screen):
	skin = """
<screen position="center,center" size="630,370" title="SoftCam manager">
	<eLabel position="5,0" size="620,2" backgroundColor="#aaaaaa" />
<widget source="list" render="Listbox" position="10,15" size="340,300" scrollbarMode="showOnDemand">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (51, 40), png = 1), 
			MultiContentEntryText(pos = (65, 10), size = (275, 40), font=0, flags = RT_HALIGN_LEFT, text = 0), 
			MultiContentEntryText(pos = (5, 25), size = (51, 16), font=1, flags = RT_HALIGN_CENTER, text = 2), 
				],
	"fonts": [gFont("Regular", 26),gFont("Regular", 12)],
	"itemHeight": 50
	}
	</convert>
	</widget>
	<eLabel halign="center" position="390,10" size="210,35" font="Regular;20" text="Ecm info" transparent="1" />
	<widget name="status" position="360,50" size="320,300" font="Regular;16" halign="left" noWrap="1" />
	<eLabel position="12,358" size="148,2" backgroundColor="#00ff2525" />
	<eLabel position="165,358" size="148,2" backgroundColor="#00389416" />
	<eLabel position="318,358" size="148,2" backgroundColor="#00baa329" />
	<eLabel position="471,358" size="148,2" backgroundColor="#006565ff" />
	<widget name="key_red" position="12,328" zPosition="2" size="148,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget name="key_green" position="165,328" zPosition="2" size="148,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget name="key_yellow" position="318,328" zPosition="2" size="148,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget name="key_blue" position="471,328" zPosition="2" size="148,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.Console = Console()
		self["key_red"] = Label(_("Stop"))
		self["key_green"] = Label(_("Start"))
		self["key_yellow"] = Label(_("ReStart"))
		self["key_blue"] = Label(_("Setup"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.start,
				"red": self.stop,
				"yellow": self.restart,
				"blue": self.setup,
			}, -1)
		self["status"] = ScrollLabel()
		self["list"] = List([])
		self.actcam = config.plugins.AltSoftcam.actcam.value
		self.camstartcmd = ""
		self.CreateInfo()
		self.Timer = eTimer()
		self.Timer.callback.append(self.listecminfo)
		self.Timer.start(1000*4, False)

	def CreateInfo(self):
		if AltSoftcamConfigError is False:
			self.StartCreateCamlist()
			self.listecminfo()

	def listecminfo(self):
		listecm = ""
		try:
			ecmfiles = open("/tmp/ecm.info", "r")
			for line in ecmfiles:
				if line[32:]:
					linebreak = line[23:].find(' ') + 23
					listecm += line[0:linebreak]
					listecm += "\n" + line[linebreak + 1:]
				else:
					listecm += line
			self["status"].setText(listecm)
			ecmfiles.close()
		except:
			self["status"].setText("")

	def StartCreateCamlist(self):
		self.Console.ePopen("ls %s" % config.plugins.AltSoftcam.camdir.value, self.CamListStart)

	def CamListStart(self, result, retval, extra_args):
		if not result.startswith('ls: '):
			self.softcamlist = result
			self.Console.ePopen("chmod 755 %s/*" % config.plugins.AltSoftcam.camdir.value)
			self.Console.ePopen("pidof %s" % self.actcam, self.CamActive)

	def CamActive(self, result, retval, extra_args):
		if result.strip():
			self.CreateCamList()
		else:
			for line in self.softcamlist.splitlines():
				if line != self.actcam:
					self.Console.ePopen("pidof %s" % line, self.CamActiveFromList, line)
			self.Console.ePopen("echo 1", self.CamActiveFromList, "softcamlistend")

	def CamActiveFromList(self, result, retval, extra_args):
		if result.strip():
			if extra_args != "softcamlistend":
				self.actcam = extra_args
			else:
				self.actcam = "none"
			self.CreateCamList()

	def CreateCamList(self):
		self.list = []
		if not self.actcam:
			self.actcam = "none"
		if self.actcam != "none":
			try:
				softpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/AlternativeSoftCamManager/images/actcam.png"))
				self.list.append((self.actcam, softpng, self.checkcam(self.actcam)))
			except:
				pass
		try:
			softpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/AlternativeSoftCamManager/images/defcam.png"))
			for line in self.softcamlist.splitlines():
				if line != self.actcam:
					self.list.append((line, softpng, self.checkcam(line)))
		except:
			pass
		self["list"].setList(self.list)

	def checkcam (self, cam):
		if cam.lower().find("oscam") != -1:
			camtext = "Oscam"
		elif cam.lower().find("mgcamd") != -1:
			camtext = "Mgcamd"
		elif cam.lower().find("wicard") != -1:
			camtext = "Wicard"
		elif cam.lower().find("camd3") != -1:
			camtext = "Camd3"
		elif cam.lower().find("mcas") != -1:
			camtext = "Mcas"
		elif cam.lower().find("cccam") != -1:
			camtext = "CCcam"
		elif cam.lower().find("gbox") != -1:
			camtext = "Gbox"
		elif cam.lower().find("ufs910camd") != -1:
			camtext = "Ufs910"
		elif cam.lower().find("incubuscamd") != -1:
			camtext = "Incubus"
		elif cam.lower().find("mpcs") != -1:
			camtext = "Mpcs"
		elif cam.lower().find("mbox") != -1:
			camtext = "Mbox"
		elif cam.lower().find("newcs") != -1:
			camtext = "Newcs"
		elif cam.lower().find("vizcam") != -1:
			camtext = "Vizcam"
		elif cam.lower().find("sh4cam") != -1:
			camtext = "Sh4CAM"
		elif cam.lower().find("rucam") != -1:
			camtext = "Rucam"
		else:
			camtext = cam[0:6]
		return camtext

	def start(self):
		global AltSoftcamConfigError
		if AltSoftcamConfigError is False:
			self.camstart = self["list"].getCurrent()[0]
			if self.camstart != self.actcam:
				print "[Alternative SoftCam Manager] Start SoftCam"
				self.camstartcmd = getcamcmd(self.camstart)
				msg = _("Starting %s" % self.camstart)
				self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
				self.activityTimer = eTimer()
				self.activityTimer.timeout.get().append(self.Stopping)
				self.activityTimer.start(100, False)

	def stop(self):
		if self.actcam != "none":
			self.Console.ePopen("killall -9 %s" % self.actcam)
			print "[Alternative SoftCam Manager] stop ", self.actcam
			try:
				os.remove("/tmp/ecm.info")
			except:
				pass
			msg  = _("Stopping %s" % self.actcam)
			self.actcam = "none"
			self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			self.activityTimer = eTimer()
			self.activityTimer.timeout.get().append(self.closestop)
			self.activityTimer.start(1000, False)

	def closestop(self):
		self.activityTimer.stop()
		self.mbox.close()
		self.CreateInfo()

	def restart(self):
		global AltSoftcamConfigError
		if AltSoftcamConfigError is False:
			print "[Alternative SoftCam Manager] restart SoftCam"
			self.camstart = self.actcam
			if self.camstartcmd == "":
				self.camstartcmd = getcamcmd(self.camstart)
			msg  = _("Restarting %s" % self.actcam)
			self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			self.activityTimer = eTimer()
			self.activityTimer.timeout.get().append(self.Stopping)
			self.activityTimer.start(100, False)

	def Stopping(self):
		self.activityTimer.stop()
		self.Console.ePopen("killall -9 %s" % self.actcam)
		print "[Alternative SoftCam Manager] stopping ", self.actcam
		try:
			os.remove("/tmp/ecm.info")
		except:
			pass
		self.actcam = self.camstart
		self.currentservice = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.Starting)
		self.activityTimer.start(100, False)

	def Starting(self):
		self.activityTimer.stop()
		del self.activityTimer 
		self.Console.ePopen(self.camstartcmd)
		print "[Alternative SoftCam Manager] ", self.camstartcmd
		if self.mbox:
			self.mbox.close()
		self.session.nav.playService(self.currentservice)
		del self.currentservice
		self.CreateInfo()

	def ok(self):
		if self["list"].getCurrent()[0] != self.actcam:
			self.start()
		else:
			self.restart()

	def cancel(self):
		if config.plugins.AltSoftcam.actcam.value != self.actcam:
			config.plugins.AltSoftcam.actcam.value = self.actcam
			config.plugins.AltSoftcam.actcam.save()
		self.close()

	def setup(self):
		self.session.openWithCallback(self.CreateInfo, ConfigEdit)

class ConfigEdit(Screen, ConfigListScreen):
	skin = """
<screen name="ConfigEdit" position="center,center" size="500,200" title="Emu path configuration">
	<eLabel position="5,0" size="490,2" backgroundColor="#aaaaaa" />
<widget name="config" position="30,20" size="460,50" zPosition="1" scrollbarMode="showOnDemand" />
	<eLabel position="85,180" size="166,2" backgroundColor="#00ff2525" />
	<eLabel position="255,180" size="166,2" backgroundColor="#00389416" />
	<widget name="key_red" position="85,150" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget name="key_green" position="255,150" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Ok"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.ok,
				"green": self.ok,
				"red": self.close,
			}, -2)
		ConfigListScreen.__init__(self, [], session)
		self.camconfigold = config.plugins.AltSoftcam.camconfig.value
		self.camdirold = config.plugins.AltSoftcam.camdir.value
		self.list = []
		self.list.append(getConfigListEntry(_("SoftCam config directory"), config.plugins.AltSoftcam.camconfig))
		self.list.append(getConfigListEntry(_("SoftCam directory"), config.plugins.AltSoftcam.camdir))
		self["config"].list = self.list

	def ok(self):
		if self.camconfigold != config.plugins.AltSoftcam.camconfig.value or self.camdirold != config.plugins.AltSoftcam.camdir.value:
			self.session.openWithCallback(self.updateConfig, MessageBox, (_("Are you sure you want to save this configuration?\n\n")))
		elif not os.path.isdir(self.camconfigold) or not os.path.isdir(self.camdirold):
			self.updateConfig(True)
		else:
			self.close()

	def updateConfig(self, ret = False):
		if ret == True:
			global AltSoftcamConfigError
			msg = [ ]
			if not os.path.isdir(config.plugins.AltSoftcam.camconfig.value):
				msg.append("%s " % config.plugins.AltSoftcam.camconfig.value)
			if not os.path.isdir(config.plugins.AltSoftcam.camdir.value):
				msg.append("%s " % config.plugins.AltSoftcam.camdir.value)
			if msg == [ ]:
				if config.plugins.AltSoftcam.camconfig.value[-1] == "/":
					config.plugins.AltSoftcam.camconfig.value = config.plugins.AltSoftcam.camconfig.value[:-1]
				if config.plugins.AltSoftcam.camdir.value[-1] == "/":
					config.plugins.AltSoftcam.camdir.value = config.plugins.AltSoftcam.camdir.value[:-1]
				config.plugins.AltSoftcam.camconfig.save()
				config.plugins.AltSoftcam.camdir.save()
				AltSoftcamConfigError = False
				self.close()
			else:
				AltSoftcamConfigError = True
				self.mbox = self.session.open(MessageBox, "Directory %s not exist!\nPlease set the correct directory path!" % msg, MessageBox.TYPE_INFO, timeout = 5 )

def main(session, **kwargs):
	session.open(AltCamManager)

def StartCam(reason, **kwargs):
	global AltSoftcamConfigError
	if AltSoftcamConfigError is False and config.plugins.AltSoftcam.actcam.value != "none":
		if reason == 0: # Enigma start
			try:
				cmd = getcamcmd(config.plugins.AltSoftcam.actcam.value)
				Console().ePopen(cmd)
				print "[Alternative SoftCam Manager] ", cmd
			except:
				pass
		elif reason == 1: # Enigma stop
			try:
				Console().ePopen("killall -9 %s" % config.plugins.AltSoftcam.actcam.value)
				print "[Alternative SoftCam Manager] stopping ", config.plugins.AltSoftcam.actcam.value
			except:
				pass

def Plugins(**kwargs):
	return [
	PluginDescriptor(name = "Alternative SoftCam Manager", description = "Start, stop, restart SoftCams, change setting path.", where = [ PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU ], icon = "images/softcam.png", fnc = main),
	PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, needsRestart = True, fnc = StartCam)]
