import unittest
from unittest import mock
import os
import sys
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from ga_routing import GeneticAlgorithm

class TestGeneticAlgorithm(unittest.TestCase):

    def test_initialize_population(self):
        ga = GeneticAlgorithm(['a', 'b', 'c', 'd', 'e'], num_generations=10)
        ga.initialize_population()
        assert(ga.pop_size == 19)
        assert(ga.elite_size == 4)
        assert(len(ga.population) == 19)
        assert(len(ga.population[-1]) == 6)
        assert(ga.population[0][0] == ga.population[-1][-1] == 0)

    @mock.patch('ga_routing.Fitness.compute_route_fitness', side_effect=[(45, 0.1), (100, 0.01), (60, 0.08), (75, 0.06)])
    def test_select_parents(self, mock_fitness):
        ga = GeneticAlgorithm(['a', 'b', 'c', 'd'], 4, 2, 10)
        pop = []
        pop.append([0, 1, 3, 2, 0])
        pop.append([0, 3, 1, 2, 0])
        pop.append([0, 2, 1, 3, 0])
        pop.append([0, 3, 2, 1, 0])
        ga.population = pop
        ga.select_parents('secret', 'distance')
        rank_df = pd.DataFrame({
            'route_id': [0, 2, 3, 1],
            'distance': [45, 60, 75, 100],
            'fitness': [0.1, 0.08, 0.06, 0.01],
            'fitness_wt': [0.4, 0.32, 0.24, 0.04]
        })
        assert_frame_equal(ga.ranking, rank_df, check_dtype=False)
        assert(len(ga.parents) == 4)

    @mock.patch('random.randint', side_effect=[3, 6, 0, 3])
    def test_crossover(self, mock_rand):
        father = [0, 4, 6, 5, 3, 2, 1, 7, 0]
        mother = [0, 3, 7, 5, 1, 6, 4, 2, 0]
        ga = GeneticAlgorithm([], 4, 2, 10)
        actual = ga._crossover(father, mother)
        expected = [0, 7, 5, 6, 3, 2, 1, 4, 0]
        assert(actual == expected)
        actual = ga._crossover(father, mother)
        expected = [0, 4, 6, 5, 3, 7, 1, 2, 0]
        assert(actual == expected)
    

    @mock.patch('random.random', side_effect=[0.33, 0.25, 0.31, 0.19, 0.28])
    @mock.patch('random.randint', side_effect=[2, 0, 4, 1])
    def test_mutate(self, mock_random, mock_randint):
        route = [0, 4, 3, 1, 2, 5, 0]
        ga = GeneticAlgorithm([], 4, 2, 10)
        actual = ga._mutate(route, 0.26)
        expected = [0, 2, 1, 3, 4, 5, 0]
        assert(actual == expected)


