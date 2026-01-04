CREATE TABLE external_metabolites
(
    -- primary key
    -- e.g. CHEBI:27732 = (edb_source='chebi', edb_id='27732')
    db_source VARCHAR NOT NULL,
    db_id     VARCHAR NOT NULL,

    -- JSON
    content   VARCHAR NOT NULL,

    PRIMARY KEY (db_source, db_id)
);
