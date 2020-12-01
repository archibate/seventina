from .utils import *


class Control:
    def __init__(self, gui):
        self.gui = gui
        self.center = np.array([0, 0, 0], dtype=float)
        self.up = np.array([0, 1, 0], dtype=float)
        self.right = np.array([1, 0, 0], dtype=float)
        self.back = np.array([0, 0, 1], dtype=float)

        self.mmb = None

    def update(self):
        for e in self.gui.get_events():
            self.process(e)

    def renormalize(self):
        self.right = np.cross(self.up, self.back)
        self.up = np.cross(self.back, self.right)

        self.back /= np.linalg.norm(self.back)
        self.right /= np.linalg.norm(self.right)
        self.up /= np.linalg.norm(self.up)

    def on_mmb_drag(self, delta, origin):
        delta *= 4

        self.back += self.right * delta[0] + self.up * delta[1]
        self.right += -self.back * delta[0]
        self.up += -self.back * delta[1]

        self.up[0] = 0
        self.renormalize()

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
