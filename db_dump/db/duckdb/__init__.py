import json
import os
from typing import Iterable

import pyarrow as pa
import duckdb

from db_dump.utils import PrintProgress


def setup(edb_source, cfg, batch):
    db = DuckDBBulkInserter(
        file=cfg["edb_file"].format(edb_type=edb_source),
        batch=batch,
    )
    db.setup()

    return db


class DuckDBBulkInserter:
    def __init__(self, file: str, batch: int):
        self.con = duckdb.connect(file)
        self.batch_size = batch
        self.buffer = []

    def setup(self):
        # Create tables
        sql_dir = os.path.join(os.path.dirname(__file__), "sql")
        for sql_file in os.listdir(sql_dir):
            if sql_file.endswith(".sql"):
                table_name = os.path.splitext(sql_file)[0][4:]

                try:
                    exists = self.con.execute(
                        f"SELECT * FROM duckdb_tables() WHERE table_name = '{table_name}'"
                    ).fetchone() is not None
                except duckdb.CatalogException:
                    exists = False

                if not exists:
                    # TODO: add logging
                    print(f"Creating DuckDB table: `{table_name}`")
                    with open(os.path.join(sql_dir, sql_file), "r") as fh:
                        self.con.execute(fh.read())

                    print(self.con.execute(f"DESCRIBE {table_name}").fetchall())

    def bulk_insert(self, iterable: Iterable):
        prog = PrintProgress("{dt}sec Inserting (batch: {iter})  {spinner}")

        for b, batch in enumerate(pyarrow_batches(iterable, batch_size=self.batch_size)):
            prog.print_progress(b)
            self.con.execute("INSERT INTO external_metabolites SELECT * FROM batch")

    def close(self):
        self.con.close()


def pyarrow_batches(dict_iter, batch_size=100000):
    buffer = []

    for obj in dict_iter:
        buffer.append({
            "db_source": obj.pop("db_source"),
            "db_id": obj.pop("db_id"),
            "content": json.dumps(obj),
        })

        if len(buffer) >= batch_size:
            yield pa.Table.from_pylist(buffer)
            buffer.clear()

    if buffer:
        yield pa.Table.from_pylist(buffer)
