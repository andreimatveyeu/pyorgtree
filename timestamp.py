import re 
import datetime

class MalformedTimestamp(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)
		
class Timestamp(object):
	string = None
	active = None

	def __init__(self, string):
		pattern = re.compile("^[\[\<].{1,}[\]\>]$")
		if not pattern.match(string):
			raise MalformedTimestamp("Malformed timestamp: %s" % string)
		self.string = string

	def is_active(self):
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
		
	def get_string(self):
		return self.string
		
	def has_weekday(self):
		pattern = re.compile(".{1,}[0-9] [A-Z][a-z][a-z]")
		return pattern.match(self.string)
		
class DateStamp(Timestamp):
	date = None
	def __init__(self, string):
		super(DateStamp, self).__init__(string)
		
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
		if self.has_duration():
			date = self.get_date()
			time_string = re.sub(".{1,} (?P<time>[0-2][0-9]:[0-5][0-9])-", "\g<time>", self.string)
			hour = int(time_string[0:2])
			minute = int(time_string[3:5])
			return datetime.datetime(date.year, date.month, date.day, hour, minute)
		else:
			return None

	def get_end_datetime(self):
		if self.has_duration():
			date = self.get_date()
			time_string = re.sub(".{1,}-(?P<time>[0-2][0-9]:[0-5][0-9])", "\g<time>", self.string)
			hour = int(time_string[0:2])
			minute = int(time_string[3:5])
			return datetime.datetime(date.year, date.month, date.day, hour, minute)
		return None
		
	def get_duration(self):
		if self.has_duration():
			return self.get_end_datetime() - self.get_start_datetime()
		else:
			return None
				
class DatetimeStamp(DateStamp, Timestamp, DatetimeStampDuration):
	pass
	
class DatetimeRange(object):
	from_datetime = None
	to_datetime = None
	def get_to(self):
		return self.to_datetime
	def get_from(self):
		return self.from_datetime

