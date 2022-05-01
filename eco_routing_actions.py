# Main file for eco routing actions
# Kunj Taneja 1801CS30

from tokenize import Double
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
import random

from navbar import Navbar
from server import app


rEarth = 6371.01 # Earth's average radius in km
epsilon = 0.000001 # threshold for floating-point equality

# all global variables and access tokens
mapbox_access_token = "pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g"
geolocator = Nominatim(user_agent="Charging Station App")
location = geolocator.geocode("India")
Oid = []
input_ev_locations = []
Xnode = []
Ynode = []
paths = []
path_nodes = []
optimal_paths = []
optimal_path_nodes = []
optimal_paths_info = []
G1 = None
algo_input = {}
path_id = None


# deals with auto complete input location
@app.callback(
    [Output("er_autocomplete_list","children"),
     Output("er_location_input","value")],
    [Input("er_location_input", "value"),
     Input({'type': 'er_autocomplete_list_item', 'index': ALL}, 'n_clicks')]
)
def update_location_text(place, chosen_item):
    ctx=dash.callback_context
    if not ctx.triggered:
        if config.location is not None:
            return dash.no_update, config.location
        return dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == "er_location_input":
        if(place is None or place.strip() == ""):
            return [], dash.no_update
        
        autocomplete_list=[]

        parsed_loc = urllib.parse.quote(place)
        response = requests.get("http://api.mapbox.com/geocoding/v5/mapbox.places/"+parsed_loc+".json?country=IN&access_token=pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g")
        res=response.json()
        chosen_location=""
        cnt = 0
        for feat in res["features"]:
            autocomplete_list.append(dbc.ListGroupItem(feat["place_name"],id={'type': 'er_autocomplete_list_item','index': feat["place_name"]},action=True))
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
     Output(component_id='er_num_all_nodes_div', component_property='children'),
     Output(component_id='dl_er_all_nodes', component_property='children'),
     Output(component_id='dl_er_cs_nodes', component_property='children'),
     Output("dl_er_circle", "children"),
     Output(component_id='er_result_map', component_property='center'),
     Output(component_id='er_result_map', component_property='zoom'),
     Output(component_id='dl_er_input_all_nodes', component_property='children'),
     Output(component_id='dl_er_input_cs_nodes', component_property='children'),
     Output("dl_er_input_circle", "children"),
     Output(component_id='er_input_map', component_property='center'),
     Output(component_id='er_input_map', component_property='zoom'),
     Output(component_id='cs_input_table', component_property='options'),
    ],
    inputs = [Input('er_all_nodes_button', 'n_clicks')],
    state = [
           State(component_id='er_location_input', component_property='value'),
           State(component_id='er_radius_input', component_property='value'),
           State(component_id='er_no_of_cs_input', component_property='value'),
           ]
)
def hp_update_map(n_clicks, location, radius, number_of_cs):

    if n_clicks is None:
        if config.num_of_tot_nodes != 0:
            return 'Total Number of Nodes: {}'.format(config.num_of_tot_nodes),config.positions,config.cs_positions,\
                    config.polygon,config.center, config.zoomLevel,config.positions,config.cs_positions,\
                    config.polygon,config.center, config.zoomLevel, dash.no_update

        if n_clicks is None:
            fig, center, zoomLevel = default_location()    
            return '' ,dash.no_update,dash.no_update,dash.no_update,center, zoomLevel,dash.no_update,\
                dash.no_update,dash.no_update,center, zoomLevel, dash.no_update


    global Xnode, Ynode, G1
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
    
    # info related to cs
    config.num_of_cs = number_of_cs
    config.cs_nodes = random.sample(range(0,num_of_tot_nodes),number_of_cs)
    print(config.cs_nodes)
    config.cs_positions = [dl.Marker(position=[Ynode[i],Xnode[i]],children=dl.Tooltip(i, direction='top', permanent=True),\
        riseOnHover=True,icon={'iconUrl':'https://icon-library.com/images/station-icon/station-icon-14.jpg','iconSize':[30,40]}) \
            for i in config.cs_nodes]

    dropdown_content = [[f"Cs Node{i}",f"Node{i}"] for i in config.cs_nodes]
    dropdown = pd.DataFrame(dropdown_content,columns = ['label','value'])
    config.cs_dropdown = dropdown

    # setting the global variables in config file
    config.num_of_tot_nodes, config.positions, config.polygon, config.center, config.zoomLevel = num_of_tot_nodes, positions, polygon,center, zoomLevel
    
    return 'Total Number of Nodes: {}'.format(num_of_tot_nodes),positions,config.cs_positions,\
         polygon,center, zoomLevel, positions, config.cs_positions, polygon,center, zoomLevel, config.cs_dropdown.to_dict('records')



