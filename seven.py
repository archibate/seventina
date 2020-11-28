import taichi as ti
import ezprof

from utils import *
from assimp import readobj, objorient


@ti.data_oriented
class Rasterizer:
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

    def __init__(self, N):
        self.N = tovector(N)
        self.occup = ti.field(int, self.N)
        self.depth = ti.field(float, self.N)

    @ti.kernel
    def raster(self):
        for i, j in self.occup:
            self.occup[i, j] = 0
            self.depth[i, j] = 1e6
        for f in range(self.get_num_faces()):
            A, B, C = self.get_face_vertices(f)
            for pos, wei in ti.smart(self.draw_trip(A.xy, B.xy, C.xy)):
                P = int(pos)
                depth = wei.x * A.z + wei.y * B.z + wei.z * C.z
                if ti.atomic_min(self.depth[P], depth) > depth:
                    self.occup[P] = f + 1

    def get_num_faces(self):
        raise NotImplementedError

    def get_face_vertices(self, f):
        raise NotImplementedError


class Painter(Rasterizer):
    def __init__(self, N):
        super().__init__(N)
        self.color = ti.Vector.field(3, float, self.N)

    @ti.kernel
    def paint(self):
        for P in ti.grouped(self.occup):
            f = self.occup[P] - 1
            if f == -1:
                continue
            A, B, C = self.get_face_vertices(f)
            a, b, c = A.xy, B.xy, C.xy
            n = (b - a).cross(c - a)
            abn = (a - b) / n
            bcn = (b - c) / n
            can = (c - a) / n
            w_bc = (P - b).cross(bcn)
            w_ca = (P - c).cross(can)
            wei = V(w_bc, w_ca, 1 - w_bc - w_ca)

            clra = float(V(1, 0, 0))
            clrb = float(V(0, 1, 0))
            clrc = float(V(0, 0, 1))
            color = wei.x * clra + wei.y * clrb + wei.z * clrc
            self.color[P] = color


class Main(Painter):
    def __init__(self, N=(512, 512)):
        obj = readobj('torus.obj')
        obj['v'] *= 256
        obj['v'] += 256

        self.verts = ti.Vector.field(3, float, len(obj['v']))
        self.faces = ti.Vector.field(3, int, len(obj['f']))

        super().__init__(N)

        with ezprof.scope('init0'):
            self.faces.from_numpy(obj['f'])
            self.verts.from_numpy(obj['v'])

    @ti.func
    def get_num_faces(self):
        return self.faces.shape[0]

    @ti.func
    def get_face_vertices(self, f):
        face = self.faces[f]
        A, B, C = self.verts[face.x], self.verts[face.y], self.verts[face.z]
        return A, B, C

    def main(self):
        gui = ti.GUI('raster')
        with ezprof.scope('raster0'):
            self.raster()
        with ezprof.scope('paint0'):
            self.paint()
        while gui.running and not gui.get_event(gui.ESCAPE):
            with ezprof.scope('raster'):
                self.raster()
            with ezprof.scope('paint'):
                self.paint()
            gui.set_image(ti.imresize(self.color, 512))
            gui.show()


ti.init()
Main().main()
ezprof.show()
