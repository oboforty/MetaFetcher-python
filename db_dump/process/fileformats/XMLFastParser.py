from lxml.etree import Element

from metcore.parsinglib import MultiDict
from lxml import etree


class XMLFastParser:
    """
    Parses XML files using lxml library
    """
    consumes = str, "filename"
    produces = MultiDict, "xml_tag_object"

    async def produce(self, xfn: str):
        #_, ext = os.path.splitext(fn)
        stop_at = self.cfg.get('debug.stop_after', -1, cast=int)
        xmlns = self.cfg.get('xml.xmlns')
        filter_tag = self.cfg.get('xml.root_tag')
        explore_children = set(self.cfg.get('xml.parse_hierachy_tags'))

        if xmlns:
            filter_tag = f'{{{xmlns}}}{filter_tag}'

        # parse XML file:
        nparsed = 0
        fh = open(xfn, 'rb')
        context = etree.iterparse(fh, events=('end',), tag=filter_tag)

        for event, elem in context:
            data = MultiDict()

            # parse lxml's hierarchy into a dictionary
            for tag in elem:
                tag_name = tag.tag.removeprefix('{' + xmlns + '}')

                if len(tag) == 0:
                    data.append(tag_name, tag.text)
                else:
                    if tag_name in explore_children:
                        for child in tag:
                            #assert len(child) == 0
                            data.append(tag_name, child.text)

            yield data

            elem.clear(keep_tail=True)

            nparsed += 1
            if nparsed > stop_at:
                if stop_at != -1 and nparsed > stop_at and self.app.debug:
                    print(f"{self.__PROCESSID__}: stopping early")
                    break

        # clean up
        del context
        fh.close()
