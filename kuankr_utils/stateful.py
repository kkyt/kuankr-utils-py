
class SimpleStateful(object):
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

#comp: component
class Stateful(SimpleStateful):
    def __init__(self, **options):
        self.set_options(**options)

        self.comps = self.create_comps()
        for k, x in self.comps.items():
            setattr(self, k, x)

    def create_comps(self):
        return {}

    def init_state(self):
        r = {k: {} for k, x in self.comps.items()}
        return r
        
    def set_state(self, state):
        super(Stateful, self).set_state(state)
        s = self.state
        for k, x in self.comps.items():
            x.set_state(s[k])
            
    def get_state(self):
        for k, x in self.comps.items():
            x.get_state()
        return self.state

