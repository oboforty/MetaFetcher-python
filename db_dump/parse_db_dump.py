import time

from db_dump.db import setup_connection
from db_dump.utils import PrintProgress
from db_dump import stats

from edb_handlers.db_sources import EDB_ID, EDB_ID_OTHER, CHEM_FLOAT_PROPERTY, CHEM_STRUCT_PROPERTY, CHEM_STRUCT_MULTI_DIM_PROPERTY


def parse_dump_db(
    *,
    dump_parser,
    in_file: str,
    out_file: str,
    batch: int,
    edb_sources: list[str] = None,
):
    if edb_sources is None:
        edb_sources = EDB_ID | {"names"} | CHEM_STRUCT_PROPERTY | EDB_ID_OTHER

    # setup
    db = setup_connection(out_file, batch=batch, tables=[
        'external_metabolites',
        'inverted_idx',
    ], edb_sources=edb_sources)
    # db.truncate(dump_parser.id)

    print("Looking for External IDs: ", edb_sources)

    t1 = time.time()
    i = 0

    iter_ = dump_parser.parse_file(in_file)

    db.bulk_insert(iter_)

    print('@ Done! ', i, time.time() - t1)

    # writer_tasks = [asyncio.create_task(aio_bulk_insert_task(pool, queue, batch_size=batch)) for _ in range(tasks)]


def stats_dump_db(*, dump_parser, in_file):
    from edb_handlers.db_sources import INDEXED_ATTRIBUTES
    iter_ = dump_parser.parse_file(in_file)

    prog = PrintProgress()

    record_stats = stats.RelevantIrrelevantStats(INDEXED_ATTRIBUTES)

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
