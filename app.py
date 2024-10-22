import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import osmnx as ox
from pyproj import Proj
from shapely.geometry import LineString
import geopandas as gpd

st.set_page_config(layout="wide")
# Initialize session state
if "start_coords" not in st.session_state:
    st.session_state.start_coords = None

if "end_coords" not in st.session_state:
    st.session_state.end_coords = None

if "user_input" not in st.session_state:
    st.session_state.user_input = []

if "polylines" not in st.session_state:
    st.session_state.polylines = None

if "markers" not in st.session_state:
    st.session_state.markers = []

if "m2" not in st.session_state:
    st.session_state.m2 = None

if "color_mapping" not in st.session_state:
    st.session_state.color_mapping = {
        "Route 1": '#FF5733',  # Red
        "Route 2": '#33FF57',  # Green
        "Route 3": '#3357FF'   # Blue
    }   

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
    # G_proj = ox.project_graph(G)
    # G2 = ox.consolidate_intersections(G_proj)
    return G

# get 3 shortest bike routes
def select_routes(origin_point, destination_point):

    # Set up your UTM projection for ACT (Zone 55S)
    proj_utm = Proj(proj='utm', zone=55, south=True, ellps='WGS84')
    x1, y1 = proj_utm(origin_point[0], origin_point[1])
    x2, y2 = proj_utm(destination_point[0], destination_point[1])

    orig_node = ox.nearest_nodes(Gp, x1, y1)
    dest_node = ox.nearest_nodes(Gp, x2, y2)
    # find the shortest path (by distance) between these nodes then plot it
    routes = ox.k_shortest_paths(G, orig_node, dest_node, k=5, weight="length")
    route_list = list(routes)
    # route_coords = []
    geometries = []
    for route in route_list:
        if len(geometries) == 3:
            break
        elif is_unique_route(route, route_list):
            route_gdf = ox.routing.route_to_gdf(G, route)
            route_gdf = route_gdf[route_gdf.geometry.notnull()]
            coords = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in route]
            line = LineString(coords)
            # line = reproject_route(route_gdf)
            geometries.append(line)
               
            # route_coords.append(coords)
    st.write(geometries)
    gdf = gpd.GeoDataFrame({
        'route_name': [f"Route {i+1}" for i in range(len(geometries))],
        'geometry': geometries
    }, crs="EPSG:4326")
    
    return gdf

# Function to reproject and return coordinates for folium
def reproject_route(route_gdf, target_crs="EPSG:4326"):
    # Reproject the GeoDataFrame to the desired CRS (WGS84 for Folium)
    reprojected_gdf = route_gdf.to_crs(target_crs)
    # coords = reprojected_gdf
    # Extract coordinates from reprojected geometry (lat, lon)
    coords = [(point.xy[1][0], point.xy[0][0]) for point in reprojected_gdf.geometry]
    return LineString(coords)

