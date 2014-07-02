import sys
import imp
import __builtin__

import simplejson as json
import types

from kuankr_utils import log
from kuankr_utils import module

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, types.FunctionType):
            r = {
                '__module__': obj.__module__, 
                '__name__': obj.__name__
            }
        else:
            c = obj.__class__
            r = {
                '__module__': c.__module__, 
                '__class__': c.__name__
            }
            if hasattr(obj, '__getstate__'):
                r['__state__'] = obj.__getstate__()
            else:
                r['__dict__'] = obj.__dict__
        reutrn r

def dumps(obj, **kwargs):
    return json.dumps(obj, cls=Encoder, **kwargs)
 
def encode(obj):
    return json.loads(dumps(obj))

def loads(s):
    return decode(json.loads(s))

#copy from jsonpickle
def _new_instance(cls):
    try:
        if hasattr(cls, '__new__'): # new style classes
            return cls.__new__(cls)
        else:
            return object.__new__(cls)
    except TypeError: # old-style classes
        try:
            return cls()
        except TypeError: # fail gracefully
            return None

def decode(d):
    if isinstance(d, dict):
        if '__class__' in d:
            m = d.get('__module__')
            if m is None:
                code = d.get('__code__')
                if code is None:
                    m = __builtin__
                else:
                    m = module.import_from_code(code)
            else:
                m = __import__(m)

            if '__name__' in d:
                return getattr(m, d['__name__']
            else:
                cls = getattr(m, d['__class__'])
                if '__state__' in d:
                    obj = _new_instance(cls)
                    obj.__setstate__(decode(d['__state__']))
                elif '__dict__' in d:
                    obj.__dict__.update(decode(d['__dict__']))
                else:
                    args = decode(d.get('__args__', []))
                    kwargs = decode(d.get('__kwargs__', {}))
                    return cls(*args, **kwargs)
        else:
            for k in d:
                d[k] = decode(d[k])
            return d
    elif isinstance(d, list):
        n = len(d)
        for i in range(n):
            d[i] = decode(d[i])
        return d
    else:
        return d

def decode_from_config(d):
    keys = 'module name class state dict code args kwargs'.split()
    x = {}
    for k in keys:
        if k in d:
            x['__%s__' % k] = d[k]
    return decode(x)

