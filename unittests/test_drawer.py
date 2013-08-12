from pyorgtree.drawer import *
import os

class TestDrawer(object):
	def test_drawer_simple(self):
		drawer = Drawer("LOGBOOK")
		data = "Lorem ipsum"
		drawer.set_data(data)
		assert drawer.get_data() == ":LOGBOOK:%s%s%s:END:" % (os.linesep, data, os.linesep)
