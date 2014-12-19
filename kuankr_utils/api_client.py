from __future__ import absolute_import

import os
import json
import requests
from requests.exceptions import ConnectionError

import heroics.client

from . import log
from . import serviced

class ApiClient(object):
    def __init__(self, service, **options):
        self.service = service
        self.options = options

        env = os.environ

        sd = serviced.get_serviced()
        url = sd.lookup(service, wait=True)
        if not url:
            raise Exception('unknown service: %s' % service)

        schema = env.get('%s_SCHEMA' % service.upper())
        if schema and os.path.exists(schema):
            f = open(schema)
            s = f.read()
            f.close()
        else:
            u = url + '/_schema'
            log.debug('GET ' + u)

            #wait until api is available
            s = 0.1
            while True:
                try:
                    r = requests.get(u)
                    break
                except ConnectionError as e:
                    import gevent
                    log.info('wait %s secs for api service: %s %s' % (s, service, url))
                    gevent.sleep(s)
                    s *= 2

            s = r.content

        if not s:
            raise Exception("no schema found for service: %s" % service)
        schema = json.loads(s)

        #schema = Heroics::Schema.new schema
        headers = {}
        for x in ['api_client', 'auth_token', 'admin_token']:
            v = env.get('KUANKR_%s' % x.upper())
            if v:
                h = ('x_%s' % x).replace('_', '-')
                headers[h] = v

        dh = options.get('default_headers')
        if dh:
            headers.update(dh)
        options['default_headers'] = headers

        self.schema = schema
        self.api = heroics.client.Client(schema, url, options)
        self.http = self.api._http_client

    def set_headers(self, headers):
        self.http.set_headers(headers)

_api_clients = {}

def get_api_client(service, *args, **kwargs):
    if not service in _api_clients:
        _api_clients[service] = ApiClient(service, *args, **kwargs)
    return _api_clients[service]


