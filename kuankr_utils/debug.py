import sys
import os
import traceback

import py.code

try:
    import pudb as pdb
except:
    import pdb

__all__ = [
    'set_trace', 'set_trace_',
    'in_debug',
    'pretty_traceback',
    'simple_traceback',
    'set_trace'
]

in_debug = False

def set_trace(level=0):
    global in_debug
    in_debug = True
    pdb.set_trace()

def _empty():
    pass

set_trace_ = _empty

def simple_traceback(e=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    b = traceback.format_tb(exc_traceback)
    return '\n'.join(b)

def pretty_traceback(showlocals=True, style='long', funcargs=True):
    excinfo = py.code.ExceptionInfo()
    info = excinfo.getrepr(funcargs=funcargs, showlocals=showlocals, style=style)
    return str(info)

