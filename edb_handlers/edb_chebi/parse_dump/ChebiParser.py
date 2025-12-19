import math
import os.path
from typing import Any

from db_dump.dtypes import MetaboliteExternal
from db_dump.process.fileformats.SDFParser import parse_sdf
from db_dump.toml_load import toml_load
from db_dump.metparselib.edb_specific import preprocess
from db_dump.metparselib.parsinglib import remap_keys, force_list, handle_name, isnan
from edb_handlers.edb_pubchem.parselib import split_pubchem_ids


def remap_chebi_links(attr: str, val) -> tuple[str, Any] | tuple[None, None]:
    if attr.endswith(" database links"):
        attr = attr.removesuffix(" database links")
        attr = attr.replace(" ", "_").replace("-", "_")
        attr += "_id"
        return attr, val
    if attr.endswith(" registry numbers"):
        attr = attr.removesuffix(" registry numbers")
        attr = attr.replace(" ", "_").replace("-", "_")
        attr += "_id"
        return attr, val

    return None, None


class ChebiParser:

    def __init__(self):
        self.generated = 0
        self.cfg = toml_load(os.path.join(os.path.dirname(__file__), "parse_chebi.toml"))

    def parse_file(self, file_path):
        for chebi_dict in parse_sdf(file_path):
            for chebi_record in self.parse(chebi_dict):
                yield chebi_record

    def parse(self, data: dict):
        _mapping = self.cfg['attribute_mapping']
        important_attr = set(self.cfg.get('settings.chebi_attr_etc', []))

        # strip molfile
        molfile = data.pop(None, None)
        iupac_names = force_list(data.get('IUPAC Names'))

        remap_keys(data, _mapping, remap_chebi_links)
        # data['ch_iupac_name'] = [handle_name(name) for name in iupac_names if name is not None]

        preprocess(data)

        # TODO: add pubchem substance IDs ?
        # data["pubchem_substance_id"] += split_pubchem_ids(data)
        # data.discard()

        # TODO: ITT: should we keep old data?

        # out_data, etc = map_to_edb_format(
        #     data,
        #     important_attr=important_attr,
        #     id_suffix=CH_DB_SUFFIX
        # )

        # if self.app.debug:
        #     assert_edb_dict(data)

        if isnan(data.get('mass')):
            data['mass'] = None
        if isnan(data.get('mi_mass')):
            data['mi_mass'] = None
        if isnan(data.get('charge')):
            data['charge'] = None

        # if 'chebi_id_alt' in etc and etc['chebi_id_alt']:
        #     etc['chebi_id_alt'] = list(map(lambda x: x.removeprefix("CHEBI:"), force_list(etc['chebi_id_alt'])))

        # if self.generated % 1000 == 0:
        #     self.app.print_progress(self.generated)
        self.generated += 1

        data["db_source"] = "chebi"
        data["db_id"] = data["chebi_id"]

        yield data
