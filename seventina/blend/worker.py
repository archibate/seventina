import bpy
import queue
import threading
import traceback
import numpy as np


class TaichiWorkerMT:
    def __init__(self):
        self.q = queue.Queue(maxsize=4)
        self.running = True

        self.t = threading.Thread(target=self.main)
        self.t.daemon = True
        self.t.start()

    def stop(self):
        print('Stopping worker')
        try:
            if self.running:
                self.running = False
                self.q.put((lambda self: None, [None]), block=False)
        except Exception as e:
            print(e)

    def main(self):
        print('Worker started')
        while self.running:
            try:
                func, resptr = self.q.get(block=True, timeout=1)
            except queue.Empty:
                continue

            try:
                resptr[0] = func(self)
            except Exception:
                msg = traceback.format_exc()
                print('Exception while running task:\n' + msg)
                resptr[1] = msg

            self.q.task_done()

    def launch(self, func):
        resptr = [None, None]
        self.q.put((func, resptr), block=True, timeout=None)
        return resptr

    def wait_done(self):
        self.q.join()


class TaichiWorker:
    def __init__(self):
        pass

    def stop(self):
        pass

    def launch(self, func):
        try:
            ret = func(self)
        except Exception:
            msg = traceback.format_exc()
            print('Exception while running task:\n' + msg)
            return [None, msg]
        return [ret, None]

    def wait_done(self):
        pass



def init_engine():
    import taichi as ti
    backend = getattr(ti, bpy.context.scene.seventina_backend.lower())
    ti.init(arch=backend)

    from .engine import BlenderEngine
    return BlenderEngine()


def trigger_redraw():
    print('trigger_redraw')
    if '_triggerdummyobj' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects['_triggerdummyobj'])
    if '_triggerdummymesh' in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes['_triggerdummymesh'])
    mesh = bpy.data.meshes.new('_triggerdummymesh')
    object = bpy.data.objects.new('_triggerdummyobj', mesh)
    bpy.context.collection.objects.link(object)


def render_main(width, height, region3d=None):
    is_final = region3d is None
    if is_final:
        pixels = np.empty((width * height * 4), dtype=np.float32)
    else:
        pixels = np.empty(width * height, dtype=np.uint32)

    @worker.launch
    def result(self):
        if not hasattr(self, 'engine'):
            self.engine = init_engine()

        if is_final:
            self.engine.update_default_camera()
        else:
            self.engine.update_region_data(region3d)
        self.engine.render_pixels(pixels, width, height, is_final)
        if self.engine.is_need_redraw():
            return 'redraw'
        else:
            return 'finish'

    worker.wait_done()

    if result[0] == 'redraw':
        trigger_redraw()

    return pixels


def invalidate_main(updates):
    @worker.launch
    def result(self):
        for update in updates:
            self.engine.invalidate_callback(update)

    worker.wait_done()


def start_main():
    @worker.launch
    def result(self):
        self.engine = init_engine()

    worker.wait_done()


worker = None


def register():
    global worker
    worker = TaichiWorkerMT()


def unregister():
    worker.stop()
