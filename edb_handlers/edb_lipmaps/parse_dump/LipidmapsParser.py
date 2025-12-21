from db_dump.process.fileformats.SDFParser import parse_sdf
from db_dump.metparselib.padding import strip_prefixes
from db_dump.metparselib.parsinglib import (
    remap_keys, handle_names, flatten, handle_masses
)
from edb_handlers.edb_pubchem.parselib import split_pubchem_ids


class LipidMapsParser:
    id = 'lipmaps'

    def __init__(self, cfg):
        self.generated = 0
        self.cfg = cfg

    def parse_file(self, file_path):
        for dump_dict in parse_sdf(file_path, {'compressed_file': 'structures.sdf'}):
            for record in self.parse(dump_dict):
                yield record

    def parse(self, data: dict):
        _mapping = self.cfg['attribute_mapping']

        molfile = data.pop(None)
        remap_keys(data, _mapping)

        if 'names' in data:
            handle_names(data)
        strip_prefixes(data)
        flatten(data, 'description')
        handle_masses(data)

        # TODO: add pubchem substance IDs ?
        sids = split_pubchem_ids(data)

        data["db_source"] = "lipmaps"
        data["db_id"] = data["lipmaps_id"]

        yield data
