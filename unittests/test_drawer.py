from drawer import *
import os

class TestDrawer(object):
	def test_drawer_simple(self):
		drawer = Drawer("LOGBOOK")
		data = "Lorem ipsum"
		drawer.set_data(data)
		assert "%s" % drawer == ":LOGBOOK:%s%s%s:END:" % (os.linesep, data, os.linesep)
