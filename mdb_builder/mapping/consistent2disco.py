from metcore import mapper
from metcore.parsinglib import force_flatten
from metcore.views import MetaboliteConsistent, MetaboliteDiscovery


def trim_attr_mul(opt, dst):
    return {k: v for k, v in dst.attr_mul.items() if v}


def extra_ref(n, opt):
    return set(opt.attr_mul.get(n, []))


@mapper.Mapping(MetaboliteConsistent, MetaboliteDiscovery)
def consistent2disco(mapper):
    """
    Maps MetaboliteConsistent to Discovery object
    (added for library purposes)

    :param mapper:
    :return:
    """
    # TODO: store attr other in MetaboliteDiscovery?

    # TODO: store mol file

    mapper.for_member('names', lambda opt: opt.names)
    mapper.for_member('description', mapper.ignore())

    mapper.for_member('chebi_id', lambda opt: {opt.chebi_id} | extra_ref('chebi_id', opt))
    mapper.for_member('kegg_id', lambda opt: {opt.kegg_id} | extra_ref('kegg_id', opt))
    mapper.for_member('lipmaps_id', lambda opt: {opt.lipmaps_id} | extra_ref('lipmaps_id', opt))
    mapper.for_member('pubchem_id', lambda opt: {opt.pubchem_id} | extra_ref('pubchem_id', opt))
    mapper.for_member('hmdb_id', lambda opt: {opt.hmdb_id} | extra_ref('hmdb_id', opt))

    mapper.for_member('cas_id', lambda opt: {opt.cas_id} | extra_ref('cas_id', opt))
    mapper.for_member('chemspider_id', lambda opt: {opt.chemspider_id} | extra_ref('chemspider_id', opt))
    mapper.for_member('metlin_id', lambda opt: {opt.metlin_id} | extra_ref('metlin_id', opt))

    mapper.for_member('formula', lambda opt: {opt.formula} | extra_ref('formula', opt))
    mapper.for_member('inchi', lambda opt: {opt.inchi} | extra_ref('inchi', opt))
    mapper.for_member('inchikey', lambda opt: {opt.inchikey} | extra_ref('inchikey', opt))
    mapper.for_member('smiles', lambda opt: {opt.smiles} | extra_ref('smiles', opt))

    mapper.for_member('charge', lambda opt: {opt.charge} | extra_ref('charge', opt))
    mapper.for_member('mass', lambda opt: {opt.mass} | extra_ref('mass', opt))
    mapper.for_member('mi_mass', lambda opt: {opt.mi_mass} | extra_ref('mi_mass', opt))

    mapper.for_member('mol', mapper.ignore())
    mapper.for_member('swisslipids_id', mapper.ignore())

    mapper.for_member('attr_other', 'attr_other')


@mapper.Mapping(MetaboliteDiscovery, MetaboliteConsistent)
def disco2consistent(mapper):
    """
    Maps Discovery object to Consistent metabolite object
    (added for library purposes - e.g. used in serializing bulk discovery)

    :param mapper:
    :return:
    """

    # todo: handle mol files later
    # todo: handle other attributes later

    mapper.for_member('edb_source', mapper.ignore())
    mapper.for_member('edb_id', mapper.ignore())

    mapper.for_member('names', lambda opt: opt.names)
    mapper.for_member('description', mapper.ignore())

    mapper.for_member('chebi_id', lambda opt, dst: force_flatten(opt.chebi_id, dst.attr_mul.setdefault('chebi_id', [])))
    mapper.for_member('kegg_id', lambda opt, dst: force_flatten(opt.kegg_id, dst.attr_mul.setdefault('kegg_id', [])))
    mapper.for_member('lipmaps_id', lambda opt, dst: force_flatten(opt.lipmaps_id, dst.attr_mul.setdefault('lipmaps_id', [])))
    mapper.for_member('pubchem_id', lambda opt, dst: force_flatten(opt.pubchem_id, dst.attr_mul.setdefault('pubchem_id', [])))
    mapper.for_member('hmdb_id', lambda opt, dst: force_flatten(opt.hmdb_id, dst.attr_mul.setdefault('hmdb_id', [])))

    mapper.for_member('cas_id', lambda opt, dst: force_flatten(opt.cas_id, dst.attr_mul.setdefault('cas_id', [])))
    mapper.for_member('chemspider_id', lambda opt, dst: force_flatten(opt.chemspider_id, dst.attr_mul.setdefault('chemspider_id', [])))
    mapper.for_member('metlin_id', lambda opt, dst: force_flatten(opt.metlin_id, dst.attr_mul.setdefault('metlin_id', [])))

    mapper.for_member('smiles', lambda opt, dst: force_flatten(opt.smiles, dst.attr_mul.setdefault('smiles', [])))
    mapper.for_member('inchi', lambda opt, dst: force_flatten(opt.inchi, dst.attr_mul.setdefault('inchi', [])))
    mapper.for_member('inchikey', lambda opt, dst: force_flatten(opt.inchikey, dst.attr_mul.setdefault('inchikey', [])))
    mapper.for_member('formula', lambda opt, dst: force_flatten(opt.formula, dst.attr_mul.setdefault('formula', [])))
    mapper.for_member('charge', lambda opt, dst: force_flatten(opt.charge, dst.attr_mul.setdefault('charge', [])))
    mapper.for_member('mass', lambda opt, dst: force_flatten(opt.mass, dst.attr_mul.setdefault('mass', [])))
    mapper.for_member('mi_mass', lambda opt, dst: force_flatten(opt.mi_mass, dst.attr_mul.setdefault('mi_mass', [])))

    mapper.for_member('attr_mul', trim_attr_mul)
    mapper.for_member('attr_other', 'attr_other')

    mapper.for_member('swisslipids_id', mapper.ignore())
    mapper.for_member('mol', mapper.ignore())
