import streamlit as st
import streamlit.components.v1 as components

_map_routes = components.declare_component(
    "map_routes",
    url="http://localhost:3001"
)

def map_routes(greeting, name="Streamlit", key=None):
    return _map_routes(greeting=greeting, name=name, key=key)


st.title("Component success!")

num_clicks = map_routes("Ahoy", "Streamlit")
st.write("Number of clicks:", num_clicks)