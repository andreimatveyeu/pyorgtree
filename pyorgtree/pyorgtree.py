#!/usr/bin/python
import re
import datetime
import os
import pickle
from .tree import *
from .header import *
from .schedule import *
from .data import *


class OrgTreeReader(object):

    def read_from_file(self, filename, line_number, level, tag_dict=None):
        if tag_dict:
            self.tag_dict = tag_dict
        self.level = level
        if self.level == 0:
            self.parent = None
        data = open(filename, 'r').readlines()
        tree_start_pattern = re.compile("^\*{1,} ")
        i = line_number
        while i < len(data):
            line = data[i]
            if tree_start_pattern.match(line):
                header = Header(line)
                new_level = header.get_level()
                if new_level > self.level:
                    new_child = OrgTree()
                    new_child.set_parent(self)
                    new_child.set_header(header)
                    if header.has_tags():
                        for tag in header.get_tags():
                            if tag not in self.tag_dict:
                                self.tag_dict[tag] = []
                            self.tag_dict[tag].append(new_child)
                    self.add_child(new_child)
                    continue_from  = new_child.read_from_file(filename, i+1, new_level, tag_dict=self.tag_dict)
                    if not continue_from:
                        break
                    i = continue_from
                else:
                    return i
            else:
               self.raw_data += line
               i += 1

class OrgTreeWriter(object):
    def write_to_file(self, filename):
        out = open(filename, 'w')
        tree_sequence = []
        children = self.get_children()
        for item in self:
            if not item.get_header():
                continue
            tree_sequence.append(item)
        for item in tree_sequence:
            out.write(item.get_header().get_string())
            out.write(os.linesep)
            out.write(item.get_data())
        out.close()


class OrgTree(Node, OrgTreeReader, OrgTreeWriter):
    # level, tree_type, raw_data, data, tag_dict, header, properties
    # are now instance variables initialized in __init__.

    def __init__(self, *args, **kwargs):
        super(OrgTree, self).__init__(*args, **kwargs)  # Call Node's __init__ or object.__init__
        self.level = 0
        self.tree_type = None
        self.raw_data = ""
        self.data = None
        self.tag_dict = {}
        self.header = None
        self.properties = None
        # Node class is expected to initialize self.children and self.parent (if applicable)

    def get_header(self):
        return self.header

    def set_header(self, header):
        self.header = header

    def get_tag_dict(self):
        return self.tag_dict

    def get_trees_by_tag(self, tag):
        try:
            return self.tag_dict[tag]
        except KeyError:
            return []

    def get_data(self):
        if self.data == None:
            self.data = OrgTreeData(self.raw_data)
        return self.data.get_data()

    def has_schedule(self):
        if self.data == None:
            self.data = OrgTreeData(self.raw_data)
        return self.data.has_schedule()
    def get_schedule(self):
        if self.has_schedule():
            return self.data.get_schedule()

    def has_deadline(self):
        if self.data == None:
            self.data = OrgTreeData(self.raw_data)
        return self.data.has_deadline()

    def get_deadline(self):
        if self.data == None:
            self.data = OrgTreeData(self.raw_data)
        return self.data.get_deadline()

    def has_properties(self):
        if self.data == None:
            self.data = OrgTreeData(self.raw_data)
        if self.properties == None:
            self.properties = self.data.get_properties()
        return len(list(self.properties.keys())) > 0

    def get_properties(self):
        if self.data == None:
            self.data = OrgTreeData(self.raw_data)
        if self.properties == None:
            self.properties = self.data.get_properties()
        return self.properties

    def __str__(self):
        return "OrgTree(level=%d; title=%s)" % (self.level, self.header.get_title())


class PickleSerializableOrgTree():

    def pickle_load(self, filename):
        try:
            with open(filename, 'rb') as inp:
                loaded_obj = pickle.load(inp)
            # Update the current instance's dictionary with the loaded object's dictionary
            # This ensures all instance attributes, including tree_dict and tag_dict, are restored.
            self.__dict__.update(loaded_obj.__dict__)
            return True
        except (IOError, pickle.UnpicklingError) as e:
            # It's good practice to log the error or handle it more specifically if needed
            print(f"Error during pickle_load: {e}") # Or use a proper logger
            return False

    def pickle_dump(self, filename):
        try:
            out = open(filename, 'wb')
            pickle.dump(self, out)
            out.close()
            return True
        except IOError:
            return False


class PlainSerializableOrgTree():

    def to_string(self):
        return ""


class HashedOrgTreeReader(object):

    def read_from_file(self, filename, line_number, level, tree_dict=None, tag_dict=None):
        if tree_dict:
            self.tree_dict = tree_dict
        if tag_dict:
            self.tag_dict = tag_dict
        self.level = level
        if self.level == 0:
            self.parent = None
        data = open(filename, 'r').readlines()
        tree_start_pattern = re.compile("^\*{1,} ")
        i = line_number
        while i < len(data):
            line = data[i]
            if tree_start_pattern.match(line):
                header = HashedHeader(line)
                new_level = header.get_level()
                if new_level > self.level:
                    new_child = HashedOrgTree()
                    new_child.set_parent(self)
                    new_child.set_header(header)
                    current_tree_hash = header.get_hash()
                    if current_tree_hash:
                        self.tree_dict[current_tree_hash] = new_child
                    if header.has_tags():
                        for tag in header.get_tags():
                            if tag not in self.tag_dict:
                                self.tag_dict[tag] = []
                            self.tag_dict[tag].append(new_child)
                    self.add_child(new_child)
                    continue_from  = new_child.read_from_file(filename, i+1, new_level, tree_dict=self.tree_dict, tag_dict=self.tag_dict)
                    if not continue_from:
                        break
                    i = continue_from
                else:
                    return i
            else:
               self.raw_data += line
               i += 1


class HashedOrgTree(HashedOrgTreeReader, OrgTree, PickleSerializableOrgTree, PlainSerializableOrgTree):
    # tree_dict is now an instance variable initialized in __init__.
    # tag_dict is inherited from OrgTree and initialized as an instance variable via super().__init__().
    def __init__(self):
        super(HashedOrgTree, self).__init__()
        self.tree_dict = {}

    def get_subtree_by_hash(self, subtree_hash):
        try:
            return self.tree_dict[subtree_hash]
        except KeyError:
            return None

    def get_tree_dict(self):
        return self.tree_dict
