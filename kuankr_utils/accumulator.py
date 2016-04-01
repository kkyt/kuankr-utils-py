import copy
from collections import deque

from .stateful import Stateful

class Accumulator(Stateful):
    '''
    NOTE: inherited need implement .value in one of the following ways:

    1. self.value = x
    2. @property
       def value(self):
    '''
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

class MultiAccumulator(Accumulator):
    def set_options(self, base=None):
        self.acc = base
        self.accs = {}

    def init_state(self):
        return { 'accs': {} }

    def get_state(self):
        for k,a in self.accs.items():
            a.get_state()

    def set_state(self, state):
        super(MultiAccumulator, self).set_state(state)
        for k,s in self.state['accs'].items():
            a = self.accs[k] = copy.deepcopy(self.acc)
            a.set_state(s)

    def feed(self, value):
        k, r = value
        state = self.state
        a = self.accs.get(k)
        if a is None:
            s = state['accs'].get(k)
            if s is None:
                s = state['accs'][k] = {}
            a = self.accs[k] = copy.deepcopy(self.acc)
            a.set_state(s)
        a.feed(r)

    @property
    def value(self):
        return {k: a.value for k,a in self.accs.items()}

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

