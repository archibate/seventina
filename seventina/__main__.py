from .core.engine import Engine
from .core.shader import Shader
from .core.material import CookTorrance
from .core.environ import Environ
from .core.trans import Trans
from .util.control import Control
from .util.assimp import readobj
import taichi as ti
import numpy as np

ti.init(ti.opengl)

engine = Engine(512)
trans = Trans()

img = ti.Vector.field(3, float, engine.res)

environ = Environ()
material = CookTorrance()
shader = Shader(img, environ, material)

o = readobj('assets/sphere.obj')
verts = o['v'][o['f'][:, :, 0]]

gui = ti.GUI('monkey', engine.res, fast_gui=True)
control = Control(gui)

engine.set_face_verts(verts)

while gui.running:
    control.get_trans(trans)
    engine.set_trans(trans)

    img.fill(0)
    engine.clear_depth()

    engine.render(shader)

    gui.set_image(img)
    gui.show()
