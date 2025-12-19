import argparse

def get_argparser():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "in_file",
        help=""
    )
    parser.add_argument(
        "out_file",
        help=""
    )
    parser.add_argument(
        "--backend",
        default="parquet",
        help=""
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output"
    )
    parser.add_argument(
        "--database",
        default="./data/database_config.toml",
        help=""
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=5000,
        help="Batch size (size of commit when using postgres)"
    )

    parser.add_argument(
        "--cardinality",
        action="store_true",
        default=False,
        help="Instead of insertion, does a dry run and collects cardinality statistics"
    )

    return parser
