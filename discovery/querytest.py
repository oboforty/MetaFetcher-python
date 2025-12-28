from discovery.db.duckdb import MetaboliteRepository


db = MetaboliteRepository("./data/dumps/edb_dumps.db")

db.get_indexes("names", "morphine")

# TODO: bulk query gave:
#   ['55340', '17303', '176333', '233811', '50731', '1445', '233812', '135797', '58097', '7003', '5790', '7458', '194513', '27808', '2184', '174043', '135119', '4902', '7455', '4575', '55348', '9519', '53579', '31228', '7633', '16714', '48538', '59860', '2168', '4912']

db.close()
