

def setup_connection(cfg, *, batch: int, tables=None):
    dbcfg = cfg.get(cfg["db_type"])
    match cfg["db_type"]:
        case "parquet":
            # there's no need for batching & connection pooling & multiple aio tasks for parquet setup (1 file in, 1 file out)
            from .parquet import setup
            return setup(dbcfg, batch)
        case "duckdb":
            # there's no need for batching & connection pooling & multiple aio tasks for parquet setup (1 file in, 1 file out)
            from .duckdb import DuckDBBulkInserter
            db = DuckDBBulkInserter(
                file=dbcfg["edb_file"],
                batch=batch,
                tables=tables,
            )
            db.setup()
            return db

    raise NotImplementedError(f"{cfg['db_type']} is not implemented")
