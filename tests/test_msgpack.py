
#MUST use http://git.agutong.com:3007/OpenSource/msgpack-python
import msgpack

def _test_float32(x):
    f = float(x)
    s = msgpack.dumps(f, use_single_float=True)
    g = msgpack.loads(s)
    y = str(g)
    assert y==x

def test_msgpack_float32():
    _test_float32('1.1')
    _test_float32('1.1e+30')
    _test_float32('1.23456e+30')
    _test_float32('1.23456')
    
    
