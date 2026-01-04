# Downloading metabolite database dumps

This guide explains how to download raw database dump files from various metabolite databases. These files will be imported into the local `.db` archive in the next step.

## Overview

Before importing database dumps, you need to download the raw data files from each database's website. All downloaded files should be placed in the `./data/dumps` directory.

Navigate to the project's root directory before running any commands.

## Database sources

### ChEBI

**Download page:** https://www.ebi.ac.uk/chebi/downloads

**Direct download:** https://ftp.ebi.ac.uk/pub/databases/chebi/SDF/

Download any of the SDF format files (e.g., `chebi.sdf.gz`).

### HMDB

**Download page:** https://www.hmdb.ca/downloads

Download the metabolite data in XML format (typically provided as `hmdb_metabolites.zip`).

### LipidMaps

**Download page:** https://www.lipidmaps.org/databases/lmsd/download

**Direct download:** https://www.lipidmaps.org/files/?file=LMSD&ext=sdf.zip

Download the LMSD SDF format file.

### KEGG & Pubchem compounds
*The databases are not yet supported (as they lack database dumps), but there are plans to add support around their bulk download features.*

## Next steps

After downloading the dump files, proceed to [Importing database dumps](import_db_dumps.md) to parse and import them into the local `.db` archive.

