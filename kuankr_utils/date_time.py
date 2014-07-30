# coding: utf8
from __future__ import absolute_import, unicode_literals

import six
from datetime import datetime, timedelta, time, date, tzinfo
import calendar

import pytz
import tzlocal

from aniso8601 import parse_date, parse_time, parse_datetime, parse_interval, parse_duration, parse_repeating_interval

"""
tzinfo是关于时区信息的类
tzinfo是一个抽象类，所以不能直接被实例化
"""
class UTC(tzinfo):
    """UTC"""
    def __init__(self,offset = 0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)

def localzone():
    return tzlocal.get_localzone() 

def utcnow():
    return datetime.utcnow().replace(tzinfo=pytz.utc)

def now():
    local_tz = localzone()
    # utc -> local
    return utcnow().astimezone(local_tz)

def localize(dt):
    #dt should be utc
    local_tz = localzone()
    if dt.tzinfo is None:
        dt = local_tz.localize(dt)
    elif dt.tzinfo != local_tz:
        dt = dt.astimezone(local_tz)
    return dt

def with_tzinfo(dt):
    if dt.tzinfo is None:
        dt = localzone().localize(dt)
    return dt

def to_str(dt):
    if not dt:
        return None
    elif isinstance(dt, six.string_types):
        return dt
    dt = localize(dt)
    return dt.isoformat()

def to_date_str(dt):
    n = len('2012-01-01')
    return to_str(dt)[:n]

def to_datetime(dt):
    if isinstance(dt, six.string_types):
        return parse_datetime(dt)
    elif isinstance(dt, datetime):
        return dt
    else:
        return None

def to_interval(dt):
    if isinstance(dt, six.string_types):
        return parse_interval(dt)
    else:
        return None


