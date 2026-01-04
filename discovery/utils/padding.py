_PADDINGS = {
    'hmdb': 'HMDB',
    'chebi': 'CHEBI:',
    'hmdb_id': 'HMDB',
    'chebi_id': 'CHEBI:',
    #'kegg': 'C',
    'lipmaps': 'LM',
    'lipmaps_id': 'LM',
    'inchi': 'InChI='
}


def guess_db(db_id: str) -> str | None:
    for db_tag, _pad in _PADDINGS.items():
        if db_id.startswith(_pad):
            return db_tag
    return None


def depad_id(db_id, db_tag=None):
    if db_id is None:
        return None

    if db_tag is None:
        db_tag = guess_db(db_id)

        if db_tag is None:
            raise Exception("db_tag not provided for depad_id. How couldst i depad yond hast mere db tag?")

    db_id = db_id.removeprefix(_PADDINGS.get(db_tag, ""))

    return db_id


def pad_id(db_id, db_tag) -> str:
    padding = _PADDINGS.get(db_tag)

    if padding is None or db_id.startswith(padding):
        _id = str(db_id)
    else:
        _id = padding+db_id

    return _id


def id_to_url(db_id, db_tag=None) -> str | None:
    if db_tag is None:
        db_tag = guess_db(db_id)
        if db_tag is None:
            return None

    db_id = pad_id(db_id, db_tag)
    url = None

    if db_tag == 'hmdb_id':
        url = f"https://hmdb.ca/metabolites/{db_id}"
    elif db_tag == 'chebi_id':
        url = f"https://www.ebi.ac.uk/chebi/searchId.do;?chebiId={db_id}"
    elif db_tag == 'kegg_id':
        url = f"https://www.genome.jp/dbget-bin/www_bget?cpd:{db_id}"
    elif db_tag == 'pubchem_id':
        url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{db_id}"
    elif db_tag == 'lipmaps_id':
        url = f"https://www.lipidmaps.org/data/LMSDRecord.php?LMID={db_id}"

    return url
