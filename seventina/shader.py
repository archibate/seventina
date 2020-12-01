from .utils import *


@ti.data_oriented
class MagentaShader:
    def __init__(self, color):
        self.color = color

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        self.color[P] = V(1.0, 0.0, 1.0)


@ti.data_oriented
class PositionShader:
    def __init__(self, color):
        self.color = color

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        pos = mapply_pos(engine.L2W[None], pos)
        self.color[P] = pos


@ti.data_oriented
class NormalShader:
    def __init__(self, color):
        self.color = color

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        normal = mapply_dir(engine.L2W[None], normal)
        self.color[P] = normal * 0.5 + 0.5


@ti.data_oriented
class Shader:
    def __init__(self, color):
        self.color = color

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        pos = mapply_pos(engine.L2W[None], pos)
        normal = mapply_dir(engine.L2W[None], normal)

        final = V(0.0, 0.0, 0.0)
        for l in ti.smart(engine.get_lights_range()):
            light, lcolor = engine.get_light_data(l)
            light_dir = light.xyz - pos * light.w
            light_dist = light_dir.norm()
            lcolor /= light_dist**2
            light_dir /= light_dist
            color = lcolor * max(0, normal.dot(light_dir))
            final += color

        self.color[P] = final
