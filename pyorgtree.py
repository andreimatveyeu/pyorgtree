#!/usr/bin/python
import re
import datetime
import os
import cPickle
from tree import *
from header import *
from schedule import *

class OrgTreeData(object):
	data = None
	properties_dict = None
	schedule = None
	deadline = None

	def __init__(self, data):
		self.data = data
		properties_start = re.compile(".{0,}:PROPERTIES:")
		properties_end = re.compile(".{0,}:END:")
		lines = self.data.split('\n')
		properties_open = False
		property_match = re.compile(".{0,}:[a-zA-Z0-9]{1,100}:")
		schedule_match = re.compile(".{0,}SCHEDULED: .{1,}$")
		deadline_match = re.compile(".{0,}DEADLINE: .{1,}$")
		self.properties_dict = dict()
		for line in lines:
			if properties_start.match(line):
				properties_open = True
			elif properties_end.match(line):
				break
			elif schedule_match.match(line):
				self.schedule = Schedule(line)
			elif deadline_match.match(line):
				self.deadline = Deadline(line)
			else:
				if properties_open:
					if property_match.match(line):
						prop = re.sub(".{0,}:(?P<prop>[a-zA-Z0-9]{1,100}):.{0,}$", "\g<prop>", line)
						value = re.sub(".*:(?P<val>.{1,})$", "\g<val>", line).strip()
						self.properties_dict[prop] = value

	def get_data(self):
		return self.data

	def has_properties(self):
		return len(self.properties_dict.keys()) > 0

	def get_properties(self):
		return self.properties_dict

	def has_schedule(self):
		return self.schedule != None
	def get_schedule(self):
		return self.schedule
	def has_deadline(self):
		return self.deadline != None
	def get_deadline(self):
		return self.deadline

class OrgTree(Node):
	level = 0
	tree_type = None
	raw_data = ""
	data = None
	tag_dict = dict()
	header = None
	properties = None

	def get_header(self):
		return self.header

	def set_header(self, header):
		self.header = header

	def get_tag_dict(self):
		return self.tag_dict

	def get_trees_by_tag(self, tag):
		try:
			return self.tag_dict[tag]
		except KeyError:
			return []

	def get_data(self):
		if self.data == None:
			self.data = OrgTreeData(self.raw_data)
		return self.data.get_data()

	def has_schedule(self):
		if self.data == None:
			self.data = OrgTreeData(self.raw_data)
		return self.data.has_schedule()
	def get_schedule(self):
		if self.has_schedule():
			return self.data.get_schedule()

	def has_deadline(self):
		if self.data == None:
			self.data = OrgTreeData(self.raw_data)
		return self.data.has_deadline()

	def get_deadline(self):
		if self.data == None:
			self.data = OrgTreeData(self.raw_data)
		return self.data.get_deadline()

	def has_properties(self):
		if self.data == None:
			self.data = OrgTreeData(self.raw_data)
		if self.properties == None:
			self.properties = self.data.get_properties()
		return len(self.properties.keys()) > 0

	def get_properties(self):
		if self.data == None:
			self.data = OrgTreeData(self.raw_data)
		if self.properties == None:
			self.properties = self.data.get_properties()
		return self.properties

	def read_from_file(self, filename, line_number, level, tag_dict=None):
		if tag_dict:
			self.tag_dict = tag_dict
		self.level = level
		if self.level == 0:
			self.parent = None
		data = open(filename, 'r').readlines()
		tree_start_pattern = re.compile("^\*{1,} ")
		i = line_number
		while i < len(data):
			line = data[i]
			if tree_start_pattern.match(line):
				header = Header(line)
				new_level = header.get_level()
				if new_level > self.level:
					new_child = OrgTree()
					new_child.set_parent(self)
					new_child.set_header(header)
					if header.has_tags():
						for tag in header.get_tags():
							if tag not in self.tag_dict:
								self.tag_dict[tag] = []
							self.tag_dict[tag].append(new_child)
					self.add_child(new_child)
					continue_from  = new_child.read_from_file(filename, i+1, new_level, tag_dict=self.tag_dict)
					if not continue_from:
						break
					i = continue_from
				else:
					return i
			else:
			   self.raw_data += line
			   i += 1

	def __str__(self):
		return "OrgTree(level=%d; title=%s)" % (self.level, self.header.get_title())

class PickleSerializableOrgTree():
	def pickle_load(self, filename):
		try:
			inp = open(filename, 'rb')
			self = cPickle.load(inp)
			inp.close()
			return True
		except IOError:
			return False

	def pickle_dump(self, filename):
		try:
			out = open(filename, 'wb')
			cPickle.dump(self, out)
			out.close()
			return True
		except IOError:
			return False

class TextSerializableOrgTree():
	def to_string(self):
		return ""

class HashedOrgTree(OrgTree, PickleSerializableOrgTree, TextSerializableOrgTree):
	tree_dict = dict()
	def __init__(self):
		super(HashedOrgTree, self).__init__()

	def get_subtree_by_hash(self, subtree_hash):
		try:
			return self.tree_dict[subtree_hash]
		except KeyError:
			return None

	def get_tree_dict(self):
		return self.tree_dict

	def read_from_file(self, filename, line_number, level, tree_dict=None, tag_dict=None):
		if tree_dict:
			self.tree_dict = tree_dict
		if tag_dict:
			self.tag_dict = tag_dict
		self.level = level
		if self.level == 0:
			self.parent = None
		data = open(filename, 'r').readlines()
		tree_start_pattern = re.compile("^\*{1,} ")
		i = line_number
		while i < len(data):
			line = data[i]
			if tree_start_pattern.match(line):
				header = HashedHeader(line)
				new_level = header.get_level()
				if new_level > self.level:
					new_child = HashedOrgTree()
					new_child.set_parent(self)
					new_child.set_header(header)
					current_tree_hash = header.get_hash()
					if current_tree_hash:
						self.tree_dict[current_tree_hash] = new_child
					if header.has_tags():
						for tag in header.get_tags():
							if tag not in self.tag_dict:
								self.tag_dict[tag] = []
							self.tag_dict[tag].append(new_child)
					self.add_child(new_child)
					continue_from  = new_child.read_from_file(filename, i+1, new_level, tree_dict=self.tree_dict, tag_dict=self.tag_dict)
					if not continue_from:
						break
					i = continue_from
				else:
					return i
			else:
			   self.raw_data += line
			   i += 1

class OrgTreeWriter(object):
	orgtree = None
	def __init__(self, orgtree):
		assert isinstance(orgtree, OrgTree)
		self.orgtree = orgtree

	def write(self, filename):
		tree = self.orgtree
		out = open(filename, 'w')
		for _ in range(tree.get_header().get_level()):
			out.write("*")
		out.write(" ")
		out.write(self.orgtree.get_header().get_title())
		out.write(os.linesep)
		out.write(self.orgtree.get_data())
		out.close()
