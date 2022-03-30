import dash
from dash import dcc
from dash import html
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from geopy.geocoders import Nominatim

import osmnx as ox


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


# filter details
available_indicators = [
    dbc.DropdownMenuItem('All Nodes', id="all_nodes"),
    dbc.DropdownMenuItem('Charging Stations',id="charging_stations"),
]


hp_location_input_form = dbc.FormGroup(
    [
        dbc.Label("Search Area", html_for="location", width=2),
        dbc.Col(
            dbc.Input(
                type="text", id="hp_location_input", placeholder="Enter a valid location",debounce=False
            ),
            width=10,
        ),
    ],
    row=True,
    id="hp_location_input_form"
)


autocomplete_list_ecorouting = dbc.Row(
    [
         dbc.Col(width=2),
         dbc.Col(
            dbc.ListGroup(
            [],
            id="hp_autocomplete_list",
            style={"margin-bottom":"8px"}
            ),
             width=10
        )
    ]
)

hp_radius_input_form = dbc.FormGroup(
    [
        dbc.Label("Radius (in meters)", html_for="radius", width=2),
        dbc.Col(
            dbc.Input(
                type="number", id="hp_radius_input", placeholder="Enter Radius between [500,8000] meters",min=100, step=1,max=8000
            ),
            width=10,
        ),
    ],
    row=True,
    id="hp_radius_input_form"
)


hp_all_nodes_button = dbc.Spinner(children=[dbc.Button("Find All Nodes",id="hp_all_nodes_button",color="primary")],
                                        size="sm", color="primary",id="spinner_1")

# Overall Form
all_nodes_form = dbc.Form([hp_location_input_form,autocomplete_list_ecorouting,hp_radius_input_form,
                            hp_all_nodes_button])


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
        dl.Map(style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"},
            center=Search_Region,
            zoom=5,
            children=[
                dl.LayersControl(
               [dl.TileLayer()] +
                [
                dl.Overlay(dl.LayerGroup(id="dl_hp_all_nodes"), name="All Nodes", checked=True),
                dl.Overlay(dl.LayerGroup(id="dl_hp_circle"), name="Search Area", checked=True),]
              ) 
            ], id="hp_result_map"),
    ]
    ,style=CONTAINER_STYLE
)

collapse = html.Div(
    [
        dbc.Button(
            "Enter Your Location",
            id="hp_collapse_toggle",
            className="mb-3",
            color="primary",
            n_clicks=0,
        )
        ,dbc.Collapse(
            collapse_body,
            id="hp_collapse",
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
