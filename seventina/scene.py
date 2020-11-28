from .utils import *
from .raster import DynamicPainter


@ti.data_oriented
class BlenderOutput:
    def _cook(self, color):
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

    @ti.func
    def color_at(self, img: ti.template(), i, j, width, height):
        ti.static_assert(len(img.shape) == 2)
        scale = ti.Vector(img.shape) / ti.Vector([width, height])
        pos = ti.Vector([i, j]) * scale
        color = bilerp(img, pos)
        return self._cook(color)

    @ti.kernel
    def render(self, img: ti.template(), out: ti.ext_arr(), width: int, height: int):
        for i, j in ti.ndrange(width, height):
            r, g, b = self.color_at(img, i, j, width, height)
            base = (j * width + i) * 4
            out[base + 0] = r
            out[base + 1] = g
            out[base + 2] = b
            out[base + 3] = 1


class BlenderPainter(DynamicPainter):
    def __init__(self, N, maxverts, maxfaces):
        super().__init__(N, maxverts, maxfaces)

    @ti.func
    def interp(self, wei):
        return wei

    def _update_mesh_verts(self, verts: ti.ext_arr()):
        for i in range(verts.shape[0]):
            for k in ti.static(range(3)):
                self.verts[i][k] = verts[i, k]

    def _update_mesh_faces(self, faces: ti.ext_arr()):
        for i in range(faces.shape[0]):
            for k in ti.static(range(3)):
                self.faces[i][k] = faces[i, k]

    def update_mesh(self, verts, faces):
        self._update_mesh_verts(verts * 128 + 256)
        self._update_mesh_faces(faces)
        self.nfaces[None] = len(faces)


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
    import bpy
    import bmesh

    bm = bmesh.new()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    object_eval = object.evaluated_get(depsgraph)
    bm.from_object(object_eval, depsgraph)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    verts = bmesh_verts_to_numpy(bm)
    faces = bmesh_faces_to_numpy(bm)
    assert faces.shape[1] == 3
    return verts, faces


class BlenderScene:
    def __init__(self):
        self.painter = BlenderPainter((512, 512), 4096, 4096)
        self.output = BlenderOutput()

    def update_scene(self):
        import bpy

        verts, faces = blender_get_object_mesh(bpy.data.objects['Cube'])
        self.painter.update_mesh(verts, faces)

    def render(self, pixels, width, height):
        self.update_scene()
        self.painter.raster()
        self.painter.paint()
        self.output.render(self.painter.color, pixels, width, height)
