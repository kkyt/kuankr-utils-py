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
