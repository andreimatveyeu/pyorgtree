from tree import *

class TestTree(object):
	def test_tree_iteration(self):
		tree = Node()
		subtree1 = Node()
		subtree2 = Node()
		subsubtree1 = Node()
		subsubtree2 = Node()
		subsubtree3 = Node()
		subsubsubtree1 = Node()
		subsubtree1.add_child(subsubsubtree1)
		subtree1.add_child(subsubtree1)
		subtree1.add_child(subsubtree2)
		subtree2.add_child(subsubtree3)
		tree.add_child(subtree1)
		tree.add_child(subtree2)
		counter = 0
		for item in tree:
			if counter == 0:
				assert item == tree
			counter += 1
		print counter
		assert counter == 7
			
