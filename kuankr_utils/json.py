# coding: utf8
from __future__ import absolute_import, unicode_literals

import simplejson as json
import types

import datetime
import functools
import decimal

from kuankr_utils import log, debug
from kuankr_utils.date_time import with_tzinfo, to_datetime

#ref: aspen/json_

_encoders = {}

def register_encoder(cls):
    log.debug('kuankr_utils.json.register_encoder: %s' % cls.__name__)

    global _encoders
    def inner(encoder):
        _encoders[cls] = encoder
        return encoder
    return inner

@register_encoder(datetime.datetime)
def encode_datetime(obj):
    return with_tzinfo(obj).isoformat()
    
@register_encoder(datetime.date)
def encode_date(obj):
    obj = to_datetime(obj)
    return obj.isoformat()

@register_encoder(types.GeneratorType)
def encode_generator(obj):
    return list(obj)

#NOTE: simplejson already handles Decimal
@register_encoder(decimal.Decimal)
def encode_generator(obj):
    #return float(obj)
    return str(obj)

class Encoder(json.JSONEncoder):
    def encode(self, obj):
        if hasattr(obj, 'as_json') and hasattr(obj.as_json, '__call__'):
            obj = obj.as_json()
        return super(Encoder, self).encode(obj)

    def default(self, obj):
        if hasattr(obj, 'as_json') and hasattr(obj.as_json, '__call__'):
            return obj.as_json()

        c = obj.__class__
        e = _encoders.get(c)
        if e is not None:
            return e(obj)

        if hasattr(obj, '__str__'):
            #ObjectId, UUID
            return str(obj)

        return super(Encoder, self).default(obj)

def as_json(obj):
    if hasattr(obj, 'as_json') and hasattr(obj.as_json, '__call__'):
        return obj.as_json()
    elif isinstance(obj, dict):
        return {k: as_json(v) for k,v in obj.items()}
    elif isinstance(obj, list):
        return [as_json(v) for v in obj]
    else:
        return obj

def dumps(x, pretty=False, ensure_ascii=False, **kwargs):
    if pretty:
        kwargs['indent'] = '  '
    return json.dumps(x, cls=Encoder, ensure_ascii=ensure_ascii, **kwargs)

def loads(x):
    if isinstance(x, types.GeneratorType):
        return (loads(r) for r in x)
    else:
        return json.loads(x)

def loads_stream(stream):
    for s in stream:
        yield loads(s)

def dumps_stream(stream):
    for x in stream:
        yield dumps(x)

    
