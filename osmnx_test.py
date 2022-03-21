import dash
from dash import dcc
from dash import html
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


def osmnx_layout():
    return layout
