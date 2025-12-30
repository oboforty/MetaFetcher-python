import os.path
from io import BytesIO
from lxml import etree

import requests

from edb_handlers.core.ApiClientBase import ApiClientBase
from edb_handlers.edb_pubchem.parselib import split_pubchem_ids

from metcore.parsinglib import pad_id, MultiDict, remap_keys, preprocess, map_to_edb_format
from metcore.views import MetaboliteConsistent


class ChebiClient:
    MAPPING_FILE = os.path.join(os.path.dirname(__file__), '..', 'mapping.toml')

    _reverse = (
        'pubchem_id', 'kegg_id', 'hmdb_id', 'lipmaps_id',
    )
    explore_children = {}
    explore_children_data = {
        'Synonyms',
        'IupacNames',
        'Formulae'
    }
    explore_refs = {
        'RegistryNumbers': 3,
        'DatabaseLinks': 2
    }

    def __init__(self):
        super().__init__()

        self.load_mapping('chebi')

    async def fetch_api(self, edb_id):
        edb_id = pad_id(edb_id, "chebi_id")
        url = f'https://www.ebi.ac.uk/webservices/chebi/2.0/test/getCompleteEntity?chebiId={edb_id}'
        r = requests.get(url=url)

        filter_tag = 'return'
        xmlns = "https://www.ebi.ac.uk/webservices/chebi"
        filter_tag = f"{{{xmlns}}}{filter_tag}"

        context = etree.iterparse(BytesIO(r.content), events=('end',), tag=filter_tag)
        context = iter(context)
        try:
            _xevt, xmeta = next(context)
        except StopIteration:
            # xml did not found <retun> so it's empty (chebi is yet again one API that does not know the contept of status codes)
            return None

        data = MultiDict()

        # parse lxml's hierarchy into a dictionary
        for tag in xmeta:
            tag_name = tag.tag.removeprefix(f'{{{xmlns}}}')

            if len(tag) == 0:
                data.append(tag_name, tag.text)
            else:
                if tag_name in self.explore_children:
                    for child in tag:
                        data.append(tag_name, child.text)
                elif tag_name in self.explore_children_data:
                    for child in tag:
                        if child.tag.removeprefix(f'{{{xmlns}}}') == 'data':
                            data.append(tag_name, child.text)
                elif tag_name in self.explore_refs:
                    repeat = self.explore_refs[tag_name]
                    it = iter(tag)

                    for children in zip(*([it] * repeat)):
                        sdata = next(filter(lambda x: x.tag.removeprefix(f'{{{xmlns}}}') == 'data', children))
                        stype = next(filter(lambda x: x.tag.removeprefix(f'{{{xmlns}}}') == 'type', children))

                        sub_tag = stype.text.lower().replace(' accession', '_id').replace(' registry number', '_id')

                        data.append(sub_tag, sdata.text)

        xmeta.clear(keep_tail=False)

        remap_keys(data, self._mapping)

        preprocess(data)
        sids = split_pubchem_ids(data)

        data, etc = map_to_edb_format(data, important_attr=self._important_attr)

        return MetaboliteConsistent(**data)
