import inflection
import six

def str_abbr(s, maxlen=128, concat='...'):
    if not isinstance(s, basestring):
        s = str(s)
    if len(s)>maxlen:
        n = maxlen/2
        return s[:n] + concat + s[-n:]
    else:
        return s

def to_unicode(s, encoding='utf8'):
    if isinstance(s, str):
        s = s.decode(encoding)
    elif not isinstance(s, unicode):
        s = unicode(s)
    return s

def try_to_unicode(s, encoding='utf8'):
    try:
        return to_unicode(s, encoding)
    except:
        return s

def recursive_substitute(obj, params, f=None):
    if is isinstance(obj, six.string_types):
        if f is None:
            return obj % params
        else:
            return f(obj, params)

    elif isinstance(obj, (list,tuple)):
        return [recursive_substitute(x, params, f) for x in obj]

    elif isinstance(obj, dict):
        r = {}
        for k,v in obj.iteritems():
            k = recursive_substitute(k, params, f)
            r[k] = recursive_substitute(v, params, f)
        return r

    else:
        return obj

#https://pypi.python.org/pypi/inflect
def pluralize(s, special=None):
    if special is not None and s in special:
        return special[s]
    if not s.endswith('s'):
        return s + 's'
    else:
        return s

def singularize(s, special=None):
    if special is not None and s in special:
        return special[s]
    if s.endswith('s'):
        return s[:-1]
    else:
        return s

def dashed(s):
    return s.replace('_', '-')

def underscored(s):
    return s.replace('-', '_')

def spaced(s):
    return s.replace('-', ' ').replace('_', ' ')

def camel_to_underscore(s):
    return inflection.underscore(s)
    
    

