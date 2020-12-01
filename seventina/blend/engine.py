import bpy

from ..utils import *
from ..engine import Engine
from ..shader import Shader
from .cache import IDCache


@ti.data_oriented
class OutputPixelConverter:
    def cook(self, color):
        if isinstance(color, ti.Expr):
            color = ti.Vector([color, color, color])
        elif isinstance(color, ti.Matrix):
            assert color.m == 1, color.m
            if color.n == 1:
                color = ti.Vector([color(0), color(0), color(0)])
            elif color.n == 2:
                color = ti.Vector([color(0), color(1), 0])
            elif color.n in [3, 4]:
                color = ti.Vector([color(0), color(1), color(2)])
            else:
                assert False, color.n
        return color

    @ti.kernel
    def dump(self, img: ti.template(), use_bilerp: ti.template(),
            out: ti.ext_arr(), width: int, height: int):
        for i, j in ti.ndrange(width, height):
            r, g, b = 0., 0., 0.
            if ti.static(use_bilerp):
                scale = ti.Vector(img.shape) / ti.Vector([width, height])
                pos = ti.Vector([i, j]) * scale
                r, g, b = self.cook(bilerp(img, pos))
            else:
                r, g, b = self.cook(img[i, j])
            base = (j * width + i) * 4
            out[base + 0] = r
            out[base + 1] = g
            out[base + 2] = b
            out[base + 3] = 1


class BlenderEngine(Engine):
    def __init__(self):
        super().__init__((
            bpy.context.scene.seventina_resolution_x,
            bpy.context.scene.seventina_resolution_y),
            bpy.context.scene.seventina_max_verts,
            bpy.context.scene.seventina_max_faces,
            bpy.context.scene.seventina_max_lights)
        self.output = OutputPixelConverter()
        self.cache = IDCache()

        self.color = ti.Vector.field(3, float, self.res)
        self.shader = Shader(self.color)

    def render_scene(self):
        self.clear_depth()
        self.color.fill(0)

        lights = []
        meshes = []

        for object in bpy.context.scene.objects:
            if not object.visible_get():
                continue
            if object.type == 'LIGHT':
                lights.append(object)
            if object.type == 'MESH':
                meshes.append(object)

        self.nlights[None] = len(lights)
        for i, object in enumerate(lights):
            self.update_light(i, object)

        for object in meshes:
            self.render_object(object)

    def update_light(self, i, object):
        color = np.array(object.data.color) * object.data.energy / 1000
        model = np.array(object.matrix_world)

        if object.data.type == 'SUN':
            dir = model @ np.array([0, 0, 1, 0])
        elif object.data.type == 'POINT':
            dir = model @ np.array([0, 0, 0, 1])
        else:
            assert False, f'unsupported light type: {object.data.type}'

        self.lights[i] = dir.tolist()
        self.light_color[i] = color.tolist()

    def render_object(self, object):
        self.trans.model = np.array(object.matrix_world)

        verts, faces = self.cache.lookup(blender_get_object_mesh, object)

        self.set_mesh(verts, faces)
        self.render(self.shader)

    def update_region_data(self, region3d):
        self.trans.proj = np.array(region3d.perspective_matrix)
        self.trans.view = np.eye(4)

    def update_default_camera(self):
        camera = bpy.context.scene.camera
        render = bpy.context.scene.render
        depsgraph = bpy.context.evaluated_depsgraph_get()
        self.trans.proj = np.array(camera.calc_matrix_camera(depsgraph,
            x=render.resolution_x, y=render.resolution_y,
            scale_x=render.pixel_aspect_x, scale_y=render.pixel_aspect_y))
        self.trans.view = np.linalg.inv(np.array(camera.matrix_world))

    def render_pixels(self, pixels, width, height):
        self.render_scene()
        use_bilerp = not (width == self.res.x and height == self.res.y)
        self.output.dump(self.color, use_bilerp, pixels, width, height)

    def invalidate_callback(self, update):
        object = update.id
        if update.is_updated_geometry:
            self.cache.invalidate(object)


def bmesh_verts_to_numpy(bm):
    arr = [x.co for x in bm.verts]
    if len(arr) == 0:
        print('Warning: no vertices!')
        return np.zeros((0, 3), dtype=np.float32)
    return np.array(arr, dtype=np.float32)


def bmesh_faces_to_numpy(bm):
    arr = [[y.index for y in x.verts] for x in bm.faces]
    if len(arr) == 0:
        print('Warning: no faces!')
        return np.zeros((0, 3), dtype=np.int32)
    return np.array(arr, dtype=np.int32)


def blender_get_object_mesh(object):
    import bmesh
    bm = bmesh.new()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    object_eval = object.evaluated_get(depsgraph)
    bm.from_object(object_eval, depsgraph)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    verts = bmesh_verts_to_numpy(bm)
    faces = bmesh_faces_to_numpy(bm)
    return verts, faces
