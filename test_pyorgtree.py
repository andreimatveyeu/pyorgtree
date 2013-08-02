#!/usr/bin/python
from pyorgtree import *

class TestPyOrgTree(object):
    def test_01(self):
        tree = OrgTree('')
        tree.read_from_file('test_data/tree01.org', 0, 0)
        assert tree.get_children()[0].get_hash() == '12345'
        
        tree_dict = tree.get_tree_dict()
        assert '12345' in tree_dict.keys()
        
        children = tree_dict['12345'].get_children()
        assert len(children) == 3

        children = tree.get_children()
        assert len(children) == 1

        children = tree_dict['45678'].get_children()
        assert len(children) == 0

        assert tree_dict['45678'].get_parent().get_hash() == '23456'

