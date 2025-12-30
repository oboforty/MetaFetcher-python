import dataclasses

from db_dump.utils import toml_load
from edb_handlers.db_sources import EDB_ID, EDB_ID_OTHER, CHEM_STRUCT_PROPERTY

import logging

logger = logging.getLogger("disco")


@dataclasses.dataclass
class Opt:
    discoverable: bool = False
    keep_in_result: bool = False
    fetch_api: bool = False
    cache_enabled: bool = False
    cache_api_result: bool = False


DEFAULT_OPT = {
    "default": dict(
        discoverable = True,
        fetch_api = True,
        cache_enabled = True,
        cache_api_result = False,
    ),
    # TODO: ITT: auto include everything?
    "names": dict(
        discoverable = False,
    )
}

for attr in EDB_ID:
    DEFAULT_OPT[attr] = dict(
        discoverable=True,
        fetch_api=True,
        cache_enabled=True,
        cache_api_result=False,
    )

for attr in EDB_ID_OTHER | CHEM_STRUCT_PROPERTY:
    DEFAULT_OPT[attr] = dict(
        discoverable=True,
        fetch_api=False,
        cache_enabled=True,
        cache_api_result=False,
    )


class DiscoveryOptions:
    def __init__(self, *, log_level=None, log_file=None, options=None):
        # Discovery options defined for each EDB source
        self.log_level = 'DEBUG'
        self.log_file = None

        self.disc: dict[str, Opt]
        if options:
            self.disc = _to_options(options)
        else:
            self.disc = _to_options(DEFAULT_OPT)

        self.discoverable_attributes: set[str] = set()
        self.result_attributes: set[str] = set()

        for key, opt in self.disc.items():
            if opt.discoverable:
                self.discoverable_attributes.add(key)
            if opt.keep_in_result:
                self.result_attributes.add(key)

        format_detail = '%(asctime)s %(levelname)s: %(message)s'
        formatter = logging.Formatter(format_detail)

        # TODO: how to reset loggers? where to call it?
        _logger = logging.getLogger('disco')
        _logger.setLevel(log_level)

        if log_file:
            # File logger
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                _logger.addHandler(file_handler)
        else:
            # Console logger
            stream_handler = logging.StreamHandler()
            # stream_handler.setLevel(log_level)
            stream_handler.setFormatter(formatter)
            _logger.addHandler(stream_handler)
            # logger.addHandler(logging.StreamHandler(sys.stdout))

        logger.debug(
            "Settings:\n"
            f"Result attributes: {', '.join(self.result_attributes)}\n"
        )
        # it's good to leave this in the non-verbose log too:
        logger.info(
            f"Discoverable attributes: {', '.join(self.discoverable_attributes)}\n"
        )

    def get_option(self, edb_source: str) -> Opt:
        opt = self.disc.get(edb_source)

        if not opt:
            opt = self.disc["default"]
        return opt


def _to_options(overrides: dict|str=None) -> dict[str, Opt]:
    if isinstance(overrides, str):
        # file path
        overrides = toml_load(overrides)
    # elif overrides is None:
    #     return {}

    opts = {}
    for k, v in overrides.items():
        opts[k] = Opt(**v)
    return opts
