import sys

class NamespacedRedis(object):
    def __init__(self, prefix, redis, debug=False):
        self.prefix = prefix
        self.redis = redis
        self.debug = debug
    
    def __getattr__(self, m):
        def f(*args, **kwargs):
            args = list(args)
            args[0] = self.prefix + ':' + args[0]
            g = getattr(self.redis, m)
            if self.debug:
                sys.stderr.write('NS_REDIS:%s %s %s\n' % (m, args, kwargs))
            return g(*args, **kwargs)
        return f

class Collection(object):
    def __init__(self, redis=None, key=None):
        self.redis = redis
        self.key = key

    def encoder_for_type(self, t):
        if t is None:
            return None
        elif t==bool:
            return int
        else:
            return str

    def decoder_for_type(self, t):
        if t is None:
            return None
        elif t==bool:
            return lambda x: x=='1'
        else:
            return t

class Set(Collection):
    def __init__(self, redis=None, key=None, type=None):
        super(Set, self).__init__(redis, key)
        self.type = type
        self.encoder = self.encoder_for_type(self.type)
        self.decoder = self.decoder_for_type(self.type)

    def add(self, k, m):
        if self.encoder is not None:
            m = self.encoder(m)
        self.redis.sadd(self.key+k, m)

    def remove(self, k, m):
        if self.encoder is not None:
            m = self.encoder(m)
        self.redis.srem(self.key+k, m)

    def contains(self, k, m):
        if self.encoder is not None:
            m = self.encoder(m)
        return self.redis.sismember(self.key+k, m)

    def members(self, k):
        a = list(self.redis.smembers(self.key+k))
        if self.decoder is not None:
            a = [self.decoder(x) for x in a]
        return a
        
#TODO: None handle
class Hash(Collection):
    def __init__(self, redis=None, key=None, types=None):
        super(Hash, self).__init__(redis, key)
        self.types = types

        self.decoders = {}
        self.encoders = {}

        for f, t in self.types.items():
            self.encoders[f] = self.encoder_for_type(t)
            self.decoders[f] = self.decoder_for_type(t)

    def incr(self, k, f, change):
        t = self.types.get(f)
        if t==float:
            self.redis.hincrbyfloat(self.key+k, f, change)
        elif t==int:
            self.redis.hincr(self.key+k, f, change)
        else:
            raise Exception('field %s must be int or float' % f)
        
    def get(self, k, f):
        v = self.redis.hget(self.key+k, f)
        if v is not None:
            t = self.decoders.get(f)
            if t is not None:
                v = t(v)
        return v

    def mget(self, k):
        if not self.redis.exists(self.key+k):
            return None

        x = self.redis.hgetall(self.key+k)
        for f,t in self.decoders.items():
            x[f] = t(x[f])
        return x
    
    def set(self, k, f, v):
        if v is None:
            self.redis.hdel(self.key+k, f)
            return

        t = self.encoders.get(f)
        if t is not None:
            v = t(v)
        self.redis.hset(self.key+k, f, v)

    def mset(self, k, v):
        x = dict(v)
        for f,v in x.items():
            if v is None:
                del x[f]
                self.redis.hdel(self.key+k, f)

        for f,t in self.decoders.items():
            if not f in x:
                continue
            z = x[f]
            x[f] = t(z)
        self.redis.hmset(self.key+k, x)

    def exists(self, k):
        return self.redis.exists(self.key+k)

    def remove(self, k):
        self.redis.delete(self.key+k)

