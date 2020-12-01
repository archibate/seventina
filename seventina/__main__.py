from .engine import Engine
from .shader import PositionShader as Shader
from .camera import Camera
from .control import Control
from .assimp import readobj
import taichi as ti
import numpy as np
import ezprof

engine = Engine()

img = ti.Vector.field(3, float, engine.res)
shader = Shader(img)
camera = Camera()

o = readobj('assets/monkey.obj', 'xZy')
verts, faces = o['v'], o['f'][:, :, 0]

gui = ti.GUI('monkey', engine.res)
ctl = Control(gui)

engine.set_mesh(verts, faces)

while gui.running:
    ctl.update()
    camera.view = ctl.make_view()

    engine.set_camera(camera)

    img.fill(0)
    engine.clear_depth()

    engine.render(shader)

    gui.set_image(img)
    gui.show()


ezprof.show()
