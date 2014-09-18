from __future__ import absolute_import

import bson
import re
import urlparse
import urllib
from datetime import datetime

from bson import json_util
from mongoengine import signals
from mongoengine.fields import StringField, DateTimeField
from mongoengine.base import BaseDocument
from mongoengine.queryset.base import BaseQuerySet

from kuankr_utils import log, debug
from pyutils.serializers import simple_json

from .flask import get_api_client

def as_json(obj):
    if isinstance(obj, BaseDocument):
        return simple_json.encode(obj.to_mongo())
    elif isinstance(obj, BaseQuerySet):
        #TODO
        #return simple_json.encode(list(obj.as_pymongo()))
        return as_json(list(obj.as_pymongo()))
    #TODO: more general
    elif isinstance(obj, list):
        return [as_json(x) for x in obj]
    else:
        return simple_json.encode(obj)

def as_api_json(obj):        
    if isinstance(obj, list):
        return [as_api_json(x) for x in obj]

    elif isinstance(obj, BaseDocument):
        return as_api_json(obj.to_mongo())

    elif isinstance(obj, BaseQuerySet):
        return as_api_json(list(obj.as_pymongo()))

    elif isinstance(obj, dict):
        if '_id' in obj:
            obj['id'] = str(obj['_id'])
            del obj['_id']
    return obj

OBJECT_ID_PATTERN = re.compile('[a-z0-9]{24}')

def find_by_id_or_name(model, id_or_name, where=None):
    if isinstance(id_or_name, bson.ObjectId) or OBJECT_ID_PATTERN.match(id_or_name):
        return model.objects(id=id_or_name).first()
    else:
        w = {'name': id_or_name}
        if where:
            w.update(where)
        return model.objects(**w).first()

#NOTE: cannot change `document` var name
def update_timestamp(sender, document, **kwargs):
    if document.created_at is None:
        document.created_at = datetime.now()
    document.updated_at = datetime.now()

def update_app_name(sender, document, **kwargs):
    a = document.name.split('.')
    document.app = '.'.join(a[:2])

def add_index(Doc, *fields, **kwargs):
    if not hasattr(Doc, 'meta'):
        Doc.meta = {}

    if not 'indexes' in Doc.meta:
        Doc.meta['indexes'] = []

    idx = { 'fields': fields }
    idx.update(**kwargs)
    Doc.meta['indexes'].append(idx)

def is_kuankr_api_doc(Doc):
    Doc.as_json = as_api_json

def has_timestamp(Doc):
    #TODO
    #Doc.created_at = DateTimeField(required=True)
    #Doc.updated_at = DateTimeField(required=True)
    signals.pre_save.connect(update_timestamp, sender=Doc)

def with_api_client(cls, api_client=None, **where):
    if api_client is None:
        api_client = get_api_client()
    w = {
        'api_client': api_client
    }
    w.update(where)
    r = cls.objects(**w)
    return r

def has_api_client(Doc):
    #TODO
    #Doc.api_client = StringField(required=True)
    Doc.with_api_client = classmethod(with_api_client)
    #add_index(Doc, 'api_client')

def has_app(Doc):
    #TODO
    #Doc.app = StringField(required=True)
    #add_index(Doc, 'app')
    signals.pre_save.connect(update_app_name, sender=Doc)

def has_name(Doc, unique_by=None):
    #TODO
    #Doc.name = StringField(required=True)
    if unique_by is not None:
        idx = {
            'fields': (unique_by, 'name'),
            'unique': True
        }
    else:
        idx = {
            'fields': ('name',),
            'unique': True
        }
    #add_index(Doc, **idx)
    Doc.find_by_id_or_name = classmethod(find_by_id_or_name)

def configure(api, uri=None):
    if uri is None:
        uri = 'mongodb://127.0.0.1'
    uri = urlparse.urlparse(uri)

    username = uri.username
    if username:
        username = urllib.unquote(username)

    password = uri.password
    if password:
        password = urllib.unquote(password)

    api.config['MONGODB_SETTINGS'] = {
        'DB': uri.path[1:], 
        'USERNAME' : username, 
        'PASSWORD' : password,
        'HOST' : uri.hostname or '127.0.0.1',
        'PORT': uri.port or 27017 
    }

