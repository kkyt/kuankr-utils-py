from kuankr_utils.json_obj import *

def assert_enc(x):
    d = encode(x)
    print d
    y = decode(d)
    print y
    e = encode(x)
    assert d==e
    return y

def test_simple():
    t = ExampleObj(2)
    assert_enc(t)

def test_func():
    f = example_func
    g = assert_enc(f)
    assert f==g

def test_code():
    code = """
from kuankr_utils.json_obj import ExampleObj
class T(object):
    def __init__(self, a, b=2):
        self.e = ExampleObj(a)
"""
    d = {
        'class': 'T',
        'code' : code,
        'args': [8],
        'kwargs': { 'b': 3 }
    }
    x = decode_from_config(d)
    assert x.e.c==24

