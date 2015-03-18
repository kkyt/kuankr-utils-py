import random

import gevent
from gevent.monkey import patch_all
patch_all()

from kuankr_utils.api_client import ApiClient

def _ping(id, c, n):
    for i in range(n):
        x = 'client_%s_%s' % (id,i)
        c.set_headers({'x-api-client': x})
        t = random.randint(0, 100)/10.0
        gevent.sleep(t)
        r = c.test_scenario.create()
        assert r['api_client']==x

def test_parallel():
    c = ApiClient('kuankr_auth').api
    n = 100
    m = 100

    ps = []
    for i in range(n):
        p = gevent.spawn(_ping, i, c, m)
        ps.append(p)

    gevent.joinall(ps)

