import os
import sys
import yaml

from . import template

def load_string(text, params=None):
    s = template.render_jinja2(text, params)
    return yaml.load(s)
    
def load_file(filename, params=None):
    f = open(filename, 'r')
    s = f.read()
    c = load_string(s, params)
    f.close()
    return c
    
def _name_to_key(filename):
    a = filename.split('/')
    a = a[-1].split('.')
    return '.'.join(a[:-1])

def load_dir(dirname, params=None, ext=None):
    d = {}
    if not os.path.isdir(dirname):
        return d
    for subitem in os.listdir(dirname):
        if subitem.startswith('.') or subitem.startswith('_') or subitem.endswith('~'):
            continue
        if ext is not None and not subitem.endswith(ext):
            continue
        subpath = os.path.join(dirname, subitem)
        if os.path.isdir(subpath):
            x = load_dir(subpath, params)
        else:
            x = load_file(subpath, params)
        d[_name_to_key(subitem)] = x
    return d

    
