import os
from werkzeug.wsgi import DispatcherMiddleware

#NOTE: patch_all before all others
from gevent import monkey; monkey.patch_all()

from kuankr_utils import log, debug

def not_found(environ, start_response):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']

def create_app(api):
    version = os.environ.get('KUANKR_SERVICE_VERSION', 'v1')
    app = DispatcherMiddleware(not_found, {
        '/' + version: api
    })
    return app

def run_wsgi(name, app, default_port=80, server='gevent'):
    port = os.environ.get('%s_PORT' % name.upper(), default_port)
    port = int(port)

    wsgi_debug = os.environ.get('WSGI_DEBUG')=='1'

    log.debug('run wsgi app with port: %s server: %s' % (port, server))

    if server=='gevent':
        from gevent.pywsgi import WSGIServer
        http_server = WSGIServer(('', port), app)
        http_server.serve_forever()
    else:
        app.run(debug=wsgi_debug, port=port)


