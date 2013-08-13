import os

class Drawer(object):
	data = None
	name = None
	
	def __init__(self, name):
		self.name = name
		
	def __str__(self):
		return ":%s:%s%s%s:END:" % (self.name, os.linesep, self.data, os.linesep)

	def get_name(self):
		return self.name

	def set_name(self, name):
		self.name = name
		
	def set_data(self, data):
		self.data = data
		
	def get_data(self):
		return self.data
