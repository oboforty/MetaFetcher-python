from db_dump.parsinglib import MultiDict


hmdb_id_formats = (
    # padded    - long / short
    (len('HMDB0000008'), len('HMDB00008')),
    # depadded  - long / short
    (len('0000008'), len('00008'))
)


def replace_obvious_hmdb_id(hmdb_id):
    if hmdb_id is None:
        return hmdb_id

    if hmdb_id.startswith('HMDB'):
        if len(hmdb_id) == hmdb_id_formats[0][1]:
            # keep prefix and pad with 00
            return hmdb_id[:4] + '00' + hmdb_id[4:]
        elif len(hmdb_id) != hmdb_id_formats[0][0]:
            raise Exception("Invalid HMDB ID format provided:" + str(hmdb_id))
    else:
        if len(hmdb_id) == hmdb_id_formats[1][1]:
            # pad with 00
            return '00' + hmdb_id
        elif len(hmdb_id) != hmdb_id_formats[1][0]:
            pass
            #raise Exception("Invalid HMDB ID format provided:" + str(hmdb_id))
    return hmdb_id


def flatten_hmdb_hierarchies2(r: MultiDict):
    # Secondary IDs
    secondary = r.pop('secondary_accessions', None)
    if secondary:
        r.extend('hmdb_id_alt', secondary['secondary_accessions.accession'])

    # Synonyms
    synonyms = r.pop('synonyms', None)
    if synonyms:
        r.extend('names', synonyms['synonyms.synonym'])