def get_eco_zoom_level(radius):
    level=17
    p=1
    while(p*100<radius):
        p=p*2
        level=level-1
    return level


# finds nodes based on search location and radius
def find_all_nodes(search_location, radius):
    
    parsed_loc = urllib.parse.quote(search_location)
    response = requests.get("http://api.mapbox.com/geocoding/v5/mapbox.places/"+parsed_loc+".json?country=IN&access_token=pk.eyJ1IjoiaGFyc2hqaW5kYWwiLCJhIjoiY2tleW8wbnJlMGM4czJ4b2M0ZDNjeGN4ZyJ9.XXPg4AsUx0GUygvK8cxI6g")
    res=response.json()
    lat_center=res["features"][0]["geometry"]["coordinates"][1]
    long_center=res["features"][0]["geometry"]["coordinates"][0]
    # print(search_location)
    center = [lat_center,long_center]
    zoomLevel = get_eco_zoom_level(radius)
    global G1
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
    global G1
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
    list1=B1.data
    list2=B1.row
    list3=B1.col



    my_file = open('input_graph.txt', "w+")
    my_file.write("%d \n" %len(G1.nodes))
    my_file.write("%d \n" %len(list1))

    for i in range(len(list1)):
        my_file.write("%d " %(list2[i]))  
        my_file.write("%d " %(list3[i]))  
        my_file.write("%d \n" %int(list1[i])) 
    
    
    my_file.close()

    return len(G1.nodes), G1, A, Xnode, Ynode


# callback related to number of EV input and generating content for drowpdown and updating the cirle on the input_map
@app.callback(
    [
     Output(component_id='er_num_all_ev', component_property='children'),
     Output(component_id='er_ev_input_dropdown', component_property='options'),
     Output(component_id='ev_sdinput_table', component_property='options'),
     Output(component_id='dl_er_input_cs_selected_nodes', component_property='children'),
     Output(component_id='dl_er_output_cs_selected_nodes', component_property='children'),
     Output(component_id='dl_er_cs_output_cs_selected_nodes', component_property='children'),
    ],
    inputs = [
                Input('er_vehicles_button', 'n_clicks'),
            ],
    state = [
           State(component_id='er_no_of_vehicles_input', component_property='value'),
           State(component_id='cs_input_table', component_property='value'),
           State(component_id='er_inital_charge', component_property='value'),
           State(component_id='er_ev_capacity', component_property='value'),
           ]
)
def er_input_ev(nclicks,number_of_ev,cs_input,initial_charge, ev_capacity):
    if nclicks is None:
        # if config.ev_dropdown is not None:
        #     return f"Number of ev : {config.num_of_ev}",\
        #             config.ev_dropdown.to_dict('records'),\
        #                    config.table_of_ev_inputs.to_dict('records'), dash.no_update, dash.no_update
        return "Enter number of EVs",[], [], [], [], []
    
    print(f"CS Input: {cs_input}")

    config.cs_selected_positions = config.cs_positions 
    config.cs_selected_nodes = config.cs_nodes
    if len(cs_input) > 0:
        cs_nodes = [int(i[4:]) for i in cs_input]
        config.cs_selected_nodes = cs_nodes
        print(f"Selected cs_nodes: {cs_nodes}")
        config.cs_selected_positions = [
        dl.Marker(position=[Ynode[i],Xnode[i]],children=dl.Tooltip(i, direction='top', permanent=True),\
        riseOnHover=True,icon={'iconUrl':'https://icon-library.com/images/station-icon/station-icon-14.jpg','iconSize':[30,40]}) \
            for i in cs_nodes]
    
    my_file = open('cs_input.txt', "w+")
    my_file.write("%d \n" %int(len(config.cs_selected_nodes)))
    for i in config.cs_selected_nodes:
        my_file.write("%d " %int(i))

    my_file.write("\n")
    my_file.close()

    my_file = open('ev_info.txt', "w+")
    my_file.write("%d " %int(initial_charge))
    my_file.write("%d \n" %int(ev_capacity))
    my_file.close()

    global input_ev_locations, Xnode, algo_input
    input_ev_locations = []
    algo_input = {}
    config.output_positions = {}
    config.ev_sdinput = pd.DataFrame()
    config.num_of_ev = number_of_ev
    dropdown_content = [[f"Node{i}",f"Node{i}","Not Selected"] for i in range(len(Xnode))]
    dropdown = pd.DataFrame(dropdown_content,columns = ['label','value','title'])
    config.ev_dropdown = dropdown
    
    table_content = [ [f"SRC{(i//2) + 1}" if i%2==0 else f"DST{(i//2) + 1}",
    f"SRC{(i//2) + 1}" if i%2==0 else f"DST{(i//2) + 1}"] for i in range(2*number_of_ev)]
    table = pd.DataFrame(table_content,columns = ['label','value'])
    config.table_of_ev_inputs = table
    return f"Number of ev: {number_of_ev}", \
            config.ev_dropdown.to_dict('records'),\
        config.table_of_ev_inputs.to_dict('records'), config.cs_selected_positions, config.cs_selected_positions, config.cs_selected_positions
        

