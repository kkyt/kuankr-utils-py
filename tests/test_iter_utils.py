from kuankr_utils.iter_utils import *

def test_slice_iter():
    a = iter(range(1, 10))
    b = slice_iter(a, 2)
    r = []
    for x in b:
        x = list(x)
        r.append(x)
    assert r==[[1,2],[3,4],[5,6],[7,8],[9]]
