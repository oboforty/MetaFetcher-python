import re

from metcore.parsinglib import MultiDict


KEGG_END = '///'
KEGG_START = "ENTRY"
KEGG_LINE_PATTERN = re.compile(r'[a-zA-Z0-9_]*(\s*)([a-zA-Z0-9_]*)')
to_float = {'exact_mass', 'mol_weight', 'charge'}
FL = 12


def parse_kegg(stream):
    """
    https://www.kegg.jp/kegg/docs/dbentry.html

    :param content:
    :return:
    """
    data = MultiDict()
    state = None

    line: str
    for line in stream:
        if isinstance(line, bytes):
            line = line.decode('utf8')

        new_entry, state = parse_kegg_line(line, state, data)

        if new_entry:
            # kegg entry ended, save and yield
            yield data
            data = MultiDict()

async def parse_kegg_async(stream):
    data = MultiDict()
    state = None

    async for line in stream:
        new_entry, state = parse_kegg_line(line.decode('utf8'), state, data)

        if new_entry:
            # kegg entry ended, save and yield
            yield data
            data = MultiDict()


def parse_kegg_line(line, state, data: MultiDict):
    """

    :param line: line to be parsed
    :param state: reading attribute state
    :param data: data dict for caching
    :return: tuple - indication for a new entry and the new attribute state
    """
    if line == '' or line == '\n':
        return False, state
    elif line.startswith(KEGG_END):
        # start new entry
        return True, None
    # elif line.startswith(KEGG_START) and FL == 0:
    #     # first line - determine prefix length of KEGG's format
    #     groups = re.match(KEGG_LINE_PATTERN, line)
    #     FL = len(groups[1])+len(KEGG_START)

    values = line.split()

    if not line.startswith("   "):
        # interpret new attribute labels as regular lines, but save the label state for the next lines
        state = values[0].lower()
        values = values[1:]

    if 'dblinks' == state or 'DBLINKS' == state:
        # foreign reference - split by spaces
        db_source = values[0].rstrip(':').removesuffix('_id').lower()
        data.extend(db_source, values[1:])

    else:
        # any other attribute
        if state in to_float and line:
            values = list(map(float, values))
        elif 'name' == state:
            values = set(line[FL:].strip().split(';'))
            if '' in values:
                values.remove('')
        elif state == 'entry':
            values = values[0]

        data.extend(state.lower(), values)

    return False, state
