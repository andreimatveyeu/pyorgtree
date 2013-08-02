#!/usr/bin/python
from pyorgtree import *

class TestPyOrgTree(object):
    def test_01(self):
        tree = OrgTree('')
        tree.read_from_file('tree.org', 0, 0)
        print tree
        print tree.get_data()
        tree_dict = tree.get_tree_dict()
        children = tree_dict['12345'].get_children()
        for child in children:
            print child.get_parent().get_hash()
            print child.get_header()
        print tree_dict['45678'].get_parent().get_hash()
        assert 1 == 1
