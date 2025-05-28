"""Org-mode timestamp parser module

.. moduleauthor:: Andrei Matveyeu <andrei@ideabulbs.com>

"""
import re 
import datetime
import sys

class MalformedTimestamp(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        
class Timestamp(object):
    string = None
    active = None

    def __init__(self, string):
        if not Timestamp.is_valid(string):
            raise MalformedTimestamp("Malformed timestamp: %s" % string)
        self.string = string
        
    @staticmethod
    def is_valid(string):
        """Check if the given string is a valid timestamp.
        
        :returns:  bool -- validation result
        """
        pattern = re.compile("^[\[\<].{1,}[\]\>]$")
        if not pattern.match(string):
            return False
        pattern = re.compile("^[\[\<][0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9].*[\]\>]$")
        if not pattern.match(string):
            return False
        return True
        
    def is_active(self):
        """Check if the timestamp is active.
        
        :returns:  bool -- active status
        """
        if self.active == None:
            self.active = False
            active_pattern = re.compile("^<.{1,}>$")
            if active_pattern.match(self.string):
                self.active = True
        return self.active
        
    def set_active(self, active):
        if not isinstance(active, bool):
            return False
        self.active = active
        if active:
            self.string = "<" + self.string[1:-1] + ">"
        else:
            self.string = "[" + self.string[1:-1] + "]"
        return True	
        
    def __str__(self):
        """Get the timestamp as string.
        
        :returns:  str -- timestamp string
        """
        return self.string
        
    def has_weekday(self):
        """Check if the timestamp has a weekday.
        
        :returns:  bool -- is weekday present?
        """
        pattern = re.compile(".{1,}[0-9] [A-Z][a-z][a-z]")
        return pattern.match(self.string) != None

class TimestampRepeater(object):
    repeater = -1
    repeat_interval = None
    
    def _extract_repeater(self, line):
        repeater = re.sub(".{1,} (?P<repeater>[\+]{1,2}[0-9]{1,4}[dwmy]).{1,}", "\g<repeater>", line)
        return repeater
    
    def has_repeater(self):
        return self.get_repeater() != None
                
    def get_repeater(self):
        if self.repeater == -1:
            self.repeater = None
            schedule_repeater_pattern = re.compile(".{1,} [\+]{1,2}[0-9]{1,4}[dwmy]")
            if schedule_repeater_pattern.match(self.string):
                self.repeater = self._extract_repeater(self.string)
        return self.repeater
        
    def set_repeater(self, new_repeater):
        schedule_repeater_pattern = re.compile("^[\+]{1,2}[0-9]{1,4}[dwmy]$")
        if not schedule_repeater_pattern.match(new_repeater):
            return False
        self.repeater = new_repeater
        return True
        
    def has_overdue_repeater(self):
        if self.has_repeater():
            if re.compile("\+[0-9]").match(self.get_repeater()):
                return True
            else:
                return False
        else:
            return False
        
    def get_repeat_interval(self):
        if self.repeat_interval == None and self.has_repeater():
            repeater = self.get_repeater()
            interval = re.sub("\+{1,2}(?P<num>[0-9]{1,4}).{1,}", "\g<num>", repeater)
            interval = int(interval)
            unit = re.sub(".{1,}(?P<unit>[dwmy])", "\g<unit>", repeater)
            return (interval, unit)
        else:
            return None

class TimestampDelay(object):
    delay = -1
    
    def _extract_delay(self, line):
        delay = re.sub(".{1,} (?P<repeater>[\-]{1,2}[0-9]{1,4}[dwmy]).{1,}", "\g<repeater>", line)
        return delay
        
    def has_delay(self):
        if self.delay == -1:
            self.get_delay()
        return self.delay != None
        
    def get_delay(self):
        if self.delay == -1:
            schedule_delay_pattern = re.compile(".{1,} [\-]{1,2}[0-9]{1,4}[dwmy]")
            self.delay = None
            if schedule_delay_pattern.match(self.string):
                self.delay = self._extract_delay(self.string)
        return self.delay
        
    def set_delay(self, new_delay):
        schedule_delay_pattern = re.compile("^[\-]{1,2}[0-9]{1,4}[dwmy]$")
        if not schedule_delay_pattern.match(new_delay):
            return False
        self.delay = new_delay
        return True
        
    def get_delay_interval(self):
        if self.has_delay():
            interval = re.sub("[-]{1,2}(?P<num>[0-9]{1,4}).{1,}", "\g<num>", self.delay)
            interval = int(interval)
            unit = re.sub(".{1,}(?P<unit>[dwmy])", "\g<unit>", self.delay)
        return (interval, unit)

class DateStamp(Timestamp, TimestampRepeater, TimestampDelay):
    date = None
    def __init__(self, string):
        self.string = string
        if not DateStamp.is_valid(string):
            raise MalformedTimestamp("Malformed datestamp: %s" % string)
            
    @staticmethod
    def is_valid(string):
        if not Timestamp.is_valid(string):
            return False
        pattern = re.compile("^.....-..-..( [A-Z][a-z]{2}|.{0})")
        if not pattern.match(string):
            return False
        return True
        
    def set_date(self, new_date):
        if not isinstance(new_date, datetime.date):
            return False
        pattern = "%Y-%m-%d"
        if self.has_weekday():
            pattern += " %a"
        self.string = self.string[0] + new_date.strftime(pattern) + self.string[-1]
        self.date = new_date
        return True
        
    def get_date(self):
        if self.date == None:
            year = int(self.string[1:5])
            month = int(self.string[6:8])
            day = int(self.string[9:11])
            self.date = datetime.date(year, month, day)
        return self.date
    def __sub__(self, other):
        return self.get_date() - other.get_date()
        
    def __str__(self):
        pattern = "%Y-%m-%d"
        if self.has_weekday():
            pattern += " %a"
        result = self.get_date().strftime(pattern)
        if self.has_delay():
            result += " %s" % self.get_delay()
        if self.has_repeater():
            result += " %s" % self.get_repeater()
        if self.is_active():
            result = "<" + result + ">"
        else:
            result = "[" + result + "]"
        return result
        
class DatetimeStampDuration(object):
    duration_present = None
    
    def has_duration(self):
        if self.duration_present == None:
            self.duration_present = False
            duration_pattern = re.compile(".{1,} [0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9].{1,}")
            if duration_pattern.match(self.string):
                self.duration_present = True
        return self.duration_present
        
    def get_start_datetime(self):
        return self.get_datetime()

    def get_end_datetime(self):
        if self.has_duration():
            date = self.get_date()
            time_string = re.sub(".{1,}-(?P<time>[0-2][0-9]:[0-5][0-9])", "\g<time>", self.string)
            hour = int(time_string[0:2])
            minute = int(time_string[3:5])
            return datetime.datetime(date.year, date.month, date.day, hour, minute)
        return None
        
    def get_duration(self):
        """Get the timestamp duration.
        
        :returns: datetime.timedelta -- timestamp duration
        """
        if self.has_duration():
            return self.get_end_datetime() - self.get_start_datetime()
        else:
            return None
                
class DatetimeStamp(DatetimeStampDuration, DateStamp, Timestamp):
    datetime = -1
    def __init__(self, string):
        self.string = string
        if not DatetimeStamp.is_valid(string):
            raise MalformedTimestamp("Malformed datetime stamp: %s" % string)

    def get_datetime(self):
        if self.datetime == -1:
            date = self.get_date()
            time_string = re.sub(".{1,} (?P<time>[0-2][0-9]:[0-5][0-9])", "\g<time>", self.string)
            hour = int(time_string[0:2])
            minute = int(time_string[3:5])
            self.datetime = datetime.datetime(date.year, date.month, date.day, hour, minute)
        return self.datetime
        
    def set_datetime(self, new_datetime):
        if not isinstance(new_datetime, datetime.datetime):
            return False
        self.datetime = new_datetime
        return True
        
    @staticmethod
    def is_valid(string):
        if not Timestamp.is_valid(string):
            return False
        pattern = re.compile(".{5}-.{2}-.{2}( [A-Z][a-z]{2}|.{0}) [0-2][0-9]:[0-5][0-9](.{0}|-[0-2][0-9]:[0-5][0-9])")
        if not pattern.match(string):
            return False
        return True
        
    def __str__(self):
        pattern = "%Y-%m-%d"
        if self.has_weekday():
            pattern += " %a"
        pattern += " %H:%M"
        result = self.get_datetime().strftime(pattern)
        if self.has_duration():
            end_time = self.get_end_datetime().strftime("-%H-%M")
            result += end_time
        if self.has_delay():
            result += " %s" % self.get_delay()
        if self.has_repeater():
            result += " %s" % self.get_repeater()
        if self.is_active():
            result = "<" + result + ">"
        else:
            result = "[" + result + "]"
        return result
            
    def __sub__(self, other):
        return self.get_datetime() - other.get_datetime()

class MalformedRange(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class Range(object):
    string = None
    from_timestamp = None
    to_timestamp = None
    
    @staticmethod
    def is_valid(string):
        pattern = re.compile("^.{1,}--.{1,}$")
        if not pattern.match(string):
            return False
        return True
        
    def __init__(self, string):
        self.string = string
        
    def get_to(self):
        return self.to_timestamp
        
    def set_to(self, to):
        if not isinstance(to, Timestamp):
            return False
        self.to_timestamp = to
        return True
        
    def get_from(self):
        return self.from_timestamp
        
    def set_from(self, fr):
        if not isinstance(fr, Timestamp):
            return False
        self.from_timestamp = fr
        return True
        
    def get_duration(self):
        return self.get_to() - self.get_from()

    def __str__(self):
        return "%s--%s" % (self.get_from(), self.get_to())

    def is_active(self):
        return self.get_from().is_active() and self.get_to().is_active()
        
class DateRange(Range):
    def __init__(self, string):
        if not DateRange.is_valid(string):
            raise MalformedRange("Malformed date range:")
        Range.__init__(self, string)
        stamps = string.split("--")
        self.from_timestamp = DateStamp(stamps[0])
        self.to_timestamp = DateStamp(stamps[1])
        
    @staticmethod
    def is_valid(string):
        if not Range.is_valid(string):
            return False
        stamps = string.split("--")
        if not len(stamps) == 2:
            return False
        for stamp in stamps:
            if not DateStamp.is_valid(stamp):
                return False
            ds = DateStamp(stamp)
            if ds.has_repeater() or ds.has_delay():
                return False		
        return True
        
class DatetimeRange(Range):
    def __init__(self, string):
        self.string = string
        if not DatetimeRange.is_valid(string):
            raise MalformedRange("Malformed datetime range: %s" % string)
        stamps = string.split("--")
        self.from_timestamp = DatetimeStamp(stamps[0])
        self.to_timestamp = DatetimeStamp(stamps[1])
        
    @staticmethod
    def is_valid(string):
        pattern = re.compile("^.{1,}--.{1,}$")
        if not pattern.match(string):
            return False
        stamps = string.split("--")
        if not len(stamps) == 2:
            return False
        for stamp in stamps:
            if not DatetimeStamp.is_valid(stamp):
                return False
            dts = DatetimeStamp(stamp)
            if dts.has_repeater() or dts.has_delay():
                return False		
        return True
