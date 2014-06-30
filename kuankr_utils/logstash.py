from __future__ import absolute_import

import logstash
import logging
import os

import urllib
from urlparse import urlparse

class FakeLogger(object):
    def __getattr__(self, m):
        def f(*args, **kwargs):
            pass
        return f

default_uri = None #'tcp://127.0.0.1:20110'
LOGSTASH_URI = os.environ.get('LOGSTASH_URI', default_uri)

if not LOGSTASH_URI:
    log = FakeLogger()
else:
    uri = urlparse(LOGSTASH_URI)

    if not uri.hostname:
        raise Exception("invalid LOGSTASH_URI: %s, example: %s" % (uri, default_uri))

    logger_name = os.environ.get('LOGSTASH_LOGGER', 'logstash')

    log = logging.getLogger(logger_name)
    log.setLevel(logging.DEBUG)

    if uri.scheme == 'udp':
        handler = logstash.UDPLogstashHandler(uri.hostname, uri.port)
    else:
        handler = logstash.TCPLogstashHandler(uri.hostname, uri.port)

    log.addHandler(handler)

