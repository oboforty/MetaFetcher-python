import inspect
from typing import Callable
from sqlalchemy.orm.attributes import InstrumentedAttribute

profiles_fn: dict[tuple[type, type], dict] = {}


class IgnoreAttributeMapping:
    pass


def register_mapping(ent1Class, ent2Class, mapping):
    profiles_fn[(ent1Class, ent2Class)] = mapping


def map_to(obj: object, cls_dest: type, cls_src: type= None):
    if cls_src is None:
        cls_src: type = type(obj)#.__class__

    mapping: dict[str, str | Callable] = profiles_fn.get((cls_src, cls_dest))# profiles_fn.get((cls_dest, cls_src)))

    if mapping is None:
        raise Exception(f"No mapping profile found for {cls_src}==>{cls_dest}")

    # todo: @later: use class.ForMember style chaining syntax to create mapping dict
    # todo: @later: inject args and kwargs of cls_targ when there's no default constructor? should be nice in python
    dest: object = cls_dest()

    # explore attributes to be mapped:
    attr_dest = dest.__dict__.keys()
    if hasattr(dest, '__annotations__'):
        attr_dest |= dest.__annotations__.keys()

    attr_src = set(obj.__dict__.keys())

    for attr in attr_dest:
        if attr in mapping:
            src_key = mapping[attr]
            # custom mapping rule by profile
            if src_key is IgnoreAttributeMapping:
                continue
            elif callable(src_key):
                sig = inspect.signature(src_key)
                if len(sig.parameters) == 1:
                    val = src_key(obj)
                else:
                    val = src_key(obj, dest)
            else:
                val = getattr(obj, src_key)

            setattr(dest, attr, val)
        elif attr in attr_src:
            # obvious 1-1 attribute mapping
            # todo: later: check type?
            # todo: @later: handle property cloning
            setattr(dest, attr, getattr(obj, attr))
        else:
            # no mapping found, raise
            raise Exception(f"No mapping found for attribute {cls_dest}.{attr}")

    # if mapping:
    #     # if '__complex__' in mapping:
    #     #     for fn in mapping['__complex__']:
    #     #         fn(obj, dest)

    return dest


class MappingRules:
    def __init__(self):
        self.mapping = {}

    def set_rules(self, rules):
        self.mapping.update(rules)

    def for_member(self, m1, m2):
        if isinstance(m1, InstrumentedAttribute):
            m1 = m1.key
        if isinstance(m2, InstrumentedAttribute):
            m2 = m2.key
        assert isinstance(m1, str)
        assert isinstance(m2, str) or callable(m2)

        self.mapping[m1] = m2

    def ignore(self):
        return IgnoreAttributeMapping


def Mapping(cls1: type, cls2: type):
    def _deco(wrapped):
        mappingRules = MappingRules()
        wrapped(mappingRules)

        register_mapping(cls1, cls2, mappingRules.mapping.copy())

        return wrapped
        # @functools.wraps(wrapped)
        # def _wrapper():
        #     pass
        # return _wrapper
    return _deco
