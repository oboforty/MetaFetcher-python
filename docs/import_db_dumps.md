# Importing metabolite database dumps

This guide explains how to import downloaded database dump files into the local DuckDB archive (`.db` file). The imported data will be used for metabolite discovery queries.

> **Note:** We provide a full snapshot of processed database dump files. If you prefer to skip these steps, you can rely on our cloud-provided `.parquet` files for normalizing metabolite compound IDs.

## Prerequisites

1. Ensure you have downloaded the database dump files (see [Downloading database dumps](download_db_dumps.md))
2. All dump files should be placed in `./data/dumps`
3. Navigate to the project's root directory before running commands

## Import commands

All import commands write to the same output file (`./data/dumps/edb_dumps.db`). Each command appends data to this file, so you can run them sequentially.

### ChEBI

Import ChEBI SDF dump file:

```bash
python.exe -m edb_handlers.edb_chebi.parse_dump ./data/dumps/chebi.sdf.gz --out ./data/dumps/edb_dumps.db --batch 20000
```

This parses ChEBI's database dump and imports it into the DuckDB archive format.

### HMDB

Import HMDB XML dump file:

```bash
python.exe -m edb_handlers.edb_hmdb.parse_dump ./data/dumps/hmdb_metabolites.zip --out ./data/dumps/edb_dumps.db --batch 20000
```

This parses HMDB's database dump and imports it into the DuckDB archive format.

### LipidMaps

Import LipidMaps SDF dump file:

```bash
python.exe -m edb_handlers.edb_lipmaps.parse_dump ./data/dumps/LMSD.sdf.zip --out ./data/dumps/edb_dumps.db --batch 20000
```

This parses LipidMaps' database dump and imports it into the DuckDB archive format.

## Verifying imports

After importing database dumps, verify the contents of your `.db` archive:

```bash
python.exe .\edb_handlers\check_dumps.py
```

This command displays:
- Record counts for each database source
- Inverse index counts showing cross-references between databases

## Additional databases

### KEGG and PubChem

KEGG and PubChem require additional setup steps:

- **PubChem:** Requires compiling an ID list file at `./data/dumps/pubchem_ids.txt`
- **KEGG:** Requires compiling an ID list file at `./data/dumps/kegg_ids.txt`

Import commands for these databases are currently under development.

## Next steps

Once your database dumps are imported and verified, you can proceed to [Metabolite discovery](discovery_options.md) to query metabolites using the imported data.
