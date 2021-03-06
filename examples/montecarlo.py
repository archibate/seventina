from tina.common import *
from tina.advans import *
from tina.core.shader import calc_view_dir


ti.init(ti.opengl)


class SkyboxShader(tina.Shader):
    def __init__(self, img, material=None):
        self.img = img
        self.material = material
        self.nsamples = 2

        self.skybox = texture_as_field('assets/skybox.jpg')

    @ti.func
    def shade_color(self, engine, P, f, pos, normal):
        pos = mapply_pos(engine.L2W[None], pos)
        normal = mapply_dir(engine.L2W[None], normal).normalized()
        view_dir = calc_view_dir(engine, pos)

        res = V(0.0, 0.0, 0.0)

        if ti.static(self.material is None):
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

        self.img[P] = res


engine = tina.Engine(smoothing=True)
camera = tina.Camera()
accum = tina.Accumator(engine.res)

img = ti.Vector.field(3, float, engine.res)

material = tina.CookTorrance(metallic=1.0, roughness=0.3)
shader = SkyboxShader(img, material)

obj = tina.readobj('assets/sphere.obj')
verts = obj['v'][obj['f'][:, :, 0]]
norms = obj['vn'][obj['f'][:, :, 2]]

gui = ti.GUI('skybox', engine.res)
control = tina.Control(gui)

metallic = gui.slider('metallic', 0.0, 1.0, 0.1)
roughness = gui.slider('roughness', 0.0, 1.0, 0.1)
specular = gui.slider('specular', 0.0, 1.0, 0.1)

metallic.value = material.metallic[None]
roughness.value = material.roughness[None]
specular.value = material.specular[None]

while gui.running:
    if control.get_camera(camera):
        accum.clear()

    engine.set_camera(camera)

    material.metallic[None] = metallic.value
    material.roughness[None] = roughness.value
    material.specular[None] = specular.value

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.set_face_norms(norms)
    engine.render(shader)

    accum.update(img)

    gui.set_image(tina.aces_tonemap(accum.img.to_numpy()))
    gui.show()
