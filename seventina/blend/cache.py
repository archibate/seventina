class IDCache:
    def __init__(self):
        self.lut = {}

    def lookup(self, func, object):
        idx = self.ident(object)
        if idx in self.lut:
            return self.lut[idx]
        value = func(object)
        self.lut[idx] = value
        return value

    def invalidate(self, object):
        idx = self.ident(object)
        if idx in self.lut:
            del self.lut[idx]

    def ident(self, object):
        return (type(object).__name__, object.name)
