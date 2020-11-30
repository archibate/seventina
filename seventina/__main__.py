from .engine import Engine
from .shader import Shader
from .camera import Camera, lookat, perspective
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
while gui.running and not gui.get_event(gui.ESCAPE):
    camera.view = lookat(back=(0, 0, 1))
    camera.proj = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0.4, 1],
    ])

    engine.set_camera(camera)
    engine.set_mesh(verts, faces)
    engine.render(img, shader)

    gui.set_image(img)
    gui.show()
