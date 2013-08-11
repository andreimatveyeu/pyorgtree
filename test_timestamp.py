from timestamp import *
import datetime

class TestTimestamp(object):
	def test_timestamp_active(self):
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
		assert ds.get_string() == "<2013-08-12 Mon>"
		assert ds.has_weekday()

	def test_no_weekday(self):
		ds = DateStamp("<2013-08-11>")
		assert ds.get_date() == datetime.date(2013, 8, 11)
		assert ds.is_active()
		assert not ds.has_weekday()
		assert ds.set_date(datetime.date(2013, 8, 12))
		assert ds.get_date() == datetime.date(2013, 8, 12)
		assert ds.set_active(False)
		assert ds.get_string() == "[2013-08-12]"
		
