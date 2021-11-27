import googlemaps
from datetime import datetime

class SmartRouting:
    def __init__(self, addresses, api_key):
        self.addresses = addresses
        self.api_key = api_key
        self.dist_mat = None

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




  
