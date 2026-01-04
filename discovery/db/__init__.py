

def edb_connect(file_or_conn: str):
    # TODO: strat pattern
    from .duckdb import MetaboliteRepository

    return MetaboliteRepository(file_or_conn)

