from metcore.parsinglib import MultiDict


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
