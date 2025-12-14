import unittest
import random
from decimal import Decimal

from mdb_builder.discovery import get_mdb_id
from mdb_builder.migrate_cloud.dbb_item_builder import get_primary_name, build_mdb_record, build_search_keys, build_mid_search_key

null = None


class DDBItemBuilderTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_primary_name(self):
        # arrange
        mdb = {
            'names': ["Adenosine-5'-triphosphate", "Atipi", "Glucobasin", "Adenylpyrophosphoric acid", "Adynol", "5'-ATP", "Triphosphaden", "adenosine triphosphate", "Adenosine 5'-triphosphorate", "Adenosine 5'-triphosphate", "5'-(Tetrahydrogen triphosphate) adenosine", "Adenosine triphosphate", "Cardenosine", "Fosfobion", "ATP", "ADENOSINE-5'-triphosphoric acid", "({[({[(2R,3S,4R,5R)-5-(6-amino-9H-purin-9-yl)-3,4-dihydroxyoxolan-2-yl]methoxy}(hydroxy)phosphoryl)oxy](hydroxy)phosphoryl}oxy)phosphonic acid", "Adetol", "Adephos", "Atriphos", "H4ATP", "Adenosine 5'-triphosphoric acid", "Phosphobion", "Striadyne", "Adenylpyrophosphorate", "Myotriphos", "Triadenyl", "Triphosphoric acid adenosine ester", "Adenylpyrophosphate", "Adenosine triphosphoric acid"],
            'attr_other': {}
        }

        # act
        pname1 = get_primary_name(mdb, sort_by_length=True)
        pname2 = get_primary_name(mdb)

        # assert
        self.assertEqual('ATP', pname1)
        self.assertEqual("Adenosine-5'-triphosphate", pname2)

    def test_builder(self):
        # arrange
        disco_run = {
            "names": ["5-[5-hydroxy-4-(3-hydroxyoct-1-en-1-yl)-3-oxo-hexahydro-2H-cyclopenta[b]furan-2-ylidene]pentanoic acid", "5-[5-hydroxy-4-(3-hydroxyoct-1-en-1-yl)-3-oxo-tetrahydro-3aH-cyclopenta[b]furan-2-ylidene]pentanoic acid", "7-Oxoprostaglandin I2", "   "],
            "chebi_id": [], "kegg_id": [], "lipmaps_id": [], "pubchem_id": ["54547164"], "hmdb_id": ["HMDB0247284"],
            "cas_id": [], "chemspider_id": [], "metlin_id": [], "mol": [], "formula": ["C20H30O6"],
            "inchi": ["InChI=1S/C20H30O6/c1-2-3-4-7-13(21)10-11-14-15(22)12-17-19(14)20(25)16(26-17)8-5-6-9-18(23)24/h8,10-11,13-15,17,19,21-22H,2-7,9,12H2,1H3,(H,23,24)"],
            "inchikey": ["ZHIHHYNLWRXTTN-UHFFFAOYSA-N"], "smiles": ["CCCCCC(O)C=CC1C(O)CC2OC(=CCCCC(O)=O)C(=O)C12"],
            "charge": [], "mass": [366.454], "mi_mass": [366.204238686],
            "description": {}, "attr_other": {},
            "result": {"is_consistent": True, "cons_edb_id": 1, "cons_attr_id": 1, "cons_mass": 1}
        }
        expected_record = {
            'mid': 'ZHIHHYNLWRXTTN-UHFFFAOYSA-N',
            'srt': 'mdb',
            'hmdb_id': '0247284',
            'smiles': 'CCCCCC(O)C=CC1C(O)CC2OC(=CCCCC(O)=O)C(=O)C12',
            'pubchem_id': '54547164',
            'inchikey': 'ZHIHHYNLWRXTTN-UHFFFAOYSA-N',
            'pname': '5-[5-hydroxy-4-(3-hydroxyoct-1-en-1-yl)-3-oxo-hexahydro-2H-cyclopenta[b]furan-2-ylidene]pentanoic acid',
            'mass': '366.454',
            'mi_mass': '366.204238686',
            'names': ['5-[5-hydroxy-4-(3-hydroxyoct-1-en-1-yl)-3-oxo-hexahydro-2H-cyclopenta[b]furan-2-ylidene]pentanoic acid','5-[5-hydroxy-4-(3-hydroxyoct-1-en-1-yl)-3-oxo-tetrahydro-3aH-cyclopenta[b]furan-2-ylidene]pentanoic acid', '7-Oxoprostaglandin I2', '   '],
            'inchi': 'InChI=1S/C20H30O6/c1-2-3-4-7-13(21)10-11-14-15(22)12-17-19(14)20(25)16(26-17)8-5-6-9-18(23)24/h8,10-11,13-15,17,19,21-22H,2-7,9,12H2,1H3,(H,23,24)',
            'formula': 'C20H30O6'
        }
        expected_search = [
            #{'srt': 'I:ZHIHHYNLWRXTTN-UHFFFAOYSA-N', 'mid': 'test_mid'},
            {'mid': 'H:0247284', 'srt': 'ZHIHHYNLWRXTTN-UHFFFAOYSA-N'},
            {'mid': 'S:CCCCCC(O)C=CC1C(O)CC2OC(=CCCCC(O)=O)C(=O)C12', 'srt': 'ZHIHHYNLWRXTTN-UHFFFAOYSA-N'},
            {'mid': 'P:54547164', 'srt': 'ZHIHHYNLWRXTTN-UHFFFAOYSA-N'},
        ]
        expected_mid_2nd = [
        ]

        # act
        mids = list(get_mdb_id(disco_run))
        ddb_record = build_mdb_record(disco_run, mids[0])
        ddb_search = list(build_search_keys(ddb_record, omit_gsi=True))
        ddb_mids = list(build_mid_search_key(mids))

        # assert
        self.assertEqual(expected_record, ddb_record)
        self.assertCountEqual(expected_search, ddb_search)
        self.assertCountEqual(expected_mid_2nd, ddb_mids)
