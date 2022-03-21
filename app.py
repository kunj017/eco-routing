import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
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

from IPython import get_ipython
import subprocess

from navbar import Navbar

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

mapbox_access_token = "pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g"
geolocator = Nominatim(user_agent="Charging Station App")
location = geolocator.geocode("India")

create_mat=1
roc = 50
alpha = 0.2
lamda = 0.1
#c (capacity)
capacity = 20
#epsilon (randomness coeff )
epsilon = 0

# get_ipython().system('g++ code.cpp -o code')

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

available_indicators = [
    dbc.DropdownMenuItem('All Nodes', id="all_nodes"),
    dbc.DropdownMenuItem('Charging Stations',id="charging_stations"),
   ]

location_input = dbc.FormGroup(
    [
        dbc.Label("Location", html_for="search_bar", width=2),
        dbc.Col(
            dbc.Input(
                type="text", id="search_bar", placeholder="Enter Location"
            ),
            width=10,
        ),
    ],
    row=True,
)

radius_input = dbc.FormGroup(
    [
        dbc.Label("Radius (in meters)", html_for="radius", width=2),
        dbc.Col(
            dbc.Input(
                type="number", id="radius", placeholder="Enter Radius"
            ),
            width=10,
        ),
    ],
    row=True,
)

all_nodes_form = dbc.Form([location_input,radius_input,dbc.Button("Find All Nodes",id="all_nodes_button",color="primary")])

candidate_node_input = dbc.FormGroup(
    [
        dbc.Label("Candidate Nodes", html_for="candidate_nodes", width=2),
        dbc.Col(
            dbc.Input(
                type="number", id="candidate_nodes", placeholder="Enter Number of Candidate Nodes"
            ),
            width=10,
        ),
    ],
    row=True,
)

custom_candidate_node_input = dbc.FormGroup(
    [
        dbc.Label("Choose Candidate Nodes", html_for="choose_candidate_nodes", width=2),
        dbc.Col(
            dbc.Input(
                type="text", id="choose_candidate_nodes", placeholder="Enter comma separated candidate nodes"
            ),
            width=10,
        ),
    ],
    row=True,
)

candidate_nodes_form = dbc.Form([candidate_node_input,custom_candidate_node_input,dbc.Button("Find Charging Stations",id="candiate_nodes_button",color="primary")])

CONTAINER_STYLE = {
    "padding": "2rem 1rem",
}

DROPDOWN_STYLE = {
   "margin-top": "1rem"
}

nav = Navbar()
body = dbc.Container([
    all_nodes_form,
    html.Div(id='num_all_nodes_div'),
    candidate_nodes_form,
    html.Div(id='num_candidate_nodes_div'),
    dbc.DropdownMenu(
            available_indicators, label="Filters", color="primary", style=DROPDOWN_STYLE
    ),
    dcc.Graph(
        id='map',
        figure=fig
    )],style=CONTAINER_STYLE)
layout = html.Div([
    nav,
    body
   ])

def default_location():
    location = geolocator.geocode("India")
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
    return fig

def find_all_nodes(search_location, radius):
    location=geolocator.geocode(search_location)
    num_of_tot_nodes, G1, A, Xnode, Ynode = get_all_nodes(location.latitude,location.longitude,radius)
    fig = go.Figure(go.Scattermapbox(
        lat=Ynode,
        lon=Xnode,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10
        ),
        text=list(range(1,len(G1.nodes))),
    ))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=location.latitude,
                lon=location.longitude,
            ),
            pitch=0,
            zoom=15
        )
    )
    return fig, num_of_tot_nodes, G1, A, Xnode, Ynode

def get_loaded_all_nodes(Xnode, Ynode):
    fig = go.Figure(go.Scattermapbox(
        lat=Ynode,
        lon=Xnode,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10
            ),
        )) 
    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=Ynode[0],
                lon=Xnode[0],
                ),
            pitch=0,
            zoom=15
            )
        )
    return fig

