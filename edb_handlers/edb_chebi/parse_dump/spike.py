from db_dump.fileformats.SDFParser import parse_sdf
from db_dump.utils import toml_load
from edb_handlers.edb_chebi.parse_dump.ChebiParser import ChebiParser
import os


def check_names(in_file):
    cfg = toml_load(os.path.join(os.path.dirname(__file__), "parse_chebi.toml"))
    dump_parser = ChebiParser(cfg)

    # TODO: spike
    violated_names = 0
    violated_records = 0
    names = []
    i = 0
    inames = 0

    for row in dump_parser.parse_file(in_file):
        is_violetas = False
        for name in row.get("names"):
            if ';' in name:
                names.append(name)
                is_violetas = True
                violated_names += 1
            inames += 1

        if is_violetas:
            violated_records += 1
        i += 1

    print("-----------------")
    print(inames, violated_names,'   ', i, violated_records)

    print(len(names))


def check_names2(in_file):
    cfg = toml_load(os.path.join(os.path.dirname(__file__), "parse_chebi.toml"))
    dump_parser = ChebiParser(cfg)

    reverse_mapping = set()
    for k,v in dump_parser.cfg['attribute_mapping'].items():
        if v == "names":
            reverse_mapping.add(k)

    name_keys = set()

    i = 0
    for chebi_dict in parse_sdf(in_file):
        fin = False

        for key, name in chebi_dict.items():
            if key and key.lower() in reverse_mapping:
                if name and ';' in name:
                    name_keys.add(key)
                    # for subname in name.split(';'):
                    #     print(key, "  ", subname)
                    fin = True
        if fin:
            # print(chebi_dict.get("chebi_id"), chebi_dict)
            # print("--------------------------------------------")
            i += 1

            # if i == 20:
            #     break
    print(name_keys)

check_names2("./data/dumps/chebi.sdf.gz")
