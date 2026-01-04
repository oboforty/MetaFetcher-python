import gzip
import os
import zipfile
from typing import IO

from lxml import etree

from db_dump.parsinglib import MultiDict


def parse_xml(filepath: str, parse_options: dict):
    """
    Parses XML files using lxml library
    """
    _, ext = os.path.splitext(filepath)

    if ext == '.gz':
        print(f"[XML] parsing {filepath} as gzip")
        fh_stream = gzip.open(filepath, 'rb')
    elif ext == '.zip':
        print(f"[XML] parsing {filepath} as zip")
        archive = zipfile.ZipFile(filepath, 'r')
        fh_stream: IO = archive.open(parse_options['compressed_file'])
    else:
        print(f"[XML] parsing raw {filepath}")
        fh_stream: IO = open(filepath, 'rb')

    xmlns_tag = parse_options.get('xmlns_tag')
    filter_tag = parse_options.get('root_tag')
    explore_children = set(parse_options.get('parse_hierachy_tags'))

    # parse XML file:
    context = etree.iterparse(fh_stream, events=('end',), tag=filter_tag)

    for event, elem in context:
        data = MultiDict()

        # parse lxml's hierarchy into a dictionary
        for tag in elem:
            tag_name = tag.tag.removeprefix(xmlns_tag)

            if len(tag) == 0:
                data.append(tag_name, tag.text)
            else:
                if tag_name in explore_children:
                    for child in tag:
                        #assert len(child) == 0
                        data.append(tag_name, child.text)

        yield data

        elem.clear(keep_tail=True)

    # clean up
    del context
    fh_stream.close()
