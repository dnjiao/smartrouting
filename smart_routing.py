import googlemaps
from datetime import datetime
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

class SmartRouting:
    def __init__(self, addresses, api_key):
        self.addresses = addresses
        self.api_key = api_key

    def compute_distance(self, idx1, idx2, measure):
        '''
        Method to compute the distance or driving duration from one location to another

        Parameters:
            idx1 (int): index of source address
            idx2 (int): index of destination address
            measure (str): 'distance' or 'duration
        
        Returns: 
            distance or duration
        '''
        if idx1 == idx2:
            return 0
        adr1 = self.addresses[idx1]
        adr2 = self.addresses[idx2]
        gmaps = googlemaps.Client(key=self.api_key)
        gmap_dist = gmaps.distance_matrix(adr1, adr2, departure_time=datetime.now())
        distance = gmap_dist['rows'][0]['elements'][0]['distance']['value']
        duration = gmap_dist['rows'][0]['elements'][0]['duration_in_traffic']['value']
        if measure == 'distance':
            return distance
        return duration
    
    def build_distance_matrix(self, measure):
        '''
        Method to calculate the distance matrix based on list of addresses

        Parameters:
            measure (str): 'distance' or 'duration'
        '''
        num_add = len(self.addresses)
        self.dist_mat = [[self.compute_distance(i, j, measure) for i in range(num_add)]
                        for j in range(num_add)]
    
    def print_solution(self, manager, routing, solution):
        index = routing.Start(0)
        plan_output = 'Best Route: \n'
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += f'{self.addresses[manager.IndexToNode(index)]} [{manager.IndexToNode(index)}]-> \n'
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        plan_output += f'{self.addresses[manager.IndexToNode(index)]} [{manager.IndexToNode(index)}]\n'
        print(plan_output)
    
    def find_optimal_route(self):
        manager = pywrapcp.RoutingIndexManager(len(self.addresses), 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_idx, to_idx):
            from_node = self.manager.IndexToNode(from_idx)
            to_node = self.manager.IndexToNode(to_idx)
            return self.dist_mat[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            self.print_solution(manager, routing, solution)

        
 







  
