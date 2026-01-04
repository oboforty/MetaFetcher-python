import os

from db_dump.utils import toml_load, get_argparser
from db_dump.parse_db_dump import parse_dump_db, stats_dump_db
from .LipidmapsParser import LipidMapsParser


def main():
    # input
    cli_parser = get_argparser()
    args = cli_parser.parse_args()

    cfg = toml_load(os.path.join(os.path.dirname(__file__), "parse_lipmaps.toml"))
    dump_parser = LipidMapsParser(cfg)

    if not args.cardinality:
        # db_cfg = toml_load(args.database)
        parse_dump_db(
            dump_parser=dump_parser,
            in_file=args.in_file,
            out_file=args.out,
            batch=args.batch,
        )
    else:
        stats_dump_db(
            dump_parser=dump_parser,
            in_file=args.in_file,
        )


if __name__ == "__main__":
    main()
