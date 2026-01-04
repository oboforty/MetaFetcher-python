# Limitations

## Databases

Only the following databases's DB dumps can be processed:
- HMDB
- ChEBI
- Lipidmaps

The following two databases will be supported to process DB dumps in time:
- Pubchem Compounds
- KEGG Compounds

It is not possible to download the DB dump files for these two databases. Therefore, aquiring these dumps will require the user manually querying Pubchem & KEGG IDs using the DB dumps of ChEBI, HMDB, and Lipidmaps.

## APIs
Only the following DB APIs are supported for fetching records:
- HMDB: [HMDBClient.py](../edb_handlers/edb_hmdb/api/HMDBClient.py)
- ChEBI: [ChebiClient.py](../edb_handlers/edb_chebi/api/ChebiClient.py)
- Lipidmaps: [LipidmapsClient.py](../edb_handlers/edb_lipmaps/api/LipidmapsClient.py)
- Pubchem: [PubchemClient.py](../edb_handlers/edb_pubchem/api/PubchemClient.py)
- KEGG: [KeggClient.py](../edb_handlers/edb_kegg/api/KeggClient.py)

The user can easily implement novel API clients and integrate into the discovery algorithm.

## Fields

See `INDEXED_ATTRIBUTES` in [db_sources.py](../edb_handlers/db_sources.py) to see which fields can be queried during discovery.

The following fields are not indexed:
* **names** - this groups IUPAC names and Synonyms together. There's plan to support a separate query by name, but it cannot be a reliable method to group metabolite records from differing databases together.
* **formula** - is not indexed for similar reasons. There's plan to support querying formulae, though.
* **mass** - average molecular weight
* **mi_mass** - monoisotopic mass
* **charge**
* **logp**
* *Secondary Indexes* - ChEBI, HMDB, and some other databases have these, which point to other primary indexes (e.g. this happens when two records are merged into one due to redundant error). There's plan to support these, but currently they're not.

## Search query
The database does not support search query (unless the user implements DuckDB querying).

### Range queries
Numeric attributes (mass, mi_mass, charge and logp) will support range (<, >, <=, >=) queries.
