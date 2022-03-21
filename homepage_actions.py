import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.graph_objects as go
import pandas as pd
from geopy.geocoders import Nominatim

import osmnx as ox
import networkx as nx
import numpy as np
import random
import array
import matplotlib.pyplot as plt
import json
import numpy as np
import requests
import urllib.parse
from geopy.geocoders import Nominatim
from IPython import get_ipython
import subprocess


from navbar import Navbar
from server import app

mapbox_access_token = "pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g"
geolocator = Nominatim(user_agent="Charging Station App")
location = geolocator.geocode("India")
Oid = []

@app.callback(
        Output("homepage_collapse", "is_open"),
        [Input("homepage_collapse_toggle", "n_clicks")],
        [State("homepage_collapse", "is_open")],
    )
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    [Output("autocomplete_list_ecorouting","children"),
     Output("locationE","value")],
    [Input("locationE", "value"),
     Input({'type': 'autocomplete_list_ecorouting_item', 'index': ALL}, 'n_clicks')]
)
def update_location_text(place, chosen_item):
    ctx=dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == "locationE":
        if(place is None or place.strip() == ""):
            return [], dash.no_update
        
        autocomplete_list=[]

        parsed_loc = urllib.parse.quote(place)
        response = requests.get("http://api.mapbox.com/geocoding/v5/mapbox.places/"+parsed_loc+".json?country=IN&access_token=pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g")
        res=response.json()
        chosen_location=""
        cnt = 0
        for feat in res["features"]:
            autocomplete_list.append(dbc.ListGroupItem(feat["place_name"],id={'type': 'autocomplete_list_ecorouting_item','index': feat["place_name"]},action=True))
            cnt = cnt + 1
            if chosen_location == "":
                chosen_location=feat["place_name"]
        return autocomplete_list, dash.no_update
    else:
        loc=eval(ctx.triggered[0]['prop_id'].split('.')[0])['index']
        return [], loc




#Function to form default intial map
def default_location():
    parsed_loc = urllib.parse.quote("India")
    response = requests.get("http://api.mapbox.com/geocoding/v5/mapbox.places/"+parsed_loc+".json?country=IN&access_token=pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g")
    res=response.json()
    latitude=res["features"][0]["geometry"]["coordinates"][1]
    longitude=res["features"][0]["geometry"]["coordinates"][0]
    location = geolocator.geocode("India")
    center=[]
    center.append(latitude)
    center.append(longitude)
    zoomLevel = get_eco_zoom_level(500000)
    fig = go.Figure(go.Scattermapbox(
    lat=[location.latitude],
    lon=[location.longitude]
    ))
    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=location.latitude,
                lon=location.longitude
            ),
            pitch=0,
            zoom=5,
        )
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig, center, zoomLevel


# Callback dealing with intial inputs(area and radius) and output(all nodes and polygon around the search space)
@app.callback(
    [
     Output('mapE','figure'),
     Output(component_id='mapE', component_property='center'),
     Output(component_id='mapE', component_property='zoom'),
    ],
    inputs = [Input('all_nodes_buttonE', 'n_clicks')],
    state = [
           State(component_id='locationE', component_property='value'),
           State(component_id='radiusE', component_property='value'),
           ]
)
def update_mapE(n_clicks, location, radius):

    print(location, radius)
    if n_clicks is None:
        fig, center, zoomLevel = default_location()    
        return fig,center,zoomLevel
        # return fig

    
    fig, center, zoomLevel = find_all_nodesE(location, radius)
    
    return fig, center, zoomLevel
    # return fig


def get_eco_zoom_level(radius):
    level=17
    p=1
    while(p*100<radius):
        p=p*2
        level=level-1
    return level


def find_all_nodesE(search_location, radius):
    
    parsed_loc = urllib.parse.quote(search_location)
    response = requests.get("http://api.mapbox.com/geocoding/v5/mapbox.places/"+parsed_loc+".json?country=IN&access_token=pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g")
    res=response.json()
    lat_center=res["features"][0]["geometry"]["coordinates"][1]
    long_center=res["features"][0]["geometry"]["coordinates"][0]
    center = [lat_center,long_center]
    zoomLevel = get_eco_zoom_level(radius)
    num_of_tot_nodes, G1, A, Xnode, Ynode = get_all_nodes(lat_center,long_center,radius)
    # Preparing the map to display all the nodes got from Osmnx
    fig = go.Figure(go.Scattermapbox(
        name='General nodes',
        mode='markers',
        lat = Ynode,
        lon = Xnode,
        marker=go.scattermapbox.Marker(
            size=10
        ),
        text=[search_location],
    ))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=lat_center,
                lon=long_center,
            ),
            pitch=0,
            zoom=15
        )
    )
    fig.update_layout(mapbox_style="open-street-map")
    
   
    return fig, center, zoomLevel

def getTolerance(radius):
    tolerance_value=0.0001 + math.log2(radius)/15000
    return tolerance_value

# Function to get all the nodes from osmnx and writting those nodes to input file
def get_all_nodes(latitude,longitude,radius):

    location_point=(latitude,longitude)
    G1 = ox.graph_from_point(location_point, dist=radius, simplify=True, network_type='drive', clean_periphery=False)
    ox.save_graphml(G1, filepath='network1.graphml')
    nodes1, edges1 = ox.graph_to_gdfs(G1, nodes=True, edges=True)
    
    print(f"location used: {location_point}")
    print("node data:")
    print(nodes1)
    print(edges1)

    global Oid
    Oid=pd.Series.tolist(nodes1.index)
    print("Oid list: ")
    print(Oid)
    
    
    Ynode=pd.Series.tolist(nodes1.y)
    Xnode=pd.Series.tolist(nodes1.x)
    A = nx.adjacency_matrix(G1,weight='length')
   
    B1=A.tocoo()
    print(B1)

    return len(G1.nodes), G1, A, Xnode, Ynode