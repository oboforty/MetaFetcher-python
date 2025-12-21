import json
import os.path
import sys

import duckdb


DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/dumps/edb_dumps.db")
con = duckdb.connect(DB_PATH)

term = sys.argv[1]

print("@@ SEARCH TERM: ", term)

result = con.execute(f"""
    SELECT DISTINCT db_id
    FROM inverted_idx
    WHERE referrer_source = 'names' AND referrer_id LIKE '%{term}%' AND db_source = 'chebi'
""")

#TODO: do this for each db type -- how?

db_ids = [id for id, in result.fetchall()]

print("@@ SEARCH IDS: ", db_ids)

result = con.execute(f"""
    SELECT db_source, db_id, content
    FROM external_metabolites
    WHERE db_source = 'chebi' AND db_id IN {db_ids}
    LIMIT 1000
""")

results = result.fetchall()
print(f"@@ RESULTS: ({len(results)})")
for db_source, db_id, content in results:
    data = json.loads(content)

    print("--------------------------------------------")
    print(f"#{db_source:<29} {db_id}")
    for attr, val in data.items():
        print(f"{attr:<30} {val}")

con.close()
