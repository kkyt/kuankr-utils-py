# coding: utf8
from __future__ import absolute_import, unicode_literals

import simplejson as json
import types

import datetime
import functools
import decimal

from kuankr_utils import log
from kuankr_utils.datetime import with_tzinfo

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
    
@register_encoder(types.GeneratorType)
def encode_generator(obj):
    return list(obj)

@register_encoder(decimal.Decimal)
def encode_generator(obj):
    return float(obj)

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'as_json'):
            return obj.as_json()

        c = obj.__class__
        e = _encoders.get(c)
        if e is not None:
            return e(obj)

        return super(Encoder, self).default(obj)

def dumps(x, pretty=False, ensure_ascii=False, **kwargs):
    if pretty:
        kwargs['indent'] = '  '
    return json.dumps(x, cls=Encoder, ensure_ascii=ensure_ascii, **kwargs)

def loads(x):
    if isinstance(x, types.GeneratorType):
        return (loads(r) for r in x)
    else:
        return json.loads(x)

