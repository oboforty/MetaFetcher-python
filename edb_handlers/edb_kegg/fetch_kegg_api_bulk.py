import asyncio
import math
import os
import time

from pipebro import pipe_builder
from pipebro.ProcessImpl import JSONLinesSaver

from edb_handlers.edb_kegg.dbb.KeggApiFetcher import KeggApiFetcher

cfg_path = os.path.join(os.path.dirname(__file__), 'config')
TABLE_NAME = 'edb_tmp'

DB_SPLIT = 5
PARSE_AT_ONCE = 2000
remaining_ids = []


async def task_fetch_kegg_records(task_id: int, t1, kegg_ids: list, json_kegg_saver):
    with pipe_builder() as pb:
        pb.cfg_path = cfg_path
        pb.set_runner('serial')

        pb.add_processes([
            keggfetcher := KeggApiFetcher("kegg_api", ti=task_id, t1=t1, dbsplit=DB_SPLIT, consumes="kegg_ids", produces="kegg_raw"),
            json_kegg_saver
        ])
        app = pb.build_app()

    print(f"TASK #{task_id}: Fetching {len(kegg_ids)} records from KEGG...")

    app.start_flow(kegg_ids, (list, "kegg_ids"))
    await app.run()

    print(f"Task #{task_id}: done!")

    remaining_ids.extend(keggfetcher.ids_left)

    if keggfetcher.ids_weird:
        print("IDS not asked but got in response:")
        print(keggfetcher.ids_weird)

    if keggfetcher.ids_missing:
        print("IDS missing:")
        print(keggfetcher.ids_missing)

async def main():
    # chop off first N items of kegg id list and keep the rest
    with open('db_dumps/kegg_ids.txt') as fh:
        kegg_ids = list(map(lambda x: x.rstrip('\n'), fh))
    parse_ids, kegg_ids = kegg_ids[:PARSE_AT_ONCE], kegg_ids[PARSE_AT_ONCE:]
    L = math.ceil(PARSE_AT_ONCE / DB_SPLIT)

    print(f"Spawning {DB_SPLIT} tasks to process {len(parse_ids)} kegg_ids")
    t1 = time.time()

    # shared JSON lines for one kegg dump file
    json_kegg_saver = JSONLinesSaver("json_kegg_save", consumes="kegg_raw")
    # do not dispose file handle
    def noop():
        pass
    json_kegg_saver.dispose = noop

    # spawn N tasks
    tasks = [asyncio.create_task(task_fetch_kegg_records(i, t1, parse_ids[L * i:L * (i + 1)], json_kegg_saver)) for i in range(DB_SPLIT)]
    await asyncio.gather(*tasks)

    try:
        json_kegg_saver.fh.close()
    except:
        pass

    # save remaining IDs back to file for next processing
    print('Remaining IDs to parse:', len(kegg_ids), ', skipped: ', len(remaining_ids))

    with open('db_dumps/kegg_ids.txt', 'w') as fh:
        for db_id in remaining_ids:
            fh.write(f'{db_id}\n')
        for db_id in kegg_ids:
            fh.write(f'{db_id}\n')


if __name__ == "__main__":
    from edb_builder.utils.ding import dingdingding
    asyncio.run(main())
    #dingdingding()
