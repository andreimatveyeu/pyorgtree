#!/usr/bin/python
from pyorgtree import *
import tempfile
import os
import datetime
from logging import debug, log, info

class TestHeader(object):
    def test_title_only(self):
        string = "** title test header"
        header = Header(string)
        assert not header.has_hash()
        assert header.get_hash() == None
        assert header.get_type() == None
        assert header.get_title() == "title test header"
        assert header.get_level() == 2
        assert header.get_priority() == None

    def test_header_type_hash_title(self):
        string = "*** TODO 12345: test header"
        header = Header(string)
        assert header.has_hash()
        assert header.get_hash() == "12345"
        assert header.get_type() == "TODO"
        assert header.get_title() == "test header"
        assert header.get_level() == 3

    def test_header_type_priority_hash_title(self):
        string = "* LOG [#A] z2389: TEST header"
        header = Header(string)
        assert header.has_hash()
        assert header.get_hash() == "z2389"
        assert header.get_type() == "LOG"
        assert header.get_title() == "TEST header"
        assert header.get_level() == 1
        assert header.get_priority() == "A"

    def test_header_priority_hash_title(self):
        string = "** [#A] z2389: TEST header"
        header = Header(string)
        assert header.has_hash()
        assert header.get_hash() == "z2389"
        assert header.get_type() == None
        assert header.get_title() == "TEST header"
        assert header.get_level() == 2
        assert header.get_priority() == "A"

    def test_header_priority_title(self):
        string = "** [#A] simple header"
        header = Header(string)
        assert not header.has_hash()
        assert header.get_hash() == None
        assert header.get_type() == None
        assert header.get_title() == "simple header"
        assert header.get_level() == 2
        assert header.get_priority() == "A"

    def test_header_timestamp(self):
        string = "** [1999-12-31 Wed 08:00] "
        header = Header(string)
        assert header.has_timestamp()        

        string = "** [1999-12-31 Wed 08:00]"
        header = Header(string)
        assert header.has_timestamp()        

        string = "** [1999-12-31 Wed]"
        header = Header(string)
        assert header.has_timestamp()        
        assert header.get_timestamp() == datetime.datetime(1999, 12, 31, 0, 0)
        
        string = "** LOG [1999-12-31 Wed 08:00]"
        header = Header(string)
        assert header.has_timestamp()        
        assert header.get_timestamp() == datetime.datetime(1999, 12, 31, 8, 0)

        string = "** LOG [1999-12-31 Wed 08:00] hello world"
        header = Header(string)
        assert header.has_timestamp()        
        assert header.get_timestamp() == datetime.datetime(1999, 12, 31, 8, 0)
        assert header.get_title() == "hello world"

        string = "** LOG [1999-12-31 Wed 08:00] zx839: hello world"
        header = Header(string)
        assert header.has_hash()
        assert header.get_hash() == 'zx839'
        assert header.has_timestamp()        
        assert header.get_timestamp() == datetime.datetime(1999, 12, 31, 8, 0)
        assert header.get_title() == "hello world"

        string = "***** [2011-10-14 Fri] iddww: test hello world"
        header = Header(string)
        assert header.has_hash()
        assert header.has_timestamp()
        assert header.get_timestamp(string=True) == "[2011-10-14 Fri]"
        assert header.get_timestamp(string=False) == datetime.datetime(2011, 10, 14, 0, 0)
        assert header.get_hash() == 'iddww'
        assert header.get_title() == 'test hello world'
        
    def test_header_tags(self):
        string = "** LOG simple title? :Tag1:Tag2:Tag3:"
        header = Header(string)
        assert header.has_tags()
        assert header.get_tags() == ['Tag1', 'Tag2', 'Tag3']
        assert header.get_title() == "simple title?"

        string = "** LOG simple title?\t:Tag1:"
        header = Header(string)
        assert header.has_tags()
        assert header.get_tags() == ['Tag1']
        assert header.get_title() == "simple title?"
        
        string = "** LOG :tag1:tag2:tag3"
        header = Header(string)
        assert not header.has_tags()

class TestTreeData(object):
    def test_properties(self):
        tree = OrgTree()
        tree.read_from_file('test_data/tree04.org', 0, 0)
        tree_dict = tree.get_tree_dict()

        assert tree_dict['38399'].has_properties()
        prop_dict = tree_dict['38399'].get_properties()
        assert len(prop_dict.keys()) == 2
        assert prop_dict['property1'] == 'value1'
        assert prop_dict['property2'] == 'value2'

        assert not tree_dict['38400'].has_properties()
        prop_dict = tree_dict['38400'].get_properties()
        assert len(prop_dict.keys()) == 0
        
    def test_scheduled(self):
        tree = OrgTree()
        tree.read_from_file('test_data/tree04.org', 0, 0)
        tree_dict = tree.get_tree_dict()

        assert not tree_dict['38399'].is_scheduled()
        assert tree_dict['38400'].is_scheduled()
        assert tree_dict['38400'].is_scheduled() == datetime.datetime(2013, 10, 21, 0, 0)
        
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
        assert tree.get_children()[0].get_header().get_hash() == '12345'

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
        assert tree_dict['45678'].get_parent().get_header().get_hash() == '23456'

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
        assert tree_dict['67890'].get_header().get_title() == "et felis ultrices elementum"

    def test_tags(self):
        tree = OrgTree()
        tree.read_from_file('test_data/tree03.org', 0, 0)
        tree_dict = tree.get_tree_dict()

        tag1_trees = tree.get_trees_by_tag('tag1')
        assert len(tag1_trees) == 2
        assert tag1_trees[0].get_header().get_hash() == '12345'
        assert tag1_trees[1].get_header().get_hash() == '38399'

        tree_dict['38400'].get_header().get_tags() == ['tag2', 'tag4']

        tag4_trees = tree.get_trees_by_tag('tag4')
        assert len(tag4_trees) == 2
        assert tag4_trees[0].get_header().get_hash() == '23456'
        assert tag4_trees[1].get_header().get_hash() == '38400'
        
        tag5_trees = tree.get_trees_by_tag('tag5')
        assert tag5_trees == []
        
