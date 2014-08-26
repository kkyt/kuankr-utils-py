import os
import sys
import json
import yaml


def load_string(text):
    return yaml.load(text)
    
def load_file(filename):
    f = open(filename, 'r')
    s = f.read()
    c = load_string(s)
    f.close()
    return c
    
def _name_to_key(filename):
    a = filename.split('/')
    a = a[-1].split('.')
    return '.'.join(a[:-1])

def load_dir(dirname):
    d = {}
    for subitem in os.listdir(dirname):
        if subitem.startswith('.') or subitem.startswith('_'):
            continue
        subpath = os.path.join(dirname, subitem)
        if os.path.isdir(subpath):
            x = load_dir(subpath)
        else:
            x = load_file(subpath)
        d[_name_to_key(subitem)] = x
    return d

    
