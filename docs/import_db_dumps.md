# Importing metabolite database dumps

Please note that we provide a full snapshot of the processed database dump files, so you can skip this whole page and rely on our cloud-provided `.parquet` files for normalizing metabolite compound IDs.

See XXX chapter, if you intend to skip these intermediary steps.


## 1.1. Download database dump files

For each downloaded dump file, make sure to edit `./data/dumps/files.json` accordingly! By default the json assumes the dump files are put in the same directory.


### ChEBI
https://www.ebi.ac.uk/chebi/downloads

Download any of the SDF formats: https://ftp.ebi.ac.uk/pub/databases/chebi/SDF/

### HMDB
https://www.hmdb.ca/downloads

Download the metabolite data in XML format.

### LipidMaps
https://www.lipidmaps.org/databases/lmsd/download

Download the LMSD SDF format: https://www.lipidmaps.org/files/?file=LMSD&ext=sdf.zip

## 1.2 Run db_dump parser tool

This will parse the above 3 files referenced by `./data/dumps/files.json` and transform them into indexed `.parquet` files or postgres tables (depending on settings).

    python -m db_dump --formats chebi hmdb lipidmaps

This step should have produced the following files in `./data/dumps/`:

- chebi.parquet
- hmdb.parquet
- lipmaps.parquet


- pubchem_ids.txt
- kegg_ids.txt

The parquet files are going to be used for constructing the Metabolite DB (mdb), see XXX chapter...
If you're using Postgres or Postgres_sync backends, the parquet files are not generated.


## 1.2. Download PubChem dump files
