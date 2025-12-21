CREATE TABLE inverted_idx
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

    -- TODO: investigate primary key: (referrer_id, db_id)
    PRIMARY KEY (referrer_source, referrer_id, db_source, db_id),
--     FOREIGN KEY (db_source, db_id) REFERENCES external_metabolites (db_source, db_id)
);

-- inverted index to external_metabolites
CREATE INDEX idx_inverted_referrer ON inverted_idx (referrer_source, referrer_id);

-- for inverted lookup
-- CREATE INDEX idx_inverted_target ON inverted_idx (db_source, db_id);
