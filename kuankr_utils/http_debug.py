
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


