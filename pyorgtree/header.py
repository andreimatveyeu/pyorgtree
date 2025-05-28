import re
import datetime
import os
import pickle
from .tree import *

class HeaderTags(object):
    tags = None
    def has_tags(self):
        if self.tags == None:
            self.get_tags()
        return len(self.tags) > 0
        
    def get_tags(self):
        if self.tags == None:
            if re.compile(r".{0,}( {1,5}|\t):[a-zA-Z0-9:]*:$").match(self.line):
                tag_string = re.sub(r".{0,}( |\t)(?P<tags>:[a-zA-Z0-9:]*):$", r"\g<tags>", self.line)
                self.tags = tag_string[1:].split(":")
            else:
                self.tags = []
        return self.tags
        
    def add_tag(self, tag):
        if self.tags == None:
            self.get_tags()
        pattern = re.compile(r"^[a-z0-9]{1,}$")
        if not pattern.match(tag):
            return False
        if tag not in self.tags:
            self.tags.append(tag)
            return True
        return False
        
    def remove_tag(self, tag):
        if self.tags == None:
            self.get_tags()
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        else:
            return False
        
    def remove_all_tags(self):
        self.tags = []
        
    def get_tag_string(self):
        if not self.tags:
            return ""
        result = ":"
        for tag in self.tags:
            result += tag + ":"
        return result
        
class HeaderPriority(object):
    priority = "NA"
    
    def has_priority(self):
        if self.priority == "NA":
            self.get_priority()
        return self.priority != None

    def get_priority(self):
        if self.priority == "NA":
            patterns = []
            priority_pattern = r" \[#[A-Z]\].{0,}"
            keyword_pattern = " [A-Z]{3,5}"
            timestamp_pattern = r" \[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0})\]"
            patterns.append(re.compile(r"\*{1,}%s" % (priority_pattern)))
            patterns.append(re.compile(r"\*{1,}%s%s" % (keyword_pattern, priority_pattern)))
            patterns.append(re.compile(r"\*{1,}%s%s%s" % (keyword_pattern, priority_pattern, timestamp_pattern)))  
            patterns.append(re.compile(r"\*{1,}%s%s%s" % (keyword_pattern, timestamp_pattern, priority_pattern)))  
            self.priority = None
            for pattern in patterns:
                if pattern.match(self.line):
                    prio = re.sub(r".{1,} (?P<prio>\[#[A-Z]\]).{0,}", r"\g<prio>", self.line)
                    self.priority = prio[2:3]
                    break
        return self.priority
        
    def set_priority(self, priority):
        pattern = re.compile(r"^[A-Z]$")
        if not (priority == None or pattern.match(priority)):
            return False
        self.priority = priority
        return True
        
    def get_priority_string(self):
        if self.priority == "NA":
            self.get_priority()
        if self.priority:
            return "[#%s]" % self.priority
        else:
            return ""
            
class HeaderType(object):
    header_type = "NA"
    
    def has_type(self):
        if self.header_type == "NA":
                self.get_type()
        return self.header_type

    def get_type(self):
        if self.header_type == "NA":
            self.header_type = None
            patterns = []
            patterns.append(re.compile(r"\*{1,} [A-Z]{3,5} ")) 
            for pattern in patterns:
                if pattern.match(self.line):
                    self.header_type = re.sub(r"\*{1,} (?P<type>[A-Z]{3,5}) .{0,}", r"\g<type>", self.line)
        return self.header_type

    def set_type(self, new_type):
        pattern = re.compile(r"^[A-Z]{3,5}$")
        if not (new_type == None or pattern.match(new_type)):
            return False
        self.header_type = new_type
        return True
    def get_type_string(self):
        if self.header_type == "NA":
            self.get_type()
        if self.header_type:
            return self.header_type
        else:
            return ""

class HeaderTimestamp(object):
    timestamp = -1
    timestamp_time_included = True
    def has_timestamp(self):
        if self.timestamp == -1:
            self.get_timestamp()
        return self.timestamp != None
        
    def has_dateonly(self):
        if self.timestamp == -1:
            self.get_timestamp()
        if self.timestamp:
            return not self.timestamp_time_included
        else:
            return None
        
    def get_timestamp_string(self):
        if self.timestamp == -1:
            self.get_timestamp()
        if self.timestamp == None:
            return ""
        elif self.timestamp_time_included:
            return self.timestamp.strftime("[%Y-%m-%d %a %H:%M]")	
        else:
            return self.timestamp.strftime("[%Y-%m-%d %a]")	
            
    def get_timestamp(self):
        if self.timestamp == -1:
            self.timestamp = None
            patterns = []
            keyword_pattern = " ([A-Z]{3,5}|.{0})"
            timestamp_pattern = r"\[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0})\]"
            priority_pattern = r" (\[#[A-Z]\]|.{0})"
            patterns.append(re.compile(r"\*{1,}%s%s" % (keyword_pattern, timestamp_pattern)))
            patterns.append(re.compile(r"\*{1,}%s%s%s($|.{0,})" % (keyword_pattern, priority_pattern, timestamp_pattern)))  
            patterns.append(re.compile(r"\*{1,}%s%s%s($|.{0,})" % (keyword_pattern, timestamp_pattern, priority_pattern)))  
            for pattern in patterns:
                if pattern.match(self.line):
                    time_string = re.sub(r".{0,}(?P<time>\[[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] .{3}( [0-2][0-9]:[0-5][0-9]|.{0,})\]).{0,}", r"\g<time>", self.line)
                    year = int(time_string[1:5])
                    month = int(time_string[6:8])
                    day = int(time_string[9:11])
                    try:
                        hour = int(time_string[16:18])
                        minute = int(time_string[19:21])
                    except ValueError:
                        self.timestamp_time_included = False
                        hour = 0
                        minute = 0
                    self.timestamp = datetime.datetime(year, month, day, hour, minute)
        return self.timestamp

    def set_timestamp(self, timestamp, dateonly=False):
        if not (timestamp == None or isinstance(timestamp, datetime.datetime)):
            return False
        self.timestamp = timestamp
        if not dateonly or timestamp == None:
            self.timestamp_time_included = True
        return True
        
