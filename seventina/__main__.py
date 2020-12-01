from .engine import Engine
from .shader import Shader
from .camera import Camera, lookat
from .control import Control
from .assimp import readobj
import taichi as ti
import numpy as np

engine = Engine()
shader = Shader()
camera = Camera()
o = readobj('assets/monkey.obj', 'xyZ')
verts, faces = o['v'], o['f'][:, :, 0]

img = ti.Vector.field(3, float, engine.res)

gui = ti.GUI('monkey', engine.res)
ctl = Control(gui)
while gui.running:
    ctl.update()
    camera.view = ctl.make_view()

    engine.set_camera(camera)
    engine.set_mesh(verts, faces)

    img.fill(0)
    engine.clear_depth()
    engine.render(img, shader)

    gui.set_image(img)
    gui.show()
