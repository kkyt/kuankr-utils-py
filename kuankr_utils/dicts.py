from __future__ import absolute_import

def reverse_update(d1, d2):
    for k,v in d2.iteritems():
        if not k in d1:
            d1[k] = v
    return d1

set_default = reverse_update

def extend(base, ext):
    for k,v in ext.iteritems():
        base[k] = v
    return base

def sub_dict(d, keys):
    if not d:
        return d
    return dict((k,d[k]) for k in keys if k in d)

def recursive_merge(base, ext):
    if base is None:
        base = {}
    if not ext:
        return base
    for k,v in ext.items():
        if isinstance(v, dict):
            if not k in base or not isinstance(base[k], dict):
                base[k] = v
            else:
                recursive_merge(base[k], v)
        else:
            base[k] = v
    return base

def recursive_merge_multi(base, *exts):
    for ext in exts:
        base = recursive_merge(base, ext)
    return base

recursive_extend = recursive_merge
recursive_extend_multi = recursive_merge_multi

def cleanup_dict(d, value=None):
    for k in d.keys():
        if d[k]==value:
            del d[k]
    return d

