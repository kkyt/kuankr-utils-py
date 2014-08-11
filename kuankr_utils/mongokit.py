from __future__ import absolute_import

import re
import uuid
import copy
import bson
from datetime import datetime

from kuankr_utils import date_time
from kuankr_utils.mongodb import OBJECTID_PATTERN

from mongokit import Connection, Document

def register_models(db, *models):
    for model in models:
        db.connection.register(model)
        model.generate_index(db[model.__collection__])


class Doc(Document):
    '''
    NOTE: 
        x = Doc(d) didn't create default_values
        should use: x = Doc(); x.update(d);
    '''
    structure = {
        'updated_at': datetime,
        'created_at': datetime,
        'uuid': uuid.UUID,
    }
    default_values = {
        'uuid': uuid.uuid4,
        'created_at': date_time.now,
        'updated_at': date_time.now
    }
    required_fields = [ 'uuid', 'updated_at', 'created_at' ]

    def remove(self, query):
        self.collection.remove(query)

    def create(self, d):
        x = self()
        x.update(d)
        return x

    def put_by_id(self, id, doc):
        d = self.find_one(id)
        if d is None:
            doc['_id'] = id
            d = self.create(doc)
        else:
            d.update(doc)
        d.save()
        return d

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

    def find_by_id_or_name(self, id_or_name, where=None):
        if isinstance(id_or_name, bson.ObjectId) or OBJECTID_PATTERN.match(id_or_name):
            return self.find_one(id=id_or_name)
        else:
            w = {'name': id_or_name}
            if where:
                w.update(where)
            return self.find_one(**w)
    
    def remove_by_id_or_name(self, id_or_name, where=None):
        if isinstance(id_or_name, bson.ObjectId) or OBJECTID_PATTERN.match(id_or_name):
            w = {'_id': id_or_name}
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
            d = self.find_one(id=id_or_name)
            if d is None:
                doc['_id'] = id_or_name
                d = self.create(doc)
            else:
                d.update(doc)
        else:
            w = {'name': id_or_name}
            if where:
                w.update(where)
            d = self.find_one(**w)
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

        #NOTE: not working: `if not 'app' in self`
        if not self.get('app'):
            a = self['name'].split('.')
            self['app'] = '.'.join(a[:2])

        a = self['name'].split('.')
        assert len(a)>=3

        b = self['app'].split('.')
        assert len(b)==2

        assert a[0]==b[0] and a[1]==b[1]


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
            return self.find_one(id=id_or_name)
        else:
            w = {'name': id_or_name}
            if where:
                w.update(where)
            if api_client is not None:
                w['api_client'] = api_client
            return self.find_one(**w)
    

class DocService(object):
    def __init__(self, doc_class):
        self.doc_class = doc_class

    ## basic crud
    def create(self, doc):
        return self.doc_class.create(doc)

    def find(self, id):
        if hasattr(self.doc_class, 'find_by_id_or_name'):
            return self.doc_class.find_by_id_or_name(id)
        else:
            return self.doc_class.find_one(id)

    def put(self, id, doc):
        if hasattr(self.doc_class, 'put_by_id_or_name'):
            return self.doc_class.put_by_id_or_name(id, doc)
        else:
            return self.doc_class.put_by_id(id, doc)

    def update(self, id, doc):
        d = self.put(id, doc)
        return d

    def delete(self, id):
        d = self.find(id)
        d.remove()
        return d

class ApiClientDocService(object):
    def __init__(self, doc_class, api_client=None):
        self.doc_class = doc_class
        self._api_client = api_client

    @property
    def api_client(self):
        return self._api_client

    ## basic crud
    def create(self, doc):
        doc['api_client'] = self.api_client
        return self.doc_class.create(doc)

    def find(self, id):
        if hasattr(self.doc_class, 'find_by_id_or_name'):
            return self.doc_class.find_by_id_or_name(id, api_client=self.api_client)
        else:
            return self.doc_class.find_one(id)