# Taking inputs of source and destination coordinates based on dropdown or input using map clicks
@app.callback(
    [
     Output(component_id='dl_er_input_selected_nodes', component_property='children'),
     Output(component_id='ev_sdoutput_table', component_property='data'),
     Output(component_id='er_ev_input_dropdown', component_property='value'),
    ],
    inputs = [
                Input('er_ev_input_dropdown', 'value'),  
                Input('er_sd_input_button', 'n_clicks'),  
                Input('er_input_map', 'click_lat_lng'),  
            ],
    state = [
        State(component_id='ev_sdinput_table', component_property='value')
    ]
    
)
def er_update_inputs(node,nclicks,cord_vector,vehicle):
    ctx=dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not ctx.triggered or node==None or vehicle ==None:
        return dash.no_update, dash.no_update, dash.no_update
    
    global algo_input

    if trigger_id == "er_ev_input_dropdown":
        
        vechicle_id = int(vehicle[3:])
        node_id = int(node[4:])
        algo_input[vehicle] = node
        
        config.output_positions[vehicle] = dl.Marker(position=[Ynode[node_id],Xnode[node_id]],children=dl.Tooltip(node_id, direction='top', permanent=True),
            riseOnHover=True, icon={'iconUrl':'https://api.iconify.design/clarity/map-marker-solid-badged.svg?color=red','iconSize':[30,40]})
        
        return list(config.output_positions.values()), dash.no_update , dash.no_update

    elif trigger_id == "er_input_map":
        x_cord = float(cord_vector[0])
        y_cord = float(cord_vector[1])
        cord_node = ox.distance.nearest_nodes(G1, y_cord, x_cord)
        for i in range(len(Oid)):
            if Oid[i] == cord_node:
                cord_node = i
                break

        print(cord_node)
        algo_input[vehicle] = f"Node{cord_node}"

        config.output_positions[vehicle] = dl.Marker(position=[Ynode[cord_node],Xnode[cord_node]],children=dl.Tooltip(cord_node, direction='top', permanent=True),
            riseOnHover=True, icon={'iconUrl':'https://api.iconify.design/clarity/map-marker-solid-badged.svg?color=red','iconSize':[30,40]})
        
        return list(config.output_positions.values()), dash.no_update, f"Node{cord_node}" 
    else:

        config.ev_sdinput = pd.DataFrame(list(algo_input.items()),columns = ['vehicle_id','node_id']).sort_values(by = 'vehicle_id')
        return list(config.output_positions.values()), config.ev_sdinput.to_dict('records'), dash.no_update

    
