

def setup_connection(db_file, *, batch: int, tables=None, edb_sources=None):
    if db_file.endswith(".db"):
        # DuckDB
        from .duckdb import DuckDBBulkInserter
        db = DuckDBBulkInserter(
            file=db_file,
            batch=batch,
            tables=tables,
            edb_sources=edb_sources,
        )
        db.setup()
        return db

# dbcfg = cfg.get(cfg["db_type"])
    # match cfg["db_type"]:
    #     case "parquet":
    #         # there's no need for batching & connection pooling & multiple aio tasks for parquet setup (1 file in, 1 file out)
    #         from .parquet import setup
    #         return setup(dbcfg, batch)
    #     case "duckdb":
    #         # there's no need for batching & connection pooling & multiple aio tasks for parquet setup (1 file in, 1 file out)
    #         return db
    #
    raise NotImplementedError(f"{cfg['db_type']} is not implemented")
