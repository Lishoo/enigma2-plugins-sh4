from enigma import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
from enigma import eEPGCache
from Screens.Standby import TryQuitMainloop
import os
import gettext
import time
import new
import _enigma
import re

quickepg_title= _("Quick EPG Import")
quickepg_plugindir="/usr/lib/enigma2/python/Plugins/Extensions/QuickEPG" 

os.environ['LANGUAGE']='en'
quickepg_language='en'

if os.path.exists("/etc/enigma2/settings") == True:
   f = open("/etc/enigma2/settings")
   line = f.readline()
   while (line):
	line = f.readline().replace("\n","")
	sp = line.split("=")
	if (sp[0] == "config.osd.language"):
	   sp2 = sp[1].split("_")
           quickepg_language = sp2[0]
           if os.path.exists("%s/locale/%s" % (quickepg_plugindir, quickepg_language)) == True:
              os.environ["LANGUAGE"] = sp[1]
           else:
              os.environ['LANGUAGE']='en'
   f.close

_=gettext.Catalog('QuickEPG', '%s/locale' % quickepg_plugindir).gettext


def main(session,**kwargs):
    session.open(QuickEPGPlugin)

def autostart(reason,**kwargs):
    if reason == 0:
        print "[QUICKEPG] no autostart"

def Plugins(path,**kwargs):
    return [PluginDescriptor(
        name=_("Quick EPG Import"), 
        description="Download and import EPG for exUSSR channels", 
        where = PluginDescriptor.WHERE_PLUGINMENU,icon="quick_epg.png",
        fnc = main
        ),
	PluginDescriptor(name=_("Quick EPG Import"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]

class QuickEPGPlugin(Screen):
    skin = """
        <screen position="center,center" size="600,100" title="%s" >
            <widget name="menu" position="10,10" size="590,90" scrollbarMode="showOnDemand" />
        </screen>""" % quickepg_title
        
    def __init__(self, session, args = 0):
        self.skin = QuickEPGPlugin.skin
        self.session = session
        Screen.__init__(self, session)
        self.menu = args
        quickepglist = []
        quickepglist.append((_("Download EPG - events in rus. language"), "ru"))
        quickepglist.append((_("Download EPG - events in ukr. language"), "ua"))     
        self["menu"] = MenuList(quickepglist)
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"],{"ok": self.go,"back": self.close,}, -1)

    def go(self):
	
	self.mbox = self.session.openWithCallback(self.go_continue,MessageBox,(_("Downloading... Please wait!")), MessageBox.TYPE_INFO, timeout = 3)


    def go_continue(self,ret):

	try:
		if os.path.exists('/usr/bin/enigma2.sh'):
			content = open('/usr/bin/enigma2.sh', 'r').read()
			m = re.search('epg.dat', content)
			if not m:
				os.system("cp /usr/bin/enigma2.sh /usr/bin/enigma2.sh.xmltvbak")
				line_number = 2 
				with open('/usr/bin/enigma2.sh') as f:
     					lines = f.readlines()
				lines.insert(line_number, '[ -f /media/hdd/epg_new.dat ] && cp /media/hdd/epg_new.dat /media/hdd/epg.dat\n')
				with open('/usr/bin/enigma2.sh', 'w') as f:
     					f.writelines(lines)
		lang = self["menu"].l.getCurrentSelection()[1]
		ret = os.system("wget -q http://linux-sat.tv/epg/epg_%s.dat.gz -O /hdd/epg_new.dat.gz" % (lang))
		if ret:
			self.mbox = self.session.open(MessageBox,(_("Sorry, the EPG download error. Try again later or check your internet connection")), MessageBox.TYPE_INFO, timeout = 6 )
			return
		os.system("gzip -df /hdd/epg_new.dat.gz")
		os.system("cp -f /hdd/epg_new.dat /hdd/epg.dat")
		os.system("rm -f epg_new.dat.gz")
		self.mbox = self.session.open(MessageBox,(_("the EPG download is complete")), MessageBox.TYPE_INFO, timeout = 4)
        except:
		self.mbox = self.session.open(MessageBox,(_("Error")), MessageBox.TYPE_INFO, timeout = 4 )
	try:
		epgcache = new.instancemethod(_enigma.eEPGCache_load,None,eEPGCache)
		epgcache = eEPGCache.getInstance().load()
		self.close()
	except:
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("Restart GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))

    def restartGUI(self, answer):

	if answer is True:
		self.session.open(TryQuitMainloop, 3)
