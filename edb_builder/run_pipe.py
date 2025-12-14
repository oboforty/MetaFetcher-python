import asyncio
import os
import sys
from importlib import import_module

from metcore.dal_psycopg import db
from edb_builder.utils import (
    dingdingding
)
from pipebro import SettingWrapper

from metcore.utils import toml_load


def run_pipe(module_name, *, clear_db=False, mute=False, debug=False, verbose=False, stdout=None):
    m = import_module(module_name)

    dbcfg = SettingWrapper(toml_load(os.path.dirname(__file__) + '/../db.toml'))
    conn = db.try_connect(dbcfg)

    if clear_db:
        db.clear_database(conn)

    if stdout:
        sys.stdout = open(stdout, "w")

    app = m.build_pipe(conn)

    app.debug = debug
    app.verbose = verbose

    # draw_pipes_network(pipe, filename='spike', show_queues=True)
    # debug_pipes(pipe)
    asyncio.run(app.run())

    conn.close()

    if not app.debug and not mute:
        dingdingding()
