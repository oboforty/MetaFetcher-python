import argparse
import asyncio
import json
import time
from typing import Literal

from db_dump import cli
from db_dump.dtypes import MetaboliteExternal
from db_dump.metparselib.types import EDB_SOURCES
from db_dump.process.fileformats.SDFParser import parse_sdf
from db_dump.db import setup_connection
from db_dump import stats

from db_dump.toml_load import toml_load
from db_dump.utils import PrintProgress
from .ChebiParser import ChebiParser


def main():
    # input
    parser = cli.get_argparser()
    args = parser.parse_args()

    # setup
    db = setup_connection(toml_load(args.database), batch=args.batch, tables=[
        'external_metabolites',
        'inverted_idx',
    ])
    print("Looking for External IDs: ", EDB_SOURCES)

    t1 = time.time()
    i = 0
    chebi = ChebiParser()
    prog = PrintProgress()

    iter_ = chebi.parse_file(args.in_file)

    if args.cardinality:
        record_stats = stats.RelevantIrrelevantStats()

        for i, item in enumerate(iter_):
            if i % 10000 == 0:
                prog.print_progress(i)
            record_stats.add_stats(item)

        prog.close()
        print("---------------------------------------------")
        record_stats.rel.print_statistics()
        print("---------------------------------------------")
        record_stats.etc.print_statistics()
        return

    db.bulk_insert(iter_)

    print('@ Done! ', i, time.time() - t1)

    # writer_tasks = [asyncio.create_task(aio_bulk_insert_task(pool, queue, batch_size=batch)) for _ in range(tasks)]


if __name__ == "__main__":
    main()
