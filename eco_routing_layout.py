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


# access token data 
Search_Region=[22.59372606392931, 78.57421875000001]

mapbox_access_token = "pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g"
geolocator = Nominatim(user_agent="Charging Station App")
location = geolocator.geocode("India")





CONTAINER_STYLE = {
    "padding": "2rem 1rem",
}


# location input
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

# autocomplete list
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

# radius input
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

# total number of vechicle input
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


# initial charge input
initial_charge = dbc.FormGroup(
    [
        dbc.Label("Initial charge:", html_for="no_of_vehicles", width=2),
        dbc.Col(
            dbc.Input(
                type="text", id="er_inital_charge", placeholder="Enter inital charge"
            ),
            width=10,
        ),
    ],
    row=True,
)

# ev_capacity input
ev_capacity = dbc.FormGroup(
    [
        dbc.Label("Ev capacity:", html_for="no_of_vehicles", width=2),
        dbc.Col(
            dbc.Input(
                type="text", id="er_ev_capacity", placeholder="Enter capacity of ev ( > inital charge )"
            ),
            width=10,
        ),
    ],
    row=True,
)

# total cs input
total_number_cs = dbc.FormGroup(
    [
        dbc.Label("Number of CS:", html_for="no_of_cs", width=2),
        dbc.Col(
            dbc.Input(
                type="number", id="er_no_of_cs_input", placeholder="Enter total no of cs",min=1, step=1,max=10
            ),
            width=10,
        ),
    ],
    row=True,
)

# cs dropdown list
cs_input_dropdown = dbc.FormGroup(
    [
        dbc.Label("Select CS:", html_for="no_of_cs", width=2),
        dbc.Col(
            dcc.Dropdown(options=[{'label':'None','value':'Kunj'}], value="", id="cs_input_table", multi=True),
            width=10,
        ),
    ],
    row=True,
)


# cs_input_dropdown = dcc.Dropdown(options=[{'label':'None','value':'Kunj'}], value="", id="cs_input_table"),

all_nodes_button = dbc.Spinner(children=[dbc.Button("Find All Nodes",id="er_all_nodes_button",color="primary")],size="sm", color="primary",id="spinner_1")

all_nodes_form = dbc.Form([location_input,autocomplete_list_ecorouting,radius_input,total_number_cs,all_nodes_button])

vehicles_input_form = dbc.Form([total_number_vehicles,initial_charge,ev_capacity, cs_input_dropdown,dbc.Spinner(children=[dbc.Button("Inputs for vehicles",id="er_vehicles_button",color="primary")],size="sm", color="primary",id="spinner_2")])
# cs_input_form = dbc.Form([total_number_vehicles,dbc.Spinner(children=[dbc.Button("Inputs for vehicles",id="er_vehicles_button",color="primary")],size="sm", color="primary",id="spinner_2")])

# loading navbar
nav = Navbar()

