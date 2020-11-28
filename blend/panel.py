import bpy

from . import engine


class SeventinaPanel(bpy.types.Panel):
    '''Seventina options'''

    bl_label = 'Seventina'
    bl_idname = 'SCENE_PT_seventina'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, 'taichi_use_backend')
        layout.operator(scene, 'render.render')


def register():
    bpy.types.Scene.taichi_use_backend = bpy.props.EnumProperty(name='Backend',
        items=[(item.upper(), item, '') for item in [
            'CPU', 'GPU', 'CUDA', 'OpenCL', 'OpenGL', 'Metal', 'CC',
            ]])

    bpy.utils.register_class(SeventinaPanel)


def unregister():
    bpy.utils.unregister_class(SeventinaPanel)

    del bpy.types.Scene.taichi_use_backend
