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
    confirmation_popup,
    error_popup
)
from components.nav_components import (
    header,
    filter_offcanvas,
    tooltips_offcanvas
)

dash.register_page(__name__, path='/map', name = "MAP")

def layout():
    return html.Div([
        
        html.Div(id="dummy-exit-signal", style={"display": "none"}),
        
        dcc.Store('dummy-initial'),
        dcc.Store("confirmed-bbox", data=None, storage_type='memory'),
        dcc.Store("last-drawn-bbox", data=None, storage_type='memory'),
        dcc.Store("redraw-trigger", data=None, storage_type='memory'),
        dcc.Store("df-build-time", data=None, storage_type='memory'),
        dcc.Store("df-rows-count", data=None, storage_type='memory'),
        dcc.Store("unique-status-categories", data=None, storage_type='memory'),
        dcc.Store("filtered-status", data=None, storage_type='memory'),
        dcc.Store("filtered-category", data=None, storage_type='memory'),
        dcc.Store("clicked-vessel", data=None, storage_type='memory'),
        dcc.Store('dummy-confirmation'),
        
        # Build the ships layer every 2 seconds
        dcc.Interval(id="ship-layer-interval", 
                     interval=2000, 
                     n_intervals=0, 
                     disabled=True
                     ),
        
        # Header
        header(),
        
        # Filter Offcanvas
        filter_offcanvas(),
        
        # Tooltip Offcanvas
        tooltips_offcanvas(),
        
        # Base map
        base_map(),
        
        # Initial popup
        initial_popup(),
        
        # Confirmation Popup
        confirmation_popup(),
        
        # Error popup
        error_popup()
        
        ])
