import os
import pathlib
from enum import Enum

handlers_path = str(pathlib.Path(__file__).parent)
EDB_SOURCES = set(map(lambda x: x[4:], filter(lambda x: x.startswith('edb_'), os.listdir(handlers_path))))


# TODO: glycan databases are excluded, but idk if they should be part
#       glycan, glytoucan, kegg_glycan
# TODO: substance databases are excluded
#       pubchem substance ID, brenda, brenda ligand, massbank
# TODO: same for peptide DBs
#       ?

# EDBSource = Enum("EDBSource", {x: x for x in EDB_SOURCES})

EDB_SOURCES_OTHER = {
    'cas',

    'chemspider', 'metlin', 'swisslipids', 'metabolights', 'chemspider',
    "surechembl", "chembl", "swisslipids",

    # these were automatically discovered from parsing ChEBI's DB dump!
    "knapsack",
    "comptox",
    "nmrshiftdb",
    "reaxys",
    "bindingdb",
    "metacyc",
    "beilstein",
    "kegg_drug",
    "drugcentral",
    "pdbechem",
    "drugbank",
    "gmelin",
    "vmhdb",
    "foodb",
    "golm",
    "um_bbd",
    "alan_wood's_pesticides_id",
    "molbase",
    "vsdb",
    "carotenoids",
    "smid",
    "ymdb",
    "ecmdb",
    "bpdb",
    "resid",
    "chemidplus",
    "ppr",
}

"""
List of EDB_IDs that are not yet supported by MFDB, but are well known
Also includes non-metabolite refs, like protein DBs
"""
EDB_ID_OTHER = set(map(lambda x: x+'_id', iter(EDB_SOURCES_OTHER)))

EDB_ID = set(map(lambda x: x+'_id', iter(EDB_SOURCES)))

CHEM_FLOAT_PROPERTY = {'mass', 'mi_mass', "charge"}
CHEM_STRUCT_PROPERTY = {'formula', 'inchi', 'inchikey', 'smiles'}
CHEM_STRUCT_MULTI_DIM_PROPERTY = {"mol", "mol2d"} # todo: what else?

INDEXED_ATTRIBUTES = EDB_ID | {"names"} | CHEM_STRUCT_PROPERTY | CHEM_FLOAT_PROPERTY | EDB_ID_OTHER

COMMON_ATTRIBUTES = {
    *INDEXED_ATTRIBUTES,
    "description"
}

def is_edb(reftag: str | tuple[str, str]):
    if isinstance(reftag, tuple) and len(reftag)==2:
        reftag = reftag[0]

    reftag = reftag.lower().removesuffix('_id')

    return reftag in EDB_SOURCES


def load_edb_handlers(edb_types):
    h = []

    return h


__all__ = [
    'EDB_SOURCES', "EDB_ID", "EDB_ID_OTHER",
    "CHEM_STRUCT_MULTI_DIM_PROPERTY", "CHEM_FLOAT_PROPERTY", "CHEM_STRUCT_PROPERTY",
    "COMMON_ATTRIBUTES", "INDEXED_ATTRIBUTES",
    'is_edb', 'load_edb_handlers'
]
