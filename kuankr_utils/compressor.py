import zlib
import bz2
import gzip

from kuankr_utils import log, debug

class Compressor(object):
    def compress(self, data):
        return data

    def decompress(self, data):
        return data

    def open(self, fname, mode, **kwargs):
        f = open(fname, mode, **kwargs)
        return f
        
    def close(self, f):
        f.close()

class ZipCompressor(Compressor):
    def __init__(self, level=None):
        if level is None:
            level = 6
        self.level = level

    def compress(self, data):
        return zlib.compress(data, self.level)

    def decompress(self, data):
        return zlib.decompress(data)

class Bz2Compressor(Compressor):
    def __init__(self, level=None):
        if level is None:
            level = 9
        self.level = level

    def compress(self, data):
        return bz2.compress(data, self.level)

    def decompress(self, data):
        return bz2.decompress(data)

    def open(self, fname, mode, **kwargs):
        if mode=='a':
            log.error("python 2.7 not support bz2 append, fallback to write mode")
            mode = 'w'
        f = bz2.BZ2File(fname, mode, **kwargs)
        return f

class GzipCompressor(ZipCompressor):
    def open(self, fname, mode, **kwargs):
        f = gzip.GzipFile(fname, mode, **kwargs)
        return f

class SnappyCompressor(Compressor):
    pass

compressors = {
    None: Compressor,
    'zip': ZipCompressor,
    'gzip': GzipCompressor,
    'snappy': SnappyCompressor,
    'bz2': Bz2Compressor
}

def get_compressor(c, *args, **kwargs):
    x = compressors.get(c)
    if x is not None:
        x = x(*args, **kwargs)
    return x

