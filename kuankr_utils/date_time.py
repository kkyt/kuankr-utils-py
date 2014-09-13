# coding: utf8
from __future__ import absolute_import, unicode_literals

import os
import six
from datetime import datetime, timedelta, time, date, tzinfo
import calendar

import pytz
import tzlocal

from aniso8601 import parse_date, parse_time, parse_datetime, parse_interval, parse_duration, parse_repeating_interval

DATE_LEN = len('2012-01-01')
DATETIME_LEN = len('2012-01-01T00:00:00')

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
    #TODO
    #NOTE: 在docker或VM里运行时,如果镜像没设好local zone,就会出错, 所以直接写死成 UTC8(Asia/Shanghai)
    if not os.environ.get('TZ'):
        #return UTC(8) #don't support localize
        return pytz.timezone('Asia/Shanghai')
    else:
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
    return to_str(dt)[:DATE_LEN]

def today_str():
    return to_date_str(now())

def now_str():
    return to_str(now())

def get_date(t):
    if not t:
        return t
    elif isinstance(t, date):
        return t
    elif isinstance(t, datetime):
        return t.date()
    else:
        return t[:DATE_LEN]

#ensure tzinfo
def to_datetime(dt):
    if isinstance(dt, six.string_types):
        if len(dt)<=DATE_LEN:
            return to_datetime(parse_date(dt))
        else:
            return with_tzinfo(parse_datetime(dt))

    elif isinstance(dt, date):
        return with_tzinfo(datetime(dt.year, dt.month, dt.day))

    elif isinstance(dt, datetime):
        return with_tzinfo(dt)

    else:
        return None

def to_interval(dt):
    if isinstance(dt, six.string_types):
        return parse_interval(dt)
    else:
        return None

def from_timestamp(t):
    return localize(datetime.fromtimestamp(t))

