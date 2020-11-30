import taichi as ti
import numpy as np


setattr(ti, 'static', lambda x, *xs: [x] + list(xs) if xs else x) or setattr(
        ti.Matrix, 'element_wise_writeback_binary', (lambda f: lambda x, y, z:
        (y.__name__ != 'assign' or not setattr(y, '__name__', '_assign'))
        and f(x, y, z))(ti.Matrix.element_wise_writeback_binary)) or setattr(
        ti.Matrix, 'is_global', (lambda f: lambda x: len(x) and f(x))(
        ti.Matrix.is_global)) or setattr(ti, 'pi', __import__('math').pi
        ) or setattr(ti, 'tau', __import__('math').tau) or setattr(ti, 'GUI',
        (lambda f: __import__('functools').wraps(f)(lambda x='Tina', y=512,
        *z, **w: f(x, tuple(y) if isinstance(y, ti.Matrix) else y, *z, **w)
        ))(ti.GUI)) or print('[Tai3D] version 0.0.0, thank for your support!')


ti.smart = lambda x: x

@eval('lambda x: x()')
def _():
    import copy, ast
    from taichi.lang.transformer import ASTTransformerBase, ASTTransformerPreprocess

    old_get_decorator = ASTTransformerBase.get_decorator

    @staticmethod
    def get_decorator(node):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute) and isinstance(
                    node.func.value, ast.Name) and node.func.value.id == 'ti'
                and node.func.attr in ['smart']):
            return old_get_decorator(node)
        return node.func.attr

    ASTTransformerBase.get_decorator = get_decorator

    old_visit_struct_for = ASTTransformerPreprocess.visit_struct_for

    def visit_struct_for(self, node, is_grouped):
        if not is_grouped:
            decorator = self.get_decorator(node.iter)
            if decorator == 'smart':  # so smart!
                self.current_control_scope().append('smart')
                self.generic_visit(node, ['body'])
                t = self.parse_stmt('if 1: pass; del a')
                t.body[0] = node
                target = copy.deepcopy(node.target)
                target.ctx = ast.Del()
                if isinstance(target, ast.Tuple):
                    for tar in target.elts:
                        tar.ctx = ast.Del()
                t.body[-1].targets = [target]
                return t

        return old_visit_struct_for(self, node, is_grouped)

    ASTTransformerPreprocess.visit_struct_for = visit_struct_for


def V(*xs):
    return ti.Vector(xs)


def V23(xy, z):
    return V(xy.x, xy.y, z)


def V34(xyz, w):
    return V(xyz.x, xyz.y, xyz.z, w)


ti.Matrix.xy = property(lambda v: V(v.x, v.y))
ti.Matrix.xyz = property(lambda v: V(v.x, v.y, v.z))


def totuple(x):
    if x is None:
        x = []
    if isinstance(x, ti.Matrix):
        x = x.entries
    if isinstance(x, list):
        x = tuple(x)
    if not isinstance(x, tuple):
        x = x,
    if isinstance(x, tuple) and len(x) and x[0] is None:
        x = []
    return x


def tovector(x):
    return ti.Vector(totuple(x))


def vconcat(*xs):
    res = []
    for x in xs:
        if isinstance(x, ti.Matrix):
            res.extend(x.entries)
        else:
            res.append(x)
    return ti.Vector(res)


@ti.func
def clamp(x, xmin, xmax):
    return min(xmax, max(xmin, x))


@ti.func
def ifloor(x):
    return int(ti.floor(x))


@ti.func
def iceil(x):
    return int(ti.ceil(x))


@ti.func
def bilerp(f: ti.template(), pos):
    p = float(pos)
    I = int(ti.floor(p))
    x = p - I
    y = 1 - x
    return (f[I + V(1, 1)] * x[0] * x[1] +
            f[I + V(1, 0)] * x[0] * y[1] +
            f[I + V(0, 0)] * y[0] * y[1] +
            f[I + V(0, 1)] * y[0] * x[1])


@ti.func
def mapply(mat, pos, wei):
    res = ti.Vector([mat[i, 3] for i in range(3)]) * wei
    for i, j in ti.static(ti.ndrange(3, 3)):
        res[i] += mat[i, j] * pos[j]
    rew = mat[3, 3] * wei
    for i in ti.static(range(3)):
        rew += mat[3, i] * pos[i]
    return res, rew


@ti.func
def mapply_pos(mat, pos):
    res, rew = mapply(mat, pos, 1)
    return res / rew

@ti.func
def mapply_dir(mat, pos):
    res, rew = mapply(mat, pos, 0)
    return res


@ti.pyfunc
def reflect(I, N):
    return I - 2 * N.dot(I) * N


@ti.pyfunc
def aces_tonemap(color):
    # https://zhuanlan.zhihu.com/p/21983679
    return color * (2.51 * color + 0.03) / (color * (2.43 * color + 0.59) + 0.14)


@ti.func
def lerp(k, xmin, xmax):
    return xmin * (1 - k) + xmax * k