def is_unique_route(route, existing_routes):
    for r in existing_routes:
        if route == r or route == list(reversed(r)):
            return False
        return True


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
        st.write(st.session_state.start_coords)
        st.session_state.end_coords = st.session_state.user_input[1]['geometry']['coordinates']
        st.write(st.session_state.end_coords)

        G = get_bike_routes(place="ACT, Australia")
        Gp = ox.project_graph(G)
        gdf_routes = select_routes(st.session_state.start_coords, st.session_state.end_coords)
        # routes = [[(6099160.463292609, 685425.975529575), (6099129.893893488, 685353.4779063907), (6099009.457275188, 685265.3034023275), (6098766.570395689, 685218.4773676815), (6098720.291735907, 685232.412421319), (6098657.268234268, 685294.0241892751), (6098634.606778711, 685326.5354406331), (6098597.566227471, 685483.7727386802), (6098497.377233095, 685616.322066714), (6098477.3612192925, 685620.2170225739), (6098350.557317756, 685634.9269508591), (6098327.180693739, 685710.497589728), (6098246.49876664, 685958.6039247421), (6098091.543334673, 686314.2261968546), (6098045.8953872165, 686600.9405710574), (6098023.981825297, 686873.03493985), (6098006.941190542, 687028.0734791672), (6098001.171826271, 687093.0379591824), (6097983.901329768, 687240.2270285134), (6097868.005024812, 687495.170244976), (6097734.577424798, 687690.9147645261), (6097679.753535016, 687789.6525690925), (6097551.537391886, 688009.4111751273), (6097512.225288672, 688101.8379106408), (6097488.4262134, 688169.2559668054), (6097416.3130394835, 688387.0363781331), (6097371.555041395, 688522.189140847), (6097248.734671703, 688855.3093447149), (6097209.361648459, 688918.4807576506)], [(6099160.463292609, 685425.975529575), (6099129.893893488, 685353.4779063907), (6099009.457275188, 685265.3034023275), (6098766.570395689, 685218.4773676815), (6098720.291735907, 685232.412421319), (6098657.268234268, 685294.0241892751), (6098634.606778711, 685326.5354406331), (6098597.566227471, 685483.7727386802), (6098497.377233095, 685616.322066714), (6098477.3612192925, 685620.2170225739), (6098350.557317756, 685634.9269508591), (6098327.180693739, 685710.497589728), (6098246.49876664, 685958.6039247421), (6098091.543334673, 686314.2261968546), (6098045.8953872165, 686600.9405710574), (6098023.981825297, 686873.03493985), (6098001.171826271, 687093.0379591824), (6097983.901329768, 687240.2270285134), (6097868.005024812, 687495.170244976), (6097734.577424798, 687690.9147645261), (6097679.753535016, 687789.6525690925), (6097551.537391886, 688009.4111751273), (6097512.225288672, 688101.8379106408), (6097488.4262134, 688169.2559668054), (6097416.3130394835, 688387.0363781331), (6097371.555041395, 688522.189140847), (6097248.734671703, 688855.3093447149), (6097209.361648459, 688918.4807576506)], [(6099160.463292609, 685425.975529575), (6099129.893893488, 685353.4779063907), (6099009.457275188, 685265.3034023275), (6098766.570395689, 685218.4773676815), (6098720.291735907, 685232.412421319), (6098657.268234268, 685294.0241892751), (6098634.606778711, 685326.5354406331), (6098597.566227471, 685483.7727386802), (6098497.377233095, 685616.322066714), (6098477.3612192925, 685620.2170225739), (6098430.574874548, 685671.0084249626), (6098415.241525864, 685728.3267988975), (6098327.180693739, 685710.497589728), (6098246.49876664, 685958.6039247421), (6098091.543334673, 686314.2261968546), (6098045.8953872165, 686600.9405710574), (6098023.981825297, 686873.03493985), (6098006.941190542, 687028.0734791672), (6098001.171826271, 687093.0379591824), (6097983.901329768, 687240.2270285134), (6097868.005024812, 687495.170244976), (6097734.577424798, 687690.9147645261), (6097679.753535016, 687789.6525690925), (6097551.537391886, 688009.4111751273), (6097512.225288672, 688101.8379106408), (6097488.4262134, 688169.2559668054), (6097416.3130394835, 688387.0363781331), (6097371.555041395, 688522.189140847), (6097248.734671703, 688855.3093447149), (6097209.361648459, 688918.4807576506)]]
        # st.write(gdf_routes)
        # st.write(routes)
        with col2:
            with st.form(key='myform2'):
                m2 = folium.Map(center = [-35.28, 149.13], tiles="CartoDB positron")
                st.session_state.m2 = m2
                fg = folium.FeatureGroup(name="Markers")
                # Define colors for specific routes
                popup = folium.GeoJsonPopup(fields=["route_name"], labels=False)
                gdf_routes["style"] = [
                    {"fillColor": "#ff0000", "weight": 2, "color": "#ff0000"},
                    {"fillColor": "#00ff00", "weight": 2, "color": "#00ff00"},
                    {"fillColor": "#0000ff", "weight": 2, "color": "#0000ff"},
                ]

                # gdf_routes["highlight"] = [
                #     {"fillColor": "#ff0000", "weight": 8, "color": "#ff0000"},
                #     {"fillColor": "#00ff00", "weight": 8, "color": "#00ff00"},
                #     {"fillColor": "#0000ff", "weight": 8, "color": "#0000ff"},
                # ]
                    
                # Add hover functionality
                # style_function = 
                # highlight_function = 
                # JavaScript to make the polyline glow on hover and revert back
                polylines = folium.GeoJson(
                    data = gdf_routes, 
                    # style_function = lambda feature: {
                    #     'fillColor': color_mapping.get(feature['properties']['route_name']),   
                    #     # 'color':'#664CD9', 
                    #     'fillOpacity': 0.1, 
                    #     'weight': 4
                    # }, 
                    highlight_function = lambda feature: {
                        'weight': (8 if "e" in feature["properties"]["route_name"] else 2)
                    }, 
                    popup = popup,
                    popup_keep_highlighted = True
                )


                # polylines = []

                # for i, route in enumerate(routes):
                #     st.write(route)
                #     polyline = folium.PolyLine(route, color=["red", "blue", "green"][i], weight=[4, 6, 8][i], opacity=0.7, popup=f'Route {i+1}')

                    
                    
                #     polylines.append(polyline)
                
                
                
                st.session_state.polylines = polylines

                m2.add_child(st.session_state.polylines)
                # for pl in st.session_state.polylines:
                #     fg.add_child(pl)
                # Add markers for the origin and destination
                mk1 = folium.Marker(location=st.session_state.start_coords, popup='Origin')
                mk2 = folium.Marker(location=st.session_state.end_coords, popup='Destination')
                st.session_state["markers"].append(mk1)
                st.session_state["markers"].append(mk2)
                
                # fg.add_child(mk1)
                # fg.add_child(mk2)
                for marker in st.session_state["markers"]:
                    fg.add_child(marker)
                
                st_data = st_folium(m2, feature_group_to_add=fg, width = 800, height = 600, zoom = 12)
                st.form_submit_button("Refresh")
                
                # if refresh:
                #     st.session_state.polylines = polylines
                #     st.session_state.m2 = m2
                #     st.session_state["markers"].append(mk1)
                #     st.session_state["markers"].append(mk2)
    else:
        st.write('Please select origin and destination')   