
from __future__ import absolute_import

import six
import pickle
import functools

from kuankr_utils import log, debug, json, msgpack

#unified interface to josn,msgpack,yaml etc

class Serializer(object):
    def __init__(self, **options):
        self.options = options

    #TODO: default to '\n'?
    def sep(self):
        return ''

    def dumps(self, x):
        return x

    def loads(self, s):
        return s

    def loads_stream(self, stream, ignore_error=True):
        #for show in stack traceback
        n = 0 
        for x in stream:
            n += 1
            try:
                yield self.loads(x)
            except Exception as e:
                if not ignore_error:
                    raise
                else:
                    log.error('%r\n%s' % (x, e))

    def dumps_stream(self, stream, ignore_error=True):
        n = 0 
        for x in stream:
            n += 1
            try:
                yield self.dumps(x)
            except Exception as e:
                if not ignore_error:
                    raise
                else:
                    log.error('%r\n%s' % (x, e))

    def load(self, f):
        return None

    def dump(self, x, f):
        f.write(self.dumps(x))

    def dump_sep(self, x, f):
        f.write(self.dumps(x) + self.sep())

    def load_stream(self, f, ignore_error=True):
        n = 0 
        for line in f:
            n += 1
            try:
                yield self.loads(line)
            except Exception as e:
                if not ignore_error:
                    raise
                else:
                    log.error('%r\n%s' % (line, e))
    
    def dump_stream(self, stream, f, ignore_error=True):
        n = 0 
        for x in stream:
            n += 1
            try:
                self.dump_sep(x, f)
            except Exception as e:
                if not ignore_error:
                    raise
                else:
                    log.error('%r\n%s' % (x, e))
        
class JsonSerializer(Serializer):
    def __init__(self, float_repr=None, compact=None, **kwargs):
        if compact is None:
            compact = True
        if float_repr is not None:
            #NOTE: HACK globally impact
            from simplejson import encoder
            encoder.FLOAT_REPR = float_repr
        if compact:
            self.separators = (',',':')
            
    def dumps(self, x):
        return json.dumps(x, separators=self.separators)

    def loads(self, s):
        return json.loads(s)

    def sep(self):
        return '\n'

class MsgpackSerializer(Serializer):
    def __init__(self, encoding=None, unicode_errors=None):
        self.encoding = encoding
        self.unicode_errors = unicode_errors

    def dumps(self, x):
        return msgpack.dumps(x)

    def loads(self, s):
        return msgpack.loads(s, encoding=self.encoding, unicode_errors=self.unicode_errors)

    def load_stream(self, f, ignore_error=True):
        return msgpack.load_stream(f, encoding=self.encoding, unicode_errors=self.unicode_errors)

    def dump_stream(self, stream, f, sep=None):
        return msgpack.streaming_dump(stream, f)


serializers = {
    None: Serializer,
    'json': JsonSerializer,
    'msgpack': MsgpackSerializer
}

def get_serializer(s, *args, **kwargs):
    x = serializers.get(s)
    if x is not None:
        x = x(*args, **kwargs)
    return x

'''
encoders = {
    None: lambda x: x,
    'string': str,
    'pickle': pickle.dumps,
    'json': json.dumps,
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
'''
    
