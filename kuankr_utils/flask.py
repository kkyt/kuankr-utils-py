from __future__ import absolute_import

import os
import types

from flask import Flask, Blueprint, Response
from flask import request, abort, stream_with_context
from werkzeug.exceptions import default_exceptions, HTTPException, NotFound

from kuankr_utils import debug
from kuankr_utils.logstash import log as logstash_log

from kuankr_utils import api_json

from flask.ext.api import status

from .http import HTTP_400_BAD_REQUEST

class JsonResponse(Response):
    default_mimetype = 'application/json'

class APIMixin(object):
    def get(self, rule, **options):
        options['methods'] = ['GET']
        return self.route(rule, **options)

    def post(self, rule, **options):
        options['methods'] = ['POST']
        return self.route(rule, **options)

    def put(self, rule, **options):
        options['methods'] = ['PUT']
        return self.route(rule, **options)

    def put_or_patch(self, rule, **options):
        options['methods'] = ['PUT', 'PATCH']
        return self.route(rule, **options)

    def patch(self, rule, **options):
        options['methods'] = ['PATCH']
        return self.route(rule, **options)

    def delete(self, rule, **options):
        options['methods'] = ['DELETE']
        return self.route(rule, **options)

class APIBlueprint(Blueprint, APIMixin):
    pass

class API(Flask, APIMixin):
    response_class = JsonResponse

    def __init__(self, *args, **kwargs):
        super(API, self).__init__(*args, **kwargs)

        for code in default_exceptions.iterkeys():
            self.error_handler_spec[None][code] = self.make_json_error

    def make_json_error(self, ex):
        if isinstance(ex, HTTPException):
            status_code = ex.code
            id = ex.name
            msg = ex.description
        else:
            status_code = 500
            id = 'Internal Server Error'
            msg = str(ex)
        r = {
            'id': id,
            'status': status_code,
            'error': msg,
        }
        return self.make_response((r, status_code))

    def convert_response(self, x):
        if isinstance(x, (dict,list)):
            x = api_json.dumps(x)
        elif isinstance(x, types.GeneratorType):
            x = stream_with_context(x)
            x = api_json.dumps(x)
            x = self.response_class(x)
        return x

    def make_response(self, rv):
        if rv is None:
            if request.method == 'GET':
                return self.make_json_error(NotFound())
            else:
                rv = {}
                
        if isinstance(rv, tuple):
            rv = list(rv)
            rv[0] = self.convert_response(rv[0])
            rv = tuple(rv)
        else:
            rv = self.convert_response(rv)
        r = super(API, self).make_response(rv)

        if os.environ.get('WSGI_DEBUG_LOGGER')=='1':
            #TODO
            rec = {
                'request': request.data,
                'response': r
            }
            logstash_log.info('api_call', extra=rec)
            print request.data
            print r

        return r

    def handle_exception(self, exc_info):
        print debug.pretty_traceback()
        return super(API, self).handle_exception(exc_info)
        
def request_json_body():
    return request.get_json(force=True, silent=True)
    #return api_json.loads(request.data)

def ensure_header(x):
    r = request.headers.get(x)
    if not r:
        abort(HTTP_400_BAD_REQUEST, '%s header is missing' % x)
    return r

def get_api_client():
    return ensure_header('X-Api-Client')

def get_api_token():
    return ensure_header('X-Api-Token')

