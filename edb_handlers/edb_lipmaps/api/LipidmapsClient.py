import os
import requests

from edb_handlers.core.ApiClientBase import ApiClientBase
from metcore.parsinglib import pad_id


class LipidmapsClient:
    MAPPING_FILE = os.path.join(os.path.dirname(__file__), '..', 'mapping.toml')

    def __init__(self):
        super().__init__()

        self.load_mapping('lipidmaps')

    async def fetch_api(self, edb_id):
        url = f'https://www.lipidmaps.org/rest/compound/lm_id/{pad_id(edb_id, "lipmaps_id")}/all/'
        r = requests.get(url=url)

        data = r.json()
        if not data:
            return None

        raise NotImplementedError()

        remap_keys(data, self._mapping)
        preprocess(data)
        data, etc = map_to_edb_format(data, important_attr=self._important_attr, edb_format=None, exclude_etc={None})

        return MetaboliteConsistent(**data)
