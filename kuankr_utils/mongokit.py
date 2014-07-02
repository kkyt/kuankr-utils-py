from __future__ import absolute_import

import re
import uuid
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
    structure = {
        'updated_at': datetime,
        'uuid': uuid.UUID,
    }
    default_values = {
        'uuid': uuid.uuid4,
        'updated_at': date_time.now
    }
    required_fields = [ 'uuid', 'updated_at' ]

    def remove(self, query):
        self.collection.remove(query)

    @classmethod
    def create(cls, d):
        x = cls()
        x.update(d)
        return x

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
    
class HasApiClient(Document):
    structure = {
        'api_client': basestring,
    }
    required_fields = [
        'api_client'
    ]

