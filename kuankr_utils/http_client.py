#coding: utf8
from __future__ import absolute_import

import requests

from kuankr_utils import api_json as json
from kuankr_utils import log, dicts
from kuankr_utils.requests import response_hook, HTTPStreamAdapter

class Resource(object):
    def __init__(self, client, path):
        self.client = client
        self.path = path

    def __getattr__(self, method):
        pass

def flat_dict_repr(d):
    if not d:
        return ''
    else:
        return '; '.join('%s=%s' % (k,v) for k,v in sorted(d.items()))

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

    def http(self, method, path, data=None, params=None, stream=False, **kwargs):
        #NOTE: stream is for response body, not for request body
        log.info('%s %s %s' % (method.upper(), path, flat_dict_repr(params)))
        log.debug('%s' % flat_dict_repr(self.session.headers))

        if data is None:
            log.debug('\nnull')
        else:
            data = json.dumps(data)

            #TODO
            #gevent socket cannot send unicode
            if isinstance(data, unicode):
               data = data.encode('utf8')

            log.debug('\n%s' % data)

        m = getattr(self.session, method)
        r = m(self.base+path, data=data, params=params, stream=stream, **kwargs)
        if stream:
            def g():
                #NOTE:
                #work before response_hook
                #for x in r.iter_lines(chunk_size=1):

                #work after response_hook
                for x in r.iter_chunks():
                    yield json.loads(x)
            r.raise_for_status()
            return g()
        else:
            log.debug('%s' % flat_dict_repr(r.headers))
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

