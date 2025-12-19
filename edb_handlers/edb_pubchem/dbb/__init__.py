import os

from pipebro import pipe_builder
from pipebro.ProcessImpl import DBSaver as LocalEDBSaver

from edb_builder.utils import PIPECFG_PATH
from db_dump.dtypes import MetaboliteExternal
from db_dump.process.fileformats.SDFParser import SDFParser

from .PubchemParser import PubchemParser

DUMP_DIR = 'db_dumps/'
BULK_FILE = os.path.join(DUMP_DIR, 'PubChem_compound_cache_midb_records.sdf.gz')
#BULK_FILE = os.path.join(DUMP_DIR, 'PubChem_compound_cache_midb.csv.gz')


def build_pipe(conn):

    if not os.path.exists(BULK_FILE):
        # download file first
        raise Exception("Please manually download pubchem bulk file. See our website for recommended Search IDs")

    with pipe_builder() as pb:
        pb.cfg_path = os.path.join(os.path.dirname(__file__), 'config')
        pb.set_runner('serial')

        pb.add_processes([
            #CSVParser("csv_pubchem", consumes="pubchem_dump", produces="raw_pubchem"),
            SDFParser("sdf_pubchem", consumes="pubchem_dump", produces="raw_pubchem"),

            PubchemParser("parse_pubchem", consumes="raw_pubchem", produces="edb_dump"),
        ], cfg_path=os.path.dirname(__file__))

        pb.add_processes([
            #DebugProd("asdasd", consumes="pubchem_dump", produces="edb_dump"),

            # - Meta Entity -
            # CSVSaver("edb_csv", consumes=(MetaboliteExternal, "edb_dump")),
            # Debug("debug_names", consumes=(MetaboliteExternal, "edb_dump")),
            LocalEDBSaver("db_dump", consumes=(MetaboliteExternal, "edb_dump"), table_name='edb_tmp', conn=conn),
        ], cfg_path=PIPECFG_PATH)

        app = pb.build_app()

    app.start_flow(BULK_FILE, (str, "pubchem_dump"))
    return app
