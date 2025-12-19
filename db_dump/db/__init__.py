

def setup_connection(edp_source, cfg, *, batch: int):
    dbcfg = cfg.get(cfg["db_type"])
    match cfg["db_type"]:
        case "parquet":
            # there's no need for batching & connection pooling & multiple aio tasks for parquet setup (1 file in, 1 file out)
            from .parquet import setup
            return setup(edp_source, dbcfg, batch)
        case "duckdb":
            # there's no need for batching & connection pooling & multiple aio tasks for parquet setup (1 file in, 1 file out)
            from .duckdb import setup
            return setup(edp_source, dbcfg, batch)

    raise NotImplementedError(f"{cfg['db_type']} is not implemented")
