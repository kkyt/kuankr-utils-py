
from __future__ import absolute_import

import struct
import datetime
import decimal
import types
from collections import Sequence, Mapping, Set
from io import BytesIO

import msgpack

from kuankr_utils import log, debug, date_time

try:
    import bson
    import bson.objectid
except:
    bson = None

EXT_DATETIME = 1

__all__ = ['dumps', 'loads', 'load', 'dump', 'load_stream']

def default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)

    elif isinstance(obj, types.GeneratorType):
        return list(obj)

    elif isinstance(obj, datetime.datetime):
        s = struct.pack('>q', date_time.to_microsecond(obj))
        return msgpack.ExtType(EXT_DATETIME, s)

    elif bson is not None and isinstance(obj, bson.objectid.ObjectId):
        return str(obj)

    else:
        return obj

def ext_hook(code, data):
    if code == EXT_DATETIME:
        t = struct.unpack('>q', data)[0]
        return date_time.from_microsecond(t)
    else:
        log.warn('unknow msgpack ext code: %s' % code)
        return data

def loads(s, encoding=None, unicode_errors=None):
    if unicode_errors is None:
        unicode_errors = 'strict'
    return msgpack.unpackb(s, ext_hook=ext_hook, encoding=encoding, unicode_errors=unicode_errors)

def dumps(x):
    return msgpack.packb(x, default=default)

def dump(x, f):
    f.write(dumps(x))

def load(f):
    return loads(f.read())

#TODO
"""
def dumps_stream(x):
    if isinstance(x, types.GeneratorType):
        for e in x:
            yield dumps(e)
    else:
        yield dumps(x)

def loads_stream(s):
    buf = BytesIO()
    buf.write(s)
    buf.seek(0)
    return streaming_load(buf)
"""

def load_stream(f, ignore_error=True, **options):
    unpacker = msgpack.Unpacker(f, **options)
    n = 0
    while True:
        n += 1
        try:
            e = next(unpacker)
        except StopIteration:
            break
        except Exception as e:
            if ignore_error:
                log.error('%r\n%s\n' % (e, r))
            else:
                raise


