import os

from pipebro import pipe_builder
from pipebro.ProcessImpl import DBSaver as LocalEDBSaver

from .HMDBParser import HMDBParser

from db_dump.dtypes import MetaboliteExternal, SecondaryID
from db_dump.process.fileformats.XMLFastParser import XMLFastParser
from edb_builder.utils import downloads, PIPECFG_PATH

DUMP_DIR = 'db_dumps/'
BULK_URL = 'https://hmdb.ca/system/downloads/current/hmdb_metabolites.zip'
BULK_FILE = os.path.join(DUMP_DIR, 'hmdb_metabolites.xml')


def build_pipe(conn):

    if not os.path.exists(BULK_FILE):
        bulk_zip = os.path.join(DUMP_DIR, os.path.basename(BULK_URL))

        if not os.path.exists(bulk_zip):
            # download file first
            print(f"Downloading HMDB dump file...")
            downloads.download_file(BULK_URL, bulk_zip)

        downloads.uncompress_hierarchy(bulk_zip)
        os.unlink(bulk_zip)

    with pipe_builder() as pb:
        pb.cfg_path = os.path.join(os.path.dirname(__file__), 'config')
        pb.set_runner('serial')

        pb.add_processes([
            XMLFastParser("xml_hmdb", consumes="hmdb_dump", produces="raw_hmdb"),

            HMDBParser("parse_hmdb", consumes="raw_hmdb", produces=("edb_dump", "2nd_id")),
        ], cfg_path=os.path.dirname(__file__))

        pb.add_processes([
            # - Meta Entity -
            # CSVSaver("edb_csv", consumes=(MetaboliteExternal, "edb_dump")),
            # Debug("debug_names", consumes=(MetaboliteExternal, "edb_dump")),
            LocalEDBSaver("db_dump", consumes=(MetaboliteExternal, "edb_dump"), table_name='edb_tmp', conn=conn),

            # - Secondary IDs -
            #CSVSaver("2nd_csv", consumes=(SecondaryID, "2nd_id")),
            LocalEDBSaver("2nd_dump", consumes=(SecondaryID, "2nd_id"), table_name='secondary_id', conn=conn),
        ], cfg_path=PIPECFG_PATH)

        app = pb.build_app()

    app.start_flow(BULK_FILE, (str, "hmdb_dump"))

    return app
