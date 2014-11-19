
from __future__ import absolute_import

import six
import pickle
import functools

from kuankr_utils import log, debug, json, msgpack

class Serializer(object):
    def __init__(self, *args, **kwargs):
        pass

    def encode(self, x):
        return x

    def decode(self, s):
        return s

    def decode_stream(self, stream, ignore_error=True):
        n = 0 
        for x in stream:
            n += 1
            try:
                yield self.decode(x)
            except Exception as e:
                if not ignore_error:
                    raise
                else:
                    log.error('%r\n%s' % (x, e))

    def encode_stream(self, stream, ignore_error=True):
        n = 0 
        for x in stream:
            n += 1
            try:
                yield self.encode(x)
            except Exception as e:
                if not ignore_error:
                    raise
                else:
                    log.error('%r\n%s' % (x, e))

    def decode_file(self, f, ignore_error=True):
        #for show in stack traceback
        n = 0 
        for line in f:
            n += 1
            try:
                yield self.decode(line)
            except Exception as e:
                if not ignore_error:
                    raise
                else:
                    log.error('%r\n%s' % (line, e))
    
    def encode_file(self, stream, f, sep='\n', ignore_error=True):
        n = 0 
        for x in stream:
            n += 1
            try:
                s = self.encode(x) + sep
                f.write(s)
            except Exception as e:
                if not ignore_error:
                    raise
                else:
                    log.error('%r\n%s' % (line, e))
        
class JsonSerializer(Serializer):
    def __init__(self, float_repr=None, **kwargs):
        if float_repr is not None:
            #Hack globally impact
            from simplejson import encoder
            encoder.FLOAT_REPR = float_repr
            
    def encode(self, x):
        return json.dumps(x)

    def decode(self, s):
        return json.loads(s)

class MsgpackSerializer(Serializer):
    def __init__(self, encoding=None, unicode_errors=None):
        self.encoding = encoding
        self.unicode_errors = unicode_errors

    def encode(self, x):
        return msgpack.dumps(x)

    def decode(self, s):
        return msgpack.loads(s, encoding=self.encoding, unicode_errors=self.unicode_errors)

    def decode_file(self, f, ignore_error=True):
        return msgpack.streaming_load(f)

    def encode_file(self, stream, f, sep=''):
        return msgpack.streaming_dump(stream, f)

serializers = {
    None: Serializer,
    'json': JsonSerializer,
    'msgpack': MsgpackSerializer
}

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

def get_serializer(s, *args, **kwargs):
    x = serializers.get(s)
    if x is not None:
        x = x(*args, **kwargs)
    return x

def get_decoder(s, encoding=None):
    f = decoders.get(s)
    if encoding is not None:
        f = functools.partial(f, encoding=encoding)
    return f

def get_encoder(s):
    f = encoders.get(s)
    return f
    
