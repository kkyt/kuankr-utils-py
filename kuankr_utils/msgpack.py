
from __future__ import absolute_import

import struct
import datetime
import decimal
import types
from collections import Sequence, Mapping, Set
from io import BytesIO

import msgpack

from pyutils import datetime_utils, debug, log

try:
    import bson
    import bson.objectid
except:
    bson = None

EXT_DATETIME = 1

__all__ = ['dumps', 'loads', 'load', 'dump', 'streaming_load', 'streaming_dump']

def default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)

    elif isinstance(obj, types.GeneratorType):
        return list(obj)

    elif isinstance(obj, datetime.datetime):
        s = struct.pack('>q', datetime_utils.datetime_to_microsecond(obj))
        return msgpack.ExtType(EXT_DATETIME, s)

    elif bson is not None and isinstance(obj, bson.objectid.ObjectId):
        return str(obj)

    else:
        return obj

def ext_hook(code, data):
    if code == EXT_DATETIME:
        t = struct.unpack('>q', data)[0]
        return datetime_utils.microsecond_to_datetime(t)
    else:
        log.warn('unknow msgpack ext code: %s' % code)
        return data

def loads(s, encoding=None):
    return msgpack.unpackb(s, ext_hook=ext_hook, encoding=encoding)

def dumps(x):
    return msgpack.packb(x, default=default)

def dump(x, f):
    f.write(dumps(x))

def load(f):
    return loads(f.read())

#TODO
"""
def streaming_dumps(x):
    if isinstance(x, types.GeneratorType):
        for e in x:
            yield dumps(e)
    else:
        yield dumps(x)

def streaming_loads(s):
    buf = BytesIO()
    buf.write(s)
    buf.seek(0)
    return streaming_load(buf)
"""

def streaming_dump(x, f):
    if isinstance(x, types.GeneratorType):
        for e in x:
            f.write(dumps(e))
    else:
        f.write(dumps(x))

def streaming_load(f):
    unpacker = msgpack.Unpacker(f)
    for e in unpacker:
        yield decode(e)


