import bpy

from . import worker


class SeventinaOptionPanel(bpy.types.Panel):
    '''Seventina engine options'''

    bl_label = 'Seventina'
    bl_idname = 'RENDER_PT_seventina'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, 'seventina_backend')
        layout.prop(scene, 'seventina_resolution_x')
        layout.prop(scene, 'seventina_resolution_y')
        layout.prop(scene, 'seventina_max_faces')
        layout.prop(scene, 'seventina_max_lights')
        layout.prop(scene, 'seventina_smoothing')
        layout.prop(scene, 'seventina_culling')
        layout.prop(scene, 'seventina_clipping')
        layout.prop(scene, 'seventina_viewport_samples')
        layout.prop(scene, 'seventina_render_samples')


def on_param_update(self, context):
    worker.start_main()


def register():
    bpy.types.Scene.seventina_backend = bpy.props.EnumProperty(name='Backend', items=[(item.upper(), item, '') for item in ['CPU', 'GPU', 'CUDA', 'OpenGL', 'Metal', 'CC']], update=on_param_update)
    bpy.types.Scene.seventina_resolution_x = bpy.props.IntProperty(name='Resolution X', min=1, soft_min=1, subtype='PIXEL', default=1920, update=on_param_update)
    bpy.types.Scene.seventina_resolution_y = bpy.props.IntProperty(name='Resolution Y', min=1, soft_min=1, subtype='PIXEL', default=1080, update=on_param_update)
    bpy.types.Scene.seventina_max_faces = bpy.props.IntProperty(name='Max Faces Count', min=1, soft_min=1, default=65536, update=on_param_update)
    bpy.types.Scene.seventina_max_lights = bpy.props.IntProperty(name='Max Lights Count', min=1, soft_min=1, default=16, update=on_param_update)
    bpy.types.Scene.seventina_smoothing = bpy.props.BoolProperty(name='Smooth shading', default=True, update=on_param_update)
    bpy.types.Scene.seventina_culling = bpy.props.BoolProperty(name='Back face culling', default=True, update=on_param_update)
    bpy.types.Scene.seventina_clipping = bpy.props.BoolProperty(name='Viewbox clipping', default=False, update=on_param_update)
    bpy.types.Scene.seventina_viewport_samples = bpy.props.IntProperty(name='Viewport Samples', default=1)
    bpy.types.Scene.seventina_render_samples = bpy.props.IntProperty(name='Render Samples', default=16)

    bpy.utils.register_class(SeventinaOptionPanel)


def unregister():
    bpy.utils.unregister_class(SeventinaOptionPanel)

    del bpy.types.Scene.seventina_backend
    del bpy.types.Scene.seventina_resolution_x
    del bpy.types.Scene.seventina_resolution_y
    del bpy.types.Scene.seventina_max_faces
    del bpy.types.Scene.seventina_max_lights
    del bpy.types.Scene.seventina_smoothing
    del bpy.types.Scene.seventina_culling
    del bpy.types.Scene.seventina_clipping
    del bpy.types.Scene.seventina_viewport_samples
    del bpy.types.Scene.seventina_render_samples
