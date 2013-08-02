#!/usr/bin/python
import re

class OrgTree(object):
    parent = None
    children = []
    level = 0
    tree_type = None
    data = ""
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
        if prio_hash_pattern.match(line) or noprio_hash_pattern.match(line):
            return True
        return False

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
        
    def _extract_tree_hash(self, line):
        priority_pattern = re.compile("\*{1,} [A-Z]{3,5} \[\#[A-Z]\] ")
        no_priority_pattern = re.compile("\*{1,} [A-Z]{3,5} ")
        result = ""
        if priority_pattern.match(line):
            result = re.sub("\*{1,10} [A-Z]{3,5} \[\#[A-Z]\] ", "", line)[0:5]
        elif no_priority_pattern.match(line):
            result = re.sub("\*{1,10} [A-Z]{3,5} ", "", line)[0:5]
        return result
        
    def read_from_file(self, filename, line_number, level):
        type_patterns = {
            'TODO' : '\*{1,} TODO ',
            'DONE' : '\*{1,} DONE ',
        }
        self.level = level
        data = open(filename, 'r').readlines()
        print "Open file"
        tree_start_pattern = re.compile("^\*{1,}")
        for i in range(line_number, len(data)):
            line = data[i]
            if tree_start_pattern.match(line):
                new_level = self._extract_tree_level(line)
                print "Line match, level: ", new_level
                if new_level <= self.level:  # upper or same level: parent or sibling
                    break
                else:
                    new_child = OrgTree('')  # lower level: child
                    new_child.read_from_file(filename, i+1, new_level)
                    self.children.append(new_child)
                    break
                # tree_hash = self._extract_tree_hash(line)
                # print tree_hash
                # print self._has_hash(line)
                # print self._has_priority(line)
                # print self._extract_title(line)
                # for key in type_patterns.keys():
                #     if re.compile(type_patterns[key]).match(line):
                #         tree_type = key
                #         break
            else:
               self.data += line 

            #     tree_hash = self._extract_tree_hash(line)
            #     print tree_hash
            #     print self._has_hash(line)
            #     print self._has_priority(line)
            #     print self._extract_title(line)
            #     for key in type_patterns.keys():
            #         if re.compile(type_patterns[key]).match(line):
            #             tree_type = key
            #             break
            
    def __str__(self):
        return "OrgTree(level=%d)" % self.level
        
    def __init__(self, data):
        pass

