import streamlit as st
import routing
import folium
from streamlit_folium import folium_static

# Initialize session state
if "start_coords" not in st.session_state:
    st.session_state.start_coords = None

if "end_coords" not in st.session_state:
    st.session_state.end_coords = None

if "clicked_coords" not in st.session_state:
    st.session_state.clicked_coords = []

# Title and Instructions
st.title("Bike route web app")
st.write("Input origin and destination for bike-friendly routes:")

# create map
m = folium.Map(center = [-35.28, 149.13], zoom_start = 12)

# click handler on map
def handle_click(event):
    lat = event.latlng[0]
    lon = event.latlng[1]
    st.session_state.clicked_coords.append((lat, lon))
    # update marker
    folium.Marker([lat, lon]).add_to(m)

# add marker
folium.Marker([0, 0], popup=None, icon=None, draggable=False).add_to(m)
m.add_child(folium.LatLngPopup())

# display map
folium_static(m, width = 800, height = 600)

if st.button("Select Origin"):
    if len(st.session_state.clicked_coords) > 0:
        start_coords = st.session_state.clicked_coords[-1]
        st.session_state.start_coords = start_coords
        st.write("Origin selected:", start_coords)

if st.button("Select Destination"):
    if len(st.session_state.clicked_coords) > 0:
        end_coords = st.session_state.clicked_coords[-1]
        st.session_state.end_coords = end_coords
        st.write("Destination selected:", end_coords)

if st.session_state.start_coords is not None:
    st.write("Origin coordinates:", st.session_state.start_coords)

if st.session_state.start_coords is not None and st.session_state.end_coords is not None:
    st.write(f"Origin coordinates: {st.session_state.start_coords} Destination coordinates: {st.session_state.end_coords}")

    routes = routing.get_bike_friendly_routes(start_coords, end_coords)
    routes[0].add_to(m)
    routes[1].add_to(m)
    routes[2].add_to(m)

# # show selected origin and destination points
# if len(clicked_points) == 2:
#     st.write(f"Selected Origin: {clicked_points[0]}")
#     st.write(f"Selected Destination: {clicked_points[1]}")

#     origin = clicked_points[0]
#     destination = clicked_points[1]

#     routes = routing.get_bike_friendly_routes(origin, destination)

#     m.Add.ppolyline(routes[0])
#     m.Add.ppolyline(routes[1])
#     m.Add.ppolyline(routes[2])

#     m.to_streamlit(height=700)