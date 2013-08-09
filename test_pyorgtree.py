#!/usr/bin/python
from pyorgtree import *
import tempfile
import os
import datetime
from logging import debug, log, info

class TestHeader(object):
	def test_title_only(self):
		string = "** title test header"
		header = HashedHeader(string)
		assert not header.has_hash()
		assert header.get_hash() == None
		assert header.get_type() == None
		assert header.get_title() == "title test header"
		assert header.get_level() == 2
		assert header.get_priority() == None

	def test_header_type_hash_title(self):
		string = "*** TODO 12345: test header"
		header = HashedHeader(string)
		assert header.has_hash()
		assert header.get_hash() == "12345"
		assert header.get_type() == "TODO"
		assert header.get_title() == "test header"
		assert header.get_level() == 3

	def test_header_type_priority_hash_title(self):
		string = "* LOG [#A] z2389: TEST header"
		header = HashedHeader(string)
		assert header.has_hash()
		assert header.get_hash() == "z2389"
		assert header.get_type() == "LOG"
		assert header.get_title() == "TEST header"
		assert header.get_level() == 1
		assert header.get_priority() == "A"

	def test_header_priority_hash_title(self):
		string = "** [#A] z2389: TEST header"
		header = HashedHeader(string)
		assert header.has_hash()
		assert header.get_hash() == "z2389"
		assert header.get_type() == None
		assert header.get_title() == "TEST header"
		assert header.get_level() == 2
		assert header.get_priority() == "A"

	def test_header_priority_title(self):
		string = "** [#A] simple header"
		header = HashedHeader(string)
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
		header = HashedHeader(string)
		assert header.has_hash()
		assert header.get_hash() == 'zx839'
		assert header.has_timestamp()
		assert header.get_timestamp() == datetime.datetime(1999, 12, 31, 8, 0)
		assert header.get_title() == "hello world"

		string = "***** [2011-10-14 Fri] iddww: test hello world"
		header = HashedHeader(string)
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
		tree = HashedOrgTree()
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
		tree = HashedOrgTree()
		tree.read_from_file('test_data/tree04.org', 0, 0)
		tree_dict = tree.get_tree_dict()

		assert not tree_dict['38399'].has_schedule()
		assert tree_dict['38400'].has_schedule()
		assert tree_dict['38400'].get_schedule().get_datetime() == datetime.datetime(2013, 10, 21, 0, 0)

		assert tree_dict['38401'].has_schedule()
		assert tree_dict['38401'].get_schedule().get_datetime() == datetime.datetime(2013, 10, 25, 15, 0)

	def test_deadline(self):
		tree = HashedOrgTree()
		tree.read_from_file('test_data/tree04.org', 0, 0)
		tree_dict = tree.get_tree_dict()

		assert not tree_dict['38401'].has_deadline()
		assert tree_dict['38402'].has_deadline()
		assert tree_dict['38402'].get_deadline().get_datetime() == datetime.datetime(2013, 11, 30, 0, 0)

class TestSchedule(object):
	def test_schedule_date(self):
		line = "SCHEDULED: <2013-09-20 Fri>"
		schedule = Schedule(line)

		assert schedule.has_date_only()
		assert schedule.get_datetime() == datetime.datetime(2013, 9, 20, 0, 0)

	def test_schedule_datetime(self):
		line = "SCHEDULED: <2013-09-20 Fri 15:05>"
		schedule = Schedule(line)

		assert not schedule.has_date_only()
		assert schedule.get_datetime() == datetime.datetime(2013, 9, 20, 15, 5)

	def test_schedule_repeater(self):
		line = "SCHEDULED: <2013-09-20 Fri 15:05 +1d>"
		schedule = Schedule(line)
		assert schedule.has_repeater()
		assert schedule.get_repeater() == "+1d"
		assert schedule.get_repeat_interval() == (1, "d")
		assert schedule.has_overdue_repeater()

		line = "SCHEDULED: <2013-09-20 Fri 15:05 ++5y>"
		schedule = Schedule(line)
		assert schedule.has_repeater()
		assert schedule.get_repeater() == "++5y"
		assert schedule.get_repeat_interval() == (5, "y")
		assert not schedule.has_overdue_repeater()

	def test_schedule_delay(self):
		line = "SCHEDULED: <2013-09-20 Fri 15:05 -1d>"
		schedule = Schedule(line)
		assert schedule.has_delay()
		assert schedule.get_delay() == "-1d"
		assert schedule.get_delay_interval() == (1, "d")

		line = "SCHEDULED: <2013-09-20 Fri 15:05 --3w>"
		schedule = Schedule(line)
		assert schedule.has_delay()
		assert schedule.get_delay() == "--3w"
		assert schedule.get_delay_interval() == (3, "w")

	def test_schedule_repeater_and_delay(self):
		line = "SCHEDULED: <2013-09-20 Fri 15:05 +10m -5w>"
		schedule = Schedule(line)
		assert schedule.has_delay()
		assert schedule.get_delay() == "-5w"
		assert schedule.get_delay_interval() == (5, "w")
		assert schedule.has_repeater()
		assert schedule.get_repeater() == "+10m"
		assert schedule.get_repeat_interval() == (10, "m")

		line = "SCHEDULED: <2013-09-20 Fri 15:05 --30d ++2m>"
		schedule = Schedule(line)
		assert schedule.has_delay()
		assert schedule.get_delay() == "--30d"
		assert schedule.get_delay_interval() == (30, "d")
		assert schedule.has_repeater()
		assert schedule.get_repeater() == "++2m"
		assert schedule.get_repeat_interval() == (2, "m")

