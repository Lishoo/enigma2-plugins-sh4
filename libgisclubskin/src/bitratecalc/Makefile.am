include $(top_srcdir)/Rules-cpp.mak

installdir = $(libdir)/enigma2/python/Components/Converter

install_LTLIBRARIES = bitratecalc.la

bitratecalc_la_SOURCES = \
	bitratecalc.cpp \
	bitratecalc.h

bitratecalc_la_LDFLAGS = \
	-avoid-version -module

bitratecalc_la_LIBADD = \
	@LIBCRYPTO_LIBS@
