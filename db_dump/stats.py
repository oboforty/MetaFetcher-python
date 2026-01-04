import collections
import time
from typing import Any
import tabulate


class Stats:

    def __init__(self):
        self.keys = collections.Counter()

        self.min_cardinalities = collections.defaultdict(lambda: float("inf"))
        self.max_cardinalities = collections.defaultdict(int)
        self.nones = collections.defaultdict(int)

        self.total = 0
        self.t1 = time.time()

    def add_stats(self, data, keys=None):
        if keys is None:
            keys = list(data.keys())
        else:
            keys = set(keys) & set(data.keys())

        self.keys.update(keys)

        for attr in keys:
            value = data[attr]

            if value is None:
                # should we ever have Nones in datasets?
                self.nones[attr] += 1
            else:
                len_ = 1 if is_primitive(value) else len(value)

                if len_ > self.max_cardinalities[attr]:
                    self.max_cardinalities[attr] = len_
                if len_ < self.min_cardinalities[attr]:
                    self.min_cardinalities[attr] = len_

        self.total += 1

    def print_statistics(self):
        table = []
        headers = ["key", "total count", "min cardinality", "max cardinality", "nones"]
        for attr, cnt in self.keys.most_common():
            table.append([attr, cnt, self.min_cardinalities[attr], self.max_cardinalities[attr], self.nones[attr]])
        table.append(["Total:", self.total, "", "", ""])

        print(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))

        print(f"\n took: {round(time.time() - self.t1, 2)} seconds")


class RelevantIrrelevantStats:

    def __init__(self, indexed_attributes):
        self.rel = Stats()
        self.etc = Stats()

        self.indexed_attributes = indexed_attributes

    def add_stats(self, data):
        irrelevant_keys = set(data.keys()) - self.indexed_attributes
        irrelevant_keys -= {"db_id", "db_source"}

        self.rel.add_stats(data, self.indexed_attributes)
        self.etc.add_stats(data, irrelevant_keys)

def is_primitive(v: Any) -> bool:
    return isinstance(v, (int, float, bool, str, bytes))
