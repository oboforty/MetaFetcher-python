from pipebro import Process

from metcore.parsinglib import preprocess, remap_keys, map_to_edb_format, MultiDict, force_list

from .parselib import replace_obvious_hmdb_id
from edb_builder.utils.verify_edb_dict import assert_edb_dict
from db_dump.dtypes import MetaboliteExternal, SecondaryID


_key_mapping = {
    ord('\n'): ''
}


class HMDBParser(Process):
    consumes = MultiDict, "edb_obj"
    produces = (
        (MetaboliteExternal, "edb_record"),
        (SecondaryID, "2ndid")
    )

    def initialize(self):
        self.generated = 0

    async def produce(self, data: MultiDict):
        _mapping = self.cfg.conf['attribute_mapping']
        important_attr = self.cfg.get('attributes.hmdb_attr_etc', cast=set)

        remap_keys(data, _mapping)

        preprocess(data)

        # flattens lists of len=1
        data, etc = map_to_edb_format(data, important_attr=important_attr)

        # split_pubchem_ids(data)

        if self.app.debug:
            assert_edb_dict(data)

        if 'hmdb_id_alt' in etc and etc['hmdb_id_alt']:
            # strip obvious redundant IDs and only store actual secondaries
            id2nd = set(map(lambda x: x.removeprefix("HMDB").translate(_key_mapping).strip(), force_list(etc['hmdb_id_alt'])))
            id2nd -= {data['hmdb_id'], '', ' ', '  '}
            id2nd = {replace_obvious_hmdb_id(x) for x in id2nd}

            if id2nd:
                yield SecondaryID(edb_id=data['hmdb_id'], secondary_ids=list(id2nd), edb_source='hmdb'), self.produces[1]

        if 'kegg_id' in data:
            # clean kegg_id of whitespaces as some hmdb has it
            data['kegg_id'] = data['kegg_id'].strip()

        if self.generated % 1000 == 0:
            self.app.print_progress(self.generated)
        self.generated += 1

        yield MetaboliteExternal(edb_source='hmdb', **data), self.produces[0]
