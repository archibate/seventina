import taichi as ti
import ezprof

from utils import *


@ti.data_oriented
class RasterizerMethods:
    def __init__(self, N):
        self.N = tovector(N)

    @ti.func
    def calc_line(self, src, dst):
        dlt = dst - src
        adlt = abs(dlt)
        kx, ky, siz = 1.0, 1.0, 0.0
        if adlt.x >= adlt.y:
            kx = 1.0 if dlt.x >= 0 else -1.0
            ky = kx * dlt.y / dlt.x
            siz = adlt.x
        else:
            ky = 1.0 if dlt.y >= 0 else -1.0
            kx = ky * dlt.x / dlt.y
            siz = adlt.y
        return V(kx, ky), int(siz)

    @ti.func
    def draw_line(self, src, dst):
        kel, siz = self.calc_line(src, dst)
        for i in range(siz + 1):
            pos = src + kel * i
            yield pos

    @ti.func
    def draw_trip(self, a, b, c):
        bot, top = ifloor(min(a, b, c)), iceil(max(a, b, c))
        n = abs((b - a).cross(c - a))
        abn = (a - b) / n
        bcn = (b - c) / n
        can = (c - a) / n
        ab = (a - b).normalized()
        bc = (b - c).normalized()
        ca = (c - a).normalized()
        for i, j in ti.ndrange((bot.x, top.x + 1), (bot.y, top.y + 1)):
            pos = float(V(i, j))
            d_ab = (pos - a).cross(ab)
            d_bc = (pos - b).cross(bc)
            d_ca = (pos - c).cross(ca)
            dis = V(d_bc, d_ca, d_ab)
            if all(dis >= -0.5) or all(dis <= 0.5):
                w_bc = (pos - b).cross(bcn)
                w_ca = (pos - c).cross(can)
                wei = V(w_bc, w_ca, 1 - w_bc - w_ca)
                yield pos, wei


class Rasterizer(RasterizerMethods):
    def __init__(self, N, verts, faces):
        super().__init__(N)
        self.verts = verts
        self.faces = faces
        self.occup = ti.field(int, self.N)
        self.depth = ti.field(float, self.N)

    @ti.kernel
    def raster(self):
        for i, j in self.occup:
            self.occup[i, j] = 0
            self.depth[i, j] = 1e6
        for f in self.faces:
            face = self.faces[f]
            A, B, C = self.verts[face.x], self.verts[face.y], self.verts[face.z]
            for pos, wei in ti.smart(self.draw_trip(A.xy, B.xy, C.xy)):
                P = int(pos)
                depth = wei.x * A.z + wei.y * B.z + wei.z * C.z
                if ti.atomic_min(self.depth[P], depth) >= depth:
                    self.occup[P] = f + 1


class RasterizerPaint(Rasterizer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = ti.Vector.field(3, float, self.N)

    @ti.kernel
    def paint(self):
        for P in ti.grouped(self.occup):
            f = self.occup[P] - 1
            if f == -1:
                continue
            face = self.faces[f]
            A, B, C = self.verts[face.x], self.verts[face.y], self.verts[face.z]
            a, b, c = A.xy, B.xy, C.xy
            n = abs((b - a).cross(c - a))
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


class RasterizerMain(RasterizerPaint):
    def __init__(self, N=(512, 512)):
        verts = ti.Vector.field(3, float, 6)
        faces = ti.Vector.field(3, int, 2)
        super().__init__(N, verts, faces)

        with ezprof.scope('init0'):
            faces.from_numpy(np.array([
                (0, 1, 2), (3, 4, 5),
                ], dtype=np.int32))
            verts.from_numpy(np.array([
                (0, 0, 128), (512, 0, 128), (256, 512, 128),
                (256, 0, 0), (512, 512, 128), (0, 512, 256),
                ], dtype=np.float32))

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
RasterizerMain().main()
ezprof.show()
