_PADDINGS = {
    'hmdb_id': 'HMDB',
    'chebi_id': 'CHEBI:',
    #'kegg_id': 'C',
    'lipmaps_id': 'LM',
    'inchi': 'InChI='
}


def strip_attr(v: list | set | str, prefix):
    if not v:
        return v

    if isinstance(v, list):
        return list(map(lambda v: v.removeprefix(prefix).lstrip(), v))
    else:
        return v.removeprefix(prefix).lstrip()


def strip_prefixes(data: dict):
    for edb_tag, prefix in _PADDINGS.items():
        if edb_tag in data:
            data[edb_tag] = strip_attr(data[edb_tag], prefix)


def guess_db(db_id: str):
    for db_tag, _pad in _PADDINGS.items():
        if db_id.startswith(_pad):
            return db_tag


def depad_id(db_id, db_tag=None):
    if db_id is None:
        return None

    if db_tag is None:
        db_tag = guess_db(db_id)

        if db_tag is None:
            raise Exception("db_tag not provided for depad_id. How couldst i depad yond hast mere db tag?")

    db_id = db_id.removeprefix(_PADDINGS.get(db_tag, ""))

    return db_id


def pad_id(db_id, db_tag):
    padding = _PADDINGS.get(db_tag)

    if padding is None or db_id.startswith(padding):
        _id = str(db_id)
    else:
        _id = padding+db_id

    return _id


def id_to_url(db_id, db_tag=None):
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


def get_id_from_url(link):
    link = link.lower()

    if 'ebi.ac.uk/chebi' in link or 'ebi.ac.uk/webservices/chebi/' in link:
        # http://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:18102
        db_id = link.split('chebiid=chebi:')[1].upper().removesuffix('.XML')
        return db_id, 'chebi'
    elif 'chemspider.com' in link:
        # http://www.chemspider.com/Chemical-Structure.10128115.html
        db_id = link.split('.')[-2]
        return db_id, 'chemspider'
    elif 'lipidmaps.org' in link:
        # http://www.lipidmaps.org/data/LMSDRecord.php?LM_ID=LMFA07070002
        db_id = link.lower().split('lm_id=')[1].upper()
        return db_id, 'lipmaps'
    elif 'hmdb.ca' in link:
        # https://hmdb.ca/metabolites/HMDB0000791
        db_id = link.split('metabolites/')[1].upper().removesuffix('.XML')
        return db_id, 'hmdb'
    elif 'rest.kegg.jp/get' in link:
        # https://rest.kegg.jp/get/cpd:C01390+C01197
        db_ids = list(map(lambda x: x.removeprefix('cpd:').removeprefix('CPD:'), link.split('.jp/get/')[1].upper().split('+')))

        if len(db_ids) == 1:
            return db_ids[0], 'kegg'
        return db_ids, 'kegg'
    else:
        return None, None
