

import pickle
import functools

from kuankr_utils import log, debug, json, msgpack

encoders = {
    None: lambda x: x,
    'string': str,
    'pickle': pickle.dumps,
    'json': json.dumps_ln,
    'msgpack': msgpack.dumps
}

decoders = {
    None: lambda x: x,
    'string': str,
    'pickle': pickle.loads,
    'json': json.loads,
    'msgpack': msgpack.loads
}

def get_decoder(s, encoding=None):
    f = decoders.get(s)
    if encoding is not None:
        f = functools.partial(f, encoding=encoding)
    return f

def get_encoder(s):
    f = encoders.get(s)
    return f
    
