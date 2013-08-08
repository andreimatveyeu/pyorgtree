#!/usr/bin/python
import re
import datetime
import os
import cPickle
from tree import *

class Header(object):
	line = None
	title = None

	def __init__(self, line):
		self.line = line.strip()

	def get_level(self):
		level = 0
		for char in self.line:
			if char == "*":
				level += 1
			else:
				break
		return level

	def has_tags(self):
		patterns = []
		patterns.append(re.compile(".{0,}:[a-zA-Z0-9\:]{1,}:$"))
		for pattern in patterns:
			if pattern.match(self.line):
				return True
		return False

	def get_tags(self):
		if self.has_tags():
			tag_string = re.sub(".{0,}( |\t)(?P<tags>:[a-zA-Z0-9\:]*:)$", "\g<tags>", self.line)
			return tag_string[1:-1].split(":")
		return []

	def has_priority(self):
		patterns = []
		patterns.append(re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] "))
		patterns.append(re.compile("\*{1,} \[[#][A-Z]\] "))
		for pattern in patterns:
			if pattern.match(self.line):
				return True
		return False

	def get_priority(self):
		if self.has_priority():
			prio = re.sub(".{1,} (?P<prio>\[#[A-Z]\]) .{0,}", "\g<prio>", self.line)
			return prio[2:3]
		else:
			return None

	def has_type(self):
		patterns = []
		patterns.append(re.compile("\*{1,} [A-Z]{3,5} "))  # Level, keyword, priority and hash
		for pattern in patterns:
			if pattern.match(self.line):
				return True
		return False

	def get_type(self):
		if self.has_type():
			tree_type = re.sub("\*{1,} (?P<type>[A-Z]{3,5}) .{0,}", "\g<type>", self.line)
			return tree_type
		else:
			return None

	def has_hash(self):
		patterns = []
		patterns.append(re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] [a-z0-9]{5}:"))  # Level, keyword, priority and hash
		patterns.append(re.compile("\*{1,} \[\#[A-Z]\] [a-z0-9]{5}:"))  # Level, priority and hash
		patterns.append(re.compile("\*{1,} [A-Z]{3,5} [a-z0-9]{5}:"))  # Level, keyword, and hash
		patterns.append(re.compile("\*{1,} ([A-Z]{3,5} |.{0,})\[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0,})\]($|.{0,}) [a-z0-9]{5}:"))  # Level, keyword, timestamp
		patterns.append(re.compile("\*{1,} [a-z0-9]{5}:")) # Level, hash
		for pattern in patterns:
			if pattern.match(self.line):
				return True
		return False

	def has_timestamp(self):
		patterns = []
		patterns.append(re.compile("\*{1,} ([A-Z]{3,5} |.{0,})\[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0,})\]($|.{0,})"))  # Level, keyword, timestamp
		for pattern in patterns:
			if pattern.match(self.line):
				return True
		return False

	def get_timestamp(self, string=False):
		if self.has_timestamp():
			time_string = re.sub(".{0,}(?P<time>\[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0,})\]).{0,}", "\g<time>", self.line)
			if not string:
				year = int(time_string[1:5])
				month = int(time_string[6:8])
				day = int(time_string[9:11])
				try:
					hour = int(time_string[16:18])
					minute = int(time_string[19:21])
				except ValueError:
					hour = 0
					minute = 0
				return datetime.datetime(year, month, day, hour, minute)
			else:
				return time_string
		else:
			return None

	def get_title(self):
		if self.title == None:
			result = self.line
			if self.has_tags():
				tag_string = re.sub(".{0,}( |\t)(?P<tags>:[a-zA-Z0-9\:]*:)$", "\g<tags>", result)
				result = re.sub(tag_string, "", result)
			if self.has_hash():
				tree_hash = self.get_hash()
				result = re.sub(tree_hash + ':', '', result)
			if self.has_priority():
				priority = self.get_priority()
				result = re.sub('\[#%s\]' % priority , '', result)
			if self.has_type():
				tree_type = self.get_type()
				result = re.sub(tree_type, '', result)
			if self.has_timestamp():
				timestamp = self.get_timestamp(string=True)
				timestamp = re.sub("\[", "\\[", timestamp)
				timestamp = re.sub("\]", "\\]", timestamp)
				result = re.sub(timestamp, '', result)
			self.title = result[self.get_level():].strip()
		return self.title

	def get_hash(self):
		patterns = []
		patterns.append(re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] "))  # Level, keyword, priority and hash
		patterns.append(re.compile("\*{1,} \[\#[A-Z]\] "))  # Level, priority and hash
		patterns.append(re.compile("\*{1,} ([A-Z]{3,5} |.{0,})\[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0,})\] "))  # Level, keyword, timestamp
		patterns.append(re.compile("\*{1,} [A-Z]{3,5} "))  # Level, keyword, and hash
		patterns.append(re.compile("\*{1,} ")) # Level, hash
		if self.has_hash():
			for pattern in patterns:
				if pattern.match(self.line):
					return pattern.sub('', self.line)[0:5]
		else:
			return None

