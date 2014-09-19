#coding: utf8
from __future__ import absolute_import

import os
import types
import requests

from kuankr_utils import api_json
from kuankr_utils import log, debug, dicts

from .requests import response_hook, HTTPStreamAdapter
from .http_debug import headers_line, stream_with_echo

class Resource(object):
    def __init__(self, client, path):
        self.client = client
        self.path = path

    def __getattr__(self, method):
        pass

class HttpClient(object):
    def __init__(self, base, headers=None, options=None, async_send=False):
        self.base = base
        self.options = options or {}

        h = {'content-type': 'application/json'}
        dicts.reverse_update(headers, h)

        self.session = ses = requests.Session()
        self.set_headers(headers)
        ses.hooks.update(response=response_hook)
        if async_send:
            #NOTE: must patch_all, otherwise it will hangs
            from gevent import monkey; monkey.patch_all()
            ses.mount('http://', HTTPStreamAdapter())
            #TODO https

    def http(self, method, path, data=None, params=None, stream=False, **kwargs):
        #NOTE: stream is for response body, not for request body
        log.info('%s %s %s' % (method.upper(), self.base+path, headers_line(params)))
        log.debug('%s' % headers_line(self.session.headers))

        stream_debug = os.environ.get('KUANKR_API_STREAM_DEBUG')=='1'

        if data is None:
            log.debug('\nnull')
        else:
            data = api_json.dumps(data)

            if isinstance(data, types.GeneratorType):
                #TODO
                #requests send wrong chunk size for unicoode
                data = (x.encode('utf8') if isinstance(x, unicode) else x for x in data)

                if stream_debug:
                    data = stream_with_echo(data)
                else:
                    log.debug('\n<stream>')
            else:
                #TODO
                #gevent socket cannot send unicode
                if isinstance(data, unicode):
                   data = data.encode('utf8')

                log.debug('\n%s' % data)

        m = getattr(self.session, method)
        r = m(self.base+path, data=data, params=params, stream=stream, **kwargs)
        log.debug('%s' % headers_line(r.headers))
        if stream:
            def g():
                #NOTE:
                #work before response_hook
                #for x in r.iter_lines(chunk_size=1):

                #work after response_hook
                chunks = r.iter_chunks()
                if stream_debug:
                    chunks = stream_with_echo(chunks)
                for x in chunks:
                    yield api_json.loads(x)
            r.raise_for_status()
            if not stream_debug:
                log.debug('\n<stream>')
            return g()
        else:
            s = r.content
            log.debug('\n%s' % s)
            r.raise_for_status()
            return r.json()

    def set_headers(self, headers):
        if headers:
            self.session.headers.update(headers)

    def get(self, path, params=None, **kwargs):
        #TODO: params
        return self.http('get', path, **kwargs)

    def delete(self, path, params, **kwargs):
        #TODO: params
        return self.http('delete', path, **kwargs)

    def post(self, path, data, **kwargs):
        return self.http('post', path, data, **kwargs)

    def patch(self, path, data):
        return self.http('patch', path, data, **kwargs)

    def put(self, path, data):
        return self.http('put', path, data, **kwargs)

