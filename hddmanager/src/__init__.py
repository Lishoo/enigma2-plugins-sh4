from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

from gettext import bindtextdomain, dgettext, gettext
from os import environ


def localeInit():
	environ["LANGUAGE"] = language.getLanguage()[:2]
	bindtextdomain("HddManager", resolveFilename(SCOPE_PLUGINS, \
		"Extensions/HddManager/locale"))

def _(txt):
	t = dgettext("HddManager", txt)
	if t == txt:
		t = gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)

