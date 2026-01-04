import time
import os.path
import sys
import argparse


if sys.version_info > (3, 10):
    import tomllib

    def toml_load(fn):
        with open(os.path.abspath(fn), 'rb') as fh:
            return tomllib.load(fh)
else:
    import toml
    def toml_load(fn):
        with open(os.path.abspath(fn), 'rb') as fh:
            return toml.loads(fh.read())


def get_argparser():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "in_file",
        type=str,
        help=""
    )
    parser.add_argument(
        "--out",
        default='./data/dumps/edb_dumps.db',
        type=str,
        # default="./data/database_config.toml",
        help=""
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output"
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=5000,
        help="Batch size (size of commit when using postgres)"
    )

    parser.add_argument(
        "--cardinality",
        action="store_true",
        default=False,
        help="Instead of insertion, does a dry run and collects cardinality statistics"
    )

    return parser


class PrintProgress:
    def __init__(self, tpl=None):
        self.tstart = None
        self.start()
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

    def print_final(self, msg):
        dt = None
        if self.tstart:
            dt = time.strftime('%H:%M:%S', time.gmtime(time.time() - self.tstart))

        print("\n" + msg.format(dt=dt))

    def close(self):
        print("")
