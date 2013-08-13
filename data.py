import re
from schedule import *
from drawer import *

class OrgTreeData(object):
	data = None
	properties_dict = None
	schedule = None
	deadline = None
	drawers = []
	def __init__(self, data):
		self.data = data
		properties_start = re.compile(".{0,}:PROPERTIES:")
		properties_end = re.compile(".{0,}:END:")
		drawer_end = re.compile(".{0,}:END:")
		lines = self.data.split('\n')
		property_match = re.compile(".{0,}:[a-zA-Z0-9]{1,100}:")
		drawer_match = re.compile(".{0,}:[A-Z0-9]{1,100}:")
		schedule_match = re.compile(".{0,}SCHEDULED: .{1,}$")
		deadline_match = re.compile(".{0,}DEADLINE: .{1,}$")
		self.properties_dict = dict()
		properties_open = False
		drawer_open = False
		for line in lines:
			if not properties_open and properties_start.match(line):
				properties_open = True
				drawer_open = False
			elif properties_open and properties_end.match(line):
				properties_open = False
			elif drawer_open and drawer_end.match(line):
				drawer_open = False
			elif schedule_match.match(line):
				self.schedule = ScheduleAbstractFactory.get_schedule(line)
			elif deadline_match.match(line):
				self.deadline = DeadlineAbstractFactory.get_deadline(line)
			elif not properties_open and drawer_match.match(line):
				properties_open = False
				drawer_name = re.sub('.*:(?P<name>[A-Z0-9]{1,}):*$', '\g<name>', line)
				self.drawers.append(Drawer(drawer_name))
				drawer_open = True
			else:
				if properties_open:
					if property_match.match(line):
						prop = re.sub(".{0,}:(?P<prop>[a-zA-Z0-9]{1,100}):.{0,}$", "\g<prop>", line)
						value = re.sub(".*:(?P<val>.{1,})$", "\g<val>", line).strip()
						self.properties_dict[prop] = value
				elif drawer_open:
					drawer_data = self.drawers[-1].get_data()
					self.drawers[-1].set_data(drawer_data + line)

	def get_drawers(self):
		return self.drawers
		
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
