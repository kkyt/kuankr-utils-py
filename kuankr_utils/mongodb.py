import re
import bson

#TODO: remove
"""
from kuankr_utils.json import register_encoder

@register_encoder(bson.ObjectId)
def encode_objectid(obj):
    return str(obj)
"""

OBJECTID_PATTERN = re.compile('[a-z0-9]{24}')

def find_by_id_or_name(col, id_or_name, where=None):
    if isinstance(id_or_name, bson.ObjectId) or OBJECTID_PATTERN.match(id_or_name):
        return col.find_one(id_or_name)
    else:
        w = {'name': id_or_name}
        if where:
            w.update(where)
        return col.find_one(w)


