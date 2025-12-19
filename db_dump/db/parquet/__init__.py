import pyarrow as pa
import pyarrow.parquet as pq


def get_edb_schema() -> pa.Schema:
    return pa.schema([
        pa.field("names", pa.list_(pa.string())),

        pa.field("attr_mul", pa.map_(
            pa.string(),
            pa.list_(pa.string())
        )),

        # normalize attr_other to map<string, list<string>>
        pa.field("attr_other", pa.map_(
            pa.string(),
            pa.list_(pa.string())
        )),

        pa.field("chebi_id", pa.string()),
        pa.field("kegg_id", pa.string()),
        pa.field("lipmaps_id", pa.string()),
        pa.field("pubchem_id", pa.string()),
        pa.field("hmdb_id", pa.string()),

        pa.field("cas_id", pa.string()),
        pa.field("chemspider_id", pa.string()),
        pa.field("metlin_id", pa.string()),
        pa.field("swisslipids_id", pa.string()),

        pa.field("formula", pa.string()),
        pa.field("inchi", pa.string()),
        pa.field("inchikey", pa.string()),
        pa.field("smiles", pa.string()),

        pa.field("charge", pa.float64()),
        pa.field("mass", pa.float64()),
        pa.field("mi_mass", pa.float64()),

        pa.field("description", pa.string()),
        pa.field("edb_source", pa.string()),
    ])
