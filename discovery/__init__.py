from typing import Callable

from .alg import DiscoveryAlg, EDB_REF, ExternalAPI, LocalEDB
from .db import edb_connect
from .options import DiscoveryOptions
from .utils.padding import depad_id, pad_id


def discover(
    edp_sources: EDB_REF | dict | list[EDB_REF] | list[dict],
    *,
    db_file: str,
    options: dict | str = None,
    log_file: str = None,
    log_level = None,
    mapper: Callable = None
) -> list[DiscoveryAlg]:
    edp_sources: list[dict]
    if isinstance(edp_sources, list) and len(edp_sources) == 0:
        raise IndexError('No edp_sources provided (len=0)')

    # force to list[dict]
    if mapper is not None:
        edp_sources = dict([mapper(s,v) for s,v in edp_sources]) # noqa
    elif isinstance(edp_sources, dict):
        edp_sources = [edp_sources]
    elif isinstance(edp_sources, tuple):
        edp_sources = [dict([edp_sources])] # noqa
    elif not (isinstance(edp_sources, list) and isinstance(edp_sources[0], dict)):
        raise NotImplementedError("Invalid edp_sources type: {}".format(type(edp_sources)))

    # merge with default options
    alg_options = DiscoveryOptions(
        log_level=log_level,
        log_file=log_file,
        options=options
    )

    apis: dict[str, ExternalAPI] = {}
    edb: LocalEDB = edb_connect(db_file)

    runs = []
    for meta_start in edp_sources:
        alg = DiscoveryAlg(apis=apis, edb=edb, options=alg_options)
        alg.set_input(meta_start)

        runs.append(alg)

    return runs