class Header(HeaderTags, HeaderPriority, HeaderType, HeaderTimestamp):
    line = None
    title = None
    level = None
    
    def __init__(self, line):
        self.line = line.strip()
        self.level = 0
        for char in self.line:
            if char == "*":
                self.level += 1
            else:
                break

    def get_level(self):
        return self.level

    def set_level(self, level):
        if level < 1:
            return False
        self.level = level
        return True
        
    def get_title(self):
        if self.title == None:
            result = self.line
            if self.has_tags():
                tag_string = re.sub(r".{0,}( |\t)(?P<tags>:[a-zA-Z0-9:]*:)$", r"\g<tags>", result)
                result = re.sub(tag_string, "", result)
            if self.has_priority():
                priority = self.get_priority()
                result = re.sub(r'\[#%s\]' % priority , '', result)
            if self.has_type():
                tree_type = self.get_type()
                result = re.sub(tree_type, '', result)
            if self.has_timestamp():
                result = re.sub(r".{1,} \[[0-9][0-9].{1,}\]", "", result)
            self.title = re.sub(r"^\*{1,}", "", result).strip()
        return self.title
        
    def set_title(self, title):
        if title == None or not isinstance(title, str) or not title.strip():
            return False
        self.title = title
        return True
        
    def get_string(self):
        if self.title == None:
            self.get_title()
        result = ""
        for _ in range(self.level):
            result += "*"
        if self.has_type():
            result += " %s" % self.get_type_string()
        if self.has_timestamp():
            result += " %s" % self.get_timestamp_string()
        if self.has_priority():
            result += " %s" % self.get_priority_string()
        result += " %s" % self.get_title()
        if self.has_tags():
            result += " %s" % self.get_tag_string()
        return result

    def __eq__(self, other):
        if not isinstance(other, Header):
            return NotImplemented
        # Ensure all attributes are resolved before comparison
        self.get_title()
        other.get_title()
        self.get_tags()
        other.get_tags()
        self.get_priority()
        other.get_priority()
        self.get_type()
        other.get_type()
        self.get_timestamp()
        other.get_timestamp()

        return (self.level == other.level and
                self.title == other.title and
                self.tags == other.tags and
                self.priority == other.priority and
                self.header_type == other.header_type and
                self.timestamp == other.timestamp and
                self.timestamp_time_included == other.timestamp_time_included)

class HashedHeader(Header):
    header_hash = "NA"
    def get_hash(self):
        if self.header_hash == "NA":
            self.header_hash = None
            title = super(HashedHeader, self).get_title()
            if re.compile(r"^[a-z0-9]{5}: ").match(title):
                self.header_hash = title[0:5]
        return self.header_hash
        
    def has_hash(self):
        if self.header_hash == "NA":
            self.get_hash()
        return self.header_hash != None

    def get_title(self):
        title = super(HashedHeader, self).get_title()
        if self.has_hash():
            tree_hash = self.get_hash()
            title = re.sub(tree_hash + ':', '', title).strip()
        return title

    def get_string(self):
        if self.title == None:
            self.get_title()
        result = ""
        for _ in range(self.level):
            result += "*"
        if self.has_type():
            result += " %s" % self.get_type_string()
        if self.has_timestamp():
            result += " %s" % self.get_timestamp_string()
        if self.has_priority():
            result += " %s" % self.get_priority_string()
        if self.has_hash():
            result += " %s:" % self.get_hash()
        result += " %s" % self.get_title()
        if self.has_tags():
            result += " %s" % self.get_tag_string()
        return result

    def __eq__(self, other):
        if not isinstance(other, HashedHeader):
            return NotImplemented
        # Call parent's __eq__ for common attributes
        if not super().__eq__(other):
            return False
        
        # Ensure hash is resolved
        self.get_hash()
        other.get_hash()
        
        return self.header_hash == other.header_hash
