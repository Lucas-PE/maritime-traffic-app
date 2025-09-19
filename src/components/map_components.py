from dash import html, dcc
import dash_leaflet as dl
import dash_bootstrap_components as dbc
from components.tile_layers import tile_layers

# BASE MAP FOR SELECTION
def base_map():
    # Initiate empty GeoJSON
    return dl.Map(
        [
            dl.TileLayer(id="basemap"),
            dl.FeatureGroup([
                dl.EditControl(
                    id="edit_control",
                    draw={"rectangle": True, "polygon": False, "polyline": False,
                          "circle": False, "marker": False, "circlemarker": False},
                    edit={"edit": False, "remove": True}
                    ),
                ]),
            dl.LayerGroup(id="selected-rectangle-layer"),
            dl.LayerGroup(id="ship-layer")
            ],
        id="map",
        className="base-map",
        center=[30, 0],
        zoom = 3
        )

  
# MAP FOR REAL TIME DATA


# INITIAL POPUP
def initial_popup():
    return dbc.Modal(
        [
            dbc.ModalHeader("""🛟 Welcome to Another Maritime Traffic App 🛟""", close_button=False, class_name='initial-modal-header'),
            dbc.ModalBody(
                [
                    html.Div(["Heed the instructions below, sailor, and the seas will treat you kindly !"], className='initial-modal-catchphrase'),
                    html.Div(["1. Choose your map layout :"]),
                    dcc.Dropdown(
                        id='basemap-dropdown',
                        options=[{"label": name, "value": name} for name in tile_layers.keys()],
                        value="CartoDB Light",
                        clearable=False,
                        className='initial-modal-select'
                        ),
                    html.Div([
                        """2. Click on "START SAILING" and draw a rectangle.""",
                        html.Br(),
                        html.Br(),
                        "The Websocket will start and display the real-time maritime traffic in your zone.",
                        html.Br(),
                        html.Br(),
                        html.Span("Additionnal information on vessels are not available as soon as their position.", className='initial-modal-info')
                        ], className='initial-modal-second-step'),
                    html.Div([
                        html.Span("---------------------", className='button-span'),
                        dbc.Button("START SAILING", id="btn-select", color="primary", className='initial-modal-button'),
                        html.Span("---------------------", className='button-span'),
                    ], className='initial-modal-button-div')
                    ],
                class_name='initial-modal-body'
                ),
            ],
        id="initial-modal",
        is_open=True,  
        backdrop="static",
        keyboard=False,
        centered=True,
        class_name="initial-modal"
        )


# CONFIRMATION POPUP
def confirmation_popup():
    return dbc.Modal(
        [
            dbc.ModalHeader("Rectangle Coordinates", close_button=False),
            dbc.ModalBody(id="rectangle-coords-display"),
            dbc.ModalFooter([
                dbc.Button("OK", id="btn-ok", color="success", className="me-2"),
                dbc.Button("Redraw", id="btn-redraw", color="danger")
                ])
            ],
        id="confirmation-modal",
        is_open=False,
        backdrop="static",
        keyboard=False,
        centered=True,
        class_name='confirmation-modal'
        )
