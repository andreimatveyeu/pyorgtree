#!/usr/bin/python
from pyorgtree import *
import tempfile
import os
from logging import debug, log, info

class TestPyOrgTree(object):
    _temp_file = None
    def teardown(self):
        if self._temp_file:
            print "Deleting temp file: %s" % self._temp_file
            os.unlink(self._temp_file)
            self._temp_file = None
            
    def test_parse(self):
        tree = OrgTree()
        tree.read_from_file('test_data/tree01.org', 0, 0)

        log(1, "Verify that first child hashes match")
        assert tree.get_children()[0].get_hash() == '12345'

        log(1, "Verify that first child is present in the tree hash map")
        tree_dict = tree.get_tree_dict()
        assert '12345' in tree_dict.keys()

        log(1, "Verify that first child has children")
        children = tree_dict['12345'].get_children()
        assert len(children) == 3

        log(1, "Verify that there is one root")
        children = tree.get_children()
        assert len(children) == 1

        log(1, "Verify that a leaf node has no children")
        children = tree_dict['45678'].get_children()
        assert len(children) == 0

        log(1, "Verify that a leaf node has correct parent")
        assert tree_dict['45678'].get_parent().get_hash() == '23456'

    def test_serialize(self):
        tree = OrgTree()
        tree.read_from_file('test_data/tree01.org', 0, 0)
        tree_dict = tree.get_tree_dict()
        
        _, self._temp_file = tempfile.mkstemp()
        log(1, "Dumping tree to file: %s" % self._temp_file)
        tree.pickle_dump(self._temp_file)

        log(1, "Loading tree from file: %s" % self._temp_file)
        new_tree = OrgTree()
        new_tree.pickle_load(self._temp_file)

        assert tree.get_tree_dict().keys() == new_tree.get_tree_dict().keys()
        for tree_hash in tree.get_tree_dict().keys():
            log(1, "Comparing trees: %s " % tree_hash)
            new_tree_dict = new_tree.get_tree_dict()
            assert new_tree_dict[tree_hash].get_data() == tree_dict[tree_hash].get_data()
            assert new_tree_dict[tree_hash].get_header() == tree_dict[tree_hash].get_header()

    def test_multiple(self):
        tree = OrgTree()
        tree.read_from_file('test_data/tree02.org', 0, 0)
        tree_dict = tree.get_tree_dict()

        assert len(tree.get_children()) == 2

        assert isinstance(tree_dict['67890'], OrgTree)
        assert tree_dict['67890'].get_title() == "et felis ultrices elementum"
