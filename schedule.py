import re
import datetime
import os
import cPickle

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