# Callback leading to generating all paths and which path to show for the simple output map
@app.callback(
    [
     Output(component_id='dl_er_output_all_nodes', component_property='children'),
     Output("dl_er_output_circle", "children"),
     Output(component_id='er_output_map', component_property='center'),
     Output(component_id='er_output_map', component_property='zoom'),
     Output(component_id='dl_er_output_path', component_property='children'),
     Output(component_id='dl_er_output_path_nodes', component_property='children'),
     Output(component_id='ev_path_table', component_property='options'),
     Output(component_id='ev_path_index_table', component_property='options'),
     Output(component_id='ev_sd_input_validation', component_property='children'),
    ],
    inputs = [
                Input('er_generate_paths_button', 'n_clicks'), 
                Input('ev_path_table', 'value'),  
                Input('er_generate_selected_path_button', 'n_clicks'),  
            ],
    state = [
                State('ev_path_index_table', 'value'),  
    ]
    
)
def generate_paths(nclicks, path_id_input, ncliks2, path_index_input):
    # if nclicks is None:
    #     return config.positions, config.polygon, config.center, config.zoomLevel, dash.no_update, dash.no_update, [], []
    
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


    if trigger_id == "er_generate_paths_button":
        # print(f"er_generate_paths_button triggered : {algo_input}, {config.num_of_ev}")
        if len(algo_input) < 2*config.num_of_ev:
            # print("if condition entered")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Please Enter input for all EVs"
        
        # print(f"hey {len(algo_input)}, {config.num_of_ev}")
        my_file = open('queries.txt', "w+")
        my_file.write("%d \n" %(config.num_of_ev))

        for i in range(1,config.num_of_ev+1):
            my_file.write("%d " %int(algo_input[f"SRC{i}"][4:]))
            my_file.write("%d \n" %int(algo_input[f"DST{i}"][4:]))
        
        my_file.close()

        subproces = subprocess.check_call("./cs_algo")
        # subproces = subprocess.check_call("./algo")

        global paths, path_nodes
        paths = []
        path_nodes = []

        my_file = open("output_graph.txt","r")

        Q = int(my_file.readline())
        color_index = 0
        color_list = ["red","orange","yellow","green","pink"]

        # print(f"We got Q : {Q}")

        for i in range(Q):
            number_of_paths = int(my_file.readline())
            temp = []
            path_nodes_temp = []
            for id in range(number_of_paths):
                n,energy = list(map(int,my_file.readline().split()))
                arr = list(map(int,my_file.readline().split()))
                # print(arr)
                path = []
                path_node = []
                path.append(
                    dl.Marker(position=[Ynode[arr[0]],Xnode[arr[0]]],\
                                children=dl.Tooltip(f"SRC: Node{arr[0]}", direction='top', permanent=True),
                                riseOnHover=True, \
                                icon={'iconUrl':'https://api.iconify.design/clarity/map-marker-solid-badged.svg?color=green','iconSize':[30,40]})
                )
                if len(arr)>1:
                    path.append(
                        dl.Marker(position=[Ynode[arr[-1]],Xnode[arr[-1]]],\
                                    children=dl.Tooltip(f"DST: Node{arr[-1]}", direction='top', permanent=True),
                                    riseOnHover=True, \
                                    icon={'iconUrl':'https://api.iconify.design/clarity/map-marker-solid-badged.svg?color=green','iconSize':[30,40]})
                    )
                for node_id in arr:
                    path_node.append(
                                dl.Marker(position=[Ynode[node_id],Xnode[node_id]],\
                                children=dl.Tooltip(node_id, direction='top', permanent=True),
                                riseOnHover=True, \
                                icon={'iconUrl':'https://api.iconify.design/clarity/map-marker-solid-badged.svg?color=green','iconSize':[30,40]}))

                for j in range(len(arr)-1):
                    corners = [[Ynode[arr[j]],Xnode[arr[j]]], [Ynode[arr[j+1]],Xnode[arr[j+1]]]]
                    polyline = dl.Polyline(color=color_list[color_index],weight=4,positions=corners)
                    path.append(polyline)

                color_index = (color_index+1)%len(color_list)
                temp.append(path)
                path_nodes_temp.append(path_node)

            paths.append(temp)
            path_nodes.append(path_nodes_temp)

        my_file.close()
        
        config.path_inputs = pd.DataFrame(columns = ['label','value'])
        for i in range(Q):
            dropdown_data = {'label':f"Path{i}", "value":f"Path{i}"}
            config.path_inputs = config.path_inputs.append(dropdown_data,ignore_index=True)
        
        return config.positions, config.polygon, config.center, config.zoomLevel, [],[], config.path_inputs.to_dict('records'), [], ""

    elif trigger_id == "ev_path_table":
        global path_id
        path_id = int(path_id_input[4:])
        options = []
        for i in range(len(paths[path_id])):
            options.append({'label':f"Path_option{i}", "value":f"Path_option{i}"})
        return config.positions, config.polygon, config.center, config.zoomLevel, [],[], config.path_inputs.to_dict('records'), options, ""

    else:
        path_index = int(path_index_input[11:])
        return config.positions, config.polygon, config.center, config.zoomLevel, paths[path_id][path_index],path_nodes[path_id][path_index], dash.no_update, dash.no_update, ""
        


