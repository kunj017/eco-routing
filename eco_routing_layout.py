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

mapbox_access_token = "pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g"
geolocator = Nominatim(user_agent="Charging Station App")
location = geolocator.geocode("India")





CONTAINER_STYLE = {
    "padding": "2rem 1rem",
}


location_input = dbc.FormGroup(
    [
        dbc.Label("Search Area", html_for="location", width=2),
        dbc.Col(
            dbc.Input(
                type="text", id="er_location_input", placeholder="Enter a valid location",debounce=False
            ),
            width=10,
        ),
    ],
    row=True,
    id="er_location_input_form"
)


autocomplete_list_ecorouting = dbc.Row(
    [
         dbc.Col(width=2),
         dbc.Col(
            dbc.ListGroup(
            [],
            id="er_autocomplete_list",
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
                type="number", id="er_radius_input", placeholder="Enter Radius between [500,8000] meters",min=100, step=1,max=8000
            ),
            width=10,
        ),
    ],
    row=True,
    id="er_radius_input_form"
)

total_number_vehicles = dbc.FormGroup(
    [
        dbc.Label("Number of Vehicles:", html_for="no_of_vehicles", width=2),
        dbc.Col(
            dbc.Input(
                type="number", id="er_no_of_vehicles_input", placeholder="Enter total no of vehicles",min=1, step=1,max=10
            ),
            width=10,
        ),
    ],
    row=True,
)


all_nodes_button = dbc.Spinner(children=[dbc.Button("Find All Nodes",id="er_all_nodes_button",color="primary")],size="sm", color="primary",id="spinner_1")

all_nodes_form = dbc.Form([location_input,autocomplete_list_ecorouting,radius_input,all_nodes_button])

vehicles_input_form = dbc.Form([total_number_vehicles,dbc.Spinner(children=[dbc.Button("Inputs for vehicles",id="er_vehicles_button",color="primary")],size="sm", color="primary",id="spinner_2")])


nav = Navbar()

# App layout
body = dbc.Container([
    
    html.P(id='placeholder'),
    html.Br(),
    html.Br(),  
    html.H1("Eco Routing App", style={'text-align': 'center'},id="bluffing_input"),   
    html.Br(),
    all_nodes_form, 
    html.Div(id="verificationComments"),
    html.Br(),
    html.Div(id='er_num_all_nodes_div'),
    html.Br(),
    html.H1("Visualise Generated Nodes", style={'text-align': 'center'}),
    dl.Map(style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"},
            center=Search_Region,
            zoom=5,
            children=[
                dl.LayersControl(
               [dl.TileLayer()] +
                [
                dl.Overlay(dl.LayerGroup(id="dl_er_all_nodes"), name="General Nodes", checked=True),
                dl.Overlay(dl.LayerGroup(id="dl_er_circle"), name="Search Area", checked=True),]
              ) 
            ], id="er_result_map"),
    html.Br(),
    html.Br(),
    
    vehicles_input_form ,

    html.H1("Input for EVs", style={'text-align': 'center'}),
    html.Br(),
    html.Div(id='er_num_all_ev'),

    html.Div(
        [
            html.Div(
                dl.Map(style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"},
                        center=Search_Region,
                        zoom=5,
                        children=[
                            dl.LayersControl(
                                [dl.TileLayer()] +
                                    [
                                    dl.Overlay(dl.LayerGroup(id="dl_er_input_circle"), name="Search Area", checked=True),
                                    dl.Overlay(dl.LayerGroup(id="dl_er_input_all_nodes"), name="General Nodes", checked=False),
                                    dl.Overlay(dl.LayerGroup(id="dl_er_input_selected_nodes"), name="selected Nodes", checked=True),
                                    ]
                                ) 
                        ]
                        ,id="er_input_map"),
                style = {'width': '50%', 'display': 'inline-block'}
            ),
            html.Div(
                dcc.Dropdown(options=[{'label':'None','value':'Kunj'}], value="", id="ev_sdinput_table"),
                style = {'width': '20%', 'display': 'inline-block','margin-left':'50px','margin-bottom':'400px'}
            ),
            html.Div(
                dcc.Dropdown(options=[], value="", id="er_ev_input_dropdown"),
                style = {'width': '20%', 'display': 'inline-block','margin-left':'50px','margin-bottom':'400px'}
            )
        ]
    ),
    
    html.Br(),
    html.Hr(),
     
    html.Br(),
     html.Div([
                dash.dash_table.DataTable(
            id='ev_sdoutput_table',
            columns=[{'id':'vehicle_id','name':'Input'},{'id':'node_id','name':'Selected Node'},],
            data=[],
            style_table={'overflowX': 'scroll'},
            style_as_list_view=True,
            style_cell={'textAlign': 'center'},
            style_header={'backgroundColor': 'white','fontWeight': 
            'bold'},
         )
        ]),
    html.Div(dbc.Spinner(children=[dbc.Button("Inputs for vehicles",id="er_generate_paths_button",color="primary")],size="sm", color="primary",id="spinner_2"))
     ,html.Br(),
    html.Hr(),
     html.H1("Visualise Generated Paths", style={'text-align': 'center'}),
     html.Div(
         [
            html.Div(
                dl.Map(style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"},
                            center=Search_Region,
                            zoom=5,
                            children=[
                                dl.LayersControl(
                                    [dl.TileLayer()] +
                                        [
                                        dl.Overlay(dl.LayerGroup(id="dl_er_output_circle"), name="Search Area", checked=True),
                                        dl.Overlay(dl.LayerGroup(id="dl_er_output_all_nodes"), name="General Nodes", checked=False),
                                        dl.Overlay(dl.LayerGroup(id="dl_er_output_path"), name="Path", checked=True),
                                        ]
                                    ) 
                            ]
                            ,id="er_output_map"),
                    style = {'width': '70%', 'display': 'inline-block'}
            ),
            html.Div(
                dcc.Dropdown(options=[], value="", id="ev_path_table"),
                style = {'width': '20%', 'display': 'inline-block','margin-left':'50px','margin-bottom':'400px'}
            ),

        ]
     ),
    

])


layout = html.Div([
    nav,
    body
   ])



def eco_routing_layout():
    return layout