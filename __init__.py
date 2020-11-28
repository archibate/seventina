bl_info = {
        'name': 'Seventina',
        'description': 'A soft-renderer based on Taichi programming langurage',
        'author': 'archibate <1931127624@qq.com>',
        'version': (0, 0, 0),
        'blender': (2, 81, 0),
        'location': 'Seventina Window',
        'support': 'COMMUNITY',
        'wiki_url': 'https://github.com/archibate/seventina/wiki',
        'tracker_url': 'https://github.com/archibate/seventina/issues',
        'category': 'Physics',
}


def register():
    from .blend import register
    register()


def unregister():
    from .blend import unregister
    unregister()
