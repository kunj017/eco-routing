# Web Application

## Homepage

----
The main action functions of homepage_layout are:

- toggle_collapse: 
    - Info: deals with homepage toggle
    - Inputs: 
        - ("hp_collapse_toggle", "n_clicks") => Click event of toggle button
    - State: 
        - ("hp_collapse", "is_open") => toggle state
    - Outputs: 
        - ("hp_collapse", "is_open") => toggle state


- update_location_text: 
    - Info: Deals with autocomplete list for location
    - Inputs: 
        - ("hp_location_input", "value") => location
        - ({'type': 'hp_autocomplete_list_item', 'index': ALL}, 'n_clicks') => item from auto-complete list
    - State: None
    - Outputs: 
        - ("hp_autocomplete_list","children")=> items in auto-complete list
        - ("hp_location_input","value") => value of location

- hp_update_map: 
    - Info: deals with initial inputs and map updates for centre, zoom and dash components like nodes and circle.
    - Inputs: 
        - ('hp_all_nodes_button', 'n_clicks') => all nodes button
    - State: 
        - (component_id='hp_location_input', component_property='value') => location value
        - (component_id='hp_radius_input', component_property='value') => radius value
    - Outputs: 
        -(component_id='num_all_nodes_div', component_property='children') => Div output
        - (component_id='dl_hp_all_nodes', component_property='children') => leaflet component all nodes
        - ("dl_hp_circle", "children") => leaflet component of circle
        - (component_id='hp_result_map', component_property='center') => map centre
        - (component_id='hp_result_map', component_property='zoom') => map zoom

## Eco-Routing

----

- update_location_text: 
    - Info: Deals with auto-complete list
    - Inputs: 
        - ("er_location_input", "value") => location value
        - ({'type': 'er_autocomplete_list_item', 'index': ALL}, 'n_clicks') => input from auto-complete list
    - State: None
    - Outputs: 
        - ("er_autocomplete_list","children") => auto-complete list value
        - ("er_location_input","value") => location value

- hp_update_map: 
    - Info: Deals with initial input including location, radius and cs which alters in result map ans well as input map along with their dash leaflet components.
    - Inputs: 
        - ('er_all_nodes_button', 'n_clicks') => all nodes button
    - State: 
        - (component_id='er_location_input', component_property='value') => location input 
        - (component_id='er_radius_input', component_property='value') => radius input
        - (component_id='er_no_of_cs_input', component_property='value') => number of charging stations input.
    - Outputs: 
        - (component_id='er_num_all_nodes_div', component_property='children') => Text box for number of nodes
        - (component_id='dl_er_all_nodes', component_property='children') => dash leaflet component for all nodes
        - (component_id='dl_er_cs_nodes', component_property='children') => dash leaflet component for all cs nodes
        - ("dl_er_circle", "children") => dash leaflet component for zoom circle
        - (component_id='er_result_map', component_property='center') => centre for result map
        - (component_id='er_result_map', component_property='zoom') => zoom for result map
        - (component_id='dl_er_input_all_nodes', component_property='children') => dash leaflet component for input map for all nodes
        - (component_id='dl_er_input_cs_nodes', component_property='children') => dash leaflet component for input map for all cs nodes
        - ("dl_er_input_circle", "children") => input map circle
        - (component_id='er_input_map', component_property='center') => input map centre
        - (component_id='er_input_map', component_property='zoom') => input map zoom
        - (component_id='cs_input_table', component_property='options') => input multi table cs input options.

- er_input_ev: 
    - Info: Taking input about ev like how many query, which cs, initial charge, capacity etc.
    - Inputs: 
        - ('er_vehicles_button', 'n_clicks') => input vechiles button
    - State: 
        - (component_id='er_no_of_vehicles_input', component_property='value') => number of ev paths
        - (component_id='cs_input_table', component_property='value') => list of selected cs inputs
        - (component_id='er_inital_charge', component_property='value') => initial charge value
        - (component_id='er_ev_capacity', component_property='value') => initial capacity value
    - Outputs: 
        - (component_id='er_num_all_ev', component_property='children') => text box for number of ev
        - (component_id='er_ev_input_dropdown', component_property='options') => drowdown options for src dst input for input map
        - (component_id='ev_sdinput_table', component_property='options') => options for all nodes dropdown for input map
        - (component_id='dl_er_input_cs_selected_nodes', component_property='children') => all selected cs nodes dash leaflet component
        - (component_id='dl_er_output_cs_selected_nodes', component_property='children') => all selected cs input dash leaflet component for output map
        - (component_id='dl_er_cs_output_cs_selected_nodes', component_property='children') => all selected cs input dash leaflet component for output cs map

