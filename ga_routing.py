import googlemaps
from datetime import datetime
import random
import operator
import pandas as pd
import numpy as np

class Location:
    def __init__(self, address):
        self.address = address
    
    def compute_distance(self, location, api_key, measure):
        gmaps = googlemaps.Client(api_key)
        gmap_dist = gmaps.distance_matrix(self.address, location.address, departure_time=datetime.now())
        distance = gmap_dist['rows'][0]['elements'][0]['distance']['value']
        duration = gmap_dist['rows'][0]['elements'][0]['duration_in_traffic']['value']
        if measure == 'distance':
            return distance
        return duration

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
    
    def compute_route_fitness(self, key, measure):
        for i in range(0, len(self.route)):
            from_loc = self.route[i]
            to_loc = None
            if i + 1 < len(self.route):
                to_loc = self.route[i + 1]
            else:
                to_loc = self.route[0]
            self.distance += from_loc.compute_distance(to_loc, key, measure)
        self.fitness = 1 / float(self.distance)

class GeneticAlgorithm:
    def __init__(self, locations, pop_size, elite_size, num_generations):
        self.locations = locations
        self.pop_size = pop_size
        self.elite_size = elite_size
        self.num_generations = num_generations
        self.population = []
        self.ranking = None
        self.parents = []

    def initialize_population(self):
        loc_ids = range(1, len(self.locations))
        for i in range(0, self.pop_size):
            loc_ids = random.shuffle(loc_ids)
            loc_ids = [0, *loc_ids, 0]
            self.population.append(loc_ids)
    
    def select_parents(self):
        distances = []
        scores = []
        for i in range(len(self.population)):
            route = [self.locations[j] for j in self.population[i]]
            fit = Fitness(route)
            fit.compute_route_fitness()
            distances[i] = fit.distance
            scores[i] = fit.fitness
        self.ranking = pd.DataFrame({
            'route_id': range(len(self.population)),
            'distances': distances,
            'fitness': scores
        }).sort_values(by='fitness', ascending=False)
        self.ranking['fitness_wt'] = self.ranking['fitness'] / self.ranking['fitness'].sum()
        ranked_pop = [self.population[i] for i in self.ranking['route_id'].values]
        weights = self.ranking['fitness_wt'].values
        self.parents
        self.parents = np.random.choice(ranked_pop, self.pop_size-self.elite_size, p=weights)

    def _breed(self, father, mother):
        father = father[1:-1]
        mother = mother[1:-1]
        rand1 = random.randint(0, len(father))
        rand2 = random.randint(0, len(father))
        start = min(rand1, rand2)
        stop = max(rand1, rand2)
        child = []
        child.append(0)
        cur_len = 0
        for l in mother:
            if cur_len >= start and cur_len < stop:
                for i in range(start, stop):
                    child.append(father(i))
                    cur_len += 1
            else:
                if l not in father[start, stop]:
                    child.append(l)
                    cur_len += 1
        return child

    def breed_population(self):
        children = []
        for i in range(len(self.population)):
            child = self._breed(self.parents[i], self.parents[len(self.parents)-i-1])
            children.append(child)
        self.population = children

    def _mutate(self, route, rate):
        route = route[1:-1]
        for i in range(len(route)):
            if(random.random() < rate):
                j = random.randint(0, len(route))
                loc1 = route[i]
                loc2 = route[j]
                route[j] = loc1
                route[j] = loc2
        route = [0, *route, 0]
        return route

    def mutate_population(self, mut_rate=0.1):
        mutated_pop = []
        for i in range(len(self.population)):
            mutated = self._mutate(self.population[i], mut_rate)
            mutated_pop.append(mutated)
        return mutated

    def find_best_route(self, measure):
        self.initialize_population()
        best_dist = []
        best_fitness = []
        best_route = []
        for i in range(self.num_generations):
            self.select_parents()
            best_dist.append(self.ranking.at[0, 'distance'])
            best_fitness.append(self.ranking.at[0, 'fitness'])
            best_route.append(self.ranking.at[0, 'route_id'])
            self.breed_population()
            self.mutate_population()
            
        print(f'Best Route found with {measure} {best_dist[-1]}')
        print(best_route[-1])
