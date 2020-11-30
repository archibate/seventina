from .engine import Engine
from .shader import Shader
from .camera import Camera
from .assimp import readobj
import taichi as ti

engine = Engine()
shader = Shader()
camera = Camera()
o = readobj('assets/monkey.obj', 'xyZ')
verts, faces = o['v'], o['f'][:, :, 0]

img = ti.Vector.field(3, float, engine.res)

gui = ti.GUI('monkey', engine.res)
while gui.running and not gui.get_event(gui.ESCAPE):

    engine.set_perspective(camera.pers)
    engine.set_mesh(verts, faces)
    engine.render(img, shader)

    gui.set_image(img)
    gui.show()
