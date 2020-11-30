from .utils import *


@ti.data_oriented
class Engine:
    @ti.func
    def draw_line(self, src, dst):
        dlt = dst - src
        adlt = abs(dlt)
        k, siz = V(1.0, 1.0), 0
        if adlt.x >= adlt.y:
            k.x = 1.0 if dlt.x >= 0 else -1.0
            k.y = k.x * dlt.y / dlt.x
            siz = int(adlt.x)
        else:
            k.y = 1.0 if dlt.y >= 0 else -1.0
            k.x = k.y * dlt.x / dlt.y
            siz = int(adlt.y)
        for i in range(siz + 1):
            pos = src + k * i
            yield pos, i / siz

    @ti.func
    def draw_trip(self, a, b, c):
        bot, top = ifloor(min(a, b, c)), iceil(max(a, b, c))
        bot, top = max(bot, 0), min(top, self.N - 1)
        n = (b - a).cross(c - a)
        abn = (a - b) / n
        bcn = (b - c) / n
        can = (c - a) / n
        for i, j in ti.ndrange((bot.x, top.x + 1), (bot.y, top.y + 1)):
            pos = float(V(i, j))
            w_bc = (pos - b).cross(bcn)
            w_ca = (pos - c).cross(can)
            wei = V(w_bc, w_ca, 1 - w_bc - w_ca)
            if all(wei >= 0):
                yield pos, wei

    def __init__(self, N, maxverts, maxfaces, maxlights):
        self.N = tovector(N)
        self.occup = ti.field(int, self.N)
        self.depth = ti.field(float, self.N)

        self.verts = ti.Vector.field(3, float, maxverts)
        self.faces = ti.Vector.field(3, int, maxfaces)
        self.nfaces = ti.field(int, ())

        self.L2V = ti.Matrix.field(4, 4, float, ())
        self.L2W = ti.Matrix.field(4, 4, float, ())

        self.lights = ti.Vector.field(4, float, maxlights)
        self.light_color = ti.Vector.field(3, float, maxlights)
        self.nlights = ti.field(int, ())

        @ti.materialize_callback
        @ti.kernel
        def _():
            self.L2V[None] = ti.Matrix.identity(float, 4)
            self.L2W[None] = ti.Matrix.identity(float, 4)
            for i, j in self.depth:
                self.depth[i, j] = 1e6

    @ti.func
    def to_viewspace(self, p):
        return mapply_pos(self.L2V[None], p)

    @ti.func
    def to_viewport(self, p):
        return (p.xy * 0.5 + 0.5) * self.N

    @ti.kernel
    def raster(self):
        for i, j in self.occup:
            self.occup[i, j] = 0
        for f in ti.smart(self.get_faces_range()):
            A, B, C = self.get_face_vertices(f)
            A, B, C = [self.to_viewspace(p) for p in [A, B, C]]
            a, b, c = [self.to_viewport(p) for p in [A, B, C]]
            for pos, wei in ti.smart(self.draw_trip(a, b, c)):
                P = int(pos)
                depth = wei.x * A.z + wei.y * B.z + wei.z * C.z
                if ti.atomic_min(self.depth[P], depth) > depth:
                    self.occup[P] = f + 1

    @ti.kernel
    def paint(self, color: ti.template(), shader: ti.template()):
        for P in ti.grouped(self.occup):
            f = self.occup[P] - 1
            if f == -1:
                continue

            A, B, C = self.get_face_vertices(f)
            a, b, c = [self.to_viewport(self.to_viewspace(p)) for p in [A, B, C]]
            n = (b - a).cross(c - a)
            abn = (a - b) / n
            bcn = (b - c) / n
            can = (c - a) / n
            w_bc = (P - b).cross(bcn)
            w_ca = (P - c).cross(can)
            wei = V(w_bc, w_ca, 1 - w_bc - w_ca)

            wei /= V(*[mapply(self.L2V[None], p, 1)[1] for p in [A, B, C]])
            wei /= wei.x + wei.y + wei.z
            color[P] = self.interpolate(shader, wei, A, B, C)

    @ti.kernel
    def clear_depth(self):
        for P in ti.grouped(self.depth):
            self.depth[P] = 1e6

    def render(self, color, shader):
        self.raster()
        self.paint(color, shader)

    @ti.func
    def interpolate(self, shader: ti.template(), wei, A, B, C):
        pos = wei.x * A + wei.y * B + wei.z * C
        normal = (B - A).cross(C - A).normalized()
        return shader.shade_color(self, pos, normal)

    @ti.func
    def get_faces_range(self):
        for i in range(self.nfaces[None]):
            yield i

    @ti.func
    def get_face_vertices(self, f):
        face = self.faces[f]
        A, B, C = self.verts[face.x], self.verts[face.y], self.verts[face.z]
        return A, B, C

    @ti.func
    def get_lights_range(self):
        for i in range(self.nlights[None]):
            yield i

    @ti.func
    def get_light_vector(self, l):
        return self.lights[l], self.light_color[l]
