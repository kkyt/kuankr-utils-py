

from kuankr_utils.date_time import now
from kuankr_utils.json import *

from decimal import Decimal

def test_simple():
    s = [1, Decimal(3), {
        2: now(), 
        'a': (now() for x in range(3))
    }]

    print dumps(s)

def test_decimal():
    import simplejson
    import json

    j = simplejson
    print json.dumps([22/10.0])

