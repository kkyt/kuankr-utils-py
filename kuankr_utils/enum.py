from ctypes import Structure, c_ubyte

#TODO: use enum32

def Enum(*options):
    """
    Fast enums are very important when we want really tight
    loops. These are probably going to evolve into pure C structs
    anyways so might as well get going on that.
    """
    class cstruct(Structure):
        _fields_ = [(o, c_ubyte) for o in options]
        __iter__ = lambda s: iter(range(len(options)))

    return cstruct(*range(len(options)))


