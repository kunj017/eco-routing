# manages actions for homepage

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.graph_objects as go
import pandas as pd
from geopy.geocoders import Nominatim
import dash_leaflet as dl
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
from math import asin,cos,pi,sin, log2, atan2, sqrt
import subprocess
import config


from navbar import Navbar
from server import app


rEarth = 6371.01 # Earth's average radius in km
epsilon = 0.000001 # threshold for floating-point equality

mapbox_access_token = "pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g"
geolocator = Nominatim(user_agent="Charging Station App")
location = geolocator.geocode("India")
Oid = []

@app.callback(
        Output("hp_collapse", "is_open"),
        [Input("hp_collapse_toggle", "n_clicks")],
        [State("hp_collapse", "is_open")],
    )
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    [Output("hp_autocomplete_list","children"),
     Output("hp_location_input","value")],
    [Input("hp_location_input", "value"),
     Input({'type': 'hp_autocomplete_list_item', 'index': ALL}, 'n_clicks')]
)
def update_location_text(place, chosen_item):
    ctx=dash.callback_context
    if not ctx.triggered:
        if config.location is not None:
            return dash.no_update, config.location
        return dash.no_update, dash.no_update
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == "hp_location_input":
        if(place is None or place.strip() == ""):
            return [], dash.no_update
        
        autocomplete_list=[]

        parsed_loc = urllib.parse.quote(place)
        response = requests.get("http://api.mapbox.com/geocoding/v5/mapbox.places/"+parsed_loc+".json?country=IN&access_token=pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g")
        res=response.json()
        chosen_location=""
        cnt = 0
        for feat in res["features"]:
            autocomplete_list.append(dbc.ListGroupItem(feat["place_name"],id={'type': 'hp_autocomplete_list_item','index': feat["place_name"]},action=True))
            cnt = cnt + 1
            if chosen_location == "":
                chosen_location=feat["place_name"]
        return autocomplete_list, dash.no_update
    else:
        loc=eval(ctx.triggered[0]['prop_id'].split('.')[0])['index']
        config.location = loc
        return [], loc

def deg2rad(angle):
    return angle*pi/180


def rad2deg(angle):
    return angle*180/pi

# Function to form polygon with 24 sides around the search space
def pointRadialDistance(lat1, lon1, bearing, distance):
    """
    Return final coordinates (lat2,lon2) [in degrees] given initial coordinates
    (lat1,lon1) [in degrees] and a bearing [in degrees] and distance [in km]
    """
    rlat1 = deg2rad(lat1)
    rlon1 = deg2rad(lon1)
    rbearing = deg2rad(bearing)
    rdistance = distance / rEarth # normalize linear distance to radian angle

    rlat = asin( sin(rlat1) * cos(rdistance) + cos(rlat1) * sin(rdistance) * cos(rbearing) )

    if cos(rlat) == 0 or abs(cos(rlat)) < epsilon: # Endpoint a pole
        rlon=rlon1
    else:
        rlon = ( (rlon1 - asin( sin(rbearing)* sin(rdistance) / cos(rlat) ) + pi ) % (2*pi) ) - pi

    lat = rad2deg(rlat)
    lon = rad2deg(rlon)
    return (lat, lon)

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
     Output(component_id='num_all_nodes_div', component_property='children'),
     Output(component_id='dl_hp_all_nodes', component_property='children'),
     Output("dl_hp_circle", "children"),
     Output(component_id='hp_result_map', component_property='center'),
     Output(component_id='hp_result_map', component_property='zoom'),
    ],
    inputs = [Input('hp_all_nodes_button', 'n_clicks')],
    state = [
           State(component_id='hp_location_input', component_property='value'),
           State(component_id='hp_radius_input', component_property='value'),
           ]
)
def hp_update_map(n_clicks, location, radius):

    if n_clicks is None:
        if config.num_of_tot_nodes != 0:
            return 'Total Number of Nodes: {}'.format(config.num_of_tot_nodes),config.positions,\
                    config.polygon,config.center, config.zoomLevel

        if n_clicks is None:
            fig, center, zoomLevel = default_location()    
            return '' ,dash.no_update,dash.no_update,center, zoomLevel

    fig, num_of_tot_nodes, G1, A, Xnode, Ynode, center, zoomLevel, latitude, longitude = find_all_nodes(location, radius)

    testcases = []
    corners = []
    for x in range(0,361,1):
        testcases.append((latitude,longitude,x,(radius+350)/1000))
    
    for lat1, lon1, bear, dist in testcases:
        (lat,lon) = pointRadialDistance(lat1,lon1,bear,dist)
        corners.append([lat,lon])
    polygon = dl.Polygon(positions=corners)
    
    positions = []
    for i in range(len(Xnode)):
        temp = []
        temp.append(Ynode[i])
        temp.append(Xnode[i])
        positions.append(dl.Marker(position=temp,children=dl.Tooltip(i, direction='top', permanent=True),riseOnHover=True))
    
    # setting the global variables in config file
    config.num_of_tot_nodes, config.positions, config.polygon, config.center, config.zoomLevel = num_of_tot_nodes, positions, polygon,center, zoomLevel
    
    return 'Total Number of Nodes: {}'.format(num_of_tot_nodes),positions, polygon,center, zoomLevel



def get_eco_zoom_level(radius):
    level=17
    p=1
    while(p*100<radius):
        p=p*2
        level=level-1
    return level


# finds all nodes based on search location and radius
def find_all_nodes(search_location, radius):
    
    parsed_loc = urllib.parse.quote(search_location)
    response = requests.get("http://api.mapbox.com/geocoding/v5/mapbox.places/"+parsed_loc+".json?country=IN&access_token=pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g")
    res=response.json()
    lat_center=res["features"][0]["geometry"]["coordinates"][1]
    long_center=res["features"][0]["geometry"]["coordinates"][0]
    # print(search_location)
    center = [lat_center,long_center]
    zoomLevel = get_eco_zoom_level(radius)
    num_of_tot_nodes, G1, A, Xnode, Ynode = get_all_nodes(lat_center,long_center,radius)
    
    # Preparing the map to display all the nodes got from Osmnx
    all_nodes = go.Figure(go.Scattermapbox(
        name='General nodes',
        lat=Ynode,
        lon=Xnode,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10
        ),
    text=[search_location],
    ))

    all_nodes.update_layout(
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
    all_nodes.update_layout(mapbox_style="open-street-map")
    
    return all_nodes, num_of_tot_nodes, G1, A, Xnode, Ynode, center, zoomLevel, lat_center, long_center

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