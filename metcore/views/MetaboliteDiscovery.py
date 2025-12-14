from dataclasses import dataclass, field

from mdb_builder.discovery.consistency import get_discovery_attribute_consistencies, \
    ConsistencyClass
from ..parsinglib import strip_attr, pad_id
from ..parsinglib.structs import repr_set, AlmostEqualSet, TrimSet, MultiDict
from .. import mapper


@dataclass
class MetaboliteDiscovery:
    names: set[str] = field(default_factory=TrimSet)

    chebi_id: set[str] = field(default_factory=lambda: TrimSet(trimmer=lambda x: strip_attr(x, 'CHEBI:')))
    kegg_id: set[str] = field(default_factory=TrimSet)
    lipmaps_id: set[str] = field(default_factory=lambda: TrimSet(trimmer=lambda x: strip_attr(x, 'LM')))
    pubchem_id: set[str] = field(default_factory=TrimSet)
    hmdb_id: set[str] = field(default_factory=lambda: TrimSet(trimmer=lambda x: strip_attr(x, 'HMDB')))
    cas_id: set[str] = field(default_factory=TrimSet)
    chemspider_id: set[str] = field(default_factory=TrimSet)
    metlin_id: set[str] = field(default_factory=TrimSet)

    # structures
    mol: set[str] = field(default_factory=TrimSet)
    formula: set[str] = field(default_factory=TrimSet)
    inchi: set[str] = field(default_factory=TrimSet)
    inchikey: set[str] = field(default_factory=TrimSet)
    smiles: set[str] = field(default_factory=TrimSet)

    # mass
    charge: set[float] = field(default_factory=TrimSet)
    mass: set[float] = field(default_factory=AlmostEqualSet)
    mi_mass: set[float] = field(default_factory=AlmostEqualSet)

    description: dict[str, str] = field(default_factory=dict)

    attr_other: dict[str, str] = field(default_factory=MultiDict)

    @property
    def primary_name(self):
        # @todo: policy to find primary_name ?
        return list(self.names)[0]

    def merge(self, other):
        if isinstance(other, MetaboliteDiscovery):
            for attr in self.__dict__:
                getattr(self, attr).update(getattr(other, attr))
        else:
            # try to map obj to MetaboliteDiscovery and then merge
            mapped_obj = mapper.map_to(other, cls_dest=MetaboliteDiscovery)
            return self.merge(mapped_obj)

    def to_dict(self):
        d = {}

        for k,v in self.__dict__.items():
            if isinstance(v, TrimSet):
                d[k] = list(set(pad_id(s, k) for s in v))
            elif isinstance(v, AlmostEqualSet):
                d[k] = list(v.equivalence_set)
            elif isinstance(v, dict):
                d[k] = v

        return d

    def __repr__(self):
        repr_dict = self.to_dict()
        sb = [self.__class__.__name__]
        repr_dict.update(repr_dict.pop('attr_other'))

        consistencies = get_discovery_attribute_consistencies(self)

        for attr, vals in repr_dict.items():
            c = consistencies.get(attr, ConsistencyClass.Consistent)

            sb.append(f'  {attr:<16}: {str(c)} {repr_set(vals)}')

        return '\n'.join(sb)
