import sys
import imp

from kuankr_utils import log, debug

def get_module(module):
    m = sys.modules.get(module)
    if m is None:
        #NOTE: __import__('a.b') returns module a
        __import__(module)
        m = sys.modules[module]
    return m

def import_from_code(code, module_name=None):
    if module_name is None:
        module_name = '_import_module_from_code_'
    mod = imp.new_module(module_name)
    exec code in mod.__dict__
    preserve_module(mod)
    return mod

def load_attribute(module_and_name, raise_exception=True):
    """Loads the module and returns the class.

    load_attribute('datetime.datetime')
    """
    try:
        a = module_and_name.rsplit('.', 1)
        if len(a)==2:
            module, name = a
        else:
            #return builtins directly, such as 'list', 'dict'
            if hasattr(__builtin__, a[0]):
                return getattr(__builtin__, a[0])

            module = a[0]
            name = None

        m = sys.modules.get(module)
        if m is not None:
            __import__(module)
            m = sys.modules[module]
        else:
            #NOTE: don't do reload, may cause
            #mod.A (old one stored somewhere) != mod.A (reloaded one)
            pass

        if name is not None:
            return getattr(m, name)
        else:
            return m

    except Exception, e:
        if raise_exception:
            raise
        log.error(e)
        return None

import sys
def preserve_module(mod):
    sys.modules[mod.__name__] = mod

