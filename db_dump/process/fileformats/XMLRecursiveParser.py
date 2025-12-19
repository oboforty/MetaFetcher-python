import xml.etree.ElementTree as ET

from metcore.parsinglib import MultiDict

from .parsing.xml import parse_xml_recursive


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
