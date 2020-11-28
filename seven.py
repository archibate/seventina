import taichi as ti

def V(*xs):
  return ti.cast(ti.Vector(xs), float)

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
            self.img[int(pos)] = 1

    @ti.kernel
    def render(self, mx: float, my: float):
        self.draw_line(V(self.N // 2, self.N // 2), V(mx, my))

    def main(self):
        gui = ti.GUI('raster')
        while gui.running and not gui.get_event(gui.ESCAPE):
            self.img.fill(0)
            mx, my = gui.get_cursor_pos()
            self.render(mx * self.N, my * self.N)
            gui.set_image(ti.imresize(self.img, 512))
            gui.show()

Raster().main()
