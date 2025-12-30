from collections import UserDict
from typing import Iterator


class MetaboliteIndex(UserDict):
    allowed_keys: set[str] = set()
    keys_kept_split: set[str] = set()

    # TODO: implement keys_kept_split -> keep these merged dicts separate

    def append(self, key, value):
        if key not in self.allowed_keys:
            return

        if (oldval := self.data.get(key)) is not None:
            # there are multiple entries in buffer, store them in a list
            if not isinstance(oldval, list):
                oldval = [oldval]
                self.data[key] = oldval

            oldval.append(value)
        else:
            self.data[key] = value

    def extend(self, key, value: list | set | Iterator):
        for x in iter_of_type(value):
            self.append(key, x)

    def update(self, dict2, **kwargs) -> None:
        for key, value in dict2.items():
            for x in iter_of_type(value):
                self.append(key, x)


def iter_of_type(arr_or_prim):
    """
    Yields either a scalar type or iterates a collection of the same type
    """
    if isinstance(arr_or_prim, (list, tuple, set)):
        for x in arr_or_prim:
            yield x
    else:
        yield arr_or_prim
