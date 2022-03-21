import dash
from dash import dcc
from dash import html
import dash_leaflet as dl
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
from server import app

ox.config(use_cache=True, log_console=True)
Search_Region=[22.59372606392931, 78.57421875000001]

# Header section using navbar
nav = Navbar()


# Body section using graph input first
MAP_ID = "input_map"
MARKER_GROUP_ID = "marker-group"
# map global data
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



# graph figure
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


# filter details
available_indicators = [
    dbc.DropdownMenuItem('All Nodes', id="all_nodes"),
    dbc.DropdownMenuItem('Charging Stations',id="charging_stations"),
]


location_input = dbc.FormGroup(
    [
        dbc.Label("Search Area", html_for="location", width=2),
        dbc.Col(
            dbc.Input(
                type="text", id="locationE", placeholder="Enter a valid location",debounce=False
            ),
            width=10,
        ),
    ],
    row=True,
    id="location_input_form1"
)


autocomplete_list_ecorouting = dbc.Row(
    [
         dbc.Col(width=2),
         dbc.Col(
            dbc.ListGroup(
            [],
            id="autocomplete_list_ecorouting",
            style={"margin-bottom":"8px"}
            ),
             width=10
        )
    ]
)

radius_input = dbc.FormGroup(
    [
        dbc.Label("Radius (in meters)", html_for="radius", width=2),
        dbc.Col(
            dbc.Input(
                type="number", id="radiusE", placeholder="Enter Radius between [500,8000] meters",min=100, step=1,max=8000
            ),
            width=10,
        ),
    ],
    row=True,
    id="radius_input_form1"
)

charging_stations_input = dbc.FormGroup(
    [
        dbc.Label("Charging Stations", html_for="no_of_stations", width=2),
        dbc.Col(
            dbc.Input(
                type="number", id="no_of_stationsE", placeholder="Enter no of charging stations(atleast 1)",min=1, step=1
            ),
            width=10,
        ),
    ],
    row=True,
    id="charging_stations_input_form1"
)


all_nodes_button = dbc.Spinner(children=[dbc.Button("Find All Nodes",id="all_nodes_buttonE",color="primary")],size="sm", color="primary",id="spinner_1")

# Overall Form
all_nodes_form = dbc.Form([location_input,autocomplete_list_ecorouting,radius_input,charging_stations_input,all_nodes_button])

# all_nodes_form = dbc.Form([location_input,radius_input,dbc.Button("Find All Nodes",id="all_nodes_button",color="primary")])


CONTAINER_STYLE = {
    "padding": "2rem 1rem",
}

DROPDOWN_STYLE = {
   "margin-top": "1rem"
}

nav = Navbar()

collapse_body = dbc.Container(
    [
        all_nodes_form,
        html.Div(id='num_all_nodes_div'),
        dcc.Graph(
            id='mapE',
            figure=fig
        )
    ]
    ,style=CONTAINER_STYLE
)

collapse = html.Div(
    [
        dbc.Button(
            "Enter Your Location",
            id="homepage_collapse_toggle",
            className="mb-3",
            color="primary",
            n_clicks=0,
        )
        ,dbc.Collapse(
            collapse_body,
            id="homepage_collapse",
            is_open=True,
        )
    ]
)

second_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Eco Routing", className="card-title"),
            html.P("EcoRouting Algorithm Analysis"),
            dbc.Button("Go to Eco Routing", color="primary", href="/eco_routing",external_link=True),
        ]
    )
)

third_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Charging Station Placement", className="card-title"),
            html.P("Enter Location and Radius to get placement of charging stations. Supports various features such as online/offline maps, different candidate node selection algorithms and compare history feature."),
            dbc.Button("Go to Charging Station Placement", color="primary", href="/charging_station_placement",external_link=True),
        ]
    )
)

fourth_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Graph API OSMNX", className="card-title"),
            html.P("Taking graph input for India"),
            dbc.Button("Go to Test OSMNX", color="primary", href="/osmnx",external_link=True),
        ]
    )
)

cards = dbc.Row([dbc.Col(second_card, width=4), dbc.Col(third_card, width=4), dbc.Col(fourth_card, width=4)])

CONTAINER_STYLE = {
    "padding": "2rem 1rem",
}

body = dbc.Container([
    collapse,
    # dl.Map(style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"},
    #         center=Search_Region,
    #         zoom=5,
    #         children=[
    #             dl.LayersControl(
    #            [dl.TileLayer()] +
    #             [dl.Overlay(dl.LayerGroup(id=MARKER_GROUP_ID), name="marker", checked=True),
    #             dl.Overlay(dl.LayerGroup(id="stationsInInput"), name="markers", checked=True),
    #             dl.Overlay(dl.LayerGroup(id="CircleAreaE"), name="polygon", checked=True)]
    #           ) 
    #         ], id=MAP_ID),
    html.H1("Available Domains"),
    cards
    ],
    style=CONTAINER_STYLE
)

def Homepage():
    layout = html.Div([
    nav,
    body
    ])

    return layout
