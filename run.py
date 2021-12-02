from or_routing import ORRouting
from ga_routing import GeneticAlgorithm
from datetime import datetime
import sys

api_key = input('Enter a valid Google Maps API key: ')
addr_fl = input('\nNow enter the name of file that contains a list of addresses:')
with open(addr_fl) as f:
    addresses = [line.rstrip() for line in f.readlines()]
print(addresses)
attempts = 0
while True:
    if attempts == 3:
        sys.exit('Invalid choice. Exiting...')
    algo = input('\nSelect Algorithm\nLocal Search[1] or Genetic Algorithm[2]: ')
    if algo not in ['1', '2']:
        print('Please type 1 or 2.')
        attempts += 1
        continue
    else:
        break
attempts = 0
while True:
    if attempts == 3:
        sys.exit('Invalid choice. Exiting...')
    measure_choice = input('\nSelect Measure\nDriving distance[1] or Driving duration[2]: ')
    if measure_choice not in ['1', '2']:
        print('Please type 1 or 2.')
        attempts += 1
        continue
    else:
        break
measure = 'distance' if measure_choice == '1' else 'duration'
if algo == '1':      
    sr = ORRouting(addresses, api_key)
    sr.build_distance_matrix(measure)
    sr.find_optimal_route()
else:
    ga = GeneticAlgorithm(addresses, api_key, measure, pop_size=20, num_generations=5)
    print(f'GA starts at {datetime.now()}')
    distances = ga.find_best_route(api_key, measure)
    print(f'GA ends at {datetime.now()}')
    print(distances)
