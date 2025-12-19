CREATE TABLE edb_inverted_idx
(
    -- primary key pointing to (db_source, db_id)
    -- e.g. CHEBI:27732 = (edb_source='chebi', edb_id='27732')
    referrer_source VARCHAR NOT NULL,
    referrer_id     VARCHAR NOT NULL,

    -- primary key in `external_metabolites` table as referenced by `referrer_id`
    -- e.g. CHEBI:27732 refers to --> (edb_source='KEGG', edb_id='C07481')
    db_source  VARCHAR NOT NULL,
    db_id      VARCHAR NOT NULL,

    -- is referrer_id a secondary ID (url redirection to a primary compound ID)?
    secondary  BOOLEAN DEFAULT FALSE,

    PRIMARY KEY (referrer_source, referrer_id),
    FOREIGN KEY (db_source, db_id) REFERENCES external_metabolites (db_source, db_id)
);
