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

   
def filter_offcanvas():
    return html.Div(
        id='filter-offcanvas-div',
        children=
        [
            dbc.Button("⏷     FILTERS     ⏷", 
                       id="filter-button",
                       className="filter-button"
                       ),
            dbc.Offcanvas(
                id='filter-offcanvas',
                children=[
                   html.Div([
                       html.Span("Check any element to hide it :"),
                       html.Br(),
                       html.Br(),
                       html.H6("Navigational Status"),
                       dcc.Checklist(
                           id="status-checklist",
                           options=[],
                           value=[],
                           labelStyle={"display": "block"},
                           className='status-checklist'
                           ),
                       html.Br(),
                       html.H6("Vessel Category"),
                       dcc.Checklist(
                           id="type-checklist",
                           options=[],
                           value=[],
                           className='type-checklist'
                           )
                       ], className='checklist-div')
                ],
                title="FILTERS",
                placement='end',
                is_open=False,
                backdrop=False,
                scrollable=True,
                class_name='filter-offcanvas' 
            )    
        ], className='filter-offcanvas-div'
    )


def tooltips_offcanvas():
    return html.Div(
        id='tooltips-offcanvas-div',
        children=
        [
            dbc.Button("⏷     TOOLTIP     ⏷", 
                       id="tooltips-button",
                       className="tooltips-button"
                       ),
            dbc.Offcanvas(
                id='tooltips-offcanvas',
                children=[
                   html.Span("tooltips here") 
                ],
                title="VESSEL INFORMATION",
                placement='start',
                is_open=False,
                backdrop=False,
                scrollable=True,
                class_name='tooltips-offcanvas' 
            )    
        ], className='tooltips-offcanvas-div'
    )