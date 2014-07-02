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

