import bpy

from . import worker


class TinaOptionPanel(bpy.types.Panel):
    '''Tina engine options'''

    bl_label = 'Tina'
    bl_idname = 'RENDER_PT_seventina'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, 'tina_backend')
        layout.prop(scene, 'tina_resolution_x')
        layout.prop(scene, 'tina_resolution_y')
        layout.prop(scene, 'tina_max_faces')
        layout.prop(scene, 'tina_max_lights')
        layout.prop(scene, 'tina_smoothing')
        layout.prop(scene, 'tina_culling')
        layout.prop(scene, 'tina_clipping')
        layout.prop(scene, 'tina_viewport_samples')
        layout.prop(scene, 'tina_render_samples')


def on_param_update(self, context):
    worker.start_main()


def register():
    bpy.types.Scene.tina_backend = bpy.props.EnumProperty(name='Backend', items=[(item.upper(), item, '') for item in ['CPU', 'GPU', 'CUDA', 'OpenGL', 'Metal', 'CC']], update=on_param_update)
    bpy.types.Scene.tina_resolution_x = bpy.props.IntProperty(name='Resolution X', min=1, soft_min=1, subtype='PIXEL', default=1920, update=on_param_update)
    bpy.types.Scene.tina_resolution_y = bpy.props.IntProperty(name='Resolution Y', min=1, soft_min=1, subtype='PIXEL', default=1080, update=on_param_update)
    bpy.types.Scene.tina_max_faces = bpy.props.IntProperty(name='Max Faces Count', min=1, soft_min=1, default=65536, update=on_param_update)
    bpy.types.Scene.tina_max_lights = bpy.props.IntProperty(name='Max Lights Count', min=1, soft_min=1, default=16, update=on_param_update)
    bpy.types.Scene.tina_smoothing = bpy.props.BoolProperty(name='Smooth shading', default=True, update=on_param_update)
    bpy.types.Scene.tina_culling = bpy.props.BoolProperty(name='Back face culling', default=True, update=on_param_update)
    bpy.types.Scene.tina_clipping = bpy.props.BoolProperty(name='Viewbox clipping', default=False, update=on_param_update)
    bpy.types.Scene.tina_viewport_samples = bpy.props.IntProperty(name='Viewport Samples', default=8)
    bpy.types.Scene.tina_render_samples = bpy.props.IntProperty(name='Render Samples', default=32)

    bpy.utils.register_class(TinaOptionPanel)


def unregister():
    bpy.utils.unregister_class(TinaOptionPanel)

    del bpy.types.Scene.tina_backend
    del bpy.types.Scene.tina_resolution_x
    del bpy.types.Scene.tina_resolution_y
    del bpy.types.Scene.tina_max_faces
    del bpy.types.Scene.tina_max_lights
    del bpy.types.Scene.tina_smoothing
    del bpy.types.Scene.tina_culling
    del bpy.types.Scene.tina_clipping
    del bpy.types.Scene.tina_viewport_samples
    del bpy.types.Scene.tina_render_samples
