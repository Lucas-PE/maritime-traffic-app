from dash import html, dcc
import dash_bootstrap_components as dbc
from components.tile_layers import tile_layers

def header():
    return html.Div(
        id='header-div',
        children=
        [
            dcc.Dropdown(
                id='header-tile-dropdown',
                placeholder="Change Map Layout",
                options=[{"label": name, "value": name} for name in tile_layers.keys()],
                clearable=False,
                className='header-tile-dropdown'
                ),
            html.Span("ANOTHER MARITIME TRAFFIC APP", className='header-title'),
            dbc.Button("Center view", 
                       id="header-center-button",
                       className="header-center-button"
                       )
            ], className='header-div'
        )