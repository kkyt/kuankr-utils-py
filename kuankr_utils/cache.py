import copy

def simple_cached_function(f):
    cache = {}
    def g(*args):
        name = args[0]
        c = cache.get(name)
        if c is None:
            c = cache[name] = f(name)
        return copy.deepcopy(c)
    return g

