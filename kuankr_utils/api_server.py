import os
from werkzeug.wsgi import DispatcherMiddleware

#NOTE: patch_all before all others
from gevent import monkey; monkey.patch_all()

from kuankr_utils import log, debug, http_debug, serviced

def not_found(environ, start_response):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']

def create_app(api, admin_app=None, name=None):
    version = os.environ.get('KUANKR_SERVICE_VERSION', 'v1')
    d = {
        '/' + version: api
    }
    if admin_app is not None:
        d['/admin'] = admin_app
    app = DispatcherMiddleware(not_found, d)

    if name is not None:
        s = name.upper()
        uri = os.environ.get('%s_URI' % s)
        if not uri:
            port = os.environ.get('%s_PORT' % s)
            if port:
                uri = 'http://127.0.0.1:%s' % port
        if uri:
            sd = serviced.get_serviced()
            sd.register(name, uri)

    return app

def namespaced_app(routes):
    return DispatcherMiddleware(not_found, routes)

def run_wsgi(name, app, default_port=80, server='gevent'):
    port = os.environ.get('%s_PORT' % name.upper(), default_port)
    port = int(port)

    log.debug('run wsgi app with port: %s server: %s' % (port, server))

    if server=='gevent':
        from gevent.pywsgi import WSGIServer
        http_server = WSGIServer(('', port), app)
        http_server.serve_forever()
    else:
        app.run(debug=http_debug.HTTP_SERVER_DEBUG, port=port)


