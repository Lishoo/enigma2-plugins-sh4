# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from gettext import bindtextdomain, dgettext, gettext
from os import environ

def localeInit():
	environ["LANGUAGE"] = language.getLanguage()[:2]
	bindtextdomain("AlternativeSoftCamManager", resolveFilename(SCOPE_PLUGINS, \
		"Extensions/AlternativeSoftCamManager/locale"))

def _(txt):
	t = dgettext("AlternativeSoftCamManager", txt)
	if t == txt:
		t = gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
