from .utils import *


@ti.data_oriented
class Shader:
    @ti.func
    def shade_color(self, engine, pos, normal):
        pos = mapply_pos(engine.L2W[None], pos)
        normal = mapply_dir(engine.L2W[None], normal)

        final = V(0.0, 0.0, 0.0)
        for l in ti.smart(engine.get_lights_range()):
            light, lcolor = engine.get_light_vector(l)
            light_dir = light.xyz - pos * light.w
            light_dist = light_dir.norm()
            lcolor /= light_dist**2
            light_dir /= light_dist
            color = lcolor * max(0, normal.dot(light_dir))
            final += color
        return final
