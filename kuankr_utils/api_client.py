from __future__ import absolute_import

import os
import json
import requests

import heroics.client

class ApiClient(object):
    def __init__(self, service, **options):
        self.service = service
        self.options = options

        env = os.environ

        url = env['%s_URI' % service.upper()]
        schema = env['%s_SCHEMA' % service.upper()]
        if os.path.exists(schema):
            f = open(schema)
            s = f.read()
        else:
            r = requests.get(url + '/_schema')
            s = r.content
        schema = json.loads(s)
        f.close()

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

        self.api = heroics.client.Client(schema, url, options)
        self.http = self.api._http_client

    def set_headers(self, headers):
        self.http.set_headers(headers)

