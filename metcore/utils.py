import sys
import configparser


if sys.version_info > (3, 10):
    import tomllib

    def toml_load(fn):
        with open(fn, 'rb') as fh:
            return tomllib.load(fh)
else:
    import utils
    toml_load = toml
