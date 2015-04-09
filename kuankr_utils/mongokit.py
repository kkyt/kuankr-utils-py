from __future__ import absolute_import

import re
import six
import uuid
import copy
import bson
from datetime import datetime

from kuankr_utils import log, debug, date_time
from kuankr_utils.mongodb import OBJECTID_PATTERN

from mongokit import Connection, Document, OR

numeric = OR(float, int, long)
string_or_dict = OR(basestring, unicode, dict)

def register_models(db, *models):
    for model in models:
        db.connection.register(model)
        model.generate_index(db[model.__collection__])

def to_object_id(id):
    if id is None:
        return id
    if not isinstance(id, bson.ObjectId):
        try:
            id = bson.ObjectId(id)
        except:
            id = None
    return id
        
class HasUUID(Document):
    structure = {
        'uuid': uuid.UUID,
    }
    default_values = {
        'uuid': uuid.uuid4,
    }
    required_fields = [ 'uuid' ]

class HasTimestamp(Document):
    structure = {
        'updated_at': datetime,
        'created_at': datetime,
    }
    default_values = {
        'created_at': date_time.now,
        'updated_at': date_time.now
    }
    required_fields = [ 'updated_at', 'created_at' ]

class DocBase(Document):
    '''
    NOTE: 
        x = Doc(d) didn't create default_values
        should use: x = Doc(); x.update(d);
    '''

    protected_fields = ['id', '_id']

    #will be the default in future mongokit release
    use_schemaless = True

    def after_create(self):
        return

    def before_save(self):
        return

    def auto_convert(self):
        #NOTE: auto convert iso string to datetime
        for k, v in self.structure.items():
            if v==datetime:
                x = self.get(k)
                if isinstance(x, six.string_types):
                    self[k] = date_time.to_datetime(x)

    def remove(self, query):
        self.collection.remove(query)

    def remove_by_id(self, id):
        return self.remove({'_id': to_object_id(id)})

    def get_field(self, id, field, default=None):
        r = self.collection.find_one({'_id': to_object_id(id)})
        if r is None:
            return None
        else:
            return r.get(field, default)

    def set_field(self, id, field, value):
        self.collection.update(
            {'_id': to_object_id(id)}, 
            {'$set': {field: value}}
        )

    def inc_field(self, id, field, change):
        self.collection.update(
            {'_id': to_object_id(id)}, 
            {'$inc': {field: change}}
        )
    
    def create(self, d):
        #NOTE: Model() doesn't work
        x = self()
        if d is None:
            d = {}
        else:
            d = dict(d)
        for f in self.protected_fields:
            if f in d:
                del d[f]
        x.update(d)
        x.after_create()
        return x

    def save(self):
        self.before_save()
        return super(DocBase, self).save()

    def put_by_id(self, id, doc):
        id = to_object_id(id)
        d = self.find_by_id(id)
        if d is None:
            doc['_id'] = id
            d = self.create(doc)
        else:
            d.update(doc)
        d.save()
        return d

    def find_by_id(self, id, where=None):
        id = to_object_id(id)
        if id is None:
            return None
        w = {'_id': id}
        if where:
            w.update(where)
        return self.find_one(w)

    def as_json(self):
        d = dict(self)
        if '_id' in d:
            d['id'] = d['_id']
            del d['_id']
        return d
        
class DocWithoutUUID(DocBase, HasTimestamp):
    #for create cleanup
    protected_fields = ['updated_at', 'created_at', 'id', '_id']

class DocWithUUID(DocBase, HasTimestamp, HasUUID):
    protected_fields = ['updated_at', 'created_at', 'uuid', 'id', '_id']

Doc = DocWithoutUUID

class HasName(Document):
    structure = {
        'name': basestring,
    }
    required_fields = [
        'name'
    ]
    indexes = [{
        'fields': 'name',
        'unique': True
    }]

    def find_by_name(self, name, where=None):
        w = {'name': name}
        if where:
            w.update(where)
        return self.find_one(w)

    def find_by_id_or_name(self, id_or_name, where=None):
        if isinstance(id_or_name, bson.ObjectId) or OBJECTID_PATTERN.match(id_or_name):
            return self.find_by_id(id_or_name)
        else:
            return self.find_by_name(id_or_name, where=where)
    
    def remove_by_id_or_name(self, id_or_name, where=None):
        if isinstance(id_or_name, bson.ObjectId) or OBJECTID_PATTERN.match(id_or_name):
            id = to_object_id(id_or_name)
            w = {'_id': id}
        else:
            w = {'name': id_or_name}
        if where:
            w.update(where)
        self.collection.remove(w)

    def update_by_id_or_name(self, id_or_name, doc, where=None):
        r = self.find_by_id_or_name(id_or_name, where)
        if r is not None:
            r.update(doc)
            r.save()
        return r
        
    def put_by_id_or_name(self, id_or_name, doc, where=None):
        if isinstance(id_or_name, bson.ObjectId) or OBJECTID_PATTERN.match(id_or_name):
            id = to_object_id(id_or_name)
            d = self.find_by_id(id)
            if d is None:
                doc['_id'] = id
                d = self.create(doc)
            else:
                d.update(doc)
        else:
            w = {'name': id_or_name}
            if where:
                w.update(where)
            d = self.find_one(w)
            if d is None:
                d = self.create(doc)
                d['name'] = id_or_name
                if where:
                    d.update(where)
            else:
                d.update(doc)
        d.save()
        return d

