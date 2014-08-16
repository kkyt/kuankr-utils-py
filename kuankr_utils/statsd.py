from __future__ import absolute_import

import os
import urllib
from urlparse import urlparse

import statsd

def create_statsd_client():
    uri = os.environ.get('STATSD_URI', 'statsd://127.0.0.1:8125')
    uri = urlparse(uri)

    prefix = None
    if len(uri.path)>1:
        prefix = uri.path[1:] + '.'

    c = statsd.StatsClient(uri.hostname, uri.port, prefix=prefix)
    return c


