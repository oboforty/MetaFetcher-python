# Metabolite discovery

The discovery module allows you to query and discover metabolite information from the imported database archives. It can search across multiple databases and resolve cross-references between them.

## Basic usage

Query a metabolite by database source and ID:

```bash
python.exe -m discovery hmdb HMDB0000010
```

The command accepts database source and ID pairs. Supported database sources include: `chebi`, `hmdb`, `lipidmaps`, `pubchem`, `kegg`, and others.

## Configuration options

You can control how each database is queried using a TOML configuration file. This allows you to specify whether to use the local `.db` cache, fetch from external APIs, or exclude certain attributes from results.

### Using a custom options file

```bash
python.exe -m discovery hmdb HMDB0000010 -v --options ./my_profile.toml
```

### Using built-in profiles

Built-in configuration profiles are available in `discovery/profiles/`:

```bash
python.exe -m discovery hmdb HMDB0000010 -v --options ./discovery/profiles/full_discovery.toml
```

## Discovery options

Each database source (or attribute) can be configured with the following options:

```toml
[hmdb]
discoverable = true
fetch_api = true
cache_enabled = true
cache_api_result = false
keep_in_result = true
```

### Option descriptions

* **discoverable** - Enables querying for this attribute. Set to `true` if you plan to use either the `.db` cache or API fetches.
* **cache_enabled** - When enabled, metabolite entries are queried from the local `.db` cache first.
* **fetch_api** - When enabled, if metabolite entries are not found in the `.db` cache, the external database's API is queried instead.
  * API support is available for: ChEBI, HMDB, LipidMaps, PubChem, and KEGG.
* **cache_api_result** - *(Not yet supported)*
* **keep_in_result** - When disabled, both discovered and undiscovered attributes are excluded from the output.
  * Useful for filtering out unwanted attributes (e.g., `pubmed_id`).

## Default behavior

You can set default behavior for all unspecified database sources using a `[default]` section:

```toml
[default]
discoverable = true
fetch_api = false
cache_enabled = true
cache_api_result = false
keep_in_result = true
```

This configuration will only query the local `.db` file and will not attempt API fetches for unspecified sources.

## Example configurations

### Local cache only

Query only from the local `.db` archive, no API calls:

```toml
[default]
discoverable = true
fetch_api = false
cache_enabled = true
keep_in_result = true
```

### Names attribute

Example configuration for the `names` attribute:

```toml
[names]
discoverable = true
fetch_api = false
cache_enabled = false
keep_in_result = true
```
