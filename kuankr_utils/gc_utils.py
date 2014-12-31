import operator
import sys
import random
import gc
from collections import defaultdict

import objgraph

def type_stats_count(objs=None):
    if objs is None:
        objs = gc.get_objects()
    stats = defaultdict(int)
    for o in objs:
        stats[type(o).__name__] += 1
    return stats

def type_stats_size(objs=None):
    if objs is None:
        objs = gc.get_objects()
    stats = defaultdict(int)
    for o in objs:
        stats[type(o).__name__] += sys.getsizeof(o)
    return stats

def sorted_stats(stats):
    return sorted(stats.items(), key=operator.itemgetter(1), reverse=True)

#s2-s1
def diff_stats(s1, s2):
    diff = defaultdict(int)
    for k,v in s2.iteritems():
        diff[k] = v - s1.get(k, 0)
    return diff

def show_backrefs_by_type(t):
    o = objgraph.by_type(t)
    if len(o)==0:
        return False
    obj = o[random.randint(0, len(o)-1)]
    objgraph.show_backrefs([obj], max_depth=10)
    return True


def show_backrefs(*args, **kwargs):
    objgraph.show_backrefs(*args, **kwargs)

