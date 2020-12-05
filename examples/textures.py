import taichi as ti
import numpy as np
import tina

ti.init(ti.opengl)

engine = tina.Engine(texturing=True)
camera = tina.Camera()

img = ti.Vector.field(3, float, engine.res)

lighting = tina.Lighting()
material = tina.CookTorrance(
        basecolor=tina.Texture('assets/cloth.jpg'),
        )
shader = tina.Shader(img, lighting, material)

obj = tina.readobj('assets/monkey.obj')
verts = obj['v'][obj['f'][:, :, 0]]
coors = obj['vt'][obj['f'][:, :, 1]]

gui = ti.GUI('texture', engine.res, fast_gui=True)
control = tina.Control(gui)

while gui.running:
    control.get_camera(camera)
    engine.set_camera(camera)

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.set_face_coors(coors)
    engine.render(shader)

    gui.set_image(img)
    gui.show()
