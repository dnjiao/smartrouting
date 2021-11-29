from smart_routing import SmartRouting

api_key = input('Enter a valid Google Maps API key: ')
print('\nNow enter a list of addresses (Enter only to exit)')
addresses = []
while True:
    addr = input('Enter an address: ')
    if not addr:
        break
    addresses.append(addr)
print(addresses)

sr = SmartRouting(addresses, api_key)
sr.find_optimal_route()