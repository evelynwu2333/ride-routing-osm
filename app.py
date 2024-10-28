import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import osmnx as ox
from pyproj import Proj
from shapely.geometry import LineString
import geopandas as gpd
import json

st.set_page_config(page_title="Recommend me Bike Routes!", page_icon=":bicyclist:", layout="wide")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Initialize session state
if "start_coords" not in st.session_state:
    st.session_state.start_coords = None

if "end_coords" not in st.session_state:
    st.session_state.end_coords = None

if "user_input" not in st.session_state:
    st.session_state.user_input = []

if "gdf_routes" not in st.session_state:
    st.session_state.gdf_routes = None

if "polylines" not in st.session_state:
    st.session_state.polylines = None

if "markers" not in st.session_state:
    st.session_state.markers = []

if "m2" not in st.session_state:
    st.session_state.m2 = None

if "submit" not in st.session_state:
    st.session_state.submit = False

if "color_mapping" not in st.session_state:
    st.session_state.color_mapping = {
        "Route 1": '#FF5733',  # Red
        "Route 2": '#33FF57',  # Green
        "Route 3": '#3357FF'   # Blue
    }   

# Title and Instructions
st.title("Bike route web app")
st.write("Input origin and destination for bike-friendly routes:")

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
    routes = ox.k_shortest_paths(G, orig_node, dest_node, k=50, weight="length")
    route_list = list(routes)
    geometries = []
    # gdf_combined = pd.DataFrame()
    for route in route_list:
        if len(geometries) == 3:
            break
        elif unique_different_route(route, route_list, 0.93):
            route_gdf = ox.routing.route_to_gdf(G, route)
            route_gdf = route_gdf[route_gdf.geometry.notnull()]
            # coords = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in route]
            # print(coords)
            line = reproject_route(route_gdf)
            # line = reproject_route(route_gdf)
            # combine two GeoDataFrames
            # gdf_combined = pd.concat([gdf_combined, route_gdf])
            geometries.append(line)
            # route_coords.append(coords)
    # coords = [(point.xy[1][0], point.xy[0][0]) for point in gdf_combined.geometry]
    # gdf_combined = gpd.GeoDataFrame(coords, geometry="geometry")
    # gdf_combined = gdf_combined.to_crs("EPSG:4326")
    st.write(geometries)
    # Convert the WKT strings to shapely LineString objects
    # shapely_geometry = [wkt.loads(line) for line in geometries] 
    d = {
        'route_name': [f"Route {i+1}" for i in range(len(geometries))],
        'geometry': geometries
    }
    gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")
    print(gdf)
    return gdf

# Function to reproject and return coordinates for folium
def reproject_route(route_gdf, target_crs="EPSG:4326"):
    # Reproject the GeoDataFrame to the desired CRS (WGS84 for Folium)
    reprojected_gdf = route_gdf.to_crs(target_crs)
    # coords = reprojected_gdf
    # Extract coordinates from reprojected geometry (lat, lon)
    coords = [(point.xy[1][0], point.xy[0][0]) for point in reprojected_gdf.geometry]
    return LineString(coords)

def unique_different_route(route, existing_routes, tolerance=0.93):
    set1 = set(route)
    for r in existing_routes:
        set2 = set(r)
        # Find the intersection of the two sets
        intersection = set1.intersection(set2)
        # Check if the overlap is greater than the tolerance level (e.g., 90% similarity)
        similarity = len(intersection) / min(len(set1), len(set2))
        # print(similarity)
        # if route == r or route == list(reversed(r)):
        #     return False
        if similarity >= tolerance:
            return False
        return True

def create_map2():
    m2 = folium.Map(center = [-35.28, 149.13], tiles="CartoDB positron")
    # Define colors for specific routes
    popup = folium.GeoJsonPopup(fields=["route_name"], labels=False)
        
    color_mapping = st.session_state.color_mapping
    route_style_function = lambda feature: {
        'color': color_mapping.get(feature['properties']['route_name']),   
        'opacity': 0.1, 
        'weight': 4
    }
    route_highlight_function = lambda feature: {
        'color': color_mapping.get(feature['properties']['route_name']),   
        'opacity': 0.1, 
        'weight': 8
    }
    if st.session_state.gdf_routes is not None:
        gdf_routes = st.session_state.gdf_routes
        geojson_routes = json.loads(gdf_routes.to_json())
        
        folium.GeoJson(
            data = geojson_routes, 
            control = True,
            style_function = route_style_function,
            highlight_function = route_highlight_function,
            tooltip = folium.features.GeoJsonTooltip(
                # using fields from the geojson file
                fields=['route_name'],
                aliases=['Route name: '],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
            ),
            popup = popup,
            popup_keep_highlighted = True,
            zoom_on_click = True
        ).add_to(m2)

        return m2


col1, col2 = st.columns(2)
with col1:
    with st.form(key='myform'):
        # create map
        m = folium.Map(center = [-35.28, 149.13], tiles="CartoDB positron")
        Draw(export=False, draw_options={
            'polyline': False,
            'polygon': False,
            'circle': False,
            'circlemarker': False,
            'rectangle': False,
            'marker': True
        }).add_to(m)
        # display map
        output = st_folium(m, width = 800, height = 600, zoom = 12)
        # st.write(output)
        submit = st.form_submit_button("Find Path")

# st.write(st.session_state.user_input)
if submit:
    # st.write(output)
    if len(output['all_drawings']) == 2:
        st.session_state.user_input = output['all_drawings']
        st.session_state.start_coords = st.session_state.user_input[0]['geometry']['coordinates']
        st.session_state.end_coords = st.session_state.user_input[1]['geometry']['coordinates']
        st.write(f"""
            Origin coordinates: {st.session_state.start_coords[1]}, {st.session_state.start_coords[0]}
            
            Destination coordinates: {st.session_state.end_coords[1]}, {st.session_state.end_coords[0]}
        """)

        G = get_bike_routes(place="ACT, Australia")
        Gp = ox.project_graph(G)
        gdf_routes = select_routes(st.session_state.start_coords, st.session_state.end_coords)
        st.session_state.gdf_routes = gdf_routes

        st.session_state.submit = True
    else:
        st.write('Please select origin and destination')   

with col2:            
    if st.session_state.submit:
        # st.write(st.session_state.m2)
        m2 = create_map2() 
        output2 = st_folium(m2, width = 800, height = 600, zoom = 12)
        st.write(output2)