from enum import IntFlag

from edb_handlers.db_sources import EDB_ID_OTHER, EDB_ID


attr_master_ids = {'pubchem_id', 'inchikey', 'inchi', 'formula'}
attr_edb_ids = (EDB_ID | EDB_ID_OTHER) - {'pubchem_id', 'swisslipids_id'}
attr_masses = {'mass', 'mi_mass'}
attr_etc = {'smiles', 'charge', 'formula', 'mol'}

# TODO: refactor to Rough set / fuzzy set ?

class ConsistencyClass(IntFlag):
    NONE = 0
    Consistent = 1
    Inconsistent = 2
    Missing = 4
    Huh = 8

    def __str__(self):
        if self == self.Consistent:
            return '🗸'
        elif self == self.Inconsistent:
            return '↯'
        elif self == self.Missing:
            return '∅'


def get_strict_consistency(s):
    """
    Gets strict consistency, meaning that empty sets are marked as missing
    :param s:
    :return:
    """
    length = len(s) if not hasattr(s, 'equivalence_set') else len(s.equivalence_set)
    if length == 1:
        return ConsistencyClass.Consistent
    elif length == 0:
        return ConsistencyClass.Missing
    return ConsistencyClass.Inconsistent


def get_light_consistency(s):
    """
    Gets soft consistency. Empty sets are marked consistent, as these are not mandatory attributes
    :param s:
    :return:
    """
    length = len(s) if not hasattr(s, 'equivalence_set') else len(s.equivalence_set)
    if length == 1 or length == 0:
        return ConsistencyClass.Consistent
    return ConsistencyClass.Inconsistent


def get_discovery_attribute_consistencies(meta) -> dict[str, ConsistencyClass]:
    attr_consistencies = {k: get_strict_consistency(getattr(meta, k)) for k in (attr_master_ids | attr_masses | attr_etc)}
    attr_consistencies.update({k: get_light_consistency(getattr(meta, k)) for k in attr_edb_ids})

    return attr_consistencies


def get_consistency_class(meta) -> tuple[ConsistencyClass, ConsistencyClass, ConsistencyClass]:
    c_mass = ConsistencyClass.NONE
    c_edb_ids = ConsistencyClass.NONE
    c_master_ids = ConsistencyClass.NONE

    attr_consistencies = get_discovery_attribute_consistencies(meta)

    if all(map(lambda x: attr_consistencies[x] == ConsistencyClass.Consistent, attr_master_ids)):
        c_master_ids |= ConsistencyClass.Consistent
    elif any(map(lambda x: attr_consistencies[x] == ConsistencyClass.Missing, attr_master_ids)):
        c_master_ids |= ConsistencyClass.Missing
    else:
        c_master_ids |= ConsistencyClass.Inconsistent

    if all(map(lambda x: attr_consistencies[x] == ConsistencyClass.Consistent, attr_edb_ids)):
        c_edb_ids |= ConsistencyClass.Consistent
    elif any(map(lambda x: attr_consistencies[x] == ConsistencyClass.Missing, attr_edb_ids)):
        c_edb_ids |= ConsistencyClass.Missing
    else:
        c_edb_ids |= ConsistencyClass.Inconsistent

    if all(map(lambda x: attr_consistencies[x] == ConsistencyClass.Consistent, attr_master_ids)):
        c_mass |= ConsistencyClass.Consistent
    elif any(map(lambda x: attr_consistencies[x] == ConsistencyClass.Missing, attr_master_ids)):
        c_mass |= ConsistencyClass.Missing
    else:
        c_mass |= ConsistencyClass.Inconsistent

    return c_master_ids, c_edb_ids, c_mass
