import os

from . import log

HTTP_SERVER_DEBUG = os.environ.get('HTTP_SERVER_DEBUG')=='1'

HTTP_CLIENT_DEBUG = os.environ.get('HTTP_CLIENT_DEBUG')=='1'

HTTP_STREAM_DEBUG = os.environ.get('HTTP_STREAM_DEBUG')=='1'


def headers_line(headers):
    if not headers:
        return ''
    f = lambda a: '%s=%s' % a
    h = sorted(headers.items())
    return ' '.join(map(f, h))

def request_line(req):
    return req.method + ' ' + req.url + '\n' + headers_line(req.headers)
    
def response_line(resp):
    return headers_line(resp.headers)


def stream_with_echo(stream, fmt=None):
    for x in stream:
        if fmt is not None:
            s = fmt(x)
        else:
            s = x
        log.debug('%s' % s)
        yield x

