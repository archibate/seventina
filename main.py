import taichi as ti
import numpy as np
import sys

from seventina import tina

ti.init(ti.gpu)

obj = tina.readobj(sys.argv[1], scale='auto')
verts = obj['v'][obj['f'][:, :, 0]]
norms = obj['vn'][obj['f'][:, :, 2]]

engine = tina.Engine(maxfaces=len(verts), smoothing=True)
camera = tina.Camera()

img = ti.Vector.field(3, float, engine.res)

shader = tina.SimpleShader(img)

gui = ti.GUI('visualize', engine.res, fast_gui=True)
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
