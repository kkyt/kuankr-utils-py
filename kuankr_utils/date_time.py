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
    return datetime.utcnow().replace(tzinfo=utc)

def now():
    z = localzone()
    # utc -> local
    return utcnow().astimezone(z)

def today():
    return to_datetime(date.today())

def to_utc(dt):
    z = utc
    if dt.tzinfo is None:
        return dt.replace(tzinfo=z)
    elif dt.tzinfo != z:
        return dt.astimezone(z)
    else:
        return dt

def to_local(dt):
    if dt is None:
        return None
    z = localzone()
    try:
        if dt.tzinfo is None:
            #NOTE: tzinfo=null is not utc

            #2014-11-29T16:00:46+08:06
            #return dt.replace(tzinfo=utc)

            #2014-11-29T16:00:46+08:00
            return z.localize(dt)
        elif dt.tzinfo != z:
            return dt.astimezone(z)
        else:
            return dt
    except OverflowError:
        return None

def with_tzinfo(dt, utc=False):
    if dt.tzinfo is None:
        if utc:
            dt = dt.replace(tzinfo=utc)
        else:
            dt = to_local(dt)
    return dt

def to_str(dt, local=True):
    if isinstance(dt, six.string_types):
        return dt
    if local:
        dt = to_local(dt)
    if dt is None:
        return None
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
        if dt=='today':
            return today()

        elif dt=='now':
            return now()

        elif len(dt)<=DATE_LEN:
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
        if dt.find('/')>=0:
            t0, t1 = dt.split('/')
            return (to_datetime(t0), to_datetime(t1))
        else:
            dt = to_datetime(dt)
            return (dt, dt)
    elif isinstance(dt, (list, tuple)):
        return (dt[0], dt[1])
    else:
        return (dt, dt)

def from_timestamp(t):
    return to_local(datetime.fromtimestamp(t))

#datetime range
def to_datetime_range(s, include_stop=False, **delta):
    is_range = isinstance(s,(list,tuple)) or isinstance(s, six.string_types) and s.find('/')>=0
    #special case
    if not is_range:
        yield to_datetime(s)
        return

    if not delta:
        delta = {'days': 1}
    delta = timedelta(**delta)

    a = to_interval(s)
    start = a[0]
    stop = a[1]


    x = start
    while x<stop or (include_stop and x==stop):
        yield x
        x += delta

#NOTE: utcfromtimestamp
utc = pytz.utc
unix_time_epoch = datetime.utcfromtimestamp(0).replace(tzinfo=utc)
ad_epoch = datetime(1,1,1, tzinfo=utc)

#######################

def microsecond_from_timedelta(td):
    return td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6


################# unix time

def unix_time(t):
    delta = to_utc(t) - unix_time_epoch
    return delta.total_seconds()

def _unix_time_microsecond(t):
    #TODO
    t = t.replace(tzinfo=None)
    td = t - unix_time_epoch
    return microsecond_from_timedelta(td)

def to_timestamp(t):
    return int(unix_time(t))
    #return int(to_datetime(t).strftime('%s'))

def from_timestamp(t):
    return datetime.utcfromtimestamp(t)

def timestamp_to_datetime_local(t):
    return datetime.fromtimestamp(t)

def to_millisecond(t):
    return _unix_time_microsecond(t)/1000
    #return int(round(mktime(t.timetuple())*1000))

def to_microsecond(t):
    if isinstance(t, six.integer_types):
        return int(t)
    if isinstance(t, six.string_types):
        t = to_datetime(t)
    return _unix_time_microsecond(t)
    #return int(round(mktime(t.timetuple())*1000000)) + t.microsecond

def from_microsecond(t):
    return datetime.utcfromtimestamp(t/1000000).replace(microsecond=t%1000000)


############## microsecond ad

def microsecond_from_ad(t):
    t = to_utc(t)
    td = t - ad_epoch
    return microsecond_from_timedelta(td)

def to_microsecond_ad(t):
    if isinstance(t, six.integer_types):
        return int(t)
    if isinstance(t, six.string_types):
        t = to_datetime(t)
    return microsecond_from_ad(t)

def from_microsecond_ad(t):
    t -= to_microsecond_ad(unix_time_epoch)
    r = datetime.utcfromtimestamp(t/1000000).replace(microsecond=t%1000000, tzinfo=utc)
    return to_local(r)

