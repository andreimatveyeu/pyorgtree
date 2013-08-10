class Timestamp(object):
	string = None
	active = None

	def __init__(self, string):
		self.string = string

	def is_active(self, string):
		if self.active == None:
			self.active = False
			active_pattern = re.compile("^<.{1,}>$")
			if active_pattern.match(self.string):
				self.active = True
		return self.active

class DateStamp(Timestamp):
	def __init__(self):
		pass

class DatetimeStamp(Timestamp):
	duration_present = None
	def __init__(self):
		pass
	def has_duration(self, string):
		if self.duration_present == None:
			self.duration_present = False
			duration_pattern = re.compile(".{1,} [0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9].{1,}")
			if duration_pattern.match(self.string):
				self.duration_present = True
		return self.duration_present
	
class DatetimeRange(object):
	from_datetime = None
	to_datetime = None
	def get_to(self):
		return self.to_datetime
	def get_from(self):
		return self.from_datetime
