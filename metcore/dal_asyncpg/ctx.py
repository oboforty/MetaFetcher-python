import json
import os.path
import asyncpg

from .. import srv
from ..utils import toml_load

Repository, get_repo = srv.declare_service_type('Repo', 'T')

dbcfg = toml_load(os.path.dirname(__file__)+"/../../db.toml")

single_connection = True
pool: asyncpg.Pool | None = None


async def setup_conn(conn):
    def _encoder(value):
        return b'\x01' + json.dumps(value).encode('utf-8')
    def _decoder(value):
        return json.loads(value[1:].decode('utf-8'))
    await conn.set_type_codec('jsonb', encoder=_encoder, decoder=_decoder, schema='pg_catalog', format='binary')
    await conn.set_type_codec('json', encoder=json.dumps, decoder=json.loads, schema='pg_catalog', format='text')

    for repo in srv.iter_services('Repo'):
        if single_connection:
            repo.conn = conn
            # single connection
        #connections.append(conn)


async def initialize_db(pool_size=None):
    global pool, single_connection
    if pool:
        # already initialized
        return

    dbopts = dbcfg['driver_asyncpg']
    conncfg = dbcfg[f'conn_{dbcfg["db"]["conn"]}']

    if 'dsn' not in conncfg:
        conncfg['dsn'] = f'{dbcfg.get("db.conn")}://{conncfg.pop("username")}:{conncfg.pop("password")}@{conncfg.pop("host")}/{conncfg.pop("database")}'

    min_size, max_size = pool_size or dbopts.get('pool_size') or (10, 10)
    single_connection = dbopts.get('single_connection', True)

    pool = asyncpg.create_pool(
        **conncfg,
        min_size=min_size,
        max_size=max_size,
        max_queries=dbopts.get('max_queries', 50000),
        max_inactive_connection_lifetime=dbopts.get('max_inactive_connection_lifetime', 300.0),

        # conn kwargs
        max_cached_statement_lifetime=dbopts.get('max_cached_statement_lifetime', 0),
        statement_cache_size=dbopts.get('statement_cache_size', 100),
        init=setup_conn,

        server_settings={
            'jit': 'off'
        }
    )

    if not single_connection:
        for repo in srv.iter_services('Repo'):
            repo.pool = pool

# async def create_connection(dbtype=None):
#     if dbtype is None:
#         dbtype = config.get('db.dbhandler')
#     dbcfg = config[dbtype]
#
#     conn = await asyncpg.connect(dbcfg.pop('dsn'), max_cached_statement_lifetime=0)
#
#     connections.append(conn)


async def close_db():
    if single_connection:
        await pool.close()
    else:
        pass
        # for conn in connections:
        #     await conn.close()
        #
        # connections.clear()


async def get_conn():
    #return connections[0]
    pass
    # async with pool.acquire() as connection:
