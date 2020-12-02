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

engine = Engine((1024, 768), smoothing=True)

environ = Environ()
material = CookTorrance(roughness=0.1)

img = ti.Vector.field(3, float, engine.res)
shader = Shader(img, environ, material)
trans = Trans()

o = readobj('assets/sphere.obj')
verts = o['v'][o['f'][:, :, 0]]
norms = o['vn'][o['f'][:, :, 2]]

gui = ti.GUI('monkey', engine.res, fast_gui=True)
control = Control(gui)

while gui.running:
    control.get_trans(trans)
    engine.set_trans(trans)

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.set_face_norms(norms)
    engine.render(shader)

    gui.set_image(img)
    gui.show()
