import math

EPS = 1e-7

def rel_eq(a, b, atol=EPS, rtol=EPS):
    return math.fabs(a - b) <= (atol + rtol * math.fabs(b))

def float_eq(a, b, eps=EPS):
    return math.fabs(a-b) <= eps

def int_floor(f, eps=EPS):
    return int(f+eps)


