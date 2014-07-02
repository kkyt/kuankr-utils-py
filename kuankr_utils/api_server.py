import os

#NOTE: patch_all before all others
from gevent import monkey; monkey.patch_all()

from kuankr_utils import log, debug

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


