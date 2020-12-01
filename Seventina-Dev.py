bl_info = {
        'name': 'Seventina (dev mode)',
        'description': 'A soft-renderer based on Taichi programming language',
        'author': '彭于斌 <1931127624@qq.com>',
        'version': (0, 0, 0),
        'blender': (2, 81, 0),
        'location': 'Seventina Window',
        'support': 'TESTING',
        'wiki_url': 'https://github.com/archibate/seventina/wiki',
        'tracker_url': 'https://github.com/archibate/seventina/issues',
        'warning': 'Development mode',
        'category': 'Render',
}


import sys
sys.path.insert(0, '/home/bate/Develop/seven')


# https://stackoverflow.com/questions/28101895/reloading-packages-and-their-submodules-recursively-in-python
def reload_package(package):
    import os
    import types
    import importlib

    assert(hasattr(package, "__package__"))
    fn = package.__file__
    fn_dir = os.path.dirname(fn) + os.sep
    module_visit = {fn}
    del fn

    def reload_recursive_ex(module):
        importlib.reload(module)

        for module_child in vars(module).values():
            if isinstance(module_child, types.ModuleType):
                fn_child = getattr(module_child, "__file__", None)
                if (fn_child is not None) and fn_child.startswith(fn_dir):
                    if fn_child not in module_visit:
                        # print("reloading:", fn_child, "from", module)
                        module_visit.add(fn_child)
                        reload_recursive_ex(module_child)

    reload_recursive_ex(package)


registered = False


def register():
    print('Seventina-Dev register...')
    import seventina
    seventina.register()

    global registered
    registered = True
    print('...register done')


def unregister():
    print('Seventina-Dev unregister...')
    import seventina
    seventina.unregister()

    global registered
    registered = False
    print('...unregister done')


def reload():
    import seventina
    if registered:
        seventina.unregister()
    reload_package(seventina)
    seventina.register()

    import bpy
    bpy.context.scene.frame_current = bpy.context.scene.frame_current

__import__('bpy').a = reload
