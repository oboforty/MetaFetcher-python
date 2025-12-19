

class CSVSerializable:
    edb_id: str

    @classmethod
    def to_serialize(cls):
        """
        Lists attributes for CSV serialization, in order
        :return:
        """
        return []

    @classmethod
    def to_json(cls):
        """
        Lists attributes that needs to be serialized before CSV serializing
        :return:
        """
        return []

    @property
    def as_dict(self):
        return {}
