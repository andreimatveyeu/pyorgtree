#!/usr/bin/python
import re
import cPickle

class Header(object):
    line = None
    def __init__(self, line):
        self.line = line.strip()
        
    def get_level(self):
        level = 0
        for char in self.line:
            if char == "*":
                level += 1
            else:
                break
        return level

    def has_priority(self):
        patterns = []
        patterns.append(re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] "))
        patterns.append(re.compile("\*{1,} \[\#[A-Z]\] "))
        for pattern in patterns:
            if pattern.match(self.line):
                return True
        return False

    def has_type(self):
        patterns = []
        patterns.append(re.compile("\*{1,} [A-Z]{3,5}"))  # Level, keyword, priority and hash
        for pattern in patterns:
            if pattern.match(self.line):
                return True
        return False
        
    def has_hash(self):
        patterns = []
        patterns.append(re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] [a-z0-9]{5}:"))  # Level, keyword, priority and hash
        patterns.append(re.compile("\*{1,} [A-Z]{3,5} [a-z0-9]{5}:"))  # Level, keyword, and hash
        patterns.append(re.compile("\*{1,} [a-z0-9]{5}:")) # Level, hash
        for pattern in patterns:
            if pattern.match(self.line):
                return True
        return False

    def get_title(self):
        if self.has_hash():
            return re.sub('^.{1,}[a-z0-9]{5}: ', '', self.line)
        elif self.has_priority():
            return re.sub('^.{1,}\[#[A-Z]\] ', '', self.line)
        elif self.has_type():
            return re.sub('^\*{1,} [A-Z]{3,5} ', '', self.line)
        else:
            return re.sub('^\*{1,} ', '', self.line)

    def get_hash(self):
        patterns = []
        patterns.append(re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] "))  # Level, keyword, priority and hash
        patterns.append(re.compile("\*{1,} [A-Z]{3,5} "))  # Level, keyword, and hash
        patterns.append(re.compile("\*{1,} ")) # Level, hash
        if self.has_hash():
            for pattern in patterns:
                if pattern.match(self.line):
                    return pattern.sub('', self.line)[0:5]
        else:
            return None
        
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
    def set_header(self, header):
        self.header = header
        
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
                                  
    def read_from_file(self, filename, line_number, level, tree_dict=None):
        if tree_dict:
            self.tree_dict = tree_dict
        self.level = level
        if self.level == 0:
            self.parent = None
        data = open(filename, 'r').readlines()
        tree_start_pattern = re.compile("^\*{1,}")
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
                    current_tree_hash = header.get_hash()
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


