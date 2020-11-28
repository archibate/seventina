from .utils import *


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
        for f in ti.smart(self.get_faces_range()):
            A, B, C = self.get_face_vertices(f)
            for pos, wei in ti.smart(self.draw_trip(A.xy, B.xy, C.xy)):
                P = int(pos)
                depth = wei.x * A.z + wei.y * B.z + wei.z * C.z
                if ti.atomic_min(self.depth[P], depth) > depth:
                    self.occup[P] = f + 1

    def get_faces_range(self):
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

            self.color[P] = self.interp(wei)

    def interp(self):
        raise NotImplementedError


class DynamicPainter(Painter):
    def __init__(self, N, maxverts, maxfaces):
        super().__init__(N)

        self.maxverts, self.maxfaces = maxverts, maxfaces
        self.verts = ti.Vector.field(3, float, self.maxverts)
        self.faces = ti.Vector.field(3, int, self.maxfaces)
        self.nfaces = ti.field(int, ())

    @ti.func
    def interp(self, wei):
        return wei

    @ti.func
    def get_faces_range(self):
        for i in range(self.nfaces[None]):
            yield i

    @ti.func
    def get_face_vertices(self, f):
        face = self.faces[f]
        A, B, C = self.verts[face.x], self.verts[face.y], self.verts[face.z]
        return A, B, C


class Main(Painter):
    def __init__(self, N=(512, 512)):
        super().__init__(N)

        from .assimp import readobj

        obj = readobj('assets/monkey.obj')
        obj['v'] *= 256
        obj['v'] += 256

        self.verts = ti.Vector.field(3, float, len(obj['v']))
        self.faces = ti.Vector.field(3, int, len(obj['f']))

        import ezprof
        with ezprof.scope('init0'):
            self.faces.from_numpy(obj['f'])
            self.verts.from_numpy(obj['v'])

    @ti.func
    def interp(self, wei):
        return wei

    @ti.func
    def get_faces_range(self):
        for i in self.faces:
            yield i

    @ti.func
    def get_face_vertices(self, f):
        face = self.faces[f]
        A, B, C = self.verts[face.x], self.verts[face.y], self.verts[face.z]
        return A, B, C

    def main(self):
        import ezprof
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
        ezprof.show()
