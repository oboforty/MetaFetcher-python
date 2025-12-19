from collections.abc import Callable

from .padding import strip_prefixes
from .parsinglib import force_flatten, try_flatten, handle_names, flatten, handle_masses
from .structs import MultiDict
from .types import EDB_SOURCES, EDB_ID_OTHER, COMMON_ATTRIBUTES

EDB_IDS = set(map(lambda x:x+'_id', EDB_SOURCES))

# TODO: refactor, move this into parsinglib?


def preprocess(data: dict):
    """
    Executes general EDB parsing that are needed for all major DBs
    :param data:
    :return:
    """
    handle_names(data)

    strip_prefixes(data)

    flatten(data, 'description')

    handle_masses(data)
