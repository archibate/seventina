bl_info = {
        'name': 'Seventina',
        'description': 'A soft-renderer based on Taichi programming language',
        'author': '彭于斌 <1931127624@qq.com>',
        'version': (0, 0, 0),
        'blender': (2, 81, 0),
        'location': 'Render -> Seventina Options',
        'support': 'COMMUNITY',
        'wiki_url': 'https://github.com/archibate/tina/wiki',
        'tracker_url': 'https://github.com/archibate/tina/issues',
        'category': 'Render',
}

__version__ = bl_info['version']
__author__ = bl_info['author']

print('[Tai3D] version', '.'.join(map(str, __version__)))


def register():
    from . import blend
    blend.register()


def unregister():
    from . import blend
    blend.unregister()


@eval('lambda x: x()')
def __getattr__():
    def gettr(name):
        def do_import(path):
            module = __import__(path)
            for name in path.split('.')[1:]:
                module = getattr(module, name)
            return module

        if gettr.entered:
            raise AttributeError(name)

        try:
            gettr.entered = True

            try:
                return __import__(f'tina.{name}')
            except ImportError:
                pass

            for sm_name in ['core', 'util']:
                try:
                    try:
                        module = do_import(f'tina.{sm_name}')
                    except ImportError:
                        continue
                    return getattr(module, name)
                except AttributeError:
                    pass
                try:
                    return do_import(f'tina.{sm_name}.{name}')
                except ImportError:
                    pass

            for sm_name in ['core', 'util']:
                try:
                    try:
                        module = do_import(f'tina.{sm_name}.{name.lower()}')
                    except ImportError:
                        continue
                    return getattr(module, name)
                except AttributeError:
                    pass

            for sm_name in ['common', 'advans', 'core.shader',
                    'core.material', 'util.assimp']:
                try:
                    try:
                        module = do_import(f'tina.{sm_name}')
                    except ImportError:
                        continue
                    return getattr(module, name)
                except AttributeError:
                    pass

            raise AttributeError(name)
        finally:
            gettr.entered = False

    gettr.entered = False

    def wrapped(name):
        if name in wrapped.cache:
            return wrapped.cache[name]
        value = wrapped.cache[name] = gettr(name)
        return value

    wrapped.cache = {}

    return wrapped
