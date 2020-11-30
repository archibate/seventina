from seventina.engine import Engine
from seventina.shader import Shader
from seventina.assimp import readobj
import taichi as ti

e = Engine()
s = Shader()
o = readobj('assets/monkey.obj', 'xyZ')

img = ti.Vector.field(3, float, e.res)

verts, faces = o['v'], o['f'][:, :, 0]
e.set_mesh(verts, faces)
e.render(img, s)

gui = ti.GUI('monkey', e.res)
while gui.running and not gui.get_event(gui.ESCAPE):
    gui.set_image(img)
    gui.show()
