from .common import *

import melt


class NodeSystem(melt.NodeSystem):
    type2socket = {
        'a': 'scalar',
        'v': 'vector',
        'c': 'color',
        'm': 'material',
    }
    type2option = {
            'i': 'int',
            'f': 'float',
            'b': 'bool',
            's': 'str',
            'dt': 'enum',
            'so': 'search_object',
            'i2': 'vec_int_2',
            'i3': 'vec_int_3',
            'f2': 'vec_float_2',
            'f3': 'vec_float_3',
    }
    type2items = {
            'dt': 'float int i8 i16 i32 i64 u8 u16 u32 u64 f32 f64'.split(),
    }


print('[Tina] Start loading node system...')

A = NodeSystem()


@A.register
def Def(material):
    '''
    Name: material_output
    Category: output
    Inputs: material:m
    Output:
    '''

    if material is None:
        return tina.CookTorrance()
    return material


@A.register
def Def(color):
    '''
    Name: lambert
    Category: shader
    Inputs: color:c
    Output: material:m
    '''

    return tina.Lambert(color=color)


@A.register
def Def(diffuse, specular, shineness, normal):
    '''
    Name: blinn_phong
    Category: shader
    Inputs: diffuse:c specular:a shineness:a normal:v
    Output: material:m
    '''

    return tina.BlinnPhong(diffuse=diffuse, specular=specular,
            shineness=shineness, normal=normal)


@A.register
def Def(basecolor, roughness, metallic, specular, normal):
    '''
    Name: cook_torrance
    Category: shader
    Inputs: basecolor:c roughness:a metallic:a specular:a normal:v
    Output: material:m
    '''

    return tina.CookTorrance(basecolor=basecolor, roughness=roughness,
            metallic=metallic, specular=specular, normal=normal)


@A.register
class Def:
    '''
    Name: geometry
    Category: input
    Inputs:
    Output: pos:v% normal:v% texcoord:v%
    '''

    def __init__(self):
        self.pos = tina.Input('pos')
        self.normal = tina.Input('normal')
        self.texcoord = tina.Input('texcoord')


@A.register
def Def(path, texcoord):
    '''
    Name: image_texture
    Category: texture
    Inputs: path:s texcoord:v
    Output: color:c
    '''

    return tina.Texture(path, texcoord=texcoord)


@A.register
def Def(value):
    '''
    Name: scalar_constant
    Category: input
    Inputs: value:f
    Output: value:a
    '''

    return tina.Const(value)


@A.register
def Def(x, y, z):
    '''
    Name: vector_constant
    Category: input
    Inputs: x:f y:f z:f
    Output: vector:v
    '''

    return tina.Const(tina.V(x, y, z))


@A.register
def Def(expr, lhs, rhs):
    '''
    Name: custom_function
    Category: converter
    Inputs: expr:s lhs:a rhs:a
    Output: result:a
    '''

    import taichi as ti
    expr = expr.replace('int', 'ti.ti_int')
    expr = expr.replace('float', 'ti.ti_float')
    expr = expr.replace('max', 'ti.ti_max')
    expr = expr.replace('min', 'ti.ti_min')
    expr = expr.replace('abs', 'ti.ti_abs')
    func = eval(f'lambda x, y: ({expr})')
    return lambda pars: func(lhs(pars), rhs(pars))


@A.register
class Def(tina.Node):
    '''
    Name: map_range
    Category: converter
    Inputs: value:a src0:f src1:f dst0:f dst1:f clamp:b
    Output: result:a
    '''

    def __init__(self, value, src0=0, src1=1, dst0=0, dst1=1, clamp=False):
        assert isinstance(value, IField)

        self.value = value
        self.src0 = src0
        self.src1 = src1
        self.dst0 = dst0
        self.dst1 = dst1
        self.clamp = clamp

    @ti.func
    def __call__(self, pars):
        k = (self.value(pars) - self.src0) / (self.src1 - self.src0)
        if ti.static(self.clamp):
            k = clamp(k, 0, 1)
        return self.dst1 * k + self.dst0 * (1 - k)


print(f'[Tina] Node system loaded: {len(A)} nodes')
