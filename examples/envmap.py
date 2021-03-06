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

        refl_dir = reflect(-view_dir, normal)
        lcolor = sample_cube(self.skybox, refl_dir)
        self.img[P] = lcolor


engine = tina.Engine(smoothing=True)
camera = tina.Camera()

img = ti.Vector.field(3, float, engine.res)

shader = SkyboxShader(img)

obj = tina.readobj('assets/sphere.obj')
verts = obj['v'][obj['f'][:, :, 0]]
norms = obj['vn'][obj['f'][:, :, 2]]

gui = ti.GUI('skybox', engine.res)
control = tina.Control(gui)

while gui.running:
    control.get_camera(camera)
    engine.set_camera(camera)

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.set_face_norms(norms)
    engine.render(shader)

    gui.set_image(img)
    gui.show()
