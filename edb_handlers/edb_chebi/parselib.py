from typing import Any


def remap_chebi_links(attr: str, val) -> tuple[str, Any] | tuple[None, None]:
    if attr.endswith(" database links"):
        attr = attr.removesuffix(" database links")
        attr = attr.replace(" ", "_").replace("-", "_")
        attr += "_id"
        return attr, val
    if attr.endswith(" registry numbers"):
        attr = attr.removesuffix(" registry numbers")
        attr = attr.replace(" ", "_").replace("-", "_")
        attr += "_id"
        return attr, val

    return None, None
