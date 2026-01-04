from discovery.db.duckdb import MetaboliteRepository


db = MetaboliteRepository("./data/dumps/edb_dumps.db")

print(db.count())

result = db.get_metabolites("chebi", "17303")

for item in result:
    print(item['chebi_id'], item.get("names"))

db.close()
