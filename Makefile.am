ACLOCAL_AMFLAGS = -I m4

SUBDIRS = \
	alternativesoftcammanager \
	antiscrollbar \
	audiosync \
	automaticcleanup \
	automatictimerlistcleanup \
	automaticvolumeadjustment \
	autoresolution \
	autotimer \
	babelzapper \
	bitrateviewer \
	bonjour \
	cdinfo \
	curlytx \
	dreamirc \
	dreammediathek \
	dvdbackup \
	dyndns \
	easyinfo \
	easymedia \
	ecasa \
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
	httpproxy \
	imdb \
	infobartunerstate \
	kiddytimer \
	lastfm \
	letterbox \
	libgisclubskin \
	logomanager \
	mediadownloader \
	menusort \
	merlinepg \
	merlinepgcenter \
	meteoitalia \
	mosaic \
	moviecut \
	movielistpreview \
	movieretitle \
	moviesearch \
	movieselectionquickbutton \
	movietagger \
	movieepg \
	mphelp \
	multirc \
	mytube \
	namezap \
	ncidclient \
	netcaster \
	networkbrowser \
	ofdb \
	orfat \
	orfteletext \
	partnerbox \
	passwordchanger \
	permanentclock \
	permanenttimeshift \
	pipservicerelation \
	pipzap \
	pluginhider \
	pluginsort \
	podcast \
	porncenter \
	quickbutton \
	quickepg \
	reconstructapsc \
	remotetimer \
	rsdownloader \
	sambaserver \
	seekbar \
	serienfilm \
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
	tvcharts \
	unwetterinfo \
	valixdcontrol \
	virtualzap \
	vlcplayer \
	vps \
	weatherplugin \
	webcamviewer \
	webbouqueteditor \
	webinterface \
	werbezapper \
	youtubeplayer \
	yttrailer \
	zaphistorybrowser \
	zapstatistic \
	zdfmediathek

metadir = $(datadir)/meta
meta_DATA = index-enigma2-plugins.xml
CLEANFILES = index-enigma2-plugins.xml

index-enigma2-plugins.xml: $(top_srcdir)/genmetaindex.py $(top_srcdir)/*/meta/plugin_*.xml
	$(AM_V_GEN)$(PYTHON) $^ > $@
