import csv
import sys

import tabulate

from discovery.metabolite import MetaboliteIndex, iter_scalars
from edb_handlers.db_sources import EDB_ID, EDB_ID_OTHER, CHEM_FLOAT_PROPERTY, CHEM_STRUCT_PROPERTY


import csv
import json
from typing import Iterable, Mapping, Optional


class CSVWriter:
    """
    Context-managed CSV writer using csv.DictWriter.

    Example:
        with CSVWriter("data.csv", fieldnames=["a", "b"], delimiter=";") as w:
            w.write_row({"a": 1, "b": 2})
    """

    def __init__(
        self,
        path: str,
        fieldnames: Iterable[str],
        *,
        multi_value_sep = "|",
        write_header: bool = True,
        **csv_kwargs,
    ):
        self.path = path
        self.fieldnames = list(fieldnames)
        self.write_header = write_header
        self.multi_sep = multi_value_sep
        self.csv_kwargs = csv_kwargs

        self._file = None
        self._writer: Optional[csv.DictWriter] = None

    def __enter__(self):
        self._file = open(self.path, mode="w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(
            self._file,
            fieldnames=self.fieldnames,
            **self.csv_kwargs,
        )
        if self.write_header:
            self._writer.writeheader()
        return self

    def write(self, meta: MetaboliteIndex):
        if not self._writer:
            raise RuntimeError("CSVWriter not initialized (use within a with block)")
        d = {}
        for k,v in meta.data.items():
            d[k] = self.serialize_value(v)
        self._writer.writerow(d)

    def write_rows(self, rows: Iterable[Mapping]):
        if not self._writer:
            raise RuntimeError("CSVWriter not initialized (use within a with block)")
        self._writer.writerows(rows)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            self._file.close()
        return False  # propagate exceptions

    def serialize_value(self, value):
        if isinstance(value, (list, set, tuple)):
            return self.multi_sep.join(map(str, value))
        return value

class JSONLinesWriter:
    """
    Context-managed JSON Lines (JSONL) writer.

    Example:
        with JSONLinesWriter("data.jsonl") as w:
            w.write({"a": 1})
            w.write({"b": 2})
    """

    def __init__(self, path: str, **json_kwargs):
        self.path = path
        self.json_kwargs = json_kwargs

        self._file = None

    def __enter__(self):
        self._file = open(self.path, mode="w", encoding="utf-8")
        return self

    def write(self, meta: MetaboliteIndex):
        if not self._file:
            raise RuntimeError("JSONLinesWriter not initialized (use within a with block)")
        json.dump(
            meta.data,
            self._file,
            **self.json_kwargs,
        )
        self._file.write("\n")

    def write_many(self, objs: Iterable):
        for obj in objs:
            self.write(obj)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            self._file.close()
        return False  # propagate exceptions


class STDWriter:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def write(self, meta: MetaboliteIndex):
        table = []

        for attr in EDB_ID:
            _append_table_multi(table, attr, meta.get(attr))
        table.append(["",""])

        for attr in EDB_ID_OTHER:
            _append_table_multi(table, attr, meta.get(attr))
        table.append(["",""])

        for attr in CHEM_FLOAT_PROPERTY:
            _append_table_multi(table, attr, meta.get(attr))
        for attr in CHEM_STRUCT_PROPERTY:
            _append_table_multi(table, attr, meta.get(attr))
        table.append(["",""])

        attr = "names"
        _append_table_multi(table, attr, meta.get(attr))

        attr = "description"
        _append_table_multi(table, attr, meta.get(attr))

        sys.stdout.write(tabulate.tabulate(table, tablefmt="outline"))
        sys.stdout.flush()


def _append_table_multi(table, id, values):
    if values is None:
        return

    for i, x in enumerate(iter_scalars(values)):
        if i == 0:
            table.append([id, x])
        else:
            table.append(["", x])
