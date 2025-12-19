import os.path
import sys
import configparser


if sys.version_info > (3, 10):
    import tomllib

    def toml_load(fn):
        with open(os.path.abspath(fn), 'rb') as fh:
            return tomllib.load(fh)
else:
    import toml_load
    toml_load = toml
