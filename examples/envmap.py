from seventina.common import *
from seventina.core.shader import calc_view_dir


ti.init(ti.opengl)


@ti.func
def tangentspace(nrm):
    up = V(0., 1., 0.)
    bitan = nrm.cross(up).normalized()
    tan = bitan.cross(nrm)
    return ti.Matrix.cols([tan, bitan, nrm])


@ti.func
def spherical(h, p):
    unit = V(ti.cos(p * ti.tau), ti.sin(p * ti.tau))
    dir = V23(ti.sqrt(1 - h**2) * unit, h)
    return dir


@ti.func
def unspherical(dir):
    p = ti.atan2(dir.y, dir.x) / ti.tau
    return dir.z, p


@ti.func
def sample_cube(tex: ti.template(), dir):
    I = V(0., 0.)
    eps = 1e-5
    dps = 1 - 12 / tex.shape[0]
    dir.y, dir.z = dir.z, -dir.y
    if dir.z >= 0 and dir.z >= abs(dir.y) - eps and dir.z >= abs(dir.x) - eps:
        I = V(3 / 8, 3 / 8) + V(dir.x, dir.y) / dir.z / 8 * dps
    if dir.z <= 0 and -dir.z >= abs(dir.y) - eps and -dir.z >= abs(dir.x) - eps:
        I = V(7 / 8, 3 / 8) + V(-dir.x, dir.y) / -dir.z / 8 * dps
    if dir.x <= 0 and -dir.x >= abs(dir.y) - eps and -dir.x >= abs(dir.z) - eps:
        I = V(1 / 8, 3 / 8) + V(dir.z, dir.y) / -dir.x / 8 * dps
    if dir.x >= 0 and dir.x >= abs(dir.y) - eps and dir.x >= abs(dir.z) - eps:
        I = V(5 / 8, 3 / 8) + V(-dir.z, dir.y) / dir.x / 8 * dps
    if dir.y >= 0 and dir.y >= abs(dir.x) - eps and dir.y >= abs(dir.z) - eps:
        I = V(3 / 8, 5 / 8) + V(dir.x, -dir.z) / dir.y / 8 * dps
    if dir.y <= 0 and -dir.y >= abs(dir.x) - eps and -dir.y >= abs(dir.z) - eps:
        I = V(3 / 8, 1 / 8) + V(dir.x, dir.z) / -dir.y / 8 * dps
    I = V(tex.shape[0], tex.shape[0]) * I
    return bilerp(tex, I)


def texture_as_field(filename):
    img_np = np.float32(ti.imread(filename) / 255)
    img = ti.Vector.field(3, float, img_np.shape[:2])

    @ti.materialize_callback
    def init_texture():
        img.from_numpy(img_np)

    return img


class SkyboxShader(tina.Shader):
    def __init__(self, color, material):
        self.color = color
        self.material = material
        self.nsamples = 4

        self.skybox = texture_as_field('assets/skybox.jpg')

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        pos = mapply_pos(engine.L2W[None], pos)
        normal = mapply_dir(engine.L2W[None], normal).normalized()
        view_dir = calc_view_dir(engine, pos)

        res = V(0.0, 0.0, 0.0)

        if ti.static(0):
            refl_dir = reflect(-view_dir, normal)
            lcolor = sample_cube(self.skybox, refl_dir)

            res += lcolor

        else:
            for i in range(self.nsamples):
                cos_i = ti.random()
                phi_pi = ti.random()
                light_dir = tangentspace(normal) @ spherical(cos_i, phi_pi)

                lcolor = sample_cube(self.skybox, light_dir)
                mcolor = self.material.brdf(normal, light_dir, view_dir)

                res += cos_i * lcolor * mcolor

        self.color[P] = res


engine = tina.Engine(smoothing=True)
camera = tina.Camera()

img = ti.Vector.field(3, float, engine.res)

lighting = tina.Lighting()
material = tina.CookTorrance()
shader = SkyboxShader(img, material)

obj = tina.readobj('assets/sphere.obj')
verts = obj['v'][obj['f'][:, :, 0]]
norms = obj['vn'][obj['f'][:, :, 2]]

gui = ti.GUI('matball', engine.res)
control = tina.Control(gui)

metallic = gui.slider('metallic', 0.0, 1.0, 0.1)
roughness = gui.slider('roughness', 0.0, 1.0, 0.1)
specular = gui.slider('specular', 0.0, 1.0, 0.1)

metallic.value = material.metallic[None]
roughness.value = material.roughness[None]
specular.value = material.specular[None]

while gui.running:
    control.get_camera(camera)
    engine.set_camera(camera)

    material.metallic[None] = metallic.value
    material.roughness[None] = roughness.value
    material.specular[None] = specular.value

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.set_face_norms(norms)
    engine.render(shader)

    gui.set_image(tina.aces_tonemap(img.to_numpy()))
    gui.show()
