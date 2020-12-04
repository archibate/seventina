import taichi as ti
import numpy as np

from seventina import t3

ti.init(ti.opengl)

engine = t3.Engine((1024, 768))
camera = t3.Camera()

img = ti.Vector.field(3, float, engine.res)

lighting = t3.Lighting()
material = t3.CookTorrance()
shader = t3.Shader(img, lighting, material)

obj = t3.readobj('assets/monkey.obj')
verts = obj['v'][obj['f'][:, :, 0]]

gui = ti.GUI('monkey', engine.res, fast_gui=True)
control = t3.Control(gui)

while gui.running:
    control.get_camera(camera)
    engine.set_camera(camera)

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.render(shader)

    gui.set_image(img)
    gui.show()
