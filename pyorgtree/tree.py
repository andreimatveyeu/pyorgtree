class Node(object):
    parent = None
    children = []
    def __iter__(self):
        yield self
        for child in self.children:
            for item in child:
                yield item
    def add_child(self, new_child):
        self.children.append(new_child)
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
        if item_index == 0:
            return self
        elif item_index > 0 and item_index <= len(self.children):
            return self.children[item_index-1]
        else:
            raise IndexError("Node index out of range")
