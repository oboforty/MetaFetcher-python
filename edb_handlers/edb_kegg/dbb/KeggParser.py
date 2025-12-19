from pipebro import Process

from metcore.parsinglib import preprocess, remap_keys, map_to_edb_format, MultiDict

from edb_handlers import EDB_SOURCES_OTHER, EDB_SOURCES
from db_dump.dtypes.MetaboliteExternal import MetaboliteExternal


class KeggParser(Process):
    consumes = MultiDict, "edb_obj"
    produces = MetaboliteExternal, "edb_record"

    def initialize(self):
        self.generated = 0

    async def produce(self, data: dict):
        _mapping = {attr: attr+'_id' for attr in EDB_SOURCES | EDB_SOURCES_OTHER} | self.cfg.conf['attribute_mapping']
        important_attr = self.cfg.get('settings.kegg_attr_etc', cast=set, default=set())

        # strip molfile
        #molfile = data.pop(None, None)

        remap_keys(data, _mapping)
        preprocess(data)
        data, etc = map_to_edb_format(data, important_attr=important_attr)

        if self.generated % 1000 == 0:
            self.app.print_progress(self.generated)
        self.generated += 1

        yield MetaboliteExternal(edb_source='kegg', **data), self.produces
