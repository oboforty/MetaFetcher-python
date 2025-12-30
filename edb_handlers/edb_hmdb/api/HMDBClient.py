import requests

import os.path
from io import StringIO, BytesIO

from lxml import etree

from edb_handlers.core.ApiClientBase import ApiClientBase
from metcore.parsinglib import pad_id, map_to_edb_format, preprocess, remap_keys, MultiDict
from metcore.views import MetaboliteConsistent


class HMDBClient:
    MAPPING_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'dbb', 'parse_hmdb.toml'))

    _reverse = (
        'pubchem_id', 'kegg_id', 'chebi_id',
    )

    explore_children = {'secondary_accessions','synonyms'}

    def __init__(self):
        super().__init__()

        self.load_mapping('hmdb')

    async def fetch_api(self, edb_id):
        db_id = pad_id(edb_id, 'hmdb_id')
        r = requests.get(url=f'https://hmdb.ca/metabolites/{db_id}.xml', allow_redirects=False)

        if r.is_redirect or r.status_code == 301:
            # we queried a secondary ID, follow the redirect of the api
            next_url = r.next.url+'.xml'
            print("  HMDB: redirecting to", next_url)
            r = requests.get(url=next_url)

        is_xml = r.headers['content-type'].startswith('application/xml')
        if r.status_code != 200 and r.status_code != 304 or r.content is None or not is_xml:
            return None

        #xmlns = 'http://www.hmdb.ca'
        #filter_tag = f'{{{xmlns}}}metabolite'
        filter_tag = 'metabolite'

        context = etree.iterparse(BytesIO(r.content), events=('end',), tag=filter_tag)
        context = iter(context)
        _xevt, xmeta = next(context)

        data = MultiDict()

        # parse lxml's hierarchy into a dictionary
        for tag in xmeta:
            tag_name = tag.tag#.removeprefix('{' + xmlns + '}')

            if len(tag) == 0:
                data.append(tag_name, tag.text)
            else:
                if tag_name in self.explore_children:
                    for child in tag:
                        # assert len(child) == 0
                        data.append(tag_name, child.text)
        xmeta.clear(keep_tail=False)

        remap_keys(data, self._mapping)
        preprocess(data)
        data, etc = map_to_edb_format(data, important_attr=self._important_attr)

        return MetaboliteConsistent(**data)
