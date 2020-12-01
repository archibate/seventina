from .core.engine import Engine
from .core.shader import Shader
from .core.environ import Environ
from .core.material import CookTorrance
from .core.trans import Trans
from .util.control import Control
from .util.assimp import readobj
import taichi as ti
import numpy as np

ti.init(ti.opengl)

engine = Engine()

environ = Environ()
material = CookTorrance(roughness=0.1)

img = ti.Vector.field(3, float, engine.res)
shader = Shader(img, environ, material)
trans = Trans()

o = readobj('assets/monkey.obj')
verts, faces = o['v'], o['f'][:, :, 0]

gui = ti.GUI('monkey', engine.res, fast_gui=True)
control = Control(gui)

engine.set_mesh(verts, faces)

while gui.running:
    control.get_trans(trans)
    engine.set_trans(trans)

    img.fill(0)
    engine.clear_depth()

    engine.render(shader)

    gui.set_image(img)
    gui.show()
