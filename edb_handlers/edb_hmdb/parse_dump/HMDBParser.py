from db_dump.fileformats.XMLFastParser import parse_xml
from db_dump.parsinglib import (
    remap_keys, handle_names, flatten, handle_masses, force_list, strip_prefixes
)
from edb_handlers.edb_pubchem.parselib import split_pubchem_ids

from .parselib import replace_obvious_hmdb_id


_key_mapping = {
    ord('\n'): ''
}


class HMDBParser:
    id = 'hmdb'

    def __init__(self, cfg):
        self.generated = 0
        self.cfg = cfg

        xmlns = 'http://www.hmdb.ca'
        self.xml_parse_options = dict(
            compressed_file='hmdb_metabolites.xml',
            xmlns_tag= f'{{{xmlns}}}',
            root_tag =  f'{{{xmlns}}}metabolite',
            parse_hierachy_tags = ['secondary_accessions', 'synonyms']
        )

    def parse_file(self, file_path):
        for dump_dict in parse_xml(file_path, self.xml_parse_options):
            for record in self.parse(dump_dict):
                yield record

    def parse(self, data: dict):
        _mapping = self.cfg['attribute_mapping']

        remap_keys(data, _mapping)

        handle_names(data)
        strip_prefixes(data)
        flatten(data, 'description')
        handle_masses(data)

        if 'hmdb_id_alt' in data and data['hmdb_id_alt']:
            # strip obvious redundant IDs and only store actual secondaries
            id2nd = set(map(lambda x: x.removeprefix("HMDB").translate(_key_mapping).strip(), force_list(data['hmdb_id_alt'])))
            id2nd -= {data['hmdb_id'], '', ' ', '  '}
            id2nd = {replace_obvious_hmdb_id(x) for x in id2nd}

            data['hmdb_id_alt'] = list(id2nd)

        if 'kegg_id' in data:
            if data['kegg_id'] is None:
                del data['kegg_id']
            else:
                # clean kegg_id of whitespaces as some hmdb has it
                data['kegg_id'] = data['kegg_id'].strip()

        data["db_source"] = "hmdb"
        data["db_id"] = data["hmdb_id"]
        yield data.as_dict()
