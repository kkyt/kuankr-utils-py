import math

EPS = 1e-7

def rel_eq(a, b, atol=EPS, rtol=EPS):
    return math.fabs(a - b) <= (atol + rtol * math.fabs(b))

def float_eq(a, b, eps=EPS):
    return math.fabs(a-b) <= eps

def int_floor(f, eps=EPS):
    return int(f+eps)


#http://stackoverflow.com/questions/3498192/c-convert-double-to-float-preserving-decimal-point-precision
'''
double round_to_decimal(float f) {
    char buf[42];
    sprintf(buf, "%.7g", f); // round to 7 decimal digits
    return atof(buf);
}
'''

def round_float32_to_decimal(s):
    #TODO
    pass
    