def get_all_candidate_nodes(G1, A, candidate_nodes, Xnode, Ynode, custom_candidate_nodes):
    selected_candidate_nodes=get_candidate_nodes(G1, A, candidate_nodes, custom_candidate_nodes)
    candidate_Xnode=[]
    candidate_Ynode=[]
    final = {}
    for i in range(len(G1.nodes)):
        final[i]=0
    for i in range(len(selected_candidate_nodes)):
        final[int(selected_candidate_nodes[i])-1] = 1
    
    for i in range(len(G1.nodes)):
        if final[i]==1:
            candidate_Ynode.append(Ynode[i])
            candidate_Xnode.append(Xnode[i])
    
    fig = go.Figure(go.Scattermapbox(
        lat=candidate_Ynode,
        lon=candidate_Xnode,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='red'
        ),
        text=selected_candidate_nodes,
    ))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=candidate_Ynode[0],
                lon=candidate_Xnode[0],
            ),
            pitch=0,
            zoom=15
        )
    )
    return fig, selected_candidate_nodes, candidate_Xnode, candidate_Ynode

def get_dropdown_all_nodes(Xnode, Ynode, candidate_Xnode, candidate_Ynode, selected_candidate_nodes):
    fig = go.Figure(go.Scattermapbox(
        lat=Ynode,
        lon=Xnode,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10
        ),
        text=list(range(1,len(Xnode)))
    ))
    fig.add_trace(go.Scattermapbox(
        lat=candidate_Ynode,
        lon=candidate_Xnode,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='red'
        ),
        text=selected_candidate_nodes,
    ))
    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=Ynode[0],
                lon=Xnode[0],
            ),
            pitch=0,
            zoom=15
        )
    )
    return fig

def get_dropdown_charging_stations(candidate_Xnode, candidate_Ynode, selected_candidate_nodes):
    fig = go.Figure(go.Scattermapbox(
        lat=candidate_Ynode,
        lon=candidate_Xnode,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='red'
        ),
        text=selected_candidate_nodes,
    ))
    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=candidate_Ynode[0],
                lon=candidate_Xnode[0],
            ),
            pitch=0,
            zoom=15
        )
    )
    return fig

def get_candidate_nodes(G1, A, candidate_nodes, custom_candidate_nodes):
    my_file = open('sinp.txt', 'w+')
    my_file.write("%d \n" %1)
    my_file.write("%d \n" %len(G1.nodes))
    
    B1=A.tocoo()
    list1=B1.data
    list2=B1.row
    list3=B1.col
    my_file.write("%d \n" %len(list1))
    #No.of edges
    for i in range(len(list1)):
        my_file.write("%d " %(list2[i]+1))  
        my_file.write("%d " %(list3[i]+1))  
        my_file.write("%d \n" %list1[i]) 
    
    my_file.write("%d \n" %candidate_nodes)
    node_list = custom_candidate_nodes
    c_1 = 0
    while len(node_list) != candidate_nodes:
        temp_node = random.randint(1, len(G1.nodes))
        if temp_node not in node_list:
            node_list.append(temp_node)
            c_1=+ 1
        
    for i in range(candidate_nodes):
        my_file.write("%d " %node_list[i])
    my_file.write("\n%d \n" %roc)
    for i in range(candidate_nodes):
        k=random.randint(1, capacity)
        my_file.write("%d " %k)
    my_file.write("\n%s \n" %alpha)
    my_file.write("%s \n" %lamda)
    my_file.write("%s \n" %capacity)
    my_file.write("%s \n" %epsilon)
    my_file.close()
    
    #!pip install gcc
    
    subproces = subprocess.Popen("./code<sinp.txt", shell=True, stdout=subprocess.PIPE)
    tmp = subproces.stdout.read().decode('utf-8').split()
    # tmp=str(tmp)
    # tmp=tmp.split()
    
    return tmp

def get_all_nodes(latitude,longitude,radius):
    location_point=(latitude,longitude)
    G1 = ox.graph_from_point(location_point, distance=radius, simplify=False, network_type='walk')
    # G1 = ox.utils_graph.get_largest_component(G1,strongly=False)
    G1 = ox.simplification.consolidate_intersections(G1,tolerance=1000, rebuild_graph=True, dead_ends=False, reconnect_edges=True)
    ox.save_graphml(G1, filename='network1.graphml')
    nodes1, edges1 = ox.graph_to_gdfs(G1, nodes=True, edges=True)
    nodes1.to_csv('data/node1.csv')
    edges1.to_csv('data/edge1.csv')
    
    Oid=pd.Series.tolist(nodes1.osmid)
    Ynode=pd.Series.tolist(nodes1.y)
    Xnode=pd.Series.tolist(nodes1.x)
    A = nx.adjacency_matrix(G1,weight='length')
    np.savetxt("data/edg.csv", A.todense(), delimiter=",")
    return len(G1.nodes), G1, A, Xnode, Ynode

def App():
    return layout
