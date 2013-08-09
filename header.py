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
		patterns.append(re.compile("\*{1,} [A-Z]{3,5} ")) 
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

	def has_timestamp(self):
		patterns = []
		patterns.append(re.compile("\*{1,} ([A-Z]{3,5} |.{0,})\[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0,})\]($|.{0,})"))  
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


class HashedHeader(Header):
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

	def get_title(self):
		title = super(HashedHeader, self).get_title()
		if self.has_hash():
			tree_hash = self.get_hash()
			title = re.sub(tree_hash + ':', '', title).strip()
		return title
