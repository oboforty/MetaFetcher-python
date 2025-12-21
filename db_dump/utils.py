import time


class PrintProgress:
    def __init__(self, tpl=None):
        self.start()
        self.tstart = None
        self.print_called = 0

        if tpl is None:
            tpl = "{spinner} {dt}    Processing... {iter}"
        self.tpl = tpl

    def start(self):
        self.tstart = time.time()

    def print_progress(self, i, **kwargs):
        if not hasattr(self, 'print_called'):
            self.print_called = 0
        self.print_called += 1

        mod4 = self.print_called % 4
        pb = '-'
        if mod4 == 1: pb = '\\'
        elif mod4 == 2: pb = '|'
        elif mod4 == 3: pb = '/'

        dt = None
        if self.tstart:
            dt = time.strftime('%H:%M:%S', time.gmtime(time.time() - self.tstart))

        print("\r", self.tpl.format(iter=i, spinner=pb, dt=dt, **kwargs), end="")

    def close(self):
        print("")
