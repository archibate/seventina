from ..common import *


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
class DepthShader:
    def __init__(self, color):
        self.color = color

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        self.color[P] = engine.depth[P] / 4


@ti.data_oriented
class NormalShader:
    def __init__(self, color):
        self.color = color

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        normal = mapply_dir(engine.L2W[None], normal)
        self.color[P] = normal * 0.5 + 0.5


@ti.data_oriented
class ViewDirShader:
    def __init__(self, color):
        self.color = color

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        L2V = engine.L2V[None]
        V2L = L2V.inverse()
        pers_pos = mapply_pos(L2V, pos)
        pers_vdir = pers_pos
        vdir = mapply_dir(V2L, pers_vdir)
        view_dir = vdir.normalized()

        self.color[P] = view_dir# * 0.5 + 0.5


@ti.data_oriented
class SimpleShader:
    def __init__(self, color):
        self.color = color

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        normal = mapply_dir(engine.L2V[None], normal)

        self.color[P] = -normal.z


@ti.data_oriented
class Shader:
    def __init__(self, color, environ, material):
        self.color = color
        self.environ = environ
        self.material = material

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        camera_pos = mapply_pos(engine.C2L[None], V(0., 0., 0.))
        view_dir = (camera_pos - pos).normalized()

        pos = mapply_pos(engine.L2W[None], pos)
        normal = mapply_dir(engine.L2W[None], normal)
        view_dir = mapply_dir(engine.L2W[None], view_dir)

        res = V(0.0, 0.0, 0.0)
        res += self.environ.get_ambient_light_color()
        for l in ti.smart(self.environ.get_lights_range()):
            light, lcolor = self.environ.get_light_data(l)
            light_dir = light.xyz - pos * light.w
            cos_i = normal.dot(light_dir)
            if cos_i > 0:
                light_dist = light_dir.norm()
                light_dir /= light_dist
                lcolor /= light_dist**2
                mcolor = self.material.brdf(normal, light_dir, view_dir)
                res += cos_i * lcolor * mcolor

        self.color[P] = res
