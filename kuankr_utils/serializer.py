from __future__ import absolute_import

import six
import pickle
import functools
import types

from datetime import datetime

from kuankr_utils import log, debug, json, csv, api_json, date_time

#unified interface to josn,msgpack,yaml etc

class Serializer(object):
    def __init__(self, **options):
        self.options = options

    #TODO: default to '\n'?
    def sep(self):
        return ''

    def dumps(self, x):
        if isinstance(x, types.GeneratorType):
            return self.dump_stream(x)
        else:
            if isinstance(x, unicode):
                return x.encode('utf8')
            else:
                return str(x)

    def loads(self, s):
        if isinstance(s, types.GeneratorType):
            return self.load_stream(s)
        else:
            return s

    #TODO: delete
    def loads_stream(self, stream, ignore_error=False):
        log.error('use load_stream')
        return self.load_stream(stream, ignore_error)
    def dumps_stream(self, stream, ignore_error=False):
        log.error('use dump_stream')
        return self.dump_stream(stream, ignore_error)

    def load_stream(self, stream, ignore_error=False):
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

    def dump_stream(self, stream, ignore_error=False):
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
        s = self.dumps(x)
        f.write(s + self.sep())

    def load_stream(self, f, ignore_error=False):
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
    
    def dump_stream_to_file(self, stream, f, ignore_error=False):
        n = 0 
        for x in stream:
            n += 1
            try:
                self.dump_sep(x, f)
            except IOError:
                raise
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
        else:
            self.separators = (', ',': ')
            
    def dumps(self, x):
        return json.dumps(x, separators=self.separators)

    def loads(self, s):
        return json.loads(s)

    def sep(self):
        return '\n'

class ApiJsonSerializer(Serializer):
    def dumps(self, x, **kwargs):
        return api_json.dumps(x, **kwargs)

    def loads(self, x, **kwargs):
        return api_json.loads(x, **kwargs)

class TsvSerializer(Serializer):
    def __init__(self, fields=None, **kwargs):
        self.fields = fields

    def sep(self):
        return '\n'

    def dumps(self, x):
        if isinstance(x, dict):
            x = [x.get(f) for f in self.fields]

        for i,v in enumerate(x):
            if isinstance(v, unicode):
                v = v.encode('utf8')
            elif isinstance(v, datetime):
                v = date_time.to_str(v)
            elif isinstance(v, (list,dict)):
                v = json.dumps(v)
            elif v is None:
                v = ''

            x[i] = str(v).replace('\t', ' ')
                
        return '\t'.join(x)

    def loads(self, x):
        return x.split('\t')

class CsvSerializer(Serializer):
    def __init__(self, fields=None, headers=None, delimiter=None, **kwargs):
        self.fields = fields
        if headers == True:
            headers = fields
        self.headers = headers
        self.delimiter = delimiter or ','
        self.options = {
            'fields': self.fields,
            'delimiter': self.delimiter
        }


    def dumps(self, x):
        return csv.dumps(x, **self.options)

    def loads(self, x):
        return csv.dumps(x, **self.options)

    def dump_stream_to_file(self, stream, f, ignore_error=False):
        if self.headers:
            self.dump_sep(self.headers, f)
        return super(CsvSerializer, self).dump_stream_to_file(stream, f, ignore_error)
            
    def sep(self):
        return ''

class MsgpackSerializer(Serializer):
    def __init__(self, encoding=None, unicode_errors=None):
        self.encoding = encoding
        self.unicode_errors = unicode_errors

    def dumps(self, x):
        from kuankr_utils import msgpack
        if isinstance(x, types.GeneratorType):
            return self.dump_stream(x)
        else:
            return msgpack.dumps(x)

    def loads(self, s):
        from kuankr_utils import msgpack
        if isinstance(s, types.GeneratorType):
            return self.load_stream(s)
        else:
            return msgpack.loads(s, encoding=self.encoding, unicode_errors=self.unicode_errors)

    def load_stream(self, f, ignore_error=False):
        from kuankr_utils import msgpack
        return msgpack.load_stream(f, encoding=self.encoding, unicode_errors=self.unicode_errors)

    def dump_stream_to_file(self, stream, f, sep=None):
        from kuankr_utils import msgpack
        return msgpack.streaming_dump(stream, f)

class UJsonSerializer(Serializer):
    def dumps(self, x, **kwargs):
        import ujson
        return ujson.dumps(x)

    def loads(self, s, **kwargs):
        import ujson
        return ujson.loads(s)

class SimpleJsonSerializer(Serializer):
    def dumps(self, x, **kwargs):
        import simplejson
        return simplejson.dumps(x)

    def loads(self, s, **kwargs):
        import simplejson
        return simplejson.loads(s)

serializers = {
    None: Serializer,
    'raw': Serializer,
    'json': JsonSerializer,
    'ujson': UJsonSerializer,
    'simple_json': SimpleJsonSerializer,
    'api_json': ApiJsonSerializer,
    'csv': CsvSerializer,
    'tsv': TsvSerializer,
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
    
