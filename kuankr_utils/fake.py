
class FakeLogger(object):
    def __getattr__(self, m):
        def f(*args, **kwargs):
            pass
        return f
