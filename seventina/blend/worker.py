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
                func(self)
            except Exception:
                msg = traceback.format_exc()
                print('Exception while running task:\n' + msg)
                resptr[0] = msg

            self.q.task_done()

    def launch(self, func):
        resptr = [None]
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
            func(self)
        except Exception:
            msg = traceback.format_exc()
            print('Exception while running task:\n' + msg)
            return [msg]
        return [None]

    def wait_done(self):
        pass


def init_engine():
    import taichi as ti
    backend = getattr(ti, bpy.context.scene.seventina_backend.lower())
    ti.init(arch=backend)

    from .engine import BlenderEngine
    return BlenderEngine()


def render_main(width, height, region3d):
    pixels = np.empty(width * height * 4, dtype=np.float32)

    @worker.launch
    def result(self):
        if not hasattr(self, 'engine'):
            self.engine = init_engine()

        self.engine.update_region_data(region3d)
        self.engine.render_pixels(pixels, width, height)

    worker.wait_done()
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
    worker = TaichiWorker()


def unregister():
    worker.stop()
