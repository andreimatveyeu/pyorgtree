from pyorgtree.timestamp import *
import datetime

class TestTimestamp(object):
    
    def test_active(self):
        t1 = DateStamp("[2013-08-11 Sun]")
        assert not t1.is_active()
        t1 = DateStamp("<2013-08-11 Sun>")
        assert t1.is_active()
        
class TestDateStamp(object):
    def test_set_date(self):
        ds = DateStamp("[2013-08-11 Sun]")
        assert ds.has_weekday()
        assert not ds.set_date("zzz")
        assert ds.set_date(datetime.date(2013, 8, 12))
        assert ds.get_date() == datetime.date(2013, 8, 12)
        assert ds.set_active(True)
        assert "%s" % ds == "<2013-08-12 Mon>"
        assert ds.has_weekday()

    def test_no_weekday(self):
        ds = DateStamp("<2013-08-11>")
        assert ds.get_date() == datetime.date(2013, 8, 11)
        assert ds.is_active()
        assert not ds.has_weekday()
        assert ds.set_date(datetime.date(2013, 8, 12))
        assert ds.get_date() == datetime.date(2013, 8, 12)
        assert ds.set_active(False)
        assert "%s" % ds == "[2013-08-12]"
        
class TestDatetimeStamp(object):
    def test_duration(self):
        stamps = [
            "<2013-08-11 Sun 12:15-20:45>",
            "<2013-08-11 12:15-20:45>"
        ]
        for stamp in stamps:
            dts = DatetimeStamp(stamp)
            assert dts.has_weekday() or not dts.has_weekday()
            assert dts.has_duration()
            assert dts.get_date() == datetime.date(2013, 8, 11)

    def test_duration_start_end(self):
        dts = DatetimeStamp("[2013-08-11 Sun 12:15-13:35]")
        assert dts.get_start_datetime() == datetime.datetime(2013, 8, 11, 12, 15)
        assert dts.get_end_datetime() == datetime.datetime(2013, 8, 11, 13, 35)
        assert dts.get_duration() == datetime.timedelta(minutes=80)

class TestDateRange(object):
    
    def test_init(self):
        string = "<2013-08-11 Sun>--<2013-08-12 Mon>"
        dr = DateRange(string)
        assert dr.is_active()
        string = "[2013-08-11 Sun]--[2013-08-12 Mon]"
        dr = DateRange(string)
        assert not dr.is_active()

    def test_get_duration(self):
        string = "<2013-08-11 Sun>--<2013-08-12 Mon>"
        dr = DateRange(string)
        assert dr.get_duration() == datetime.timedelta(days=1)

    def test_string(self):
        string = "<2013-08-11 Sun>--<2013-08-12 Mon>"
        dr = DateRange(string)
        assert "%s" % dr == string

    def test_set(self):
        string = "<2013-08-11 Sun>--<2013-08-12 Mon>"
        dr = DateRange(string)
        
        dr.set_from(DateStamp("<2013-08-10 Sat>"))
        assert "%s" % dr == "<2013-08-10 Sat>--<2013-08-12 Mon>"
        assert dr.get_duration() == datetime.timedelta(days=2)
        
        dr.set_to(DateStamp("<2013-08-13 Tue>"))
        assert "%s" % dr == "<2013-08-10 Sat>--<2013-08-13 Tue>"
        assert dr.get_duration() == datetime.timedelta(days=3)
        
class TestDatetimeRange(object):
    
    def test_init(self):
        string = "<2013-08-11 Sun 13:00>--<2013-08-12 Mon 15:00>"
        dtr = DatetimeRange(string)
        assert dtr.is_active()
        string = "[2013-08-11 Sun 13:00]--[2013-08-12 Mon 15:00]"
        dtr = DatetimeRange(string)
        assert not dtr.is_active()
        
    def test_get_duration(self):
        string = "<2013-08-11 Sun 13:00>--<2013-08-12 Mon 15:00>"
        dtr = DatetimeRange(string)
        assert dtr.get_duration() == datetime.timedelta(days=1, hours=2)

    def test_string(self):
        string = "<2013-08-11 Sun 13:00>--<2013-08-12 Mon 15:00>"
        dtr = DatetimeRange(string)
        assert "%s" % dtr == string

    def test_set(self):
        string = "<2013-08-11 Sun 13:00>--<2013-08-12 Mon 15:00>"
        dtr = DatetimeRange(string)
        
        dtr.set_from(DatetimeStamp("<2013-08-10 Sat 15:00>"))
        assert "%s" % dtr == "<2013-08-10 Sat 15:00>--<2013-08-12 Mon 15:00>"
        assert dtr.get_duration() == datetime.timedelta(days=2)
        
        dtr.set_to(DatetimeStamp("<2013-08-13 Tue 16:00>"))
        assert "%s" % dtr == "<2013-08-10 Sat 15:00>--<2013-08-13 Tue 16:00>"
        assert dtr.get_duration() == datetime.timedelta(days=3, hours=1)

class TestRepeater(object):
    def test_repeater(self):
        string = "<2013-08-11 Sun 13:00 +1d>"
        dts = DatetimeStamp(string)
        assert dts.has_repeater()
        
        string = "<2013-08-11 Sun 13:00 ++1d>"
        dts = DatetimeStamp(string)
        assert dts.has_repeater()
        
    def test_set_repeater(self):
        string = "<2013-08-11 Sun 13:00 +1d>"
        dts = DatetimeStamp(string)
        assert dts.set_repeater("+5m")
        assert dts.get_repeater() == "+5m"
        assert "%s" % dts == "<2013-08-11 Sun 13:00 +5m>"

class TestDelay(object):
    def test_delay(self):
        string = "<2013-08-11 Sun 13:00 -1d>"
        dts = DatetimeStamp(string)
        assert dts.has_delay()
    
        string = "<2013-08-11 Sun 13:00 --1d>"
        dts = DatetimeStamp(string)
        assert dts.has_delay()

    def test_set_repeater(self):
        string = "<2013-08-11 Sun 13:00 -1d>"
        dts = DatetimeStamp(string)
        assert dts.set_delay("-5m")
        assert dts.get_delay() == "-5m"
        assert "%s" % dts == "<2013-08-11 Sun 13:00 -5m>"
        
class TestDelayRepeater(object):
    def test_delay_repeater(self):
        string = "<2013-08-11 Sun -1d +5d>"
        ds = DateStamp(string)
        assert ds.has_delay()
        assert ds.get_delay() == "-1d"
        assert ds.has_repeater()
        assert ds.get_repeater() == "+5d"
        assert ds.get_date() == datetime.date(2013, 8, 11)
