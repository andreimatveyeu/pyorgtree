class Tree(object):
	parent = None
	children = []
	def __init__(self):
		self.children = []
	def get_parent(self):
		return self.parent
	def set_parent(self, parent):
		self.parent = parent
	def get_children(self):
		return self.children
	def __getitem__(self, item_index):
		return self.children[item_index]
