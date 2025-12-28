import enum
import json
import os.path
import sys

import duckdb

class RangeQueryType(enum.Enum):
    # used for floats like mass, mi_mass, charge, logp
    EQUI = "equi"
    APPROX = "approx"


class StringQueryType(enum.Enum):
    # text-based
    EQUI = "equi"

    STR_LIKE = "like"
    STR_LEVENSHTEIN = "levi"
    STR_DAMERAU_LEVENSHTEIN = "dale"
    STR_JACCARD = "jaccard"
    STR_HAMMING = "hamming"
    STR_JARO = "jaro"
    STR_JARO_WINKLER = "jawi"



class MetaboliteRepository:
    """
    The inverse index table is an undirected graph relationship, and not strictly directed as (referrer id->db id)!
    RelDBs and DuckDB (allegedly) are sargable if they don't mix two indexes,
    so we use a union for this query
    """
    Q_IDX_TPL = """
        SELECT db_source, db_id
        FROM inverted_idx
        WHERE {where_clause_1}
        --WHERE referrer_source = $src AND referrer_id = $id
        UNION ALL
        SELECT referrer_source AS db_source, referrer_id AS db_id
        FROM inverted_idx
        WHERE {where_clause_2}
        --WHERE db_source = $src AND db_id = $id;
    """

    Q_EDB_EQUI = """
    WITH idx_lookup AS ({idx_query})
    SELECT edb.*
    FROM external_metabolites edb
    JOIN idx_lookup idx
      ON edb.db_source = idx.db_source
     AND edb.db_id     = idx.db_id;
    """

    def __init__(self, file: str):
        if not os.path.exists(file):
            raise FileNotFoundError(f"{file} does not exist")

        self.con = duckdb.connect(file)

    def get_metabolites(self, db_source, db_id):
        pass

    def get_indexes(self, db_source, db_id):
        results: duckdb.DuckDBPyRelation = self.con.query(sql, params=dict(src=db_source, id=db_id))

        # TODO: fetch in batch? is it really needed?
        for result in results.fetchall():
            print(result)

    def _get_sql_str_approx(self, attr: str, str_query_type: StringQueryType, str_approx_threshold: float):
        match str_query_type.value:
            case RangeQueryType.EQUI:
                clause = "{col}_source = '{attr}' AND {col}_id = $id"
            case _:
                raise NotImplementedError(f"")

        # TODO: validate: e.g. only mass/mi_mass/etc can be with ranges & _ids can't be queried with STR Approx functions!

        return self.Q_IDX_TPL.format(
            where_clause_1=clause.format(attr=attr, col="referrer"),
            where_clause_2=clause.format(attr=attr, col="db"),
        )

    def close(self):
        self.con.close()
