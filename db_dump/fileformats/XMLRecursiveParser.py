import xml.etree.ElementTree as ET

from db_dump.parsinglib import MultiDict


def parse_xml_recursive(context, cur_elem=None, tag_path=None, has_xmlns=True):
    items = MultiDict()

    if cur_elem and cur_elem.attrib:
        items.update(cur_elem.attrib)

    text = None
    if tag_path is None:
        tag_path = []

    for action, elem in context:
        # print("{0:>6} : {1:20} {2:20} '{3}'".format(action, elem.tag, elem.attrib, str(elem.text).strip()))

        if action == "start":
            tag = elem.tag.split('}', 1)[1] if has_xmlns else elem.tag
            tag_path.append(tag)
            state = '.'.join(tag_path)
            #state = _mapping.get(state.lower(), tag)

            items.append(state, parse_xml_recursive(context, elem, tag_path=tag_path, has_xmlns=has_xmlns))
        elif action == "end":
            text = elem.text.strip() if elem.text else None

            #tag = elem.tag.split('}', 1)[1]
            if tag_path:
                tag_path.pop()

            elem.clear()
            break

    if len(items) == 0:
        return text

    return items
    #{ k: v[0] if len(v) == 1 else v for k, v in items.items() }


class XMLParser:
    """
    Recursive XML parser
    """
    consumes = str, "filename"
    produces = MultiDict, "xml_tag_object"

    async def produce(self, fn: str):
        #_, ext = os.path.splitext(fn)
        stop_at = self.cfg.get('debug.stop_after', -1, cast=int)

        # parse XML file:
        context = ET.iterparse(fn, events=("start", "end"))
        context = iter(context)

        ev_1, xroot = next(context)
        nparsed = 0

        for ev_2, xmeta in context:
            # Úgy még sosem volt, hogy valahogy ne lett volna
            r: MultiDict = parse_xml_recursive(context)
            if r is not None:
                yield r

                nparsed += 1

                if nparsed > stop_at:
                    if stop_at != -1 and nparsed > stop_at and self.app.debug:
                        print(f"{self.__PROCESSID__}: stopping early")
                        break
