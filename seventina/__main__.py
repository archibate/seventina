from .engine import Engine
from .shader import Shader
from .camera import Camera, lookat
from .control import Control
from .assimp import readobj
import taichi as ti
import numpy as np
import ezprof

engine = Engine()
shader = Shader()
camera = Camera()
o = readobj('assets/monkey.obj', 'xyZ')
verts, faces = o['v'], o['f'][:, :, 0]
@ti.func
def _():
    for i in range(len(faces)):
        yield i
engine.get_faces_range = _

img = ti.Vector.field(3, float, engine.res)

gui = ti.GUI('monkey', engine.res)
with ezprof.scope('set_mesh'):
    engine.set_mesh(verts, faces)

while gui.running:
    with ezprof.scope('control'):
        ctl = Control(gui)
        ctl.update()
        camera.view = ctl.make_view()

    with ezprof.scope('set_camera'):
        engine.set_camera(camera)

    with ezprof.scope('clear'):
        img.fill(0)
        engine.clear_depth()

    with ezprof.scope('render'):
        engine.render(img, shader)

    with ezprof.scope('set_image'):
        gui.set_image(img)

    gui.show()


ezprof.show()
