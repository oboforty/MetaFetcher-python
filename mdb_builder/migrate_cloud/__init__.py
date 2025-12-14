from mdb_builder.discovery import get_mdb_id
from mdb_builder.migrate_cloud.dbb_item_builder import build_mdb_record, build_search_keys, build_mid_search_key


def build_items_from_discovery(disc: dict):
    mids = list(get_mdb_id(disc))
    is_mid_inchi = disc.get('inchikey') is not None
    is_consistent_mid = len(mids) == 1

    # build main MDB record
    mdb_record = build_mdb_record(disc, mids[0])
    yield mdb_record

    # build search keys
    yield from build_search_keys(mdb_record, omit_gsi=True)

    # build extra search keys for alternative mids
    if not is_consistent_mid:
        yield from build_mid_search_key(mids[0], mids[1:])
