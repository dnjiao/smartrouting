from googlemaps import Client
from datetime import datetime
import random
import pandas as pd
import numpy as np
from math import factorial

class Location:
    def __init__(self, address):
        self.address = address
    
    def compute_distance(self, location, api_key, measure):
        gmaps = Client(api_key)
        gmap_dist = gmaps.distance_matrix(self.address, location.address, departure_time=datetime.now())
        distance = gmap_dist['rows'][0]['elements'][0]['distance']['value']
        duration = gmap_dist['rows'][0]['elements'][0]['duration_in_traffic']['value']
        if measure == 'distance':
            return distance
        return duration

class Fitness:
    def __init__(self, route):
        self.route = route
    
    def compute_route_fitness(self, key, measure):
        distance = 0
        for i in range(0, len(self.route)):
            from_loc = Location(self.route[i])
            to_loc = None
            if i + 1 < len(self.route):
                to_loc = Location(self.route[i + 1])
            else:
                to_loc = Location(self.route[0])
            distance += from_loc.compute_distance(to_loc, key, measure)
        fitness = 1 / distance
        return distance, fitness

class GeneticAlgorithm:
    def __init__(self, locations, pop_size=None, elite_size=None, num_generations=100):
        self.locations = locations
        self.pop_size = pop_size
        self.elite_size = elite_size
        self.num_generations = num_generations
        self.population = []
        self.ranking = None
        self.parents = []

    def initialize_population(self):
        if self.pop_size is None:
            self.pop_size = int(round(factorial(len(self.locations) - 1) * 0.8))
        if self.elite_size is None:
            self.elite_size = int(round(self.pop_size * 0.2))
        loc_ids = [*range(1, len(self.locations))]
        for i in range(self.pop_size):
            random.shuffle(loc_ids)
            self.population.append([0, *loc_ids, 0])
    
    def select_parents(self, api_key, measure):
        distances = []
        scores = []
        for i in range(self.pop_size):
            route = [self.locations[j] for j in self.population[i]]
            fit = Fitness(route)
            distance, fitness = fit.compute_route_fitness(api_key, measure)
            distances.append(distance)
            scores.append(fitness)
        print('Distance and fitness for each route is calculated')
        self.ranking = pd.DataFrame({
            'route_id': range(self.pop_size),
            'distance': distances,
            'fitness': scores
        }).sort_values(by='fitness', ascending=False).reset_index(drop=True)
        self.ranking['fitness_wt'] = self.ranking['fitness'] / self.ranking['fitness'].sum()
        ranked_pop = [self.population[i] for i in self.ranking['route_id'].values]
        weights = self.ranking['fitness_wt'].values
        print('Routes ranked by fitness')
        self.parents = ranked_pop[:self.elite_size]
        choices = np.random.choice(len(ranked_pop), self.pop_size-self.elite_size, p=weights).tolist()
        roulette_selection = [ranked_pop[i] for i in choices]
        self.parents.extend(roulette_selection)

    def _crossover(self, father, mother):
        father = father[1:-1]
        mother = mother[1:-1]
        rand1 = random.randint(0, len(father)-1)
        rand2 = random.randint(0, len(father)-1)
        start = min(rand1, rand2)
        stop = max(rand1, rand2)
        child = []
        child.append(0)
        cur_len = 0
        for l in mother:
            if cur_len == start:
                for i in range(start, stop):
                    child.append(father[i])
                    cur_len += 1      
            if l not in father[start: stop]:
                child.append(l)
                cur_len += 1    
        child.append(0)
        return child

    def breed_population(self):
        children = []
        for i in range(self.pop_size):
            father = self.parents[i]
            mother = self.parents[len(self.parents)-i-1]
            child = self._crossover(father, mother)
            children.append(child)
        self.population = children

    def _mutate(self, route, rate):
        route = route[1:-1]
        for i in range(len(route)):
            if(random.random() < rate):
                j = random.randint(0, len(route)-1)
                loc1 = route[i]
                loc2 = route[j]
                route[j] = loc1
                route[i] = loc2
        route = [0, *route, 0]
        return route

    def mutate_population(self, mut_rate=0.01):
        mutated_pop = []
        for i in range(len(self.population)):
            mutated = self._mutate(self.population[i], mut_rate)
            mutated_pop.append(mutated)
        self.population = mutated_pop

    def find_best_route(self, api_key, measure):
        self.initialize_population()
        print(f'Population intialized with {self.pop_size} routes')
        best_dist = []
        best_fitness = []
        best_route = []
        for i in range(self.num_generations):
            print(f'\nGeneration #{i}')
            self.select_parents(api_key, measure)
            best_dist.append(self.ranking.at[0, 'distance'])
            best_fitness.append(self.ranking.at[0, 'fitness'])
            best_route_id = self.ranking.at[0, 'route_id']
            best_route.append(self.population[best_route_id])
            
            print('Mating pool selected')
            self.breed_population()
            print('Breeding complete')
            self.mutate_population()
            print('Mutation complete')
            print(self.population[best_route_id], self.ranking.at[0, 'distance'])
            
        print(f'Best Route found with {measure} {best_dist[-1]}')
        print(best_route[-1])
        return best_dist
