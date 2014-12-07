#coding:utf8

from __future__ import absolute_import, unicode_literals

from enum import IntEnum

from datetime import datetime
from dateutil.relativedelta import relativedelta

from . import date_time

Period = IntEnum('Period', 'm1 m5 m30 day week month quarter year')
DayPeriod = IntEnum('Period', 'day week month quarter year')

def timedelta_by(period, n=1):
    if period == 'day':
        return relativedelta(days=n)
    elif period == 'week':
        return relativedelta(weeks=n)
    elif period == 'month':
        return relativedelta(months=n)
    elif period == 'quarter':
        return relativedelta(months=3*n)
    elif period == 'year':
        return relativedelta(months=12*n)
    else:
        raise Exception("invalid period %s" % period)

def datetime_by(t, minute=None, hour=None, day=None, 
        week=None, month=None, quarter=None, year=None,
        m1=None, m5=None, m30=None):
    """
    >>> print datetime_by('2011-12-31T15:32:02', minute=1)
    2011-12-31T15:32:00
    >>> print datetime_by('2011-12-31T15:32:02', minute=5)
    2011-12-31T15:30:00
    >>> print datetime_by('2011-12-31T15:04:02', minute=5)
    2011-12-31T15:00:00
    >>> print datetime_by('2011-12-31T15:32:02', hour=4)
    2011-12-31T12:00:00
    >>> print datetime_by('2011-12-31T15:04:02', day=1)
    2011-12-31T00:00:00
    >>> print datetime_by('2011-12-31T15:04:02', day=4)
    2011-12-29T00:00:00
    >>> print datetime_by('2011-12-31T15:04:02', week=1)
    2011-12-26T00:00:00
    >>> print datetime_by('2011-12-31T15:04:02', week=2)
    2011-12-19T00:00:00
    >>> print datetime_by('2011-12-31T15:04:02', month=1)
    2011-12-01T00:00:00
    >>> print datetime_by('2011-12-31T15:04:02', month=5)
    2011-11-01T00:00:00
    >>> print datetime_by('2011-12-31T15:04:02', quarter=1)
    2011-10-01T00:00:00
    >>> print datetime_by('2011-12-31T15:04:02', quarter=2)
    2011-07-01T00:00:00
    >>> print datetime_by('2011-12-31T15:04:02', year=2)
    2010-01-01T00:00:00
    """
    t = date_time.to_datetime(t)
    z = t.tzinfo
    #datetime.datetime(year, month, day, hour, minute, second, microsecond, tzinfo)

    if minute is None:
        if m1 is not None:
            minute = 1*m1
        elif m5 is not None:
            minute = 5*m5
        elif m30 is not None:
            minute = 30*m30

    if minute is not None:
        r = datetime(t.year, t.month, t.day, t.hour, t.minute/minute*minute, tzinfo=z)

    elif hour is not None:
        r = datetime(t.year, t.month, t.day, t.hour/hour*hour, tzinfo=z)

    elif day is not None:
        r = datetime(t.year, t.month, (t.day-1)/day*day+1, tzinfo=z)

    elif week is not None:
        y,w,d = t.isocalendar()
        w2 = (w-1)/week*week+1
        dw = w-w2
        dd = d-1
        dt = timedelta(days=dd, weeks=dw)
        r  = datetime(t.year, t.month, t.day, tzinfo=z) - dt

    elif month is not None:
        r = datetime(t.year, (t.month-1)/month*month+1, 1, tzinfo=z)

    elif quarter is not None:
        q = (t.month-1)/3
        q2 = q/quarter*quarter
        m2 = q2*3+1
        r = datetime(t.year, m2, 1, tzinfo=z)

    elif year is not None:
        r = datetime(t.year/year*year, 1, 1, tzinfo=z)

    else:
        raise Exception("argument error")

    return r

class DatetimeBy(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, t):
        return datetime_by(t, **self.kwargs)
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()


