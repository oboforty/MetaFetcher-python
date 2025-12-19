import argparse
import asyncio
import json
import time
from typing import Literal

from db_dump import cli
from db_dump.dtypes import MetaboliteExternal
from db_dump.metparselib.types import EDB_SOURCES
from db_dump.process.fileformats.SDFParser import parse_sdf

from .ChebiParser import ChebiParser


def main():
    parser = cli.get_argparser()
    args = parser.parse_args()

    # db_cfg = toml_load(args.database)
    process_db_dump(**vars(args))


def process_db_dump(
    in_file: str,
    out_file: str,
    formats: list[str],
    backend: Literal["parquet", "postgres", "postgres_sync"],
    tasks: int, batch: int,
    queue_size: int,
    verbose: bool = False,
):
    print("Looking for External IDs: ", EDB_SOURCES)

    if backend == "parquet":
        # there's no need for batching & connection pooling & multiple aio tasks for parquet setup (1 file in, 1 file out)
        pass
    else:
        raise NotImplementedError(f"{backend} is not implemented")

    t1 = time.time()
    i = 0
    chebi = ChebiParser()
    chebi_record: MetaboliteExternal

    for chebi_dict in parse_sdf(in_file):
        for chebi_record in chebi.parse(chebi_dict):
            if i % 50000 == 0:
                print('@', i, time.time() - t1)
                print(chebi_record)
            i += 1
    print('@ Done! ', i, time.time() - t1)

    # writer_tasks = [asyncio.create_task(aio_bulk_insert_task(pool, queue, batch_size=batch)) for _ in range(tasks)]


if __name__ == "__main__":
    main()
