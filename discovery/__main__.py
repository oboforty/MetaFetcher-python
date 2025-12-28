import logging
import sys
from argparse import ArgumentParser

from discovery.DiscoveryAlg import discover

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        'edb_tuples',
        nargs='*',
        type=str,
        help="",
    )
    parser.add_argument(
        "--file",
        default='./data/dumps/edb_dumps.db',
        type=str,
        help=""
    )
    parser.add_argument(
        "--options",
        default=None,
        type=str,
        help=""
    )
    parser.add_argument(
        "--out",
        default='./discovery.json',
        type=str,
        # default="./data/database_config.toml",
        help=""
    )
    parser.add_argument(
        "--log",
        default=None,
        type=str,
        help=""
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output"
    )
    parser.add_argument(
        "--split",
        action="store_true",
        default=False,
        help="Split each pair of EDB tuples into a separate query."
    )

    args = parser.parse_args()

    if args.options:
        from db_dump.utils import toml_load
        options = toml_load(args.options)
    else:
        # default options
        options = None

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    iter_ = iter(args.edb_tuples)

    if args.split:
        edb_tuples = [dict([kvp]) for kvp in zip(iter_, iter_)]
    else:
        edb_tuples = [dict(zip(iter_, iter_))]

    runs = discover(
        edb_tuples,
        db_file=args.file,
        options=args.options,
        log_file=args.log,
        log_level=log_level
    )
    for run in runs:
        run.run_discovery()
