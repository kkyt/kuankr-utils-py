import itertools
import functools
import heapq
import operator
import collections

def concat(*args):
    for a in args:
        for s in a:
            for x in s:
                yield x

def ihead(iter, n):
    i = 0
    for x in iter:
        i += 1
        if i>n:
            break
        yield x

def ifirst(iter):
    y = None
    for x in iter:
        if y is None:
            y = x
    return y

def slice_iter(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = itertools.islice(sourceiter, size)
        yield itertools.chain([batchiter.next()], batchiter)

def ipeekn(iterable, n):
    it = iter(iterable)
    peek = []
    for i in range(n):
        try:
            peek.append(next(it))
        except StopIteration:
            break
    return peek, itertools.chain(peek, it)

def ipeek(iterable):
    r = ipeekn(iterable, 1)
    n = len(r[0])
    if n==1:
        return r[0][0], r[1]
    elif n==0:
        return None, r[1]
    else:
        return r

def itranspose(iterable):
    it = iter(iterable)
    first, it = ipeek(it)
    if first is None:
        return tuple()

    n = len(first)

    deques = [collections.deque() for i in range(n)]
    def gen(dq):
        while True:
            if not dq:
                x = next(it)
                for i in range(n):
                    deques[i].append(x[i])
            yield dq.popleft()
    return tuple(gen(d) for d in deques)

def imerge_t(iterable, stop_early=False):
    channels = itranspose(iterable)
    return imerge(*channels, stop_early=stop_early)

def ijoin(*iterables, **kwargs):
    '''Join multiple sorted inputs into a single sorted output.

    Args:
        *iterables: [ [(key, value)] ]
        stop_early: 

    >>> list(ijoin([(1,'x'),(3,'y')], [], [(1,10), (2, 20), (3,30)], [(2, 0.5), (4, 0.3)]))
    [(1, ['x', None, 10, None]), (2, [None, None, 20, 0.5]), (3, ['y', None, 30, None]), (4, [None, None, None, 0.3])]

    >>> list(ijoin([(1,'x'),(3,'y')], [(1,10), (2, 20), (3,30)], [(2, 0.5), (4, 0.3)], stop_early=True))
    [(1, ['x', 10, None]), (2, [None, 20, 0.5]), (3, ['y', None, None])]

    >>> list(ijoin([], [(1,10), (2, 20), (3,30)], [(2, 0.5), (4, 0.3)], stop_early=True))
    []
    '''

    stop_early = kwargs.get('stop_early', False)
    itrs = []
    n = len(iterables)
    for i in range(n):
        f = lambda i, key, *args: [key, i] + list(args)
        g = functools.partial(f, i)
        itrs.append(itertools.starmap(g, iterables[i]))

    s = imerge(*itrs, stop_early=stop_early)
    for k, g in igroupby(s, lambda x: x[0]):
        r = [None]*n
        for x in g:
            r[x[1]] = x[2]
        yield k, r

def ijoin_dict(iterables, **kwargs):
    '''Join multiple sorted inputs into a single sorted output.

    Args:
        iterables: {series: [(key, value)] }
        stop_early: 

    >>> list(ijoin_dict({ 'a': [(1,'x'),(3,'y')], 'b': [(1,10), (2, 20), (3,30)], 'c': [(2, 0.5), (4, 0.3)]}))
    [(1, {'a': 'x', 'b': 10}), (2, {'c': 0.5, 'b': 20}), (3, {'a': 'y', 'b': 30}), (4, {'c': 0.3})]
    '''

    stop_early = kwargs.get('stop_early', False)
    itrs = {}
    for k in iterables:
        f = lambda k, key, *args: [key, k] + list(args)
        g = functools.partial(f, k)
        itrs[k] = itertools.starmap(g, iterables[k])

    s = imerge(*itrs.values(), stop_early=stop_early)
    for k, g in igroupby(s, lambda x: x[0]):
        r = {}
        for x in g:
            r[x[1]] = x[2]
        yield k, r

def imerge(*iterables, **kwargs):
    '''Merge multiple sorted inputs into a single sorted output.

    Equivalent to:  sorted(itertools.chain(*iterables))

    >>> list(imerge([1,3,5,7], [0,2,4,8], [5,10,15,20], [], [25]))
    [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]

    >>> list(imerge([1,3,5,7], [0,2,4,8], [5,10,15,20], [25], stop_early=True))
    [0, 1, 2, 3, 4, 5, 5, 7]

    >>> list(imerge([1,3,5,7], [], [5,10,15,20], [25], stop_early=True))
    []
    '''
    stop_early = kwargs.get('stop_early', False)
    heappop, siftup, _StopIteration = heapq.heappop, heapq._siftup, StopIteration

    h = []
    h_append = h.append
    for it in map(iter, iterables):
        try:
            next = it.next
            h_append([next(), next])
        except _StopIteration:
            if stop_early:
                return
    heapq.heapify(h)

    while 1:
        try:
            while 1:
                v, next = s = h[0]      # raises IndexError when h is empty
                yield v
                s[0] = next()           # raises StopIteration when exhausted
                siftup(h, 0)            # restore heap condition
        except _StopIteration:
            if stop_early:
                return
            heappop(h)                  # remove empty iterator
        except IndexError:
            return

def igroupby(stream, key_func):
    first = True
    k0 = None
    g = None
    for x in stream:
        k = key_func(x)
        if first or k!=k0:
            first = False
            if g:
                yield k0,g
            g = []
            k0 = k
        g.append(x)
    if g:
        yield k0,g


if __name__ == '__main__':
    import doctest
    doctest.testmod()


