import taichi as ti
import ezprof

from utils import *


@ti.data_oriented
class Rasterizer:
    def __init__(self):
        self.N = 64
        self.img = ti.field(float, (self.N, self.N))

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
        ba = (b - a).normalized()
        cb = (c - b)#.normalized()
        ac = (a - c)#.normalized()
        for i, j in ti.ndrange((bot.x, top.x + 1), (bot.y, top.y + 1)):
            pos = float(V(i, j))
            d_ab = (pos - a).cross(ba)
            d_bc = (pos - b).cross(cb)
            d_ca = (pos - c).cross(ac)
            dis = V(d_bc, d_ca, d_ab)
            if all(dis > 0) or all(dis < 0):
                yield pos

    @ti.kernel
    def render(self, mx: float, my: float):
        for ensure_serial in range(1):
            a = V(self.N//4, self.N//2)
            b = V(self.N*3//4, self.N//2)
            c = V(mx, my)
            for pos in ti.smart(self.draw_trip(a, b, c)):
                self.img[int(pos)] = 1

    def main(self):
        gui = ti.GUI('raster')
        with ezprof.scope('compile'):
            self.render(0, 0)
        while gui.running and not gui.get_event(gui.ESCAPE):
            self.img.fill(0)
            mx, my = gui.get_cursor_pos()
            with ezprof.scope('render', warmup=5):
                self.render(mx * self.N, my * self.N)
            gui.set_image(ti.imresize(self.img, 512))
            gui.show()


ti.init(print_ir=True)
Rasterizer().main()
ezprof.show()
