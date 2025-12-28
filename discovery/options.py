import dataclasses

from db_dump.utils import toml_load
import logging

logger = logging.getLogger("disco")


@dataclasses.dataclass
class Opt:
    discoverable: bool
    fetch_api: bool
    cache_enabled: bool
    cache_api_result: bool


DEFAULT_OPT = {
    "default": dict(
        discoverable = True,
        fetch_api = True,
        cache_enabled = True,
        cache_api_result = False,
    ),
    "cas": dict(
        discoverable=True,
        fetch_api=False,
        cache_enabled=False,
        cache_api_result=False,
    )
}


class DiscoveryOptions:
    def __init__(self, *, log_level=None, log_file=None, options=None):
        # Discovery options defined for each EDB source
        self.log_level = 'DEBUG'
        self.log_file = None
        self.discoverable_attributes: set[str] = set()

        self.disc: dict[str, Opt] = _to_options(DEFAULT_OPT)
        if options:
            self.disc.update(_to_options(options))

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

        logger.debug("Settings:" +
        f"Discoverable attributes: {', '.join(self.discoverable_attributes)}" +
        f"EDB: {', '.join(self.disc.keys())}")
        # "\n".join(map(str, self.opts.opts.values())))


def _to_options(overrides: dict|str=None) -> dict[str, Opt]:
    if isinstance(overrides, str):
        # file path
        overrides = toml_load(overrides)

    opts = {}
    for k, v in overrides.items():
        opts[k] = Opt(**v)
    return opts
