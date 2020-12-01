from .utils import *


class Control:
    def __init__(self, gui):
        self.gui = gui
        self.center = np.array([0, 0, 0], dtype=float)
        self.up = np.array([0, 0, 1], dtype=float)
        self.back = np.array([0, -1, 0], dtype=float)

        self.mmb = None

    def update(self):
        for e in self.gui.get_events():
            self.process(e)

    def renormalize(self):
        right = np.cross(self.up, self.back)
        self.up = np.cross(self.back, right)

        self.back /= np.linalg.norm(self.back)
        self.up /= np.linalg.norm(self.up)

    def on_mmb_drag(self, delta, origin):
        delta_phi = delta[0] * ti.pi
        delta_theta = delta[1] * ti.pi
        pos = self.back
        radius = np.linalg.norm(pos)
        theta = np.arccos(pos[2] / radius)
        phi = np.arctan2(pos[1], pos[0])

        theta = np.clip(theta + delta_theta, 0, ti.pi)
        phi -= delta_phi

        pos[0] = radius * np.sin(theta) * np.cos(phi)
        pos[1] = radius * np.sin(theta) * np.sin(phi)
        pos[2] = radius * np.cos(theta)

        print(self.back, self.up)

    def make_view(self):
        from .camera import lookat
        return lookat(pos=self.center, back=self.back, up=self.up)

    def process(self, e):
        if e.key == self.gui.ESCAPE:
            self.gui.running = False
        elif e.key == self.gui.MMB:
            if e.type == self.gui.PRESS:
                self.mmb = np.array(e.pos)
            else:
                self.mmb = None
        elif e.key == self.gui.MOVE:
            if self.mmb is not None:
                new_mmb = np.array(e.pos)
                delta_mmb = new_mmb - self.mmb
                self.on_mmb_drag(delta_mmb, self.mmb)
                self.mmb = new_mmb
