import unittest
import random

from db_dump.metparselib import cluster1d_eps
from db_dump.metparselib import AlmostEqualSet


class MassClusteringTests(unittest.TestCase):
    def setUp(self):
        # meth masses:
        mass = [149.23284 , 149.23, 149.2328]
        mi_mass = [149.12045 , 149.120449483 , 149.12044948]

        self.points = mass + mi_mass

    def test_clustering(self):
        # arrange
        random.shuffle(self.points)

        clusters = cluster1d_eps(self.points, eps=0.005)
        print(clusters)

        self.assertEqual(2, len(clusters))

    def test_almostEqualSet(self):
        # arrange
        random.shuffle(self.points)

        # act
        aes = AlmostEqualSet(self.points)

        # assert
        expected_repr_set = {149.23284, 149.120449483}
        self.assertEqual(expected_repr_set, aes.equivalence_set)