- er_update_inputs: 
    - Info: Deals with scr-dst input for ev in input map and showing them on map and updating in table.
    - Inputs: 
        - ('er_ev_input_dropdown', 'value') => Input based on drowdown value
        - ('er_sd_input_button', 'n_clicks') => push the current state in input-output
        - ('er_input_map', 'click_lat_lng') => input based on map click
    - State: 
        - (component_id='ev_sdinput_table', component_property='value') => which src or dst we are talking about
    - Outputs: 
        - (component_id='dl_er_input_selected_nodes', component_property='children') => dash leaflet component to show selected nodes.
        - (component_id='ev_sdoutput_table', component_property='data') => display current src-dst configuration in table
        - (component_id='er_ev_input_dropdown', component_property='value') => updating dropdown value based on map click


- generate_paths: 
    - Info: Deals with displaying simple paths based on which ev and which best path. Shows paths, nodes. Deals with inputs from generate paths, generate selected paths, and to toggle dropdown of available paths for an ev.
    - Inputs: 
        - ('er_generate_paths_button', 'n_clicks') => to run algo in subprocess and generate all data.
        - ('ev_path_table', 'value') => Input based on which ev is selected.
        - ('er_generate_selected_path_button', 'n_clicks') => to display selected path on click
    - State: 
        - ('ev_path_index_table', 'value') => Selected ev in first dropdown.
    - Outputs: 
        - (component_id='dl_er_output_all_nodes', component_property='children') => Display all nodes
        - ("dl_er_output_circle", "children") => display circle
        - (component_id='er_output_map', component_property='center') => centre for output map
        - (component_id='er_output_map', component_property='zoom') => zoom for output map
        - (component_id='dl_er_output_path', component_property='children') => Display path
        - (component_id='dl_er_output_path_nodes', component_property='children') => display all nodes in path
        - (component_id='ev_path_table', component_property='options') => Change number of path options based on ev value
        - (component_id='ev_path_index_table', component_property='options') => Output all paths value in second dropdown.
        - (component_id='ev_sd_input_validation', component_property='children') => Validation for sd input when generate paths is clicked.

- generate_possible_paths: 
    - Info:  Deals with displaying simple paths based on which ev and which best path. Shows paths, nodes. Deals with inputs from generate paths, generate selected paths, and to toggle dropdown of available paths for an ev. All this is for cs_output_graph.
    - Inputs: 
        - Input('er_generate_paths_button', 'n_clicks') => to run algo in subprocess and generate all data.
        - ('ev_cs_path_table', 'value') => Input based on which ev is selected.
        - ('er_cs_generate_selected_path_button', 'n_clicks') => to display selected path on click
    - State: 
        - ('ev_cs_path_index_table', 'value') => Selected ev in first dropdown.
    - Outputs: 
        - (component_id='dl_er_cs_output_all_nodes', component_property='children') => Display all nodes
        - ("dl_er_cs_output_circle", "children")  => display circle
        - (component_id='er_cs_output_map', component_property='center') => display map centre
        - (component_id='er_cs_output_map', component_property='zoom') => display map zoom
        - (component_id='dl_er_cs_output_path', component_property='children') => display dash leaflet component for path
        - (component_id='dl_er_cs_output_path_nodes', component_property='children') => display dash leaflet component for all nodes in path
        - (component_id='ev_cs_path_table', component_property='options') => display options for all ev
        - (component_id='ev_cs_path_index_table', component_property='options') => display options for all available paths
        - (component_id='ev_cs_path_info', component_property='children') => display path information.

