import taichi as ti
import numpy as np

from seventina import tina

ti.init(ti.opengl)

engine = tina.Engine((1024, 768))
camera = tina.Camera()

img = ti.Vector.field(3, float, engine.res)

lighting = tina.Lighting()
material = tina.CookTorrance()
shader = tina.Shader(img, lighting, material)

obj = tina.readobj('assets/sphere.obj')
verts = obj['v'][obj['f'][:, :, 0]]

gui = ti.GUI('monkey', engine.res, fast_gui=True)
control = tina.Control(gui)

engine.set_face_verts(verts)

while gui.running:
    control.get_camera(camera)
    engine.set_camera(camera)

    img.fill(0)
    engine.clear_depth()

    engine.render(shader)

    gui.set_image(img)
    gui.show()
