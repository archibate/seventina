import taichi as ti
import numpy as np

from seventina import tina

ti.init(ti.opengl)

engine = tina.Engine(512)
trans = tina.Trans()

img = ti.Vector.field(3, float, engine.res)

environ = tina.Environ()
material = tina.CookTorrance()
shader = tina.Shader(img, environ, material)

o = tina.readobj('assets/sphere.obj')
verts = o['v'][o['f'][:, :, 0]]

gui = ti.GUI('monkey', engine.res, fast_gui=True)
control = tina.Control(gui)

engine.set_face_verts(verts)

while gui.running:
    control.get_trans(trans)
    engine.set_trans(trans)

    img.fill(0)
    engine.clear_depth()

    engine.render(shader)

    gui.set_image(img)
    gui.show()
