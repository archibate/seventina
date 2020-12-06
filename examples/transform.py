import taichi as ti
import numpy as np
from tina.common import *

ti.init(ti.opengl)

engine = tina.Engine((1024, 768), smoothing=True)
camera = tina.Camera()

img = ti.Vector.field(3, float, engine.res)

shader = tina.SimpleShader(img)

obj = tina.readobj('assets/monkey.obj')
verts = obj['v'][obj['f'][:, :, 0]]
norms = obj['vn'][obj['f'][:, :, 2]]

gui = ti.GUI('transform', engine.res, fast_gui=True)
control = tina.Control(gui)

while gui.running:
    control.get_camera(camera)
    camera.model = tina.translate([ti.sin(gui.frame * 0.1), 0, 0])
    engine.set_camera(camera)

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.set_face_norms(norms)
    engine.render(shader)

    gui.set_image(img)
    gui.show()
