import sys

from discovery.db.duckdb import MetaboliteRepository
from edb_handlers.db_sources import EDB_SOURCES, INDEXED_ATTRIBUTES

dump_file = sys.argv[1] if len(sys.argv) > 1 else "./data/dumps/edb_dumps.db"
db = MetaboliteRepository(dump_file)

print("Dump records count:")
for src in EDB_SOURCES:
    print(f"{src}: {db.count(src)}")
print("---------------------")

print("Inverse Index count:")
for ref, to, cnt in db.count_indexes():
    print(f"{ref:<16} -> {to:<16} {cnt}")
print("---------------------")

db.close()
