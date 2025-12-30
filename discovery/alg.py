import queue
from sys import meta_path
from typing import Protocol

from .metabolite import MetaboliteIndex, iter_of_type
from .options import DiscoveryOptions
from .utils.padding import depad_id, pad_id

from logging import getLogger

logger = getLogger("disco")

EDB_REF = tuple[str, str] # should really be tuple[Literal[INDEXED_ATTRIBUTES], str]
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
    undiscovered: set[EDB_REF]
    """
    Lists EDB_IDs and ref-attributes that have been successfully queries or fetched by the algorithm
    """
    discovered: set[EDB_REF]
    """
    EDB references that have already been in the queue (as the first item in QUEUE_ITEM)
    This guarantees that the BFS algorithm eventually stops
    """
    been_in_queue: set[EDB_REF]

    def __init__(self, *, edb: LocalEDB, apis: dict[str, ExternalAPI], options: DiscoveryOptions):
        self.options = options
        self.apis = apis
        self.edb = edb

        # Data sets and state variables used for the algorithm
        self.Q = queue.Queue()
        self.undiscovered = set()
        self.secondary_ids = set()
        self.ambiguous = []
        self.discovered = set()
        self.been_in_queue = set()

        # main object to aggregate EDB sources
        self.meta: MetaboliteIndex = MetaboliteIndex()

    def run_discovery(self):
        logger.debug('Starting discovery.')

        while not self.Q.empty():
            edb_target, edb_referrer = self.Q.get()

            # Query metabolite record from local database or web api
            logger.debug(f"[QUERY] {edb_referrer[0]}:{edb_referrer[1]} => {edb_target[0]}:{edb_target[1]}")

            edb_records = self.get_metabolite(edb_target)

            if not edb_records:
                logger.debug(f'[UNDISCOVERED] Manager returned None for EDB ref: {edb_target[0]}:{edb_target[1]}')

                for edb_target_ in iter_of_type(edb_target):
                    self.undiscovered.add((edb_target[0], edb_target_))
                continue

            logger.info(f"[DISCOVERED] {edb_referrer[0]}:{edb_referrer[1]} => {edb_target[0]}:{edb_target[1]}")
            self.discovered.add(edb_target)

            for edb_record in edb_records:
                # edb record was discovered, add it to previously discovered data:
                # TODO: option to keep sources separate? or to merge them?
                edb_record.pop("db_source", None)
                edb_record.pop("db_id", None)

                # TODO: what to do with list items?

                self.meta.update(edb_record)

                self.enqueue_novel_ids(edb_target, edb_record)

        return self.finish_discovery()

    def get_metabolite(self, edb_ref: EDB_REF) -> list[dict]:
        """

        :return:
        """
        edb_records: list[dict] | None = None

        edb_source, edb_id = edb_ref[0].removesuffix('_id'), edb_ref[1]
        opts = self.options.get_option(edb_source)

        if opts.cache_enabled:
            edb_records = self.edb.get_metabolites(edb_source, edb_id)

        if not edb_records and opts.fetch_api:
            # if edb_record := await self.fetch_api(edb_source, edb_id, save_in_cache=opts.cache_upsert):
            #     #logger.debug(f"API response for {edb_source}:{edb_id}]: {edb_record}")
            #     edb_records = [edb_record]
            logger.warning(f"Record {edb_source}:{edb_id}] was not cached in bulk EDB database, "
                           f"and API fetching is disabled for {edb_source}."
                           f"You sould enable API fetching in options")

            if opts.cache_api_result:
                pass

        result = "Found" if edb_records else "Not found"
        logger.debug(f"[GET] {edb_source}:{edb_id} -- {result}")

        return edb_records

    def enqueue_novel_ids(self, edb_ref: EDB_REF, edb_record: dict):
        """
        Parses edb_record's attributes and IDs that haven't been explored before and enqueues them for discovery

        :param edb_ref: EDB reference (DB source + DB ID) for the EDB record
        :param edb_record: external database record

        :return: true if new IDs/attributes were enqueued in record
        """
        found_new = False

        # find novel EDB IDs and attribute references within this view
        for edb_id_tuple in edb_record.items():
            edb_target = edb_id_tuple[0].removesuffix('_id'), edb_id_tuple[1]
            opts = self.options.get_option(edb_target[0])

            if not opts.discoverable or edb_target in self.been_in_queue:
                for edb_target_ in iter_of_type(edb_target[1]):
                    undiscovered_entry = (edb_target[0], edb_target_)
                    if undiscovered_entry not in self.discovered:
                        logger.debug(f'[UNDISCOVERED] {edb_ref[0]}:{edb_ref[1]} -> {undiscovered_entry[0]}:{undiscovered_entry[1]}')
                        self.undiscovered.add(undiscovered_entry)
                continue

            logger.debug(f'[DISCOVERED] Found novel ID: {edb_id_tuple[0]} in {edb_ref[0]}:{edb_ref[1]} -> {edb_target[0]}:{edb_target[1]}')

            self.Q.put((edb_target, edb_ref))
            for edb_target_ in iter_of_type(edb_target[1]):
                self.been_in_queue.add((edb_target[0], edb_target_))
            found_new = True

        return found_new

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

    def set_input(self, record_input: dict):
        self.meta = MetaboliteIndex(record_input)
        self.meta.allowed_keys = self.options.discoverable_attributes

        edb_ref_input: EDB_REF = ("root_input", "-")
        self.enqueue_novel_ids(edb_ref_input, record_input)

    def clear(self):
        self.Q = queue.Queue()

        self.undiscovered.clear()
        self.secondary_ids.clear()
        self.ambiguous.clear()
        self.discovered.clear()
        self.been_in_queue.clear()


class ExternalAPI(Protocol):
    def fetch_api(self, edb_id) -> dict:
        ...


class LocalEDB(Protocol):
    def get_metabolites(self, edb_source: str, edb_id: str) -> list[dict]:
        ...
