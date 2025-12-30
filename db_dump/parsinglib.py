import math
from decimal import Decimal
from itertools import chain
from typing import Callable, Iterator

_PADDINGS = {
    'hmdb_id': 'HMDB',
    'chebi_id': 'CHEBI:',
    #'kegg_id': 'C',
    'lipmaps_id': 'LM',
    'inchi': 'InChI='
}

_REPLACE_CHARS = {
    # normalized quotations chr(8221) chr(96)
    ord('"'): '”',
    8243: '”',  # ″
    8221: '”',  # ”
    8217: "'",  # ’
    8242: "'",  # ′
    8216: "'",  # ‘
    96: "'",  # `
    # normalized dash
    173: '-',  # ­
    8211: '-',  # –
    8209: '-',  # ‑
    # special representation that are converted back frontend side
    #ord('\\'): '<ESC>',
    # manual input errors that are post-corrected (+tab, NL characters)
    160: ' ',  #  
    65279: ' ',  # ﻿
    8203: ' ',  # ​
    65533: ' ',   # �
    8201: ' ',  #
} | {i: ' ' for i in range(1, 32)}


class MultiDict(dict):
    """
    A dict-like object that tries to keep added items scalar
    """

    def append(self, key, value):
        if (oldval := self.get(key)) is not None:
            # there are multiple entries in buffer, store them in a list
            if not isinstance(oldval, list):
                oldval = [oldval]
                self.__setitem__(key, oldval)

            oldval.append(value)
        else:
            self.__setitem__(key, value)

    def extend(self, key, value: list | set | Iterator):
        if isinstance(value, (list, tuple, set)):
            for val in value:
                self.append(key, val)
        else:
            self.append(key, value)

    def update(self, dict2, **kwargs) -> None:
        for k,v in dict2.items():
            self.extend(k, v)


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


def rlen(v):
    if isinstance(v, list):
        return len(v)
    elif v is None:
        return 0
    else:
        return 1


def _nil(var):
    if not bool(var):
        return True
    # accounts for xml newlines, whitespace & etc
    s = var.strip().replace('\r', '').replace('\n', '')
    return not bool(s)


def flatten(v: dict, attr):
    if attr in v and isinstance(v[attr], (list, tuple, set)):
        v[attr] = try_flatten(v[attr])


def try_flatten(arr: list):
    """
    Flattens collections within dict if their lengths = 1
    :param v: dict
    :param attr: attribute to flatten
    :return:
    """

    if isinstance(arr, (list, tuple, set)) and len(arr) <= 1:
        # scalar
        return next(chain(arr), None)
    return arr


def force_flatten(arr, store_in: list):
    """
    Flattens collections regardless of size
    :param coll: collection to flatten
    :param store_in: extra container to store stripped attributes in
    :return:
    """
    if isinstance(arr, (list, tuple, set)):
        if len(arr) > 1:
            store_in.append(list(arr)[1:])
            return arr[0]

        return next(chain(arr), None)
    # scalar
    return arr


def force_list(coll):
    """
    Forces value to be a list of element 1
    """
    if isinstance(coll, (list, tuple, set)):
        return list(coll)
    return [coll]


def remap_keys(v, _mapping: dict, remap: Callable = None):
    for k in set(v):
        if k.lower() in _mapping:
            new_key = _mapping[k.lower()]
            new_value = v.pop(k)
        else:
            if remap:
                new_key, new_value = remap(k.lower(), v[k])

                if new_key is None:
                    # keep old kvp (but make it lowercase)
                    new_key = k.lower()
                    new_value = v.pop(k)
                else:
                    # drop old value
                    v.pop(k)
            else:
                # keep old kvp (but make it lowercase)
                new_key = k.lower()
                new_value = v.pop(k)

        if new_key not in v:
            # best effort to keep things scalar
            v[new_key] = new_value
        else:
            # if multiple values found, extend it to be a list
            if not isinstance(v[new_key], list):
                v[new_key] = [v[new_key]]

            if isinstance(new_value, list):
                v[new_key].extend(new_value)
            else:
                v[new_key].append(new_value)


def strip_esc_ad(txt):
    if '\\d' in txt:
        txt = txt.replace('\\d', 'd')
    if '\\a' in txt:
        txt = txt.replace('\\a', 'a')
    return txt


def handle_name(name: str):
    return strip_esc_ad(name).translate(_REPLACE_CHARS)


def handle_names(data: dict):
    if not isinstance(data['names'], (tuple, list, set)):
        data['names'] = [handle_name(data['names'])]
    else:
        data['names'] = list(set(handle_name(n) for n in data['names'] if n is not None))


def handle_masses(me: dict):
    try:
        me['mass'] = float(me['mass'])
    except (TypeError, KeyError, ValueError):
        me['mass'] = None
    try:
        me['mi_mass'] = float(me['mi_mass'])
    except (TypeError, KeyError, ValueError):
        me['mi_mass'] = None
    try:
        me['charge'] = float(me['charge'])
    except (TypeError, KeyError, ValueError):
        me['charge'] = None


def replace_esc(s: str):
    if '\\' in s:
        return s.replace('\\', '<ESC>')
    return s

def isnan(value):
    if isinstance(value, Decimal):
        return value.is_nan()

    try:
        return math.isnan(value)
    except (TypeError, ValueError):
        pass

    return False
