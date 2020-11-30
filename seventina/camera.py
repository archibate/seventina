from .utils import *


@ti.data_oriented
class Camera:
    def __init__(self):
        self.proj = np.eye(4)
        self.view = np.eye(4)
        self.model = np.eye(4)


def affine(lin, pos):
    lin = np.concatenate([lin, np.zeros((1, 3))], axis=0)
    pos = np.concatenate([pos, np.ones(1)])
    lin = np.concatenate([lin, pos[..., None]], axis=1)
    return lin


def lookat(pos=(0, 0, 0), back=(0, 0, 1), up=(0, 1, 0)):
    pos = np.array(pos, dtype=float)
    back = np.array(back, dtype=float)
    up = np.array(up, dtype=float)

    fwd = -back
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, up)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)

    lin = np.stack([right, up, -fwd])
    return affine(lin, pos + back)

def ortho(left=-1, right=1, bottom=-1, top=1, near=-1, far=1):
    lin = np.eye(4)
    lin[0, 0] = (right - left) / 2
    lin[1, 1] = (top - bottom) / 2
    lin[2, 2] = (far - near) / 2
    lin[0, 3] = (right + left) / 2
    lin[1, 3] = (top + bottom) / 2
    lin[2, 3] = (far + near) / 2
    return lin
