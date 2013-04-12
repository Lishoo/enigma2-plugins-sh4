# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from os import environ
import gettext

def localeInit():
	environ["LANGUAGE"] = language.getLanguage()[:2]
	gettext.bindtextdomain("AlternativeSoftCamManager", resolveFilename(SCOPE_PLUGINS, \
		"Extensions/AlternativeSoftCamManager/locale"))

def _(txt):
	t = gettext.dgettext("AlternativeSoftCamManager", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
