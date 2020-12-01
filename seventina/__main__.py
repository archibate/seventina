from .engine import Engine
from .shader import Shader
from .camera import Camera, frustum
from .control import Control
from .assimp import readobj
import taichi as ti
import numpy as np
import ezprof

#print(frustum(-1, 1, -1, 1, 1, 2))
#exit(1)

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
    ctl.apply(camera)
    engine.set_camera(camera)

    img.fill(0)
    engine.clear_depth()

    engine.render(shader)

    gui.set_image(img)
    gui.show()


ezprof.show()
