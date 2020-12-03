import taichi as ti
import numpy as np

from seventina import tina

tina.inject

ti.init(ti.cuda)

engine = tina.Engine()
camera = tina.Camera()

img = ti.Vector.field(3, float, engine.res)

lighting = tina.Lighting()
material = tina.CookTorrance()
shader = tina.Shader(img, lighting, material)

obj = tina.readobj('assets/monkey.obj')
verts = obj['v'][obj['f'][:, :, 0]]

gui = ti.GUI('monkey', engine.res, fast_gui=True)
control = tina.Control(gui)

while gui.running:
    control.get_camera(camera)
    engine.set_camera(camera)

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.render(shader)

    gui.set_image(img)
    gui.show()
