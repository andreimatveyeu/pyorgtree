import re
import datetime
import os
import cPickle
from tree import *

class HeaderTags(object):
	tags = None
	def has_tags(self):
		if self.tags == None:
			self.get_tags()
		return len(self.tags) > 0
		
	def get_tags(self):
		if self.tags == None:
			if re.compile(".{0,}( |\t):[a-zA-Z0-9\:]*:$").match(self.line):
				tag_string = re.sub(".{0,}( |\t)(?P<tags>:[a-zA-Z0-9\:]*):$", "\g<tags>", self.line)
				self.tags = tag_string[1:].split(":")
			else:
				self.tags = []
		return self.tags

class HeaderPriority(object):
	priority = "NA"
	
	def has_priority(self):
		if self.priority == "NA":
			self.get_priority()
		return self.priority != None

	def get_priority(self):
		if self.priority == "NA":
			patterns = []
			patterns.append(re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] "))
			patterns.append(re.compile("\*{1,} \[[#][A-Z]\] "))
			self.priority = None
			for pattern in patterns:
				if pattern.match(self.line):
					prio = re.sub(".{1,} (?P<prio>\[#[A-Z]\]) .{0,}", "\g<prio>", self.line)
					self.priority = prio[2:3]
					break
		return self.priority

class HeaderType(object):
	header_type = "NA"
	
	def has_type(self):
		if self.header_type == "NA":
				self.get_type()
		return self.header_type

	def get_type(self):
		if self.header_type == "NA":
			self.header_type = None
			patterns = []
			patterns.append(re.compile("\*{1,} [A-Z]{3,5} ")) 
			for pattern in patterns:
				if pattern.match(self.line):
					self.header_type = re.sub("\*{1,} (?P<type>[A-Z]{3,5}) .{0,}", "\g<type>", self.line)
		return self.header_type

class HeaderTimestamp(object):
	timestamp = datetime.datetime(1970, 1, 1, 0, 0)
	timestamp_time_included = True
	def has_timestamp(self):
		if self.timestamp == datetime.datetime(1970, 1, 1, 0, 0):
			self.get_timestamp()
		return self.timestamp != None
		
	def get_timestamp_string(self):
		if self.timestamp == datetime.datetime(1970, 1, 1, 0, 0):
			self.get_timestamp()
		if self.timestamp_time_included:
			return self.timestamp.strftime("[%Y-%m-%d %a %H:%M]")	
		else:
			return self.timestamp.strftime("[%Y-%m-%d %a]")	
			
	def get_timestamp(self):
		if self.timestamp == datetime.datetime(1970, 1, 1, 0, 0):
			self.timestamp = None
			patterns = []
			patterns.append(re.compile("\*{1,} ([A-Z]{3,5} |.{0,})\[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0,})\]($|.{0,})"))  
			for pattern in patterns:
				if pattern.match(self.line):
					time_string = re.sub(".{0,}(?P<time>\[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0,})\]).{0,}", "\g<time>", self.line)
					year = int(time_string[1:5])
					month = int(time_string[6:8])
					day = int(time_string[9:11])
					try:
						hour = int(time_string[16:18])
						minute = int(time_string[19:21])
					except ValueError:
						self.timestamp_time_included = False
						hour = 0
						minute = 0
					self.timestamp = datetime.datetime(year, month, day, hour, minute)
		return self.timestamp
	
class Header(HeaderTags, HeaderPriority, HeaderType, HeaderTimestamp):
	line = None
	title = None
	level = None
	
	def __init__(self, line):
		self.line = line.strip()
		self.level = 0
		for char in self.line:
			if char == "*":
				self.level += 1
			else:
				break

	def get_level(self):
		return self.level

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
				result = re.sub(".{1,} \[[0-9][0-9].{1,}\]", "", result)
			self.title = re.sub("^\*{1,}", "", result).strip()
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
