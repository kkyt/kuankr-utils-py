from collections import deque

class Accumulator(object):
    def __init__(self, **options):
        self.set_options(**options)

    def set_options(self):
        pass

    def set_state(self, state):
        if state is None:
            state = {}
        if not state:
            state.update(self.init_state())
        self.state = state

    def init_state(self):
        return {}

    def get_state(self):
        return self.state

    @property
    def value(self, **kwargs):
        return None

    def feed(self, value):
        pass

    def feed_many(self, values):
        for v in values:
            self.feed(v)

    def remove(self, value):
        raise NotImplementedError()

    def remove_many(self, values):
        for v in self.values:
            self.remove(v)

class Recent(Accumulator):
    def set_options(self, n=None):
        self.n = n

    def init_state(self):
        return { 'a': [] }

    def feed(self, v):
        self.a.append(v)
    
    @property
    def value(self):
        return self.a

    def set_state(self, state):
        super(Recent, self).set_state(state)
        self.a = deque(self.state['a'], maxlen=self.n)

    def get_state(self):
        self.state['a'] = list(self.a)
        return self.state

class Count(Accumulator):
    def init_state(self):
        return { 'n': 0 }

    def feed(self, value):
        if value is not None:
            self.state['n'] += 1

    def feed_many(self, values):
        self.state['n'] += len(values)

    def remove(self, value):
        if value is not None:
            self.state['n'] -= 1

    def remove_many(self, values):
        self.state['n'] -= len(values)

    @property
    def value(self):
        return self.state['n']

class Sum(Accumulator):
    def set_options(self, init=0):
        self.init = init

    def init_state(self):
        return { 's': self.init }

    def feed(self, value):
        if value is not None:
            self.state['s'] += value

    def feed_many(self, values):
        self.state['s'] += sum(values)

    def remove(self, value):
        if value is not None:
            self.state['s'] -= value

    def remove_many(self, values):
        self.state['s'] -= sum(values)

    @property
    def value(self):
        return self.state['s']

class Average(Accumulator):
    def init_state(self):
        return { 'a': 0, 'n': 0}

    def feed(self, value):
        if value is not None:
            s = self.state
            n = s['n']
            s['n'] += 1
            s['a'] = s['a']*float(n)/(n+1)+value/(n+1)

    def feed_many(self, values):
        s = self.state
        n = s['n']
        m = len(values)
        s['n'] += m
        s['a'] = s['a']*float(n)/(n+m)+sum(values)/(n+m)

    def remove(self, value):
        if value is not None:
            s = self.state
            n = s['n']
            s['n'] -= 1
            s['a'] = (s['a']*float(n))/(n-1)-value/(n-1)

    def remove_many(self, values):
        s = self.state
        n = s['n']
        m = len(values)
        s['n'] -= m
        s['a'] = s['a']*float(n)/(n-m)-sum(values)/(n-m)

    @property
    def value(self):
        return self.state['a']

class CompositeAccumulator(Accumulator):
    def __init__(self, **options):
        self.set_options(**options)
        self.comps = self.create_comps()

    def create_comps(self):
        return {}

    def init_state(self):
        r = {k: {} for k, x in self.comps.items()}
        return r
        
    def set_state(self, state):
        super(CompositeAccumulator, self).set_state(state)
        s = self.state
        for k, x in self.comps.items():
            setattr(self, k, x)
            x.set_state(s[k])
            
    def get_state(self):
        for k, x in self.comps.items():
            x.get_state()
        return self.state

