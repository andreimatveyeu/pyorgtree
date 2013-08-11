import re
import datetime
import os
import cPickle
from timestamp import *

class Schedule(object):
	keyword = "SCHEDULED"
	def __str__(self):
		return "%s: %s" % (self.keyword, super(Schedule, self).__str__())

class ScheduleDatetime(Schedule, DatetimeStamp):
	pass

class ScheduleDate(Schedule, DateStamp):
	pass

class ScheduleDatetimeRange(Schedule, DatetimeRange):
	pass

class ScheduleDateRange(Schedule, DateRange):
	pass

class MalformedScheduleException(Exception):
	def __init__(self, message):
		self.message = message
		
class ScheduleAbstractFactory(object):
	@staticmethod
	def get_schedule(string):
		keyword = "SCHEDULED"
		string = string.strip()
		if not string.startswith("%s:" % keyword):
			raise MalformedScheduleException("Malformed schedule string")
		schedule = re.sub("^.*%s:" % keyword, "", string).strip()
		if DatetimeRange.is_valid(schedule):
			return ScheduleDatetimeRange(schedule)
		elif DateRange.is_valid(schedule):
			return ScheduleDateRange(schedule)
		elif DatetimeStamp.is_valid(schedule):
			return ScheduleDatetime(schedule)
		elif DateStamp.is_valid(schedule):
			return ScheduleDate(schedule)
		else:
			raise MalformedScheduleException("Malformed schedule string")

class Deadline(Schedule):
	keyword = "DEADLINE"

class DeadlineDatetime(Deadline, ScheduleDatetime):
	pass

class DeadlineDate(Deadline, ScheduleDate):
	pass

class DeadlineAbstractFactory(object):
	@staticmethod
	def get_deadline(string):
		keyword = "DEADLINE"
		string = string.strip()
		if not string.startswith("%s:" % keyword):
			raise MalformedScheduleException("Malformed deadline string")
		schedule = re.sub("^.*%s:" % keyword, "", string).strip()
		if DatetimeStamp.is_valid(schedule):
			return DeadlineDatetime(schedule)
		elif DateStamp.is_valid(schedule):
			return DeadlineDate(schedule)
		else:
			raise MalformedScheduleException("Malformed deadline string")
