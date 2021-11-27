import requests
from geopy.geocoders import Nominatim

class OpenSmartRouting:
  def __init__(self, addresses):
    self.addresses = addresses
    self.dist_mat = None
  
  def _get_distance_and_duration(self, start_lon, start_lat, stop_lon, stop_lat):
    '''
    Helper function to calculate distance and duration between two locations
    '''
    url = f'http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{stop_lon},{stop_lat}'
    r = requests.get(url) 
    if r.status_code != 200:
      raise Exception(f'OSRM api returns {r.status_code}')
    res = r.json()  
    
    distance = res['routes'][0]['distance']
    duration = res['routes'][0]['duration']

    return distance, duration
  
  def _address_to_coordinates(self, address):
    '''
    Helper function to convert physical address to latitude and longitude
    '''
    geolocator = Nominatim()
    loc = geolocator.geocode(address)
    return loc.latitude, loc.longitude

  def compute_distance(self, idx1, idx2, measure):
    loc1 = self._address_to_coordinates(self.addresses[idx1])
    loc2 = self._address_to_coordinates(self.addresses[idx2])
    dist, dur = self._get_distance_and_duration(loc1[1], loc1[0], loc2[1], loc2[0])
    if measure == 'distance':
      print(dist)
      return dist
    print(dur)
    return dur
  
  def build_distance_matrix(self, measure):
    '''
    Method to calculate the distance matrix based on list of addresses

    Parameters:
      measure (str): 'distance' or 'duration'
    '''
    num_add = len(self.addresses)
    self.dist_mat = [[self.compute_distance(i, j, measure) for i in range(num_add)]
                     for j in range(num_add)]
    


  
