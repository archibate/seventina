import taichi as ti
import functools
import time


def inject(module, name):
    def decorator(hook):
        func = getattr(module, name)
        if hasattr(func, '_injected'):
            func = func._injected

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            _taichi_skip_traceback = 1
            clb = hook(*args, **kwargs)
            ret = func(*args, **kwargs)
            if clb is not None:
                clb(ret)
            return ret

        wrapped._injected = func
        setattr(module, name, wrapped)
        return hook

    return decorator


@inject(ti.Kernel, 'materialize')
def materialize(self, key=None, args=None, arg_features=None):
    if key is None:
        key = (self.func, 0)
    if not self.runtime.materialized:
        self.runtime.materialize()
    if key in self.compiled_functions:
        return
    grad_suffix = ""
    if self.is_grad:
        grad_suffix = "_grad"
    kernel_name = "{}_c{}_{}{}".format(self.func.__name__,
                                        self.kernel_counter, key[1],
                                        grad_suffix)
    t0 = time.time()

    def callback(ret):
        t1 = time.time()
        dt = t1 - t0
        print(f'[{dt:8.05f}] {kernel_name}')

    return callback


@inject(ti.Func, '__call__')
def materialize(self, *args):
    if not ti.inside_kernel():
        return
    #print(f'{time.time():.05f} Func call: {self.func}')
