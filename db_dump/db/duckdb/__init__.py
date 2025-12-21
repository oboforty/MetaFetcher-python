import json
import os
from typing import Iterable

import pyarrow as pa
import duckdb

from db_dump.metparselib.types import INDEXED_ATTRIBUTES, EDB_ID, CHEM_FLOAT_PROPERTY, CHEM_STRUCT_PROPERTY, \
    EDB_ID_OTHER
from db_dump.utils import PrintProgress


# TODO: refactor everything to sub modules
#
# def setup(cfg, batch):
#     db = DuckDBBulkInserter(
#         file=cfg["edb_file"],
#         batch=batch,
#     )
#     db.setup()
#
#     return db


SQL_DIR = os.path.join(os.path.dirname(__file__), "sql")

INS_RECORD = 0
INS_INVIDX = 1

SCHEMA_RECORD = pa.schema([
    pa.field('db_source', pa.string()),
    pa.field('db_id', pa.string()),

    pa.field('content', pa.json_())
], metadata={
})


SCHEMA_INVIDX = pa.schema([
    pa.field('referrer_source', pa.string()),
    pa.field('referrer_id', pa.string()),

    pa.field('db_source', pa.string()),
    pa.field('db_id', pa.string()),

    pa.field('secondary', pa.bool_())
], metadata={
})


INDEXED_STR_ATTRIBUTES = EDB_ID | {"names"} | CHEM_STRUCT_PROPERTY | EDB_ID_OTHER

#TODO: handle CHEM_FLOAT_PROPERTY
#TODO: handle CHEM_MULTI_DIM_PROPERTY

class DuckDBBulkInserter:

    def __init__(self, file: str, batch: int, tables: list[str] = None):
        self.con = duckdb.connect(file)
        self.batch_size = batch
        self.buffer = []
        self.tables = tables

        if not self.tables:
            self.tables = []

            for sql_file in os.listdir(SQL_DIR):
                if sql_file.endswith(".sql"):
                    table_name = os.path.splitext(sql_file)[0][4:]
                    self.tables.append(table_name)

    def setup(self):
        exists = self.con.execute(
            f"SELECT table_name FROM duckdb_tables()"
        ).fetchall()

        notexists = set(self.tables) - set(x[0] for x in exists)

        if notexists:
            for sql_file in os.listdir(SQL_DIR):
                if sql_file.endswith(".sql"):
                    table_name = os.path.splitext(sql_file)[0][4:]

                    # TODO: add logging
                    print(f"Creating DuckDB table: `{table_name}`")
                    with open(os.path.join(SQL_DIR, sql_file), "r") as fh:
                        sql = fh.read()

                    for sql_statement in sql.split(";\n"):
                        if sql_statement:
                            print(f"   `{sql_statement[:10]}`...")
                            self.con.execute(sql_statement)

                    print(self.con.execute(f"DESCRIBE {table_name}").fetchall())

    def bulk_insert(self, iterable: Iterable):
        prog = PrintProgress("{dt}sec Inserting (batch: {iter})  {spinner}")

        for b, (insert_type, batch) in enumerate(pyarrow_batches(iterable, batch_size=self.batch_size)):
            prog.print_progress(b)

            if insert_type == INS_INVIDX:
                self.con.execute("INSERT INTO inverted_idx SELECT * FROM batch")

            if insert_type == INS_RECORD:
                self.con.execute("INSERT INTO external_metabolites SELECT * FROM batch")

        prog.close()

    def truncate(self, edb_source=None):
        if edb_source is None:
            self.con.execute("TRUNCATE TABLE external_metabolites")
            self.con.execute("TRUNCATE TABLE inverted_idx")
        else:
            self.con.execute(f"DELETE FROM external_metabolites WHERE db_source = '{edb_source}'")
            self.con.execute(f"DELETE FROM inverted_idx WHERE db_source = '{edb_source}'")

    def close(self):
        self.con.close()


def pyarrow_batches(dict_iter, batch_size=100000):
    record_buffer = []
    invidx_buffer = []

    for record in dict_iter:
        db_source = record.pop("db_source")
        db_id = record.pop("db_id")

        record_buffer.append({
            "db_source": db_source,
            "db_id": db_id,
            "content": json.dumps(record),
        })

        # Metabolite record table
        if len(record_buffer) >= batch_size:
            yield INS_RECORD, pa.Table.from_pylist(record_buffer, SCHEMA_RECORD)
            record_buffer.clear()

        # TODO: @later -- separate idx tables:
        #           handle mass, mi_mass, charge
        #           handle MOL3d / MOL2d
        # todo: @later -- handle 2ndary (can go to inverted idx table)

        # Inverted Index table
        for ref_attr in INDEXED_STR_ATTRIBUTES:
            ext_ids = record.get(ref_attr)
            if ext_ids is None:
                continue
            ref_source = ref_attr.removesuffix('_id')

            if not isinstance(ext_ids, (list, set, tuple)):
                ext_ids = [ext_ids]

            for ext_id in ext_ids:
                invidx_buffer.append({
                    "referrer_source": ref_source,
                    "referrer_id": ext_id,

                    "db_source": db_source,
                    "db_id": db_id,

                    # TODO: determine if 2ndary index
                })

                if len(invidx_buffer) >= batch_size:
                    yield INS_INVIDX, pa.Table.from_pylist(invidx_buffer, SCHEMA_INVIDX)
                    invidx_buffer.clear()

    if record_buffer:
        yield INS_RECORD, pa.Table.from_pylist(record_buffer, SCHEMA_RECORD)
        record_buffer.clear()

    if invidx_buffer:
        yield INS_INVIDX, pa.Table.from_pylist(invidx_buffer, SCHEMA_INVIDX)
        invidx_buffer.clear()
