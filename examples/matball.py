import taichi as ti
import numpy as np
import tina as t3

ti.init(ti.opengl)

engine = t3.Engine(smoothing=True)
camera = t3.Camera()

img = ti.Vector.field(3, float, engine.res)

lighting = t3.Lighting()
material = t3.CookTorrance()
shader = t3.Shader(img, lighting, material)

obj = t3.readobj('assets/sphere.obj')
verts = obj['v'][obj['f'][:, :, 0]]
norms = obj['vn'][obj['f'][:, :, 2]]

gui = ti.GUI('matball', engine.res)
control = t3.Control(gui)

metallic = gui.slider('metallic', 0.0, 1.0, 0.1)
roughness = gui.slider('roughness', 0.0, 1.0, 0.1)
specular = gui.slider('specular', 0.0, 1.0, 0.1)

metallic.value = material.metallic[None]
roughness.value = material.roughness[None]
specular.value = material.specular[None]

while gui.running:
    control.get_camera(camera)
    engine.set_camera(camera)

    material.metallic[None] = metallic.value
    material.roughness[None] = roughness.value
    material.specular[None] = specular.value

    img.fill(0)
    engine.clear_depth()

    engine.set_face_verts(verts)
    engine.set_face_norms(norms)
    engine.render(shader)

    gui.set_image(t3.aces_tonemap(img.to_numpy()))
    gui.show()
