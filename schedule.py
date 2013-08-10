import re
import datetime
import os
import cPickle

class ScheduleBase(object):
	schedule_line = None
	keyword = ""
	def __init__(self, schedule_line):
		self.schedule_line = schedule_line		
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

class ScheduleRepeater(object):
	repeater = -1
	repeat_interval = None
	def has_repeater(self):
		if self.repeater == -1:
			self.get_repeater()
		return self.repeater != None
		
	def get_repeater(self):
		if self.repeater == -1:
			self.repeater = None
			schedule_repeater_pattern = re.compile(".{1,} [\+]{1,2}[0-9]{1,4}[dwmy]")
			if schedule_repeater_pattern.match(self.schedule_line):
				self.repeater = self._extract_repeater(self.schedule_line)
		return self.repeater
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

class ScheduleDelay(object):
	delay = -1
	def has_delay(self):
		if self.delay == -1:
			self.get_delay()
		return self.delay != None
		
	def get_delay(self):
		if self.delay == -1:
			schedule_delay_pattern = re.compile(".{1,} [\-]{1,2}[0-9]{1,4}[dwmy]")
			self.delay = None
			if schedule_delay_pattern.match(self.schedule_line):
				self.delay = self._extract_delay(self.schedule_line)
		return self.delay
		
	def get_delay_interval(self):
		if self.has_delay():
			interval = re.sub("[-]{1,2}(?P<num>[0-9]{1,4}).{1,}", "\g<num>", self.delay)
			interval = int(interval)
			unit = re.sub(".{1,}(?P<unit>[dwmy])", "\g<unit>", self.delay)
		return (interval, unit)
	
class Schedule(ScheduleBase, ScheduleRepeater, ScheduleDelay):
	datetime = -1
	keyword = "SCHEDULED"
	date_only = None
	
	def __init__(self, schedule_line):
		super(Schedule, self).__init__(schedule_line)

	def has_date_only(self):
		if self.datetime == -1:
			self.get_datetime()
		return self.date_only
		
	def get_datetime(self):
		if self.datetime == -1:
			self.datetime = None
			schedule_datetime_pattern = re.compile(".{0,}%s: <[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [a-zA-Z]{3} [0-2][0-9]:[0-5][0-9].{0,}$" % self.keyword)
			schedule_date_pattern = re.compile(".{0,}%s: <[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [a-zA-Z]{3}.{0,}$" % self.keyword)
			if schedule_datetime_pattern.match(self.schedule_line):
				self.datetime = self._extract_datetime(self.schedule_line)
				self.date_only = False
			elif schedule_date_pattern.match(self.schedule_line):
				self.datetime = self._extract_date(self.schedule_line)
				self.date_only = True
		return self.datetime

class Deadline(Schedule):
	keyword = "DEADLINE"
