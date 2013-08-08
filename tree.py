class TreeIterator(object):
	tree = None
	previous_node = None
	next_node = None
	def __init__(self, tree):
		self.tree = tree
	def has_previous(self):
		return previous_node != None
	def has_next(self):
		return next_node != None

class Node(object):
	parent = None
	children = []
	def has_children(self):
	    return len(self.children) > 0

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
