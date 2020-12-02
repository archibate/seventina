from ..common import *


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
        bot, top = max(bot, 0), min(top, self.res - 1)
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

    def __init__(self, res=512, maxfaces=65536,
            smoothing=False, culling=True, clipping=False):

        self.res = tovector((res, res) if isinstance(res, int) else res)
        self.culling = culling
        self.clipping = clipping
        self.smoothing = smoothing

        self.depth = ti.field(float, self.res)

        self.nfaces = ti.field(int, ())
        self.verts = ti.Vector.field(3, float, (maxfaces, 3))
        if self.smoothing:
            self.norms = ti.Vector.field(3, float, (maxfaces, 3))

        self.L2V = ti.Matrix.field(4, 4, float, ())
        self.L2W = ti.Matrix.field(4, 4, float, ())
        self.C2L = ti.Matrix.field(4, 4, float, ())

        @ti.materialize_callback
        @ti.kernel
        def init_engine():
            self.C2L[None] = ti.Matrix.identity(float, 4)
            self.L2W[None] = ti.Matrix.identity(float, 4)
            self.L2V[None] = ti.Matrix.identity(float, 4)
            self.L2V[None][2, 2] = -1

        ti.materialize_callback(self.clear_depth)

    @ti.func
    def to_viewspace(self, p):
        return mapply_pos(self.L2V[None], p)

    @ti.func
    def to_viewport(self, p):
        return (p.xy * 0.5 + 0.5) * self.res

    @ti.kernel
    def render(self, shader: ti.template()):
        for f in ti.smart(self.get_faces_range()):
            Al, Bl, Cl = self.get_face_vertices(f)
            Av, Bv, Cv = [self.to_viewspace(p) for p in [Al, Bl, Cl]]
            facing = (Bv.xy - Av.xy).cross(Cv.xy - Av.xy)
            if facing <= 0:
                if ti.static(self.culling):
                    continue
                else:
                    Al, Bl, Cl = Al, Cl, Bl

            if ti.static(self.clipping):
                if not all(-1 <= Av <= 1):
                    if not all(-1 <= Bv <= 1):
                        if not all(-1 <= Cv <= 1):
                            continue

            Ai, Bi, Ci = [self.to_viewport(p) for p in [Av, Bv, Cv]]
            wfac = 1 / V(*[mapply(self.L2V[None], p, 1)[1] for p in [Al, Bl, Cl]])
            for pos, wei in ti.smart(self.draw_trip(Ai, Bi, Ci)):
                P = int(pos)
                depth = wei.x * Av.z + wei.y * Bv.z + wei.z * Cv.z
                if ti.atomic_min(self.depth[P], depth) > depth:
                    wei *= wfac
                    wei /= wei.x + wei.y + wei.z
                    self.interpolate(shader, P, f, facing, wei, Al, Bl, Cl)

    @ti.kernel
    def clear_depth(self):
        for P in ti.grouped(self.depth):
            self.depth[P] = 1e6

    @ti.func
    def interpolate(self, shader: ti.template(), P, f, facing, wei, A, B, C):
        pos = wei.x * A + wei.y * B + wei.z * C
        normal = V(0., 0., 0.)
        if ti.static(self.smoothing):
            An, Bn, Cn = self.get_face_normals(f)
            # TODO: actually we need to slerp normal?
            normal = (wei.x * An + wei.y * Bn + wei.z * Cn).normalized()
            if ti.static(not self.culling):
                if facing < 0:
                    normal = -normal
        else:
            normal = (B - A).cross(C - A).normalized()
        shader.shade_color(self, P, f, pos, normal)

    @ti.func
    def get_faces_range(self):
        for i in range(self.nfaces[None]):
            yield i

    @ti.func
    def get_face_vertices(self, f):
        A, B, C = self.verts[f, 0], self.verts[f, 1], self.verts[f, 2]
        return A, B, C

    @ti.func
    def get_face_normals(self, f):
        A, B, C = self.norms[f, 0], self.norms[f, 1], self.norms[f, 2]
        return A, B, C

    @ti.kernel
    def set_face_verts(self, verts: ti.ext_arr()):
        self.nfaces[None] = min(verts.shape[0], self.verts.shape[0])
        for i in range(self.nfaces[None]):
            for k in ti.static(range(3)):
                for l in ti.static(range(3)):
                    self.verts[i, k][l] = verts[i, k, l]

    @ti.kernel
    def set_face_norms(self, norms: ti.ext_arr()):
        for i in range(self.nfaces[None]):
            for k in ti.static(range(3)):
                for l in ti.static(range(3)):
                    self.norms[i, k][l] = norms[i, k, l]

    def set_trans(self, trans):
        L2W = trans.model
        L2V = trans.proj @ trans.view @ trans.model
        C2L = np.linalg.inv(trans.view @ trans.model)
        self.L2V.from_numpy(np.array(L2V, dtype=np.float32))
        self.L2W.from_numpy(np.array(L2W, dtype=np.float32))
        self.C2L.from_numpy(np.array(C2L, dtype=np.float32))
