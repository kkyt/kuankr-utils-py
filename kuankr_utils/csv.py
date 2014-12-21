from __future__ import absolute_import

from datetime import datetime
import csv
import six

from . import date_time, json

def _to_list(x, fields=None):
    if fields is not None and isinstance(x, dict):
        x = [x[f] for f in fields]

    for i,v in enumerate(x):
        if isinstance(v, unicode):
            x[i] = v.encode('utf8')
        elif isinstance(v, datetime):
            x[i] = date_time.to_str(v)
        elif isinstance(v, (list,dict)):
            x[i] = json.dumps(v)
    return x

def dumps(x, fields=None, delimiter=None):
    x = _to_list(x, fields)
    s = six.StringIO()
    w = csv.writer(s, delimiter=delimiter)
    w.writerow(x)
    return s.getvalue()

def loads(s, fields=None, delimiter=None):
    s = six.StringIO(s)
    r = csv.reader(s, delimiter=delimiter)
    r = list(r)
    return r[0]

def loads_stream(stream, **kwargs):
    for s in stream:
        yield loads(s, **kwargs)

def dumps_stream(stream, **kwargs):
    for x in stream:
        yield dumps(x, **kwargs)
    