class HasApp(Document):
    structure = {
        'app': basestring,
    }
    default_values = {
    }
    required_fields = [
    ]
    indexes = [{
        'fields': 'app'
    }]

    def validate(self, *args, **kwargs):
        super(HasApp, self).validate(*args, **kwargs)
        name = self['name']

        a = name.split('.')
        if len(a)<3:
            raise Exception('component name must be of user.app.component format, got %s' % name)

        #NOTE: not working: `if not 'app' in self`
        app = self.get('app')
        if not app:
            app = self['app'] = '.'.join(a[:2])

        b = app.split('.')
        if len(b)!=2:
            raise Exception('app name must be of user.app format, got %s' % app)

        if a[0]!=b[0] or a[1]!=b[1]:
            raise Exception('app name donot match component name: %s %s' % (app, name))

class HasTitleDesc(Document):
    structure = {
        'title': basestring,
        'description': basestring,
    }
    required_fields = [
        #don't require title
        #'title'
    ]

class HasTemplate(Document):
    structure = {
        'template': basestring,
        'options': dict,
    }
    required_fields = [
    ]

class HasCodeObject(Document):
    '''
        object: {
            'class': basestring,
            'module': basestring,
            'name': basestring,
            'arguments': list,
            'options': dict,
            'source_code': basestring,
        }
    '''
    structure = {
        'object': dict,
        'language': basestring,
        'runtime': basestring,
    }
    default_values = {
        'language': 'python',
        'runtime': 'CPython2.7',
    }
    required_fields = [
        #'object.class',
        #'object.module'
    ]
    indexes = [{
        'fields': 'language'
    }, {
        'fields': 'runtime'
    }]
    
    def create_object(self, options=None):
        from .json_obj import decode_from_config

        obj = copy.deepcopy(self['object'])
        if options and 'options' in obj:
            obj['options'].update(options)

        return decode_from_config(obj)

class HasApiClient(Document):
    structure = {
        'api_client': basestring,
    }
    required_fields = [
        'api_client'
    ]
    indexes = [{
        'fields': 'api_client',
    }]

class HasApiClientName(Document):
    structure = {
        'api_client': basestring,
        'name': basestring,
    }
    required_fields = [
        'api_client',
        'name'
    ]
    indexes = [{
        'fields': ['api_client', 'name'],
        'unique': True
    }]

    def find_by_id_or_name(self, id_or_name, api_client=None, where=None):
        if isinstance(id_or_name, bson.ObjectId) or OBJECTID_PATTERN.match(id_or_name):
            return self.find_by_id(id_or_name)
        else:
            w = {'name': id_or_name}
            if where:
                w.update(where)
            if api_client is not None:
                w['api_client'] = api_client
            return self.find_one(w)
    
class BaseService(object):
    def __init__(self, Model):
        self.Model = Model

    def create(self, d):
        e = self.Model.create(d)
        e.save()
        return e

    def get(self, id):
        if hasattr(self.Model, 'find_by_id_or_name'):
            return self.Model.find_by_id_or_name(id)
        else:
            return self.Model.find_by_id(id)

    def find_by_name(self, name):
        return self.Model.find_by_name(name)

    def find_by_id(self, id):
        return self.Model.find_by_id(id)

    #TODO: remove
    def info(self, id):
        log.error('TODO: remove')
        return self.get(id)

    def find_all(self, where=None):
        return self.Model.find(where)

    def put(self, id, doc):
        if hasattr(self.Model, 'put_by_id_or_name'):
            return self.Model.put_by_id_or_name(id, doc)
        else:
            return self.Model.put_by_id(id, doc)

    def update(self, id, doc):
        d = self.find_by_id(id)
        d.update(doc)
        d.save()
        return d

    def remove(self, id):
        id = to_object_id(id)
        return self.Model.remove({'_id': id})

    def _get_where(self, **kwargs):
        w = {}
        for k,v in kwargs.items():
            if v is not None:
                w[k] = v
        return w

    def list(self, order=None, **conditions):
        w = self._get_where(**conditions)
        r = self.Model.find(w)
        if order is not None:
            r = r.sort(order)
        return r

    def remove_all_batch(self, **conditions):
        w = self._get_where(**conditions)
        return self.Model.remove(w)

    def remove_all(self, **conditions):
        w = self._get_where(**conditions)
        r = self.Model.find(w)
        n = 0
        for x in r:
            n += 1
            #inherited may override remove
            self.remove(x['_id'])
        return n
        
class ServiceWithName(BaseService):
    def remove(self, id_or_name):
        return self.Model.remove_by_id_or_name(id_or_name)

    def put(self, id_or_name, d):
        e = self.Model.put_by_id_or_name(id_or_name, d)
        return e

    def get(self, id_or_name):
        return self.Model.find_by_id_or_name(id_or_name)

    def update(self, id_or_name, d):
        e = self.Model.update_by_id_or_name(id_or_name, d)
        return e

class ServiceWithAppName(ServiceWithName):
    pass
            
class ServiceWithApiClient(object):
    def __init__(self, Model, api_client=None):
        self.Model = Model
        self._api_client = api_client

    @property
    def api_client(self):
        return self._api_client

    ## basic crud
    def create(self, doc):
        doc['api_client'] = self.api_client
        return self.Model.create(doc)

    def get(self, id):
        if hasattr(self.Model, 'find_by_id_or_name'):
            return self.Model.find_by_id_or_name(id, api_client=self.api_client)
        else:
            return self.Model.find_by_id(id)


