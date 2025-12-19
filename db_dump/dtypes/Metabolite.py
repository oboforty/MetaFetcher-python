

class Metabolite:

    def __init__(self, meta_id):
        self.meta_id = meta_id

    @property
    def __DATAID__(self):
        return self.meta_id

    @classmethod
    def to_serialize(cls):
        return []
