from seventina.engine import Engine
from seventina.shader import MagentaShader as Shader
from seventina.assimp import readobj
import taichi as ti

e = Engine()
s = Shader()
o = readobj('assets/monkey.obj')

img = ti.Vector.field(3, float, e.res)

e.clear_depth()
verts, faces = o['v'], o['f'][:, :, 0]
print(verts, faces)
e.set_mesh(verts, faces)
e.render(img, s)
ti.imshow(img)
