import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash import dcc
from dash import html
from homepage import Homepage
from homepage_actions import *
from eco_routing_layout import eco_routing_layout
from osmnx_test import osmnx_layout
from csp_layout import csp_layout
from eco_routing_actions import *
from documentation import Documentation
from server import app



@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/charging_station_placement':
        return csp_layout()
    elif pathname == '/eco_routing':
        return eco_routing_layout()
    elif pathname == '/documentation':
        return Documentation()  
    elif pathname == '/osmnx':
        return osmnx_layout()
    else:
        return Homepage()


if __name__ == "__main__":
    app.run_server(debug = True)
    app.config.suppress_callback_exceptions=True