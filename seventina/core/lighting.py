from ..common import *


@ti.data_oriented
class Lighting:
    def __init__(self, maxlights=16):
        self.lights = ti.Vector.field(4, float, maxlights)
        self.light_color = ti.Vector.field(3, float, maxlights)
        self.ambient = ti.Vector.field(3, float, ())
        self.nlights = ti.field(int, ())

        @ti.materialize_callback
        @ti.kernel
        def init_lights():
            self.nlights[None] = 1
            self.lights[0] = [0, 0, 1, 0]
            for i in self.lights:
                self.light_color[i] = [1, 1, 1]

    def set_lights(self, lights):
        self.nlights[None] = len(lights)
        for i, (dir, color) in enumerate(lights):
            self.lights[i] = dir
            self.light_color[i] = color

    def set_ambient_light(self, color):
        self.ambient[None] = np.array(color).tolist()

    @ti.func
    def get_lights_range(self):
        for i in range(self.nlights[None]):
            yield i

    @ti.func
    def get_light_data(self, l):
        return self.lights[l], self.light_color[l]

    @ti.func
    def get_ambient_light_color(self):
        return self.ambient[None]
