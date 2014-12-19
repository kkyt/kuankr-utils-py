from __future__ import absolute_import

import csv
import six

def _to_list(x, fields=None):
    if fields is not None and isinstance(x, dict):
        x = [x[f] for f in fields]

    for i in range(len(x)):
        if isinstance(x[i], unicode):
            x[i] = x[i].encode('utf8')
    return x

def dumps(x, headers=None):
    x = _to_list(x, headers)
    s = six.StringIO()
    w = csv.writer(s)
    w.writerow(x)
    return s.getvalue()

def loads(s):
    s = six.StringIO(s)
    r = csv.reader(s)
    r = list(r)
    return r[0]

def loads_stream(stream):
    for s in stream:
        yield loads(s)

def dumps_stream(stream, headers=None):
    for x in stream:
        yield dumps(x)
    
