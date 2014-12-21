#coding: utf8
from __future__ import absolute_import

import os
import types
import requests

from kuankr_utils import log, debug, dicts

from .requests import response_hook, HTTPStreamAdapter
from .http_debug import headers_line, stream_with_echo, HTTP_CLIENT_DEBUG, HTTP_STREAM_DEBUG
from .serializer import get_serializer


#NOTE: remove urllib3 log
#http://stackoverflow.com/questions/16337511/log-all-requests-from-the-python-requests-module
import logging
urllib3_logger = logging.getLogger('requests.packages.urllib3')
urllib3_logger.setLevel(logging.CRITICAL)

class Resource(object):
    def __init__(self, client, path):
        self.client = client
        self.path = path

    def __getattr__(self, method):
        pass

class HttpClient(object):
    def get_serializer(self, content_type):
        s = self.serializer_cache.get(content_type)
        if s is None:
            d = {
                'application/json': 'api_json',
                'application/msgpack': 'msgpack',
                'application/octet-stream': 'raw'
            }
            t = d.get(content_type)
            if t is None:
                raise Exception('unkown content type: %s' % content_type)
            else:
                s = self.serializer_cache[content_type] = get_serializer(t)
        return s

    def __init__(self, base, headers=None, options=None, async_send=False, content_type=None):
        self.base = base
        self.options = options or {}

        if content_type is None:
            content_type = 'application/json'
        self.content_type = content_type
        self.serializer_cache = {}
        self.serializer = self.get_serializer(content_type)
        
        h = {'content-type': content_type}
        dicts.reverse_update(headers, h)

        self.session = ses = requests.Session()
        self.set_headers(headers)
        ses.hooks.update(response=response_hook)
        if async_send:
            #NOTE: must patch_all, otherwise it will hangs
            from gevent import monkey; monkey.patch_all()
            ses.mount('http://', HTTPStreamAdapter())
            #TODO https

    def http(self, method, path, data=None, params=None, stream=False, content_type=None, **kwargs):
        headers = {}

        if content_type is not None:
            serializer = self.get_serializer(content_type)
            headers['content-type'] = content_type
        else:
            serializer = self.serializer
            content_type = self.content_type

        #NOTE: stream is for response body, not for request body
        if HTTP_CLIENT_DEBUG:
            if content_type=='application/json':
                debug_repr = str
            else:
                debug_repr = repr

            log.info('%s %s %s' % (method.upper(), self.base+path, headers_line(params)))
            h = self.session.headers
            if headers:
                h = dict(h)
                h.update(headers)
            log.debug('%s' % headers_line(h))

        if data is None:
            if HTTP_CLIENT_DEBUG:
                log.debug('\nnull')
        else:
            data = serializer.dumps(data)

            if isinstance(data, types.GeneratorType):
                #TODO
                #requests send wrong chunk size for unicoode
                data = (x.encode('utf8') if isinstance(x, unicode) else x for x in data)

                if HTTP_CLIENT_DEBUG:
                    if HTTP_STREAM_DEBUG:
                        data = stream_with_echo(data)
                    else:
                        log.debug('\n<stream>')
            else:
                #TODO
                #gevent socket cannot send unicode
                if isinstance(data, unicode):
                   data = data.encode('utf8')

                if HTTP_CLIENT_DEBUG:
                    log.debug('\n%s' % debug_repr(data))

        m = getattr(self.session, method)
        r = m(self.base+path, data=data, params=params, stream=stream, headers=headers, **kwargs)

        if HTTP_CLIENT_DEBUG:
            log.debug('%s' % headers_line(r.headers))

        if stream:
            def g():
                #NOTE:
                #work before response_hook
                #for x in r.iter_lines(chunk_size=1):

                #work after response_hook
                chunks = r.iter_chunks()
                if HTTP_STREAM_DEBUG:
                    chunks = stream_with_echo(chunks)
                for x in chunks:
                    yield serializer.loads(x)
            r.raise_for_status()
            if HTTP_CLIENT_DEBUG and not HTTP_STREAM_DEBUG:
                log.debug('\n<stream>')
            return g()
        else:
            s = r.content
            if HTTP_CLIENT_DEBUG:
                log.debug('\n%s' % debug_repr(s))
            r.raise_for_status()
            return serializer.loads(s)

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

