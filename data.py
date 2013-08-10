import re
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
	def set_schedule(self, schedule):
		if not (schedule == None or isinstance(schedule, Schedule)):
			return False
		self.schedule = schedule
		return True
		
	def has_deadline(self):
		return self.deadline != None
	def get_deadline(self):
		return self.deadline
	def set_deadline(self, deadline):
		if not (deadline == None or isinstance(deadline, Deadline)):
			return False
		self.deadline = deadline
		return True
