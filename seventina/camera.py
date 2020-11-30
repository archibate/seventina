from .utils import *


@ti.data_oriented
class Camera:
    def __init__(self):
        self.proj = np.eye(4, dtype=np.float32)
        self.view = np.eye(4, dtype=np.float32)

    @property
    def pers(self):
        return self.proj @ self.view
