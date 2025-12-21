import time

from db_dump.metparselib.types import EDB_SOURCES
from db_dump.db import setup_connection
from db_dump import stats

from db_dump.utils import PrintProgress


def parse_dump_db(
    *,
    dump_parser,
    in_file,
    db_cfg,
    batch,
):
    # setup
    db = setup_connection(db_cfg, batch=batch, tables=[
        'external_metabolites',
        'inverted_idx',
    ])
    db.truncate(dump_parser.id)
    print("Looking for External IDs: ", EDB_SOURCES)

    t1 = time.time()
    i = 0

    iter_ = dump_parser.parse_file(in_file)

    db.bulk_insert(iter_)

    print('@ Done! ', i, time.time() - t1)

    # writer_tasks = [asyncio.create_task(aio_bulk_insert_task(pool, queue, batch_size=batch)) for _ in range(tasks)]


def stats_dump_db(*, dump_parser, in_file):
    iter_ = dump_parser.parse_file(in_file)

    prog = PrintProgress()

    record_stats = stats.RelevantIrrelevantStats()

    for i, item in enumerate(iter_):
        if i % 10000 == 0:
            prog.print_progress(i)
        record_stats.add_stats(item)

    prog.close()
    print("---------------------------------------------")
    print("[STATS] Attribute counts:")
    record_stats.rel.print_statistics()
    print("---------------------------------------------")
    print("[STATS] Other counts:")
    record_stats.etc.print_statistics()