# Callback leading to generating all paths and which path to show for the cs output map based on availability of paths
@app.callback(
    [
     Output(component_id='dl_er_cs_output_all_nodes', component_property='children'),
     Output("dl_er_cs_output_circle", "children"),
     Output(component_id='er_cs_output_map', component_property='center'),
     Output(component_id='er_cs_output_map', component_property='zoom'),
     Output(component_id='dl_er_cs_output_path', component_property='children'),
     Output(component_id='dl_er_cs_output_path_nodes', component_property='children'),
     Output(component_id='ev_cs_path_table', component_property='options'),
     Output(component_id='ev_cs_path_index_table', component_property='options'),
     Output(component_id='ev_cs_path_info', component_property='children'),
    ],
    inputs = [
                Input('er_generate_paths_button', 'n_clicks'), 
                Input('ev_cs_path_table', 'value'),  
                Input('er_cs_generate_selected_path_button', 'n_clicks'),  
            ],
    state = [
                State('ev_cs_path_index_table', 'value'),  
    ]
    
)
def generate_possible_paths(nclicks, path_id_input, ncliks2, path_index_input):
    # if nclicks is None:
    #     return config.positions, config.polygon, config.center, config.zoomLevel, dash.no_update, dash.no_update, [], []
    
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


    if trigger_id == "er_generate_paths_button":
        # print(f"er_generate_paths_button triggered : {algo_input}, {config.num_of_ev}")
        if len(algo_input) < 2*config.num_of_ev:
            print("if condition entered")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        print(f"hey {len(algo_input)}, {config.num_of_ev}")
        my_file = open('queries.txt', "w+")
        my_file.write("%d \n" %(config.num_of_ev))

        for i in range(1,config.num_of_ev+1):
            my_file.write("%d " %int(algo_input[f"SRC{i}"][4:]))
            my_file.write("%d \n" %int(algo_input[f"DST{i}"][4:]))
        
        my_file.close()
        # subproces = subprocess.check_call("g++ dijkstra.cpp -o dij")
        subproces = subprocess.check_call("./cs_algo")

        global optimal_paths, optimal_path_nodes, optimal_paths_info
        optimal_paths = []
        optimal_path_nodes = []
        optimal_paths_info = []

        my_file = open("cs_output_graph.txt","r")

        Q = int(my_file.readline())
        color_index = 0
        color_list = ["red","orange","yellow","green","pink"]

        print(f"We got Q : {Q}")

        for i in range(Q):
            number_of_paths = int(my_file.readline())
            temp = []
            path_nodes_temp = []
            paths_info = []
            for id in range(number_of_paths):
                n,time,energy = list(map(float,my_file.readline().split()))
                arr = list(map(int,my_file.readline().split()))
                print(arr)
                path = []
                path_node = []
                
                if n==0:
                    temp.append(path)
                    path_nodes_temp.append(path_node)
                    
                    if(arr[0]==0):
                        paths_info.append(f"Could not reach any charging station !!! \n You need to increase initial charge")
                    else:
                        paths_info.append(f"Could not reach destination !!! \n You need to increase vehicle capacity")
                    continue
                
                paths_info.append(f"Total Nodes: {n}, Total Time take : {time}, Total Energy Consumed : {energy}")
                path.append(
                    dl.Marker(position=[Ynode[arr[0]],Xnode[arr[0]]],\
                                children=dl.Tooltip(f"SRC: Node{arr[0]}", direction='top', permanent=True),
                                riseOnHover=True, \
                                icon={'iconUrl':'https://api.iconify.design/clarity/map-marker-solid-badged.svg?color=green','iconSize':[30,40]})
                )
                if len(arr)>1:
                    path.append(
                        dl.Marker(position=[Ynode[arr[-1]],Xnode[arr[-1]]],\
                                    children=dl.Tooltip(f"DST: Node{arr[-1]}", direction='top', permanent=True),
                                    riseOnHover=True, \
                                    icon={'iconUrl':'https://api.iconify.design/clarity/map-marker-solid-badged.svg?color=green','iconSize':[30,40]})
                    )
                for node_id in arr:
                    if node_id in config.cs_selected_nodes:
                        path_node.append(
                                    dl.Marker(position=[Ynode[node_id],Xnode[node_id]],\
                                    children=dl.Tooltip(node_id, direction='top', permanent=True),
                                    riseOnHover=True, \
                                    icon={'iconUrl':'https://api.iconify.design/clarity/map-marker-solid-badged.svg?color=black','iconSize':[30,40]}))
                    else:
                        path_node.append(
                                    dl.Marker(position=[Ynode[node_id],Xnode[node_id]],\
                                    children=dl.Tooltip(node_id, direction='top', permanent=True),
                                    riseOnHover=True, \
                                    icon={'iconUrl':'https://api.iconify.design/clarity/map-marker-solid-badged.svg?color=green','iconSize':[30,40]}))

                for j in range(len(arr)-1):
                    corners = [[Ynode[arr[j]],Xnode[arr[j]]], [Ynode[arr[j+1]],Xnode[arr[j+1]]]]
                    polyline = dl.Polyline(color=color_list[color_index],weight=4,positions=corners)
                    path.append(polyline)

                color_index = (color_index+1)%len(color_list)
                temp.append(path)
                path_nodes_temp.append(path_node)

            optimal_paths.append(temp)
            optimal_path_nodes.append(path_nodes_temp)
            optimal_paths_info.append(paths_info)
        
        config.path_inputs = pd.DataFrame(columns = ['label','value'])
        my_file.close()
        for i in range(Q):
            dropdown_data = {'label':f"Path{i}", "value":f"Path{i}"}
            config.path_inputs = config.path_inputs.append(dropdown_data,ignore_index=True)
        
        return config.positions, config.polygon, config.center, config.zoomLevel, [],[], config.path_inputs.to_dict('records'), [], ""

    elif trigger_id == "ev_cs_path_table":
        global path_id
        path_id = int(path_id_input[4:])
        options = []
        for i in range(len(optimal_paths[path_id])):
            options.append({'label':f"Path_option{i}", "value":f"Path_option{i}"})
        return config.positions, config.polygon, config.center, config.zoomLevel, [],[], config.path_inputs.to_dict('records'), options, dash.no_update

    else:
        path_index = int(path_index_input[11:])
        return config.positions, config.polygon, config.center, config.zoomLevel, optimal_paths[path_id][path_index],optimal_path_nodes[path_id][path_index], dash.no_update, dash.no_update, optimal_paths_info[path_id][path_index]
        


# Class helping to create the dynamic values of radioButtons
class geeks:  
    def __init__(self, vnumber, itype,value):  
        self.vnumber = vnumber  
        self.itype = itype
        self.value = value

# Function creating "val" numbers of source and destination radiobuttons
def dynamic_source_destination_maker(val):
    list = []
    for i in range(1,val+1):
        list.append(geeks(i, 'Source', 'SRC'))
    for i in range(1,val+1):
        list.append(geeks(i, 'Destination','DTN'))

    return [
        {'label': 'Vehicle {}: {}'.format(obj.vnumber,obj.itype), 'value': obj.value+' {}'.format(obj.vnumber)} for obj in list
        ]
    



