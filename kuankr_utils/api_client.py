from __future__ import absolute_import

import os
import json
import requests
from requests.exceptions import ConnectionError

import heroics.client

from . import log
from . import serviced

def normalize_header_key(s):
    return s.lower().replace('_', '-')

def normalize_headers(h):
    return { normalize_header_key(k): v for k,v in h.items()}

class ApiClient(object):
    def __init__(self, service, uri=None, **options):
        self.service = service
        self.options = options

        env = os.environ

        if uri is None:
            sd = serviced.get_serviced()
            uri = sd.lookup(service, wait=True)

        if not uri:
            raise Exception('unknown service: %s' % service)

        schema = env.get('%s_SCHEMA' % service.upper())
        s = None
        if schema and os.path.exists(schema):
            f = open(schema)
            s = f.read()
            f.close()
        else:
            u = uri + '/_schema'
            log.debug('GET ' + u)

            #wait until api is available
            sleep = 0.1
            while True:
                try:
                    r = requests.get(u, timeout=3)
                    break
                except ConnectionError as e:
                    import gevent
                    log.info('wait %s secs for api service: %s %s' % (sleep, service, uri))
                    gevent.sleep(sleep)
                    sleep *= 2
                    if sleep > 20:
                        sleep = 0.1

            if r.status_code==200:
                s = r.content

        if not s:
            log.warn("no schema found for service: %s" % service)
            #emtpy schema
            schema = {
                'properties': {}
            }
        else:
            schema = json.loads(s)

        #schema = Heroics::Schema.new schema
        headers = {}
        for x in ['api_client', 'auth_token', 'admin_token']:
            v = env.get('KUANKR_%s' % x.upper())
            if v:
                headers['x_%s' % x] = v

        headers = normalize_headers(headers)
        dh = options.get('default_headers')
        if dh:
            headers.update(normalize_headers(dh))
        options['default_headers'] = headers

        self.schema = schema
        self.api = heroics.client.Client(schema, uri, options)
        self.http = self.api._http_client

    def set_headers(self, headers):
        self.http.set_headers(headers)

_api_clients = {}

def get_api_client(service, *args, **kwargs):
    if not service in _api_clients:
        _api_clients[service] = ApiClient(service, *args, **kwargs)
    return _api_clients[service]


