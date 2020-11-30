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

        layout.prop(scene, 'seventina_resolution_x')
        layout.prop(scene, 'seventina_resolution_y')
        layout.prop(scene, 'seventina_max_faces')
        layout.prop(scene, 'seventina_max_verts')
        layout.prop(scene, 'seventina_max_lights')
        layout.prop(scene, 'seventina_backend')


def on_param_update(self, context):
    worker.start_main()

def register():
    bpy.types.Scene.seventina_resolution_x = bpy.props.IntProperty(name='Resolution X', min=1, soft_min=1, subtype='PIXEL', default=512, update=on_param_update)
    bpy.types.Scene.seventina_resolution_y = bpy.props.IntProperty(name='Resolution Y', min=1, soft_min=1, subtype='PIXEL', default=512, update=on_param_update)
    bpy.types.Scene.seventina_max_faces = bpy.props.IntProperty(name='Max Faces Count', min=1, soft_min=1, default=65536, update=on_param_update)
    bpy.types.Scene.seventina_max_verts = bpy.props.IntProperty(name='Max Vertices Count', min=1, soft_min=1, default=65536, update=on_param_update)
    bpy.types.Scene.seventina_max_lights = bpy.props.IntProperty(name='Max Lights Count', min=1, soft_min=1, default=16, update=on_param_update)
    bpy.types.Scene.seventina_backend = bpy.props.EnumProperty(name='Backend', items=[(item.upper(), item, '') for item in ['CPU', 'GPU', 'CUDA', 'OpenCL', 'OpenGL', 'Metal', 'CC']], update=on_param_update)

    bpy.utils.register_class(SeventinaOptionPanel)


def unregister():
    bpy.utils.unregister_class(SeventinaOptionPanel)

    del bpy.types.Scene.seventina_resolution_x
    del bpy.types.Scene.seventina_resolution_y
    del bpy.types.Scene.seventina_max_faces
    del bpy.types.Scene.seventina_max_verts
    del bpy.types.Scene.seventina_max_lights
    del bpy.types.Scene.seventina_backend
