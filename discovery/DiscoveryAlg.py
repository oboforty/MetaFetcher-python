import queue
from typing import Generator, Callable

from edb_handlers.db_sources import EDBSource, is_edb, EDB_REF
from .options import DiscoveryOptions
from .utils.padding import depad_id, pad_id

from logging import getLogger, Logger

logger = getLogger("disco")


QUEUE_ITEM = tuple[EDB_REF, EDB_REF]


class DiscoveryAlg:
    """
    EDB Manager that utilizes a local relational database to access EDB sources.
    It still uses remote API
    """

    """
    Queue that drives the discovery algorithm.
    - First tuple is the EDB reference (EDB source + EDB ID) to be resolved
    - Second tuple is the EDB reference that referenced the first EDB ID
    """
    Q: queue.Queue[QUEUE_ITEM]
    """
    Queue items that have failed to be resolved
    """
    undiscovered: set[QUEUE_ITEM]
    """
    Lists EDB_IDs and ref-attributes that have been successfully queries or fetched by the algorithm
    """
    discovered: set[EDB_REF]
    """
    EDB references that have already been in the queue (as the first item in QUEUE_ITEM)
    This guarantees that the BFS algorithm eventually stops
    """
    been_in_queue: set[EDB_REF]

    def __init__(self, options: DiscoveryOptions):
        self.options = options

        # Data sets and state variables used for the algorithm
        self.Q = queue.Queue()
        self.undiscovered = set()
        self.secondary_ids = set()
        self.ambiguous = []
        self.discovered = set()
        self.been_in_queue = set()

        # main object to aggregate EDB sources
        self.meta = None

    def run_discovery(self):
        logger.debug('Starting discovery.')

        while not self.Q.empty():
            edb_ref, edb_src = self.Q.get()

            # Query metabolite record from local database or web api
            logger.debug(f"{edb_src[0]}[{edb_src[1]}] -> {edb_ref[0]}[{edb_ref[1]}]")

            edb_records = self.get_metabolite(*edb_ref)

            if not edb_records:
                logger.debug(f'[UNDISCOVERED] Manager returned None for EDB ref: {edb_ref[0]}[{edb_ref[1]}]')

                self.undiscovered.add((edb_ref, edb_src))
                continue

            logger.info(f"[DISCOVERED] {edb_src[0]}[{edb_src[1]}] -> {edb_ref[0]}[{edb_ref[1]}]")
            self.discovered.add(edb_ref)

            for edb_record in edb_records:
                # edb record was discovered, add it to previously discovered data:
                self.meta.merge(edb_record)

                self.enqueue_novel_ids(edb_ref, edb_record)

        return self.finish_discovery()

    def enqueue_novel_ids(self, edb_ref: EDB_REF, edb_record: dict):
        """
        Parses edb_record's attributes and IDs that haven't been explored before and enqueues them for discovery

        :param edb_ref: EDB reference from which the record was found
        :param edb_record: external database record

        :return: true if new IDs/attributes were enqueued in record
        """
        found_new = False

        # find novel EDB IDs and attribute references within this view
        for edb_new in edb_record.items():
            if edb_new == edb_ref:
                continue

            logger.debug(f'Found novel ID: {edb_new[0]}[{edb_new[1]}] from {edb_ref[0]}[{edb_ref[1]}]')

            self.enqueue(edb_new, edb_ref)
            found_new = True

        return found_new

    def enqueue(self, edb_ref: EDB_REF, edb_src: str | EDB_REF):

        if not edb_ref not in self.options.discoverable_attributes:
            logger.debug(f'[UNDISCOVERED] Attribute {edb_ref[0]} is not discoverable by config: {edb_ref[0]}[{edb_ref[1]}]')

            # unsupported EDB source, no need to enqueue because it can't be resolved by the manager
            self.undiscovered.add((edb_ref, edb_src))
            return False
        elif edb_ref not in self.been_in_queue and edb_ref != edb_src:
            logger.debug(f'Enqueue: {edb_src[0]}[{edb_src[1]}] -> {edb_ref[0]}[{edb_ref[1]}]')

            # enqueue for exploration, but only if it hasn't occurred before
            self.Q.put((edb_ref, edb_src))
            self.been_in_queue.add(edb_ref)

        return True

    def finish_discovery(self):
        assert self.Q.empty()

        # remove secondary IDs from discovery result
        for edb_tag, edb_id in self.secondary_ids:
            s: set = getattr(self.meta, edb_tag)
            s.discard(depad_id(edb_id, edb_tag))
            s.discard(pad_id(edb_id, edb_tag))

        # todo: @later: clear and return an object representing all the data
        #self.clear()

        logger.debug("Discovery finished! --------\n")

    def clear(self):
        self.Q = queue.Queue()

        self.undiscovered.clear()
        self.secondary_ids.clear()
        self.ambiguous.clear()
        self.discovered.clear()
        self.been_in_queue.clear()


def discover(
    edp_sources: EDB_REF | dict | list[EDB_REF] | list[dict],
    *,
    db_file: str,
    options: dict = None,
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
    options = DiscoveryOptions(
        log_level=log_level,
        log_file=log_file,
        options=options
    )

    runs = []
    for meta_start in edp_sources:
        alg = DiscoveryAlg(options)
        runs.append(alg)

        alg.meta = meta_start
        input_edb_ref: EDB_REF = ("root_input", "-")
        alg.enqueue_novel_ids(input_edb_ref, alg.meta)

    return runs
