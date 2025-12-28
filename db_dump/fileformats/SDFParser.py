import gzip
import io
import os.path
import zipfile
from typing import TextIO


from db_dump.parsinglib import MultiDict


def parse_sdf(filepath: str, parse_options: dict=None):
    _, ext = os.path.splitext(filepath)

    # stop_at = self.cfg.get('debug.stop_after', -1, cast=int)

    # gzip is CPU bound clib & wrapping it aiofiles/aiogzip slows it down
    if ext == '.gz':
        print(f"[SDF] parsing {filepath} as gzip")
        fh_stream: TextIO = gzip.open(filepath, 'rt', encoding='utf8')
    elif ext == '.zip':
        print(f"[SDF] parsing {filepath} as zip")
        archive = zipfile.ZipFile(filepath, 'r')
        fh_stream: TextIO = io.TextIOWrapper(archive.open(parse_options['compressed_file']), 'utf-8')
    else:
        print(f"[SDF] parsing raw {filepath}")
        fh_stream: TextIO = open(filepath, 'r', encoding='utf8')

    buffer = MultiDict()
    state = None
    nparsed = 0

    with fh_stream as fh:
        for line in fh:
            line = line.rstrip('\n')

            if line.startswith('$$$$'):
                # parsed New entry, clean buffer
                yield buffer
                nparsed += 1

                state = None
                buffer = MultiDict()

                # if stop_at != -1 and nparsed > stop_at and self.app.debug:
                #     print(f"{self.__PROCESSID__}: stopping early")
                #     break
                continue
            elif not line:
                continue
            elif line.startswith('> <'):
                state = line[3:-1]
            else:
                buffer.append(state, line)
