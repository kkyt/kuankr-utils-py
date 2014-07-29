class OpenStruct(dict):
    def __setattr__(self,key,value):
        self[key] = value
        return value

    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            raise AttributeError(key)

        #NOTE: cause error in yaml dump
        #return self.get(key)


class DefaultOpenStruct(dict):
    defaults = {}

    def __setattr__(self, attr, value):
        self[attr] = value

    def __getattr__(self, attr):
        if not attr.startswith('__'):
            if attr in self:
                return self[attr]
            elif attr in self.defaults:
                return self.defaults[attr]
            else:
                raise AttributeError(attr)
        else:
            return super(OpenStructDefault, self).__getattr__(attr)

