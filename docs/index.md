# Metabolite Fetcher
Welcome to the python version of MetaFetcher!

This package is used to create a unified index of the most popular metabolite databases, and use them to normalize datasets by finding all relevant compound IDs and chemical attributes.


### 1. Downloading and importing database dumps

[Download database dump files](download_db_dumps.md)

[Importing the database dump files](import_db_dumps.md)

### 2. Running the discovery algorithm

[Metabolite Discovery](discovery_options.md)

## Installation
Setup your python virtual environment. You could use UV, venv and pip.

### Using uv (recommended)
Install uv package manager: https://docs.astral.sh/uv/

In the root of the repository, run:

    uv sync

This will create a virtual environment at the root of the repo and install all dependencies and the package (with all code in the src folder installed in "editable" mode).

### Using pip

In the root of the repository, run:

    pip install -e .

--- 

## Quick Guide

Download the Database dumps ([see here](download_db_dumps.md)). We recommend that you put these files in `./data/dumps`.

Run the DB dump imports:

Chebi:

    python -m edb_handlers.edb_chebi.parse_dump ./data/dumps/chebi.sdf.gz --out ./data/dumps/edb_dumps.db --batch 20000

HMDB:

    python -m edb_handlers.edb_hmdb.parse_dump ./data/dumps/hmdb_metabolites.zip --out ./data/dumps/edb_dumps.db --batch 20000

Lipidmaps:

    python -m edb_handlers.edb_lipmaps.parse_dump ./data/dumps/LMSD.sdf.zip --out ./data/dumps/edb_dumps.db --batch 20000

After you've imported everything you need into `edb_dumps.db`, use this file for metabolite discovery:

    python -m discovery hmdb HMDB0000010

    python -m discovery chebi 17303

To save these results into a file, use the `--out` flag:

    python -m discovery chebi 17303 --out results.csv

* Supported `--out` file types are .json, .tsv, .csv

* To control discovery algorithm, create a `.toml` file, and add it using the `--options` flag.
