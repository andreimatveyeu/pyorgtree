#!/usr/bin/python
from pyorgtree import *

class TestPyOrgTree(object):
    def test_01(self):
        tree = OrgTree('')
        tree.read_from_file('tree.org')
        print tree
        print tree.get_data()
        assert 1 == 1
