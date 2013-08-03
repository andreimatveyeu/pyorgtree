#!/usr/bin/python
import re
import cPickle

class OrgTree(object):
    parent = None
    children = []
    level = 0
    tree_type = None
    data = ""
    tree_dict = dict()
    header = ""

    def pickle_load(self, filename):
        try:
            inp = open(filename, 'rb')
            self = cPickle.load(inp)
            inp.close()
            return True
        except IOError:
            return False
        
    def pickle_dump(self, filename):
        try:
            out = open(filename, 'wb')
            cPickle.dump(self, out)
            out.close()
            return True
        except IOError:
            return False
        
    def get_parent(self):
        return self.parent
    def set_parent(self, parent):
        self.parent = parent
    def get_header(self):
        return self.header
    def set_header(self, line):
        self.header = line
        
    def get_subtree_by_hash(self, subtree_hash):
        try:
            return self.tree_dict[subtree_hash]
        except KeyError:
            return None

    def get_children(self):
        return self.children
        
    def get_tree_dict(self):
        return self.tree_dict
        
    def get_data(self):
        return self.data
        
    def _extract_tree_level(self, line):
        level = 0
        for char in line:
            if char == "*":
                level += 1
        return level

    def _has_priority(self, line):
        return re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] ").match(line) != None
        
    def _has_hash(self, line):
        prio_hash_pattern = re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] [a-z0-9]{5}:")
        noprio_hash_pattern = re.compile("\*{1,} [A-Z]{3,5} [a-z0-9]{5}:")
        notype_hash_pattern = re.compile("\*{1,} :")
        if prio_hash_pattern.match(line) or noprio_hash_pattern.match(line) or notype_hash_pattern:
            return True
        return False

    def get_title(self):
        return self._extract_title(self.get_header()[2:].strip())
        
    def _extract_title(self, line):
        priority = self._has_priority(line)
        tree_hash = self._has_hash(line)
        result = ""
        if priority:
            result = re.sub("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] ", "", line)
        else:
            result = re.sub("\*{1,} [A-Z]{3,5} ", "", line)
        if tree_hash:
            result = result[7:]
        return result

    def get_hash(self):
        if self._has_hash(self.get_header()):
            return self._extract_tree_hash(self.get_header())
        else:
            return None
          
    def _extract_tree_hash(self, line):
        priority_pattern = re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] ")
        no_priority_pattern = re.compile("\*{1,} [A-Z]{3,5} ")
        no_type_pattern = re.compile("\*{1,} ")
        result = ""
        if priority_pattern.match(line):
            result = re.sub("\*{1,10} [A-Z]{3,5} \[\#[A-Z]\] ", "", line)[0:5]
        elif no_priority_pattern.match(line):
            result = re.sub("\*{1,10} [A-Z]{3,5} ", "", line)[0:5]
        elif no_type_pattern.match(line):
            result = re.sub("\*{1,} ", "", line)[0:5]
        return result
        
    def read_from_file(self, filename, line_number, level, tree_dict=None):
        if tree_dict:
            self.tree_dict = tree_dict
        type_patterns = {
            'TODO' : '\*{1,} TODO ',
            'DONE' : '\*{1,} DONE ',
        }
        self.level = level
        if self.level == 0:
            self.parent = None
        data = open(filename, 'r').readlines()
        tree_start_pattern = re.compile("^\*{1,}")
        i = line_number
        while i < len(data):
            line = data[i]
            if tree_start_pattern.match(line):
                new_level = self._extract_tree_level(line)
                if new_level > self.level:
                    new_child = OrgTree()
                    new_child.set_parent(self)
                    new_child.set_header(line)
                    current_tree_hash = self._extract_tree_hash(line)
                    if current_tree_hash:
                        self.tree_dict[current_tree_hash] = new_child
                    self.children.append(new_child)
                    continue_from  = new_child.read_from_file(filename, i+1, new_level, tree_dict=self.tree_dict)
                    if not continue_from:
                        break
                    i = continue_from
                else:
                    return i
            else:
               self.data += line 
               i += 1
    def __str__(self):
        return "OrgTree(level=%d)" % self.level
        
    def __init__(self):
        self.children = []


