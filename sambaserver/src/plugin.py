from Components.ActionMap import ActionMap
from Components.Console import Console
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigText, \
	ConfigYesNo, getConfigListEntry
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen

config.plugins.SambaServer = ConfigSubsection()
config.plugins.SambaServer.Start = ConfigYesNo(default = False)
config.plugins.SambaServer.StartOnStartup = ConfigYesNo(default = True)

class SambaServer(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["Setup"]
		self.setTitle(_("Samba server configuration"))
		if config.plugins.SambaServer.Start.value:
			self.start = False
		else:
			self.start = True
		self.CreateConfig()
		self.list = []
		ConfigListScreen.__init__(self, self.list, session,
			on_change = self.UpdateList)
		self.UpdateList()
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.Cancel,
				"ok": self.Ok,
				"green": self.Ok,
				"red": self.Cancel
			}, -2)

	def CreateConfig(self):
		self.settings = []
		workgroup = "WORKGRUP"
		netbios = "Receiver"
		SMB2 = False
		share = ['root', 'media', 'hdd', 'movie']
		self.share = []
		self.sharecount = 0
		try:
			f = open("/etc/samba/smb.conf", "r")
			for line in f.readlines():
				self.settings.append(line)
			f.close()
			print "[SambaServer] load settings"
		except:
			print "[SambaServer] ERROR in open configuration file"
		if self.settings:
			for line in self.settings:
				line = line.replace(' ', '').replace('\t', '')
				name = line.lower()
				if name.startswith('workgroup='):
					workgroup = line[10:-1]
				elif name.startswith('netbiosname='):
					netbios = line[12:-1]
				elif name.startswith('maxprotocol=smb2'):
					SMB2 = True
				elif name.startswith('[') and not "[global]" in line:
					name = line[1:line.find(']')]
					self.share.append(name)
					self.share.append(ConfigYesNo(default = True))
					self.sharecount += 2
					if name in share:
						share.remove(name)
			self.workgroup = ConfigText(default = workgroup, visible_width = 100,
				fixed_size = False)
			self.netbios = ConfigText(default = netbios, visible_width = 100,
				fixed_size = False)
			self.SMB2 = ConfigYesNo(default = SMB2)
			if share:
				for line in share:
					self.share.append(line)
					self.share.append(ConfigYesNo(default = False))
					self.sharecount += 2

	def UpdateList(self):
		if self.start != config.plugins.SambaServer.Start.value and self.settings:
			self.list = []
			self.list.append(getConfigListEntry(_("Start Samba server"),
				config.plugins.SambaServer.Start))
			self.start = config.plugins.SambaServer.Start.value
			if self.start:
				self.list.append(getConfigListEntry(_("Start Samba on receiver startup"),
					config.plugins.SambaServer.StartOnStartup))
				self.list.append(getConfigListEntry(_("Workgroup"), self.workgroup))
				self.list.append(getConfigListEntry(_("Receiver name in network"),
					self.netbios))
				self.list.append(getConfigListEntry(_("Use SMB2 protocol"), self.SMB2))
				count = 0
				while count < self.sharecount:
					self.list.append(getConfigListEntry(_("Share %s") % self.share[count],
						self.share[count + 1]))
					count += 2
			self["config"].list = self.list
			self["config"].setList(self.list)

	def SaveConfig(self):
		setup = ['workgroup', 'netbios', 'SMB2', 'global']
		count = 0
		for line in self.settings:
			line = line.lower().replace(' ', '').replace('\t', '')
			if line.startswith('workgroup='):
				if "workgroup=" in setup:
					self.settings[count] = "workgroup = %s\n" % self.workgroup.value
					setup.remove('workgroup')
				else:
					self.settings[count] = ""
			elif line.startswith('netbiosname='):
				if "netbios" in setup:
					self.settings[count] = "netbios name = %s\n" % self.netbios.value
					setup.remove('netbios')
				else:
					self.settings[count] = ""
			elif line.startswith('maxprotocol=smb2'):
				if "SMB2" in setup:
					if not self.SMB2.value:
						self.settings.remove(self.settings[count])
					setup.remove('SMB2')
				else:
					self.settings[count] = ""
			count += 1
		settings = ""
		delete = False
		for line in self.settings:
			name = line.replace(' ', '').replace('\t', '')
			if name.startswith('#'):
				settings = settings + line
			else:
				if name.startswith('[global]'):
					if "global" in setup:
						settings = settings + line
						setup.remove('global')
						if "workgroup" in setup:
							settings = settings + "workgroup = %s\n" % self.workgroup.value
							setup.remove('workgroup')
						if "netbios" in setup:
							settings = settings + "netbios name = %s\n" % self.netbios.value
							setup.remove('netbios')
						if "SMB2" in setup:
							settings = settings + "max protocol = SMB2\n"
							setup.remove('SMB2')
					else:
						delete = True
				elif name.startswith('['):
					share = line[1:line.find(']')]
					count = 0
					while count < self.sharecount:
						if self.share[count] == share:
							if self.share[count + 1].value:
								delete = False
								settings = settings + line
							else:
								delete = True
							self.share.remove(share)
							self.sharecount -= 1
							count = self.sharecount
						count += 1
				elif not delete:
					settings = settings + line
		data = "read only = no\nguest ok = yes\nbrowseable = yes\n"
		data = data + "create mask = 0777\ndirectory mask = 0777\n"
		count = 0
		while count < self.sharecount:
			if self.share[count] == "root" and self.share[count + 1].value:
				settings = settings + "\n[root]\npath = /\n" + data
			elif self.share[count] == "media" and self.share[count + 1].value:
				settings = settings + "\n[media]\npath = /media\n" + data
			elif self.share[count] == "hdd" and self.share[count + 1].value:
				settings = settings + "\n[hdd]\npath = /hdd\n" + data
			elif self.share[count] == "movie" and self.share[count + 1].value:
				settings = settings + "\n[movie]\npath = /hdd/movie\n" + data
			count += 1
		try:
			f = open("/etc/samba/smb.conf", "w")
			f.write(settings)
			f.close()
			print "[SambaServer] save settings"
		except:
			print "[SambaServer] ERROR in save settings"

	def Cancel(self):
		ConfigListScreen.keyCancel(self)

	def Ok(self):
		if self.settings:
			if config.plugins.SambaServer.Start.value:
				self.SaveConfig()
				print "[SambaServer] restart samba"
				Console().ePopen("/etc/init.d/samba restart")
			else:
				print "[SambaServer] stop samba"
				Console().ePopen("/etc/init.d/samba stop")
		ConfigListScreen.keySave(self)

def main(session, **kwargs):
	session.open(SambaServer)

def StartSamba(reason, **kwargs):
	if config.plugins.SambaServer.Start.value \
		and config.plugins.SambaServer.StartOnStartup.value:
		if reason == 0: # Enigma start
			try:
				Console().ePopen("/etc/init.d/samba start")
				print "[SambaServer] start samba"
			except:
				pass
		elif reason == 1: # Enigma stop
			try:
				Console().ePopen("/etc/init.d/samba stop")
				print "[SambaServer] stop samba"
			except:
				pass

def Plugins(**kwargs):
	from os import path
	if path.exists("/etc/init.d/samba") and path.exists("/etc/samba/smb.conf"):
		from Plugins.Plugin import PluginDescriptor
		return [
		PluginDescriptor(name = _("Samba Server"),
			description = _("Configure Samba Server for network share."),
			where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main ),
		PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART,
			needsRestart = True, fnc = StartSamba)]
	return []