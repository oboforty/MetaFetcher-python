from operator import itemgetter
from typing import Iterator

from .cluster1d import get_float_precision, cluster1d_eps, get_common_min_precision


class MultiDict(dict):
    """
    A dict-like object that tries to keep added items scalar
    """

    def append(self, key, value):
        if (oldval := self.get(key)) is not None:
            # there are multiple entries in buffer, store them in a list
            if not isinstance(oldval, list):
                oldval = [oldval]
                self.__setitem__(key, oldval)

            oldval.append(value)
        else:
            self.__setitem__(key, value)

    def extend(self, key, value: list | set | Iterator):
        if isinstance(value, (list, tuple, set)):
            for val in value:
                self.append(key, val)
        else:
            self.append(key, value)

    def update(self, __m, **kwargs) -> None:
        for k,v in __m.items():
            self.extend(k, v)

class TrimSet(set):
    def __init__(self, seq=(), trimmer=None):
        super().__init__(seq)

        self.trimmer = trimmer

    def add(self, val):
        if val is not None:
            if self.trimmer:
                val = self.trimmer(val)
            super().add(val)

    def update(self, _set):
        if self.trimmer:
            _updated_set = set(self.trimmer(x) for x in _set if x is not None)
        else:
            _updated_set = set(x for x in _set if x is not None)

        if _updated_set:
            super().update(_updated_set)

    def __repr__(self):
        return repr_set(self)

class AlmostEqualSet(set):
    def __init__(self, seq=(), eps=None):
        super().__init__(seq)
        self.eps = eps

    @property
    def equivalence_set(self):
        """
        Gets representative float for each equivalence clusters (quantization buckets)
        Clusters are formed using a float-precision dependent difference (epsilon). 1D float clustering algorithm
        \n   ∀Ni,Nj ∈ cluster : Ni - Nj <= eps
        :return:
        """
        if len(self) == 0:
            return set()

        if self.eps is None:
            # eps diff scaling with the minimum flat precision of the set
            min_prec = get_common_min_precision(self)
            max_diff = pow(10, -min_prec + 1)

            clusters = cluster1d_eps(self, eps=max_diff)
        else:
            clusters = cluster1d_eps(self, eps=self.eps)

        return set(self.get_represent_for_cluster(c) for c in clusters)

    @classmethod
    def get_represent_for_cluster(cls, cluster):
        # get the float with the highest precision to represent the cluster:
        prec = [(f, get_float_precision(f)) for f in cluster]
        rf = max(prec, key=itemgetter(1))[0]
        return rf

    def update(self, _set):
        _updated_set = set(x for x in _set if x is not None)

        if _updated_set:
            super().update(_updated_set)

    def __repr__(self):
        return repr_set(self.equivalence_set)


def repr_set(s: set | TrimSet):
    if hasattr(s, 'trimmer') and s.trimmer:
        trimmer = lambda x: s.trimmer(str(x))
    else:
        trimmer = str
    return ' • '.join(map(trimmer, s))
