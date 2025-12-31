# 1. Importing metabolite database dumps

Please note that we provide a full snapshot of the processed database dump files, so you can skip this whole page and rely on our cloud-provided `.parquet` files for normalizing metabolite compound IDs.

See XXX chapter, if you intend to skip these intermediary steps.


## 1.1. Download easily accessible metabolite database dumps & import

By default, all files are stored in `./data/dumps`. Make sure to download the dump files here.

Also as a first step, navigate to this project's root folder to run the scripts.


### ChEBI
https://www.ebi.ac.uk/chebi/downloads

Download any of the SDF formats: https://ftp.ebi.ac.uk/pub/databases/chebi/SDF/

    python -m edb_handlers.edb_chebi.parse_dump ./data/dumps/chebi.sdf.gz --out ./data/dumps/edb_dumps.db --batch 10000

This will parse ChEBI's DB dump into a duckdb `.db` format. These files will be needed for Step 2.

### HMDB
https://www.hmdb.ca/downloads

Download the metabolite data in XML format.

    python -m edb_handlers.edb_hmdb.parse_dump ./data/dumps/hmdb_metabolites.zip --out ./data/dumps/edb_dumps.db --batch 10000

This will parse HMDB's DB dump into a duckdb `.db` format. These files will be needed for Step 2.

### LipidMaps
https://www.lipidmaps.org/databases/lmsd/download

Download the LMSD SDF format: https://www.lipidmaps.org/files/?file=LMSD&ext=sdf.zip

    python -m edb_handlers.edb_lipmaps.parse_dump ./data/dumps/LMSD.sdf.zip --out ./data/dumps/edb_dumps.db --batch 10000

This will parse LipidMap's DB dump into a duckdb `.db` format. These files will be needed for Step 2.


---


## 1.2. Download KEGG & Pubchem dump files

If you intend to use the KEGG metabolome database's compounds as well, compile a list of KEGG IDs (based on the databases imported in ./data/dumps/edb_dumps.db)

### Pubchem

- `./data/dumps/pubchem_ids.txt`

@TODO compile ID list & import cmd

### KEGG

- `./data/dumps/kegg_ids.txt`

@TODO compile ID list & import cmd

