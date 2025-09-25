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
                       html.Span("Check an element to hide it :", className='filter-span'),
                       html.Br(),
                       html.Br(),
                       html.H6("Navigational Status", className='filter-sub-header'),
                       dcc.Checklist(
                           id="select-all-status",
                           options=[{"label": html.Span("Hide All", style={"padding-left": "10px", 
                                                                             "font-size": 14, 
                                                                             "margin-top":"5px", 
                                                                             "margin-bottom":"5px",
                                                                             "color":"#D5F2E8"}), "value": "All"}],
                           value=[],
                           labelStyle={"display": "flex", "align-items": "center"},
                           className='select-all-status'
                           ),
                       dcc.Checklist(
                           id="status-checklist",
                           options=[],
                           value=[],
                           labelStyle={"display": "flex", "align-items": "center"},
                           className='status-checklist'
                           ),
                       html.Br(),
                       html.H6("Vessel Category", className='filter-sub-header'),
                       dcc.Checklist(
                           id="select-all-category",
                           options=[{"label": html.Span("Hide All", style={"padding-left": "10px", 
                                                                             "font-size": 14, 
                                                                             "margin-top":"5px", 
                                                                             "margin-bottom":"5px",
                                                                             "color":"#D5F2E8"}), "value": "All"}],
                           value=[],
                           labelStyle={"display": "flex", "align-items": "center"},
                           className='select-all-category'
                           ),
                       dcc.Checklist(
                           id="type-checklist",
                           options=[],
                           value=[],
                           labelStyle={"display": "flex", "align-items": "center"},
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
                children=[],
                title="VESSEL INFORMATION",
                placement='start',
                is_open=False,
                backdrop=False,
                scrollable=True,
                class_name='tooltips-offcanvas' 
            )    
        ], className='tooltips-offcanvas-div'
    )
    
def footer():
    return html.Div(
        id='footer-div',
        children=
        [
            html.Span("Refresh the page to select a new area", className="footer-info"),
            html.Div(
                id='footer-counts',
                children=[],
                className='footer-counts'
            ),
            html.Div(
                id='href-div',
                children=[
                    html.Div([
                        html.Span("WebSocket provided by", className="footer-href1-info"),
                        html.A("aisstream.io", href='https://aisstream.io/', target="_blank", className="footer-href1"),
                        ], className="aisstream-href-div"
                    ),
                    html.Div([
                        html.Span("Source code available", className="footer-href2-info"),
                        html.A("here", href="https://github.com/Lucas-PE/maritime-traffic-app", target="_blank", className="footer-href2")
                        ], className="github-href-div"
                    )
                    ], className='href-div'
                )
            ], className='footer-div'
        )