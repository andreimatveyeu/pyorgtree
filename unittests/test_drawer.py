from pyorgtree import *
from drawer import *
import os

class TestDrawer(object):
	def test_drawer_simple(self):
		drawer = Drawer("LOGBOOK")
		data = "Lorem ipsum"
		drawer.set_data(data)
		assert "%s" % drawer == ":LOGBOOK:%s%s%s:END:" % (os.linesep, data, os.linesep)

	def test_drawer_read(self):
		tree = HashedOrgTree()
		tree.read_from_file('unittests/test_data/tree07.org', 0, 0)
		drawers = tree[1].get_data().get_drawers()
		assert len(drawers) == 2
		assert drawers[0].get_data() == 'logbook data 1'
		assert drawers[1].get_data() == 'logbook data 2'
		assert drawers[0].get_name() == "LOGBOOK1"
		assert drawers[1].get_name() == "LOGBOOK2"		
