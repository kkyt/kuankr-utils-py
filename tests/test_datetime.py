from datetime import datetime

from kuankr_utils import log, debug, json

from kuankr_utils.date_time import *

def test_simple():
    print datetime.now().isoformat()
    print utcnow().isoformat()
    print now().isoformat()
    print to_str(now())

def test_json():
    print json.dumps(now().date())

def test_timezone():
    t0 = now().replace(microsecond=0)
    t1 = datetime.now().replace(microsecond=0)
    t2 = utcnow().replace(microsecond=0)
    print t0,t1,t2
    assert to_str(t0) == to_str(t1)
    assert to_str(t0) == to_str(t2)

    t = datetime(2011, 1, 4, 0, 0)
    assert json.dumps(t)=='"2011-01-04T00:00:00+08:00"'


def test_overflow():
    s = to_str(datetime.max)
    assert s==None

    s = to_str(datetime.min)
    assert s==None

def test_microsecond():
    t = to_str(from_microsecond_ad(0))
    assert t=='0001-01-01T08:00:00+08:00'

    t = to_str(from_microsecond_ad(1))
    assert t=='0001-01-01T08:00:00.000001+08:00'

