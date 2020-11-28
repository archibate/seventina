import taichi as ti

from utils import *


@ti.data_oriented
class Raster:
    def __init__(self):
        self.N = 64
        self.img = ti.field(float, (self.N, self.N))

    @ti.func
    def draw_line(self, src, dst):
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
        for i in range(int(siz) + 1):
            x = src.x + kx * i
            y = src.y + ky * i
            pos = V(x, y)
            yield pos

    @ti.func
    def draw_trip(self, a, b, c):
        for pos in ti.smart(self.draw_line(a, c)):
            yield pos
        for pos in ti.smart(self.draw_line(a, b)):
            yield pos
        for pos in ti.smart(self.draw_line(b, c)):
            yield pos

    @ti.kernel
    def render(self, mx: float, my: float):
        a, b, c = V(self.N-2, self.N-4), V(self.N//2, self.N//2), V(mx, my)
        for pos in ti.smart(self.draw_trip(a, b, c)):
            self.img[int(pos)] = 1

    def main(self):
        gui = ti.GUI('raster')
        while gui.running and not gui.get_event(gui.ESCAPE):
            self.img.fill(0)
            mx, my = gui.get_cursor_pos()
            self.render(mx * self.N, my * self.N)
            gui.set_image(ti.imresize(self.img, 512))
            gui.show()


Raster().main()
