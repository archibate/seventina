import taichi as ti
import numpy as np
import seventina as t3
import sys

ti.init(ti.gpu)

obj = t3.readobj(sys.argv[1], scale='auto')
verts = obj['v'][obj['f'][:, :, 0]]
norms = obj['vn'][obj['f'][:, :, 2]]

engine = t3.Engine((1024, 768), maxfaces=len(verts), smoothing=True)
camera = t3.Camera()

img = ti.Vector.field(3, float, engine.res)

shader = t3.SimpleShader(img)

gui = ti.GUI('visualize', engine.res, fast_gui=True)
control = t3.Control(gui)

accum = t3.Accumator(engine.res)

while gui.running:
    engine.randomize_bias(accum.count[None] <= 1)

    if control.get_camera(camera):
        accum.clear()
    engine.set_camera(camera)

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.set_face_norms(norms)
    engine.render(shader)

    accum.update(img)
    gui.set_image(accum.img)
    gui.show()
