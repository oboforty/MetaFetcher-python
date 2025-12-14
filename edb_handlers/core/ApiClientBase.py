import os.path
from abc import ABCMeta, abstractmethod

from metcore.utils import toml_load
from metcore.views import MetaboliteConsistent
from pipebro import SettingWrapper


class ApiClientBase(metaclass=ABCMeta):
    MAPPING_FILE: str = None

    _mapping: dict
    _reverse: tuple | set
    _important_attr: set

    def load_mapping(self, edb_source):
        # load mapping files
        s = SettingWrapper(toml_load(self.MAPPING_FILE))

        self._mapping = s['attribute_mapping']
        self._important_attr = set(s.get('attributes', {}).get(f'{edb_source}_attr_etc', []))

        return s

    @abstractmethod
    async def fetch_api(self, edb_id) -> MetaboliteConsistent:
        pass
