import dash
from dash import html, dcc
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.tile_layers import tile_layers
from components.map_components import (
    base_map,
    initial_popup,
    confirmation_popup
)

dash.register_page(__name__, path='/map', name = "MAP")

def layout():
    return html.Div([
        
        html.Div(id="dummy-exit-signal", style={"display": "none"}),
        
        dcc.Store('dummy-initial'),
        dcc.Store("confirmed-bbox", data=None, storage_type='memory'),
        dcc.Store("last-drawn-bbox", data=None, storage_type='memory'),
        dcc.Store('dummy-confirmation'),
        
        # Build the ships layer every 2 seconds
        dcc.Interval(id="ship-layer-interval", 
                     interval=2000, 
                     n_intervals=0, 
                     disabled=True
                     ),
        
        # Base map
        base_map(),
        
        # Initial popup
        initial_popup(),
        
        # Confirmation Popup
        confirmation_popup()
        
        ])
