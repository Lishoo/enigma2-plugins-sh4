ACLOCAL_AMFLAGS = -I m4

SUBDIRS = \
	antiscrollbar \
	audiosync \
	automaticcleanup \
	automaticvolumeadjustment \
	autoresolution \
	autotimer \
	babelzapper \
	bitrateviewer \
	bonjour \
	cdinfo \
	curlytx \
	dreamexplorer \
	dreamirc \
	dreammediathek \
	dvdbackup \
	dyndns \
	easyinfo \
	easymedia \
	eibox \
	elektro \
	emailclient \
	emission \
	epgrefresh \
	epgsearch \
	eurotictv \
	filebrowser \
	fritzcall \
	fstabeditor \
	ftpbrowser \
	googlemaps \
	growlee \
	hddmanager \
	httpproxy \
	imdb \
	infobartunerstate \
	kiddytimer \
	letterbox \
	libgisclubskin \
	logomanager \
	mediadownloader \
	merlinepg \
	merlinepgcenter \
	meteoitalia \
	mosaic \
	moviecut \
	movieretitle \
	movieselectionquickbutton \
	movietagger \
	mphelp \
	multiquickbutton \
	multirc \
	ncidclient \
	netcaster \
	networkbrowser \
	ofdb \
	orfat \
	orfteletext \
	osdadjustment \
	partnerbox \
	permanentclock \
	permanenttimeshift \
	pipservicerelation \
	pipzap \
	pluginhider \
	pluginsort \
	porncenter \
	quickbutton \
	quickepg \
	reconstructapsc \
	remotetimer \
	rsdownloader \
	sambaserver \
	seekbar \
	setpasswd \
	shoutcast \
	showclock \
	simplerss \
	startupservice \
	startuptostandby \
	subsdownloader2 \
	svdrp \
	tageditor \
	trafficinfo \
	transcodingsetup \
	tvcharts \
	toolkit \
	unwetterinfo \
	valixdcontrol \
	vfd-icons-minimalwithclock \
	virtualzap \
	vlcplayer \
	vps \
	weatherplugin \
	webcamviewer \
	werbezapper \
	youtubeplayer \
	zaphistorybrowser \
	zapstatistic \
	zdfmediathek \
	webinterface

metadir = $(datadir)/meta
meta_DATA = index-enigma2-plugins.xml
CLEANFILES = index-enigma2-plugins.xml

index-enigma2-plugins.xml: $(top_srcdir)/genmetaindex.py $(top_srcdir)/*/meta/plugin_*.xml
	$(AM_V_GEN)$(PYTHON) $^ > $@
