from __future__ import absolute_import

import os
import types
from datetime import datetime
import json

from flask import Flask, Blueprint, Response
from flask import request, abort, stream_with_context
from werkzeug.exceptions import default_exceptions, HTTPException, NotFound

from kuankr_utils import log, debug
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

base_api = APIBlueprint('base_api', __name__)

@base_api.get('/_ping')
def ping():
    return { 
        'status': 'ok', 
        'message': 'pong', 
        'time': datetime.now()
    }

@base_api.get('/_schema')
def schema():
    schema = os.environ.get("KUANKR_SCHEMA")
    if schema:
        f = open(schema)
        schema = json.loads(f.read())
        f.close()
    return schema


@base_api.get('/_test/error')
def error():
    raise Exception(request.data)

def headers_line(headers):
    return ' '.join(map(lambda a: '%s=%s' % a, headers.items()))

def request_line(req):
    return req.method + ' ' + req.url + '\n' + headers_line(req.headers)
    
def response_line(resp):
    return headers_line(resp.headers)

class API(Flask, APIMixin):
    response_class = JsonResponse

    def __init__(self, *args, **kwargs):
        super(API, self).__init__(*args, **kwargs)

        for code in default_exceptions.iterkeys():
            self.error_handler_spec[None][code] = self.make_json_error

        self.sentry = setup_sentry(self)

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
        if x is None or isinstance(x, (dict,list)):
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
                
        if isinstance(rv, tuple):
            rv = list(rv)
            rv[0] = self.convert_response(rv[0])
            rv = tuple(rv)
        else:
            rv = self.convert_response(rv)
        r = super(API, self).make_response(rv)

        if os.environ.get('WSGI_DEBUG_LOGGER') != '0':
            #TODO chunked encoding
            if request.headers.get('transfer_encoding') != 'chunked':
                req = request.data
            else:
                req = '<stream>'

            if not r.is_streamed:
                resp = ''.join(r.response)
            else:
                resp = '<stream>'

            rec = {
                'request': req,
                'response': resp
            }
            logstash_log.info('api_call', extra=rec)
            log.debug('api_request\n' + request_line(request)+'\n'+req)
            log.info('api_response\n' + response_line(r)+'\n'+resp)

        return r

    def handle_exception(self, exc_info):
        print debug.pretty_traceback()
        return super(API, self).handle_exception(exc_info)
        

def setup_sentry(app):
    from raven.contrib.flask import Sentry
    from kuankr_utils import sentry
    dsn = os.environ.get('SENTRY_DSN')
    if not dsn:
        return None
    app.config['SENTRY_DSN'] = dsn
    client = Sentry(app)
    sentry.set_client(client)
    return client

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

