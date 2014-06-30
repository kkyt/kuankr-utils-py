from pyutils import log, debug, type_utils
from pyutils import multi_json as json

def dumps(x, pretty=True):
    if isinstance(x, type_utils.string_types):
        return x
    elif type_utils.is_generator(x):
        #non-pretty dump for stream
        return (dumps(r, pretty=False) for r in x)
    else:
        if pretty:
            return json.pretty_dumps(x)
        else:
            #add line end
            return json.dumps(x) + '\n'

def loads(x):
    if type_utils.is_generator(x):
        return (json.loads(r) for r in x)
    else:
        return json.loads(x)
