import bpy
import queue
import threading
import traceback
import numpy as np
import time

from ..node_system.nodes import utils


class TaichiWorkerMT:
    def __init__(self):
        self.q = queue.Queue(maxsize=4)
        self.running = True

        self.t = threading.Thread(target=self.main)
        self.t.daemon = True
        self.t.start()

        self.table = None
        self.output = None

    def stop(self):
        print('Stopping worker')
        try:
            if self.running:
                self.running = False
                self.q.put((lambda self: None, [None, None]), block=False)
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


def init_main():
    import taichi as ti
    backend = bpy.context.scene.taichi_use_backend.lower()
    ti.init(arch=getattr(ti, backend))

    from seventina import Scene
    scene = Scene()
    return scene


def render_main(width, height, region3d):
    pixels = np.empty(width * height * 4, dtype=np.float32)

    @worker.launch
    def result(self):
        if self.scene is None:
            self.scene = init_main()

        self.scene.render(pixels, width, height)

    worker.wait_done()

    return pixels


@bpy.app.handlers.persistent
def frame_update_callback(*args):
    if worker is None or worker.output is None:
        return

    @worker.launch
    def result(self):
        self.output.update.run()

    worker.wait_done()


worker = None


def register():
    global worker
    worker = TaichiWorker()
    bpy.app.handlers.frame_change_pre.append(frame_update_callback)


def unregister():
    bpy.app.handlers.frame_change_pre.remove(frame_update_callback)
    worker.stop()
