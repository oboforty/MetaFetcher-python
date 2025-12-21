import os

from db_dump import cli
from db_dump.toml_load import toml_load
from db_dump.parse_db_dump import parse_dump_db, stats_dump_db
from .HMDBParser import HMDBParser


def main():
    # input
    cli_parser = cli.get_argparser()
    args = cli_parser.parse_args()

    cfg = toml_load(os.path.join(os.path.dirname(__file__), "parse_hmdb.toml"))
    dump_parser = HMDBParser(cfg)

    if not args.cardinality:
        db_cfg = toml_load(args.database)
        parse_dump_db(
            dump_parser=dump_parser,
            in_file=args.in_file,
            db_cfg=db_cfg,
            batch=args.batch,
        )
    else:
        stats_dump_db(
            dump_parser=dump_parser,
            in_file=args.in_file,
        )


if __name__ == "__main__":
    main()
