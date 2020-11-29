from utils import *


EPS = 1e-6
INF = 1e8


@ti.func
def reflect(I, N):
    return I - 2 * N.dot(I) * N


@ti.func
def sphere_intersect(s_pos, s_rad, r_org, r_dir):
    i_t = INF
    op = s_pos - r_org
    b = op.dot(r_dir)
    det = b**2 - op.norm_sqr() + s_rad**2
    if det >= 0:
        det = ti.sqrt(det)
        i_t = b - det
        if i_t <= EPS:
            i_t = b + det
            if i_t <= EPS:
                i_t = INF
    i_pos = r_org + i_t * r_dir
    i_nrm = (i_pos - s_pos).normalized()
    return i_t, i_pos, i_nrm


@ti.func
def union_intersect(ret1, ret2):
    t, pos, nrm = ret1
    if ret2[0] < t:
        t, pos, nrm = ret2
    return t, pos, nrm


@ti.data_oriented
class PathEngine:
    def __init__(self, res=(512, 512)):
        self.res = tovector(res)

        self.nrays = V(self.res.x, self.res.y, 1)

        self.count = ti.field(int, self.res)
        self.screen = ti.Vector.field(3, float, self.res)
        self.ray_org = ti.Vector.field(3, float, self.nrays)
        self.ray_dir = ti.Vector.field(3, float, self.nrays)
        self.ray_color = ti.Vector.field(3, float, self.nrays)

    @ti.func
    def generate_ray(self, I):
        coor = I / self.res * 2 - 1
        org = V23(coor, -1.)
        dir = V(0., 0., 1.)
        return org, dir

    @ti.kernel
    def generate_rays(self):
        for r in ti.grouped(self.ray_org):
            I = r.xy + V(ti.random(), ti.random())
            org, dir = self.generate_ray(I)
            self.ray_org[r] = org
            self.ray_dir[r] = dir
            self.ray_color[r] = V(1., 1., 1.)

    @ti.func
    def intersect(self, org, dir):
        ret1 = sphere_intersect(V(+.5, 0., 0.), 0.4, org, dir)
        ret2 = sphere_intersect(V(-.5, 0., 0.), 0.4, org, dir)
        ret = union_intersect(ret1, ret2)
        return ret

    @ti.func
    def bounce_ray(self, org, dir, i_pos, i_nrm):
        org = i_pos + i_nrm * EPS
        dir = reflect(dir, i_nrm)
        #dir *= 0
        return V(1., 1., 1.), org, dir

    @ti.kernel
    def step_rays(self):
        for r in ti.grouped(self.ray_org):
            if all(self.ray_dir[r] == 0):
                continue

            org = self.ray_org[r]
            dir = self.ray_dir[r]
            t, i_pos, i_nrm = self.intersect(org, dir)
            if t >= INF:
                self.ray_color[r] *= 0
                self.ray_dir[r] *= 0
            else:
                color, org, dir = self.bounce_ray(org, dir, i_pos, i_nrm)
                self.ray_color[r] *= color
                self.ray_org[r] = org
                self.ray_dir[r] = dir

    @ti.kernel
    def update_screen(self):
        for I in ti.grouped(self.screen):
            for samp in range(self.nrays.z):
                r = V23(I, samp)
                color = self.ray_color[r]
                count = self.count[I]
                self.screen[I] *= count / (count + 1)
                self.screen[I] += color / (count + 1)
                self.count[I] += 1

    def main(self):
        self.generate_rays()
        self.step_rays()
        self.step_rays()
        self.update_screen()
        ti.imshow(ti.imresize(self.screen, 512))


PathEngine().main()
