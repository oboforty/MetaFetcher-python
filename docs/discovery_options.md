# Metabolite discovery

    python -m discovery chebi 17303


## Options file


For each metabolite DB stored in the `.db` file, you can control how they are discovered. You can control this in a `.toml` options file, and provide that config to the command.

For example:

    python -m discovery chebi 17303 -v --options ./my_profile.toml

By default, you can use the built-in profiles in `ROOT/discovery/profiles/`

    python -m discovery chebi 17303 -v --options ./discovery/profiles/full_discovery.toml


---

## Discovery options

    [hmdb]
    discoverable = true
    fetch_api = true
    cache_enabled = true
    cache_api_result = false
    keep_in_result = true

* **discoverable** - enables that the attribute (hmdb in the example) can be queried. Enable this either if you plan to use the `.db` cache or API fetches.
* **cache_enabled** - if enabled, metabolite entries are queried from the `.db` cache
* **fetch_api** - if enabled, and metabolite entries are not found in the `.db` cache, the external database's API is fetched instead.
  * APIs are only supported for ChEBI, HMDB, Lipidmaps, Pubchem and KEGG!
* ~~**cache_api_result** - not supported feature yet~~
* **keep_in_result** - when disabled, both discovered and undiscovered attributes will not be present in the output.
  * For example, you can ignore `pubmed_id` using this option.


Since there's an abundance in metabolite databases, you can control the default behaviour for all (which are unspecified in the options file). For example:

    [default]
    discoverable = true
    fetch_api = false
    cache_enabled = true
    cache_api_result = false
    keep_in_result = true

This example will only look in the local `.db` file, and not try the APIs.

### Other useful examples

    [names]
    discoverable = true
    fetch_api = false
    cache_enabled = false
    cache_api_result = false
    keep_in_result = true
