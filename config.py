import pandas as pd

num_of_tot_nodes = 0
num_of_ev = 0
ev_options = None
ev_dropdown = pd.DataFrame(columns = ['label','value','title'])
ev_sdinput = pd.DataFrame(columns = ['vehicle_id','node_id'])
positions = 0
output_positions = []
polygon = []
center = None
zoomLevel = 0
table_of_ev_inputs = pd.DataFrame(columns = ['label','value','title'])
path_inputs = pd.DataFrame(columns = ['label','value'])
location = None