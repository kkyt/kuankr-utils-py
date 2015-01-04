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
_enable_trace = True

def enable_trace():
    global _enable_trace
    _enable_trace = True

def disable_trace():
    global _enable_trace
    _enable_trace = False
    
def set_trace(level=0):
    if not _enable_trace:
        return
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

def setup_trace_handler():
    import signal, gevent, faulthandler
    import pudb

    from gevent import monkey
    monkey.patch_all()

    faulthandler.register(signal.SIGUSR1)

    def _interrupt_handler():
        pudb._get_debugger().set_trace()

    gevent.signal(signal.SIGUSR2, _interrupt_handler)

def setup_backdoor(port=None):
    from . import log
    import gevent
    from gevent.backdoor import BackdoorServer
    if port is None:
        port = os.environ.get('BACKDOOR_PORT')
    if not port:
        return
    port = int(port)
    server = BackdoorServer(('localhost', port))
    log.info('spawn backdoor server at port: %s, use telnet to access it' % port)
    gevent.spawn(server.serve_forever)

