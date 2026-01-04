import csv
import json
import logging
import os.path
from argparse import ArgumentParser

from discovery import discover, output


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
        type=str,
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

    options = runs[0].options
    if args.out:
        _, ext = os.path.splitext(args.out)

        # TODO: CLI option: out file type? csv, tsv, jsonl, parquet, duckdb, etc?
        match ext:
            case ".csv":
                writer = output.CSVWriter(args.out, fieldnames=options.result_attributes)
            case ".tsv":
                writer = output.CSVWriter(args.out, fieldnames=options.result_attributes, delimiter="\t", quoting=csv.QUOTE_NONE, lineterminator="\n")
            case _, ".json", ".jsonl", ".jsonlines":
                writer = output.JSONLinesWriter(args.out)
    else:
        writer = output.STDWriter()

    with writer as oh:
        for run in runs:
            run.run_discovery()

            oh.write(run.meta)
