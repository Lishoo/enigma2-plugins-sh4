/*
  eEITSave E2
  (c) 2010 by Dr. Best  <dr.best@dreambox-tools.info>
*/

using namespace std;
#include <lib/dvb/dvb.h>
#include <lib/dvb/epgcache.h>
#include <fcntl.h>

#define HILO(x) (x##_hi << 8 | x##_lo)

static void SaveEIT(const char *ref, const char *filename, int  eit_event_id, time_t begTime, time_t endTime)
{
	eServiceReference mref = eServiceReference(ref);
	std::string fname = filename;
	fname.erase(fname.length()-2, 2);
	fname += "eit";
	eEPGCache::getInstance()->saveEventToFile(fname.c_str(), mref, eit_event_id, begTime, endTime);
}

extern "C" {


static PyObject *
SaveEIT(PyObject *self, PyObject *args)
{
	char* var1;
	char* var2;
	int var3;
	time_t var4;
	time_t var5;
	if (PyTuple_Size(args) != 5 || !PyArg_ParseTuple(args, "ssiii", &var1, &var2, &var3, &var4, &var5))
		Py_RETURN_NONE;
	else
		SaveEIT(var1,var2, var3, var4, var5);
	Py_RETURN_NONE;
}


static PyMethodDef module_methods[] = {
	{"SaveEIT", (PyCFunction)SaveEIT,  METH_VARARGS,
	 "SaveEIT"
	},
	{NULL, NULL, 0, NULL} 
};

PyMODINIT_FUNC
initeitsave(void)
{
	Py_InitModule3("eitsave", module_methods,
		"EIT Saver");
}
};