# App layout
body = dbc.Container([
    
    html.P(id='placeholder'),
    html.Br(),
    html.Br(),  
    html.H1("Eco Routing App", style={'text-align': 'center'},id="bluffing_input"),   
    html.Hr(),
    html.Br(),
    # first input form
    all_nodes_form, 
    html.Div(id="verificationComments"),
    html.Br(),
    html.Div(id='er_num_all_nodes_div'),
    html.Br(),
    html.H1("Visualise Generated Nodes", style={'text-align': 'center'}),
    html.Hr(),
    # visualising map
    dl.Map(style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"},
            center=Search_Region,
            zoom=5,
            children=[
                dl.LayersControl(
               [dl.TileLayer()] +
                [
                dl.Overlay(dl.LayerGroup(id="dl_er_all_nodes"), name="General Nodes", checked=False),
                dl.Overlay(dl.LayerGroup(id="dl_er_circle"), name="Search Area", checked=True),
                dl.Overlay(dl.LayerGroup(id="dl_er_cs_nodes"), name="Charging Stations", checked=True),
                ]
              ) 
            ], id="er_result_map"),
    html.Br(),
    html.Br(),
    html.H1("EV initial data", style={'text-align': 'center'}),
    html.Hr(),
    html.Br(),
    # input form for vehicles info
    vehicles_input_form ,
    html.Div(id = "vechicle_form_validation"),
    # html.Br(),
    # html.Div(
    #     dcc.Dropdown(options=[{'label':'None','value':'Kunj'}], value="", id="cs_input_table"),
    # ),

    html.H1("Input for EVs", style={'text-align': 'center'}),
    html.Hr(),
    html.Br(),
    html.Div(id='er_num_all_ev'),
    # layout for input map 
    html.Div(
        dbc.Row(
            [
                dbc.Col(
                    [
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
                                    dl.Overlay(dl.LayerGroup(id="dl_er_input_cs_nodes"), name="Charging Stations", checked=False),
                                    dl.Overlay(dl.LayerGroup(id="dl_er_input_cs_selected_nodes"), name="Selected Charging Stations", checked=True),
                                    ]
                                ) 
                        ]
                        ,id="er_input_map"),
                    ],
                    width = 6
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(options=[{'label':'None','value':'Kunj'}], value="", id="ev_sdinput_table"),
                    ],
                    width = 2
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(options=[], value="", id="er_ev_input_dropdown"),
                    ],
                    width = 2
                ),
                dbc.Col(
                    [
                        dbc.Spinner(children=[dbc.Button("Push Input",id="er_sd_input_button",color="primary")],size="sm", color="primary",id="spinner_1"),
                    ],
                    width = 2
                ),
            ]
        )
    ),
    
    html.Br(),
    html.Hr(),
     
    html.Br(),
    # table to view inputs
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
    html.Div(dbc.Spinner(children=[dbc.Button("Generate Paths for EVs",id="er_generate_paths_button",color="primary")],size="sm", color="primary",id="spinner_2"))
     ,html.Br(),
    html.Div(id='ev_sd_input_validation'),
    html.Br(),
    html.Hr(),
    html.H1("Visualise Generated Paths", style={'text-align': 'center'}),
    html.Hr(),

    # layout for output map
     html.Div(
         dbc.Row(
             [
                dbc.Col(
                    [
                        dl.Map(style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"},
                                    center=Search_Region,
                                    zoom=5,
                                    children=[
                                        dl.LayersControl(
                                            [dl.TileLayer()] +
                                                [
                                                dl.Overlay(dl.LayerGroup(id="dl_er_output_circle"), name="Search Area", checked=True),
                                                dl.Overlay(dl.LayerGroup(id="dl_er_output_all_nodes"), name="General Nodes", checked=False),
                                                dl.Overlay(dl.LayerGroup(id="dl_er_output_cs_selected_nodes"), name="CS Nodes", checked=True),
                                                dl.Overlay(dl.LayerGroup(id="dl_er_output_path"), name="Path", checked=True),
                                                dl.Overlay(dl.LayerGroup(id="dl_er_output_path_nodes"), name="Path Nodes", checked=False),
                                                ]
                                            ) 
                                    ]
                                    ,id="er_output_map"),
                        
                    ],
                    width = 6
                    
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(options=[], value="", id="ev_path_table"),
                        
                    ],
                    width = 2
                    
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(options=[], value="", id="ev_path_index_table"),

                    ],
                    width = 2
                ),
                dbc.Col(
                    [
                        dbc.Spinner(children=[dbc.Button("Visualise Path",id="er_generate_selected_path_button",color="primary")],size="sm", color="primary",id="spinner_1"),
                    ],
                    width = 2
                ),
             ]

         )
     ),
    html.Br(),
    html.Br(),
    html.Br(),
    html.H1("Possible Paths using CS", style={'text-align': 'center'}),
    html.Hr(),
    html.Br(),

    # layout for cs output map
    html.Div([
         dbc.Row([
             html.Div(id='ev_cs_path_info'),
             html.Br()
         ]
         ),
         dbc.Row(
             [
                dbc.Col(
                    [
                        dl.Map(style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"},
                                    center=Search_Region,
                                    zoom=5,
                                    children=[
                                        dl.LayersControl(
                                            [dl.TileLayer()] +
                                                [
                                                dl.Overlay(dl.LayerGroup(id="dl_er_cs_output_circle"), name="Search Area", checked=True),
                                                dl.Overlay(dl.LayerGroup(id="dl_er_cs_output_all_nodes"), name="General Nodes", checked=False),
                                                dl.Overlay(dl.LayerGroup(id="dl_er_cs_output_cs_selected_nodes"), name="CS Nodes", checked=True),
                                                dl.Overlay(dl.LayerGroup(id="dl_er_cs_output_path"), name="Path", checked=True),
                                                dl.Overlay(dl.LayerGroup(id="dl_er_cs_output_path_nodes"), name="Path Nodes", checked=False),
                                                ]
                                            ) 
                                    ]
                                    ,id="er_cs_output_map"),
                        
                    ],
                    width = 6
                    
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(options=[], value="", id="ev_cs_path_table"),
                        
                    ],
                    width = 2
                    
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(options=[], value="", id="ev_cs_path_index_table"),

                    ],
                    width = 2
                ),
                dbc.Col(
                    [
                        dbc.Spinner(children=[dbc.Button("Visualise Path",id="er_cs_generate_selected_path_button",color="primary")],size="sm", color="primary",id="spinner_1"),
                    ],
                    width = 2
                ),
             ]

         )
    ]),

])


layout = html.Div([
    nav,
    body
   ])



def eco_routing_layout():
    return layout