import osmnx as ox
import networkx as nx
from itertools import islice

# find 3 shortest paths
def k_shortest_paths(G, origin_node, destination_node, k=3, weight='length'):
    return list(islice(
        nx.shortest_simple_paths(
            G, origin_node, destination_node, weight=weight
        ), k
    ))

# get bike routes from openStreetMap
def get_bike_friendly_routes(origin_point, destination_point, place="Canberra, ACT, Australia", num_routes=3):
    # Download the bike-specific street network from OSM
    G = ox.graph_from_place(place, network_type='bike')

    # Find the nearest nodes to the origin and destination points
    orig_node = ox.distance.nearest_nodes(G, X=origin_point[1], Y=origin_point[0])
    dest_node = ox.distance.nearest_nodes(G, X=destination_point[1], Y=destination_point[0])

    # Calculate k-shortest paths (bike-friendly routes)
    routes = k_shortest_paths(G, orig_node, dest_node, k=num_routes, weight='length')

    # Convert routes into lists of coordinates (latitude, longitude)
    route_coords = []
    for route in routes:
        route_coordinates = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
        route_coords.append(route_coordinates)

    return route_coords


