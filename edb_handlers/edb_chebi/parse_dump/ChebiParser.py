import os.path

from db_dump.process.fileformats.SDFParser import parse_sdf
from db_dump.metparselib.padding import strip_prefixes
from db_dump.metparselib.parsinglib import (
    remap_keys, isnan, handle_names, flatten, handle_masses
)

from edb_handlers.edb_chebi.parselib import remap_chebi_links
from edb_handlers.edb_pubchem.parselib import split_pubchem_ids


class ChebiParser:
    id = 'chebi'

    def __init__(self, cfg):
        self.generated = 0
        self.cfg = cfg

    def parse_file(self, file_path):
        for chebi_dict in parse_sdf(file_path):
            for chebi_record in self.parse(chebi_dict):
                yield chebi_record

    def parse(self, data: dict):
        _mapping = self.cfg['attribute_mapping']
        # important_attr = set(self.cfg.get('settings.chebi_attr_etc', []))

        # strip molfile
        molfile = data.pop(None, None)
        # iupac_names = force_list(data.get('IUPAC Names'))

        remap_keys(data, _mapping, remap_chebi_links)
        # data['ch_iupac_name'] = [handle_name(name) for name in iupac_names if name is not None]

        handle_names(data)
        strip_prefixes(data)
        flatten(data, 'description')
        handle_masses(data)

        # TODO: add pubchem substance IDs ?
        sids = split_pubchem_ids(data)

        if isnan(data.get('mass')):
            data['mass'] = None
        if isnan(data.get('mi_mass')):
            data['mi_mass'] = None
        if isnan(data.get('charge')):
            data['charge'] = None

        # if 'chebi_id_alt' in etc and etc['chebi_id_alt']:
        #     etc['chebi_id_alt'] = list(map(lambda x: x.removeprefix("CHEBI:"), force_list(etc['chebi_id_alt'])))

        self.generated += 1

        data["db_source"] = "chebi"
        data["db_id"] = data["chebi_id"]

        yield data

