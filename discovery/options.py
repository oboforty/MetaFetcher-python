import dataclasses
import os.path
import pathlib

from db_dump.utils import toml_load
from edb_handlers.db_sources import EDB_ID, EDB_ID_OTHER, CHEM_STRUCT_PROPERTY, INDEXED_ATTRIBUTES, EDB_SOURCES, \
    EDB_SOURCES_OTHER

import logging

logger = logging.getLogger("disco")


@dataclasses.dataclass
class Opt:
    edb_source: str

    # if enabled, will keep this attribute in the result.
    keep_in_result: bool = False

    # allows to fetch from DB's API. will yield an error if API Client is not implemented for this external DB!
    fetch_api: bool = False

    # allows to fetch from the `.db` cache external database dump files. This option assumes that the user has inserted a DB dump file!
    cache_enabled: bool = False

    # if an API entry was found, saves it to the `.db` cache, if this option is enabled
    cache_api_result: bool = False

    @property
    def discoverable(self) -> bool:
        return self.fetch_api or self.cache_enabled

    def __repr__(self):
        return (
            f"keep_in_result:     {self.keep_in_result}\n"
            f"fetch_api:          {self.fetch_api}\n"
            f"cache_enabled:      {self.cache_enabled}\n"
            f"cache_api_result:   {self.cache_api_result}\n"
        )

DEFAULT_OPT_FILE = str(pathlib.Path(__file__).parent.joinpath("profiles/full_discovery.toml"))


class DiscoveryOptions:
    def __init__(self, *, log_level=None, log_file=None, options=None):
        # Discovery options defined for each EDB source
        self.log_level = 'DEBUG'
        self.log_file = None

        self.disc: dict[str, Opt]
        if options:
            self.disc = _to_options(options)
        else:
            self.disc = _to_options(DEFAULT_OPT_FILE)

        # self.discoverable_attributes: set[str] = set()
        self.result_attributes: set[str] = set()

        # TODO: this won't account for many EDB specific attributes!
        for key in INDEXED_ATTRIBUTES:
            opt = self.get_option(key)
            if opt.keep_in_result:
                self.result_attributes.add(key)

        formatter = logging.Formatter(
            '%(asctime)s %(message)s',
            "%Y-%m-%d %H:%M:%S"
        )

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

        options_str = []
        for key, opt in self.disc.items():
            options_str.append(f'[{key}]\n{opt}')

        logger.info(
            f"Run options:\n{'\n'.join(options_str)}"
        )
        # TODO: add some info log for the log file's start?

    def get_option(self, edb_source: str) -> Opt:
        opt = self.disc.get(edb_source)

        if not opt:
            # find default override
            if edb_source in EDB_ID or edb_source in EDB_ID_OTHER:
                opt = self.disc.get('default.ids')
            elif edb_source in INDEXED_ATTRIBUTES:
                # attributes other than ID:
                opt = self.disc.get('default.common_attributes')
            else:
                opt = self.disc.get('default.other_attributes')

        if not opt:
            # ultimate default, everything is False
            # this is present only when [default.other_attributes] is missing from the options file
            opt = Opt(edb_source)
        return opt


def _to_options(overrides: dict | str=None) -> dict[str, Opt]:
    if isinstance(overrides, str):
        # file path
        overrides = toml_load(overrides)
    # elif overrides is None:
    #     return {}

    opts = {}
    for edb_source, opt in overrides.items():
        if edb_source == 'default':
            # nested option (default.*)
            for k, v in opt.items():
                opts['default.' + k] = Opt(k, **v)
        else:
            opts[edb_source] = Opt(edb_source, **opt)
    return opts
