bl_info = {
        'name': 'Seventina (dev mode)',
        'description': 'A soft-renderer based on Taichi programming language',
        'author': 'archibate <1931127624@qq.com>',
        'version': (0, 0, 0),
        'blender': (2, 81, 0),
        'location': 'Seventina Window',
        'support': 'COMMUNITY',
        'wiki_url': 'https://github.com/archibate/seventina/wiki',
        'tracker_url': 'https://github.com/archibate/seventina/issues',
        'warning': 'Development mode',
        'category': 'Render',
}


src_path = '/home/bate/Develop/seven/seventina/__init__.py'


def register():
    import imp
    global seventina
    seventina = imp.load_source('seventina', src_path)
    seventina.dev_mode = True
    seventina.register()


def unregister():
    global seventina
    seventina.unregister()
    seventina = None
