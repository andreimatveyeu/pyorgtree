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
