from __future__ import absolute_import

import six
import types

from kuankr_utils import json

def dumps(x, pretty=True):
    #returns string as it is
    if isinstance(x, six.string_types):
        return x
    elif isinstance(x, types.GeneratorType):
        #non-pretty dump for stream
        #NOTE: don't add line end here
        return (dumps(r, pretty=False) for r in x)
    else:
        if pretty:
            return json.dumps(x, pretty=True)
        else:
            #NOTE: add line end here
            return json.dumps(x) + '\n'

def loads(x):
    if isinstance(x, types.GeneratorType):
        return (json.loads(r) for r in x)
    else:
        return json.loads(x)
