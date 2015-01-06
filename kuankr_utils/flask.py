from __future__ import absolute_import

import os
import types
from datetime import datetime
from cStringIO import StringIO

from flask import Flask, Blueprint, Response
from flask import request, abort, stream_with_context
from werkzeug.exceptions import default_exceptions, HTTPException, NotFound

from kuankr_utils import log, debug, json, http_debug, logstash

from kuankr_utils import api_json

from flask.ext.api import status

from .http import HTTP_400_BAD_REQUEST
from .http_debug import response_line, request_line, HTTP_SERVER_DEBUG

class JsonResponse(Response):
    default_mimetype = 'application/json'

class JsonStreamResponse(Response):
    default_mimetype = 'application/stream+json'
    #default_mimetype = 'text/plain'

def jsonify(x):
    return JsonResponse(json.dumps(x))

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

class APPBlueprint(Blueprint, APIMixin):
    pass

class APIBlueprint(APPBlueprint):
    pass

base_api = APIBlueprint('base_api', __name__)

@base_api.get('/_home')
def home():
    return Response('''
        <html>
        <a href="_ping">ping</a>
        <a href="_schema">schema</a>
        <a href="_inspect">inspect</a>
        <a href="/_dozer/index">memory</a>
        </html>
        ''')

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

@base_api.get('/_inspect')
def inspect():
    return {}

@base_api.get('/_test/error')
def error():
    raise Exception(request.data)

class APP(Flask, APIMixin):
    def __init__(self, *args, **kwargs):
        super(APP, self).__init__(*args, **kwargs)
        self.sentry = setup_sentry(self)

    def convert_response(self, x):
        if x is None or isinstance(x, (dict,list)):
            x = api_json.dumps(x)

        elif isinstance(x, types.GeneratorType):
            x = stream_with_context(x)
            x = api_json.dumps(x)

            #NOTE: use custom response class
            #x = self.response_class(x)
            x = JsonStreamResponse(x)
        return x

    def preprocess_request(self):
        if HTTP_SERVER_DEBUG:
            try:
                if request.headers.get('Transfer-Encoding') != 'chunked':
                    req = request.data
                    #NOTE: only needed when chunked is convert to normal request by proxy
                    request.environ['wsgi.input'] = StringIO(req)
                else:
                    req = '<stream>'
                log.debug('API_REQUEST\n' + request_line(request)+'\n'+req)
            except:
                pass
        return super(APP, self).preprocess_request()

    def make_response(self, rv):
        if isinstance(rv, tuple):
            rv = list(rv)
            rv[0] = self.convert_response(rv[0])
            rv = tuple(rv)
        else:
            rv = self.convert_response(rv)
        r = super(APP, self).make_response(rv)
        return r

    def handle_exception(self, exc_info):
        print debug.pretty_traceback()
        return super(APP, self).handle_exception(exc_info)
        
class API(APP):
    response_class = JsonResponse

    def __init__(self, *args, **kwargs):
        super(API, self).__init__(*args, **kwargs)

        for code in default_exceptions.iterkeys():
            self.error_handler_spec[None][code] = self.make_json_error

    def make_json_error(self, ex):
        #HTTPException
        if hasattr(ex, 'code'):
            status_code = ex.code
        else:
            status_code = 500

        id = ex.__class__.__name__

        if hasattr(ex, 'description'):
            msg = '%s: %s' % (id, ex.description)
        else:
            msg = '%s: %s' % (id, ex)

        r = {
            'id': id,
            'status': status_code,
            'error': msg,
        }
        return self.make_response((r, status_code))

    def make_response(self, rv):
        if rv is None:
            if request.method == 'GET':
                return self.make_json_error(NotFound())
        r = super(API, self).make_response(rv)
        if HTTP_SERVER_DEBUG:
            try:
                if not r.is_streamed:
                    resp = ''.join(r.response)
                else:
                    resp = '<stream>'

                #rec = { 'request': req, 'response': resp }
                #logstash.log.info('api_call', extra=rec)
                log.info('API_RESPONSE\n' + response_line(r)+'\n'+resp)
            except:
                pass
        return r
                

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

def response_stream(stream):
    if http_debug.HTTP_STREAM_DEBUG:
        stream = log.stream_with_echo(stream, prefix='<-- ')
    return stream

def request_stream(json=False):
    stream = request.input_stream
    #input = stream_with_context(input)
    if http_debug.HTTP_STREAM_DEBUG:
        stream = log.stream_with_echo(stream, prefix='--> ')
    if json:
        from kuankr_utils.json import loads
        stream = (loads(x) for x in stream)
    return stream

def ensure_header(x):
    r = request.headers.get(x)
    if not r:
        abort(HTTP_400_BAD_REQUEST, '%s header is missing' % x)
    return r

def get_api_client():
    return ensure_header('X-Api-Client')

def get_api_token():
    return ensure_header('X-Api-Token')

