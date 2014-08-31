from __future__ import absolute_import
import os

from mongokit import Connection, Document

from kuankr_utils.mongokit import Doc, HasName, register_models, BaseService

MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://127.0.0.1:27017/test_kuankr_utils_py')

CONN = Connection(MONGODB_URI, tz_aware=True)
DB = CONN.get_default_database()

class A(Doc, HasName):
    __collection__ = 'a'
    structure = {
        'a': basestring
    }

register_models(DB, A)
sa = BaseService(DB.A)

def setup_module():
    pass
    

def test_crud():
    sa.remove_all()
    assert list(sa.find_all()) == []

    u = sa.create({'a': 'xxx', 'name': 'test1'})
    #NOTE: u!=x since mongodb don't support microseconds
    #assert x==u

    x = sa.get(u['_id'])
    y = sa.get('test1')
    z = sa.get(str(u['_id']))
    assert x==y 
    assert x==z