class Schedule(object):
	schedule_line = None
	has_repeater = None
	datetime = None
	has_dateonly = None
	keyword = "SCHEDULED"
	repeater = None
	repeat_interval = None

	def __init__(self, schedule_line):
		schedule_datetime_match = re.compile(".{0,}%s: <[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [a-zA-Z]{3} [0-2][0-9]:[0-5][0-9].{0,}$" % self.keyword)
		schedule_date_match = re.compile(".{0,}%s: <[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [a-zA-Z]{3}.{0,}$" % self.keyword)
		schedule_repeater_match = re.compile(".{1,} [\+]{1,2}[0-9]{1,4}[dwmy]")
		schedule_delay_match = re.compile(".{1,} [\-]{1,2}[0-9]{1,4}[dwmy]")
		self.schedule_line = schedule_line
		if schedule_datetime_match.match(self.schedule_line):
			self.datetime = self._extract_datetime(self.schedule_line)
			self.has_dateonly = False
		elif schedule_date_match.match(self.schedule_line):
			self.datetime = self._extract_date(self.schedule_line)
			self.has_dateonly = True
		else:
			raise Exception("Can't parse line: %s" % self.schedule_line)
		if schedule_repeater_match.match(self.schedule_line):
			self.repeater = self._extract_repeater(self.schedule_line)
		if schedule_delay_match.match(self.schedule_line):
			self.delay = self._extract_delay(self.schedule_line)

	def _extract_repeater(self, line):
		repeater = re.sub(".{1,} (?P<repeater>[\+]{1,2}[0-9]{1,4}[dwmy]).{1,}", "\g<repeater>", line)
		return repeater
	def _extract_delay(self, line):
		delay = re.sub(".{1,} (?P<repeater>[\-]{1,2}[0-9]{1,4}[dwmy]).{1,}", "\g<repeater>", line)
		return delay

	def _extract_date(self, line):
		time_string = re.sub(".{0,}%s: <(?P<date>[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]).{0,}$" % self.keyword, "\g<date>", line)
		year = int(time_string[0:4])
		month = int(time_string[5:7])
		day = int(time_string[8:10])
		return datetime.datetime(year, month, day, 0, 0)

	def _extract_datetime(self, line):
		time_string = re.sub(".{0,}%s: <(?P<date>[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]) [a-zA-Z]{3} (?P<time>[0-2][0-9]:[0-5][0-9]).{0,}$" % self.keyword, "\g<date> \g<time>", line)
		year = int(time_string[0:4])
		month = int(time_string[5:7])
		day = int(time_string[8:10])
		hour = int(time_string[11:13])
		minute = int(time_string[14:16])
		return datetime.datetime(year, month, day, hour, minute)

	def has_date_only(self):
		return self.has_dateonly
	def has_repeater(self):
		return self.repeater != None
	def get_repeater(self):
		return self.repeater
	def has_delay(self):
		return self.delay != None
	def get_delay(self):
		return self.delay
	def has_overdue_repeater(self):
		if self.has_repeater():
			if re.compile("\+[0-9]").match(self.get_repeater()):
				return True
			else:
				return False
		else:
			return False
	def get_repeat_interval(self):
		if self.repeat_interval == None and self.has_repeater():
			repeater = self.get_repeater()
			interval = re.sub("\+{1,2}(?P<num>[0-9]{1,4}).{1,}", "\g<num>", repeater)
			interval = int(interval)
			unit = re.sub(".{1,}(?P<unit>[dwmy])", "\g<unit>", repeater)
			return (interval, unit)
		else:
			return None
	def get_delay_interval(self):
		if self.has_delay():
			interval = re.sub("[-]{1,2}(?P<num>[0-9]{1,4}).{1,}", "\g<num>", self.delay)
			interval = int(interval)
			unit = re.sub(".{1,}(?P<unit>[dwmy])", "\g<unit>", self.delay)
		return (interval, unit)

	def get_datetime(self):
		return self.datetime

class Deadline(Schedule):
	keyword = "DEADLINE"

class TreeData(object):
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
			self.data = TreeData(self.raw_data)
		return self.data.get_data()

	def has_schedule(self):
		if self.data == None:
			self.data = TreeData(self.raw_data)
		return self.data.has_schedule()
	def get_schedule(self):
		if self.has_schedule():
			return self.data.get_schedule()

	def has_deadline(self):
		if self.data == None:
			self.data = TreeData(self.raw_data)
		return self.data.has_deadline()

	def get_deadline(self):
		if self.data == None:
			self.data = TreeData(self.raw_data)
		return self.data.get_deadline()

	def has_properties(self):
		if self.data == None:
			self.data = TreeData(self.raw_data)
		if self.properties == None:
			self.properties = self.data.get_properties()
		return len(self.properties.keys()) > 0

	def get_properties(self):
		if self.data == None:
			self.data = TreeData(self.raw_data)
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

class HashedOrgTree(OrgTree):
	tree_dict = None
	
	def __init__(self):
		super(HashedOrgTree, self).__init__()
		self.tree_dict = dict()
		
	def get_subtree_by_hash(self, subtree_hash):
		try:
			return self.tree_dict[subtree_hash]
		except KeyError:
			return None
	def get_tree_dict(self):
		return self.tree_dict
		
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
				header = Header(line)
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

