import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import osmnx as ox
from pyproj import Proj

# Initialize session state
if "start_coords" not in st.session_state:
    st.session_state.start_coords = None

if "end_coords" not in st.session_state:
    st.session_state.end_coords = None

# if "clicked_coords" not in st.session_state:
#     st.session_state.clicked_coords = []
if "user_input" not in st.session_state:
    st.session_state.user_input = []
# Title and Instructions
st.title("Bike route web app")
st.write("Input origin and destination for bike-friendly routes:")

# # add marker
# folium.Marker([0, 0], popup=None, icon=None, draggable=False).add_to(m)
# m.add_child(folium.LatLngPopup())

# Download the bike-specific street network from OSM
@st.cache_data
def get_bike_routes(place="ACT, Australia"):
    G = ox.graph_from_place(place, network_type='bike', simplify=True)
    # get a GeoSeries of consolidated intersections
    G_proj = ox.project_graph(G)
    G2 = ox.consolidate_intersections(G_proj)
    return G2

# get 3 shortest bike routes
def select_routes(origin_point, destination_point):

    # Set up your UTM projection for ACT (Zone 55S)
    proj_utm = Proj(proj='utm', zone=55, south=True, ellps='WGS84')
    x1, y1 = proj_utm(origin_point[0], origin_point[1])
    x2, y2 = proj_utm(destination_point[0], destination_point[1])

    orig_node = ox.nearest_nodes(Gp, x1, y1)
    dest_node = ox.nearest_nodes(Gp, x2, y2)
    # find the shortest path (by distance) between these nodes then plot it
    routes = ox.k_shortest_paths(G2, orig_node, dest_node, k=3, weight="length")
    route_list = list(routes)

    route_coords=[]
    for i, route in enumerate(route_list):
        route_gdf = ox.routing.route_to_gdf(G2, route)
        # route_length = route_gdf["length"].sum()
        # print(f"Length of route {i+1}: {route_length} meters")

        # Extract the coordinates of the route
        coords = [(point.xy[1][0], point.xy[0][0]) for point in route_gdf.geometry]  # (lat, lon) format
        
        route_coords.append(coords)

    return route_coords


with st.form(key='myform'):

    # create map
    m = folium.Map(center = [-35.28, 149.13])
    Draw(export=True, draw_options={
        'polyline': False,
        'polygon': False,
        'circle': False,
        'circlemarker': False,
        'rectangle': False,
        'marker': True
    }).add_to(m)
    # display map
    output = st_folium(m, width = 800, height = 600, zoom = 12, returned_objects=['all_drawings'])
    
    submit = st.form_submit_button("Find Path")

# st.write(st.session_state.user_input)
if submit:
    if len(output['all_drawings']) >= 2:
        st.session_state.user_input = output['all_drawings']
        st.session_state.start_coords = st.session_state.user_input[0]['geometry']['coordinates']
        st.write(st.session_state.start_coords)
        st.session_state.end_coords = st.session_state.user_input[1]['geometry']['coordinates']
        st.write(st.session_state.end_coords)

        G2 = get_bike_routes(place="ACT, Australia")
        Gp = ox.project_graph(G2)
        routes = select_routes(st.session_state.start_coords, st.session_state.end_coords)

        for i, route in enumerate(routes):
            folium.PolyLine(route, color=["red", "blue", "green"][i], weight=5, opacity=0.7, popup=f'Route {i+1}').add_to(m)
        
        # Add markers for the origin and destination
        folium.Marker(location=st.session_state.start_coords, popup='Origin').add_to(m)
        folium.Marker(location=st.session_state.end_coords, popup='Destination').add_to(m)
        st_folium(m)
    else:
        st.write('Please select origin and destination')   