"""Org-mode timestamp parser module

.. moduleauthor:: Andrei Matveyeu <andrei@ideabulbs.com>

"""
import re 
import datetime
import sys

class MalformedTimestamp(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)
		
class Timestamp(object):
	string = None
	active = None

	def __init__(self, string):
		if not Timestamp.is_valid(string):
			raise MalformedTimestamp("Malformed timestamp: %s" % string)
		self.string = string
		
	@staticmethod
	def is_valid(string):
		"""Check if the given string is a valid timestamp.
		
		:returns:  bool -- validation result
		"""
		pattern = re.compile("^[\[\<].{1,}[\]\>]$")
		if not pattern.match(string):
			return False
		pattern = re.compile("^[\[\<][0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9].*[\]\>]$")
		if not pattern.match(string):
			return False
		return True
		
	def is_active(self):
		"""Check if the timestamp is active.
		
		:returns:  bool -- active status
		"""
		if self.active == None:
			self.active = False
			active_pattern = re.compile("^<.{1,}>$")
			if active_pattern.match(self.string):
				self.active = True
		return self.active
		
	def set_active(self, active):
		if not isinstance(active, bool):
			return False
		self.active = active
		if active:
			self.string = "<" + self.string[1:-1] + ">"
		else:
			self.string = "[" + self.string[1:-1] + "]"
		return True	
		
	def __str__(self):
		"""Get the timestamp as string.
		
		:returns:  str -- timestamp string
		"""
		return self.string
		
	def has_weekday(self):
		"""Check if the timestamp has a weekday.
		
		:returns:  bool -- is weekday present?
		"""
		pattern = re.compile(".{1,}[0-9] [A-Z][a-z][a-z]")
		return pattern.match(self.string) != None
		
class DateStamp(Timestamp):
	date = None
	def __init__(self, string):
		self.string = string
		if not DateStamp.is_valid(string):
			raise MalformedTimestamp("Malformed datestamp: %s" % string)
			
	@staticmethod
	def is_valid(string):
		if not Timestamp.is_valid(string):
			return False
		pattern = re.compile("^.....-..-..( [A-Z][a-z]{2}|.{0}).$")
		if not pattern.match(string):
			return False
		return True
		
	def set_date(self, new_date):
		if not isinstance(new_date, datetime.date):
			return False
		pattern = "%Y-%m-%d"
		if self.has_weekday():
			pattern += " %a"
		self.string = self.string[0] + new_date.strftime(pattern) + self.string[-1]
		self.date = new_date
		return True
		
	def get_date(self):
		if self.date == None:
			year = int(self.string[1:5])
			month = int(self.string[6:8])
			day = int(self.string[9:11])
			self.date = datetime.date(year, month, day)
		return self.date
	def __sub__(self, other):
		return self.get_date() - other.get_date()
		
class DatetimeStampDuration(object):
	duration_present = None
	
	def has_duration(self):
		if self.duration_present == None:
			self.duration_present = False
			duration_pattern = re.compile(".{1,} [0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9].{1,}")
			if duration_pattern.match(self.string):
				self.duration_present = True
		return self.duration_present
		
	def get_start_datetime(self):
		return self.get_datetime()

	def get_end_datetime(self):
		if self.has_duration():
			date = self.get_date()
			time_string = re.sub(".{1,}-(?P<time>[0-2][0-9]:[0-5][0-9])", "\g<time>", self.string)
			hour = int(time_string[0:2])
			minute = int(time_string[3:5])
			return datetime.datetime(date.year, date.month, date.day, hour, minute)
		return None
		
	def get_duration(self):
		"""Get the timestamp duration.
		
		:returns: datetime.timedelta -- timestamp duration
		"""
		if self.has_duration():
			return self.get_end_datetime() - self.get_start_datetime()
		else:
			return None
				
class DatetimeStamp(DatetimeStampDuration, DateStamp, Timestamp):
	def __init__(self, string):
		self.string = string
		if not DatetimeStamp.is_valid(string):
			raise MalformedTimestamp("Malformed datetime stamp: %s" % string)

	def get_datetime(self):
		date = self.get_date()
		time_string = re.sub(".{1,} (?P<time>[0-2][0-9]:[0-5][0-9])", "\g<time>", self.string)
		hour = int(time_string[0:2])
		minute = int(time_string[3:5])
		return datetime.datetime(date.year, date.month, date.day, hour, minute)
		
	@staticmethod
	def is_valid(string):
		if not Timestamp.is_valid(string):
			return False
		pattern = re.compile(".{5}-.{2}-.{2}( [A-Z][a-z]{2}|.{0}) [0-2][0-9]:[0-5][0-9](.$|-[0-2][0-9]:[0-5][0-9].$)")
		if not pattern.match(string):
			return False
		return True
		
	def __sub__(self, other):
		return self.get_datetime() - other.get_datetime()

class MalformedRange(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class Range(object):
	string = None
	from_timestamp = None
	to_timestamp = None
	def __init__(self, string):
		self.string = string
		
	def get_to(self):
		return self.to_timestamp
		
	def set_to(self, to):
		if not isinstance(to, Timestamp):
			return False
		self.to_timestamp = to
		return True
		
	def get_from(self):
		return self.from_timestamp
		
	def set_from(self, fr):
		if not isinstance(fr, Timestamp):
			return False
		self.from_timestamp = fr
		return True
		
	@staticmethod
	def is_valid(string):
		pattern = re.compile("^.{1,}--.{1,}$")
		if not pattern.match(string):
			return False
		return True
		
	def get_duration(self):
		return self.get_to() - self.get_from()

	def __str__(self):
		return "%s--%s" % (self.get_from(), self.get_to())

	def is_active(self):
		return self.get_from().is_active() and self.get_to().is_active()
		
class DateRange(Range):
	def __init__(self, string):
		if not DateRange.is_valid(string):
			raise MalformedRange("Malformed date range:")
		Range.__init__(self, string)
		stamps = string.split("--")
		self.from_timestamp = DateStamp(stamps[0])
		self.to_timestamp = DateStamp(stamps[1])
		
	@staticmethod
	def is_valid(string):
		if not Range.is_valid(string):
			raise MalformedRange("Malformed date range: %s" % string)
		stamps = string.split("--")
		if not len(stamps) == 2:
			return False
		for stamp in stamps:
			if not DateStamp.is_valid(stamp):
				return False		
		return True
		
class DatetimeRange(Range):
	def __init__(self, string):
		self.string = string
		if not DatetimeRange.is_valid(string):
			raise MalformedRange("Malformed datetime range: %s" % string)
		stamps = string.split("--")
		self.from_timestamp = DatetimeStamp(stamps[0])
		self.to_timestamp = DatetimeStamp(stamps[1])
		
	@staticmethod
	def is_valid(string):
		pattern = re.compile("^.{1,}--.{1,}$")
		if not pattern.match(string):
			return False
		stamps = string.split("--")
		if not len(stamps) == 2:
			return False
		for stamp in stamps:
			if not DatetimeStamp.is_valid(stamp):
				return False		
		return True
