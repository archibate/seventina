import seventina
import types


class namespace:
    def __init__(self, mod, path):
        self._mod = mod
        self._path = path

    def __getattr__(self, name):
        path = self._path + '.' + name
        if not hasattr(self._mod, name):
            try:
                __import__(path)
            except ImportError:
                raise AttributeError(name)
        obj = getattr(self._mod, name)
        if isinstance(obj, types.ModuleType):
            obj = namespace(obj, path)
        return obj


seventina = namespace(seventina, 'seventina')


class Bundle:
    def __getattr__(self, name):
        try:
            return getattr(seventina, name)
        except AttributeError:
            pass

        try:
            return getattr(seventina.core, name)
        except AttributeError:
            pass

        try:
            module = getattr(seventina.core, name.lower())
            return getattr(module, name)
        except AttributeError:
            pass

        try:
            module = getattr(seventina.util, name.lower())
            return getattr(module, name)
        except AttributeError:
            pass

        try:
            return getattr(seventina.core.material, name)
        except AttributeError:
            pass

        try:
            return getattr(seventina.core.shader, name)
        except AttributeError:
            pass

        try:
            return getattr(seventina.util.assimp, name)
        except AttributeError:
            pass

        try:
            return getattr(seventina.common, name)
        except AttributeError:
            pass

        raise AttributeError(name)



tina = Bundle()