class TestOrgTree(object):
	def test_read_from_file(self):
		tree = OrgTree()
		tree.read_from_file('test_data/tree00.org', 0, 0)
		assert tree[1][0].get_header().get_title() == "Lorem ipsum dolor sit amet"
		assert len(tree[1][0].get_children()) == 3
		assert tree[1][1].get_header().get_title() == "interdum in, laoreet ut nisl"
		assert tree[1][3].get_header().get_title() == "Fullam exorbitus scribit"
		assert tree[1][1][1].get_header().get_title() == "Ut ut dolor et felis ultrices"

class TestDeadline(object):
	def test_deadline_date(self):
		line = "DEADLINE: <2013-09-20 Fri>"
		deadline = Deadline(line)

		assert deadline.has_date_only()
		assert deadline.get_datetime() == datetime.datetime(2013, 9, 20, 0, 0)

	def test_deadline_datetime(self):
		line = "DEADLINE: <2013-09-20 Fri 15:05>"
		deadline = Deadline(line)

		assert not deadline.has_date_only()
		assert deadline.get_datetime() == datetime.datetime(2013, 9, 20, 15, 5)

class TestHashedOrgTree(object):
	_temp_file = None
	def teardown(self):
		if self._temp_file:
			os.unlink(self._temp_file)
			self._temp_file = None

	def test_parse(self):
		tree = HashedOrgTree()
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
		tree = HashedOrgTree()
		tree.read_from_file('test_data/tree01.org', 0, 0)
		tree_dict = tree.get_tree_dict()

		_, self._temp_file = tempfile.mkstemp()
		log(1, "Dumping tree to file: %s" % self._temp_file)
		tree.pickle_dump(self._temp_file)

		log(1, "Loading tree from file: %s" % self._temp_file)
		new_tree = HashedOrgTree()
		new_tree.pickle_load(self._temp_file)
		assert tree.get_tree_dict().keys() == new_tree.get_tree_dict().keys()
		for tree_hash in tree.get_tree_dict().keys():
			log(1, "Comparing trees: %s " % tree_hash)
			new_tree_dict = new_tree.get_tree_dict()
			assert new_tree_dict[tree_hash].get_data() == tree_dict[tree_hash].get_data()
			assert new_tree_dict[tree_hash].get_header() == tree_dict[tree_hash].get_header()

	def test_multiple(self):
		tree = HashedOrgTree()
		tree.read_from_file('test_data/tree02.org', 0, 0)
		tree_dict = tree.get_tree_dict()

		assert len(tree.get_children()) == 2
		assert isinstance(tree_dict['67890'], OrgTree)
		assert tree_dict['67890'].get_header().get_title() == "et felis ultrices elementum"

	def test_tags(self):
		tree = HashedOrgTree()
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

class TestTreeWriter(object):
	_temp_file = None
	def teardown(self):
		if self._temp_file:
			os.unlink(self._temp_file)
			self._temp_file = None

	def test_write_read_simple(self):
		tree = OrgTree()
		tree.read_from_file('test_data/tree05.org', 0, 0)
		tw = OrgTreeWriter(tree[1])
		_, self._temp_file = tempfile.mkstemp()
		tw.write(self._temp_file)
		original_file = open('test_data/tree05.org', 'r').read()
		written_file = open(self._temp_file, 'r').read()
		assert written_file == original_file
