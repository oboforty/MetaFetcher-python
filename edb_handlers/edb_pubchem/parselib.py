
from db_dump.parsinglib import MultiDict, try_flatten, strip_attr, get_id_from_url


def parse_pubchem(edb_id, content, cont_refs, _mapping):
    """
    Parses API response for PubChem

    :param edb_id:
    :param c0:
    :param c1:
    :return:
    """

    data = MultiDict()

    # parse xrefs:
    if cont_refs:
        _links = cont_refs['InformationList']['Information'][0]['SBURL']

        # guess xref IDs
        for link in _links:
            link = link.lower()

            db_id, api_db_tag = get_id_from_url(link)

            if db_id is None:
                # unrecognized XREF
                continue
            data.append(api_db_tag+'_id', db_id)

    _resp = content['PC_Compounds'][0]
    props = _resp.pop('props')
    data.append('pubchem_id', str(_resp['id']['id']['cid']))

    hat_geci = []

    for prop in props:
        label = prop['urn']['label']

        attr, valt = _mapping.get(label, (label, 'sval'))
        attr = attr.lower()

        if isinstance(prop['value'], dict):
            value = prop['value'].get(valt)

            if value is not None:
                data.append(attr, value)
            else:
                # skip attr as it's not mapped
                hat_geci.append((attr, valt, prop['value']))
        else:
            data.append(attr, prop['value'])

    # merge and transform to standard json
    return dict(data)


def split_pubchem_ids(r):
    sids = []

    if 'pubchem_id' in r:
        if not isinstance(r['pubchem_id'], (list, tuple, set)):
            r['pubchem_id'] = [strip_attr(r['pubchem_id'], 'CID:')]

        # filter out substance IDs and flatten remaining IDs if possible
        sids = list(filter(lambda x: x.startswith("SID:"), r['pubchem_id']))
        r['pubchem_id'] = strip_attr(try_flatten(list(filter(lambda x: not x.startswith("SID:"), r['pubchem_id']))), 'CID:')

    return sids
