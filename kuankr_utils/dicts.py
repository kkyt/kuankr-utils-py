from __future__ import absolute_import

def reverse_update(d1, d2, none_as_missing=False):
    for k,v in d2.iteritems():
        if not k in d1 or none_as_missing and d1[k] is None:
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

#process dict/list
def recursive_merge_with_list(base, ext):
    if ext is None:
        return base
        
    if base is None:
        return ext
        
    if isinstance(base, dict):
        if isinstance(ext, dict):
            for k in ext:
                base[k] = recursive_merge_with_list(base.get(k), ext[k])
            return base
        else:
            return ext

    elif isinstance(base, list):
        if isinstance(ext, list):
            while len(base) < len(ext):
                base.append(None)
            for i in range(len(ext)):
                base[i] = recursive_merge_with_list(base[i], ext[i])
            return base
        else:
            return ext
        
    else:
        return ext

def cleanup_dict(d, value=None):
    for k in d.keys():
        if d[k]==value:
            del d[k]
    return d

def default_get_multi(key, default, *args):
    for d in args:
        if d and key in d:
            return d[key]
    return default

