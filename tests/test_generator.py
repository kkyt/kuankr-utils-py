

state = {}

def g(n):
    for i in range(n):
        yield i
    state['g'] = n

def test_generator():
    state['g'] = 0
    a = list(g(3))
    assert state['g']==3
    
