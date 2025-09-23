from dash import html, dcc
import dash_leaflet as dl
import dash_bootstrap_components as dbc
from components.tile_layers import tile_layers

BASE_EDIT_CONTROL = dl.EditControl(
    id="base_edit_control",
    draw={"rectangle": True, "polygon": False, "polyline": False,
          "circle": False, "marker": False, "circlemarker": False},
    edit={"edit": False, "remove": True}
    )

LIVE_EDIT_CONTROL = dl.EditControl(
    id="live_edit_control",
    draw={"rectangle": False, "polygon": False, "polyline": False,
          "circle": False, "marker": False, "circlemarker": False},
    edit={"edit": False, "remove": False}
    )

LIVE_MEASURE_CONTROL = dl.MeasureControl(
    position="topright",
    primaryLengthUnit="kilometers",
    primaryAreaUnit="hectares",
    activeColor="#7ED9D0",
    completedColor="#25A1A9",
    )

# BASE MAP FOR SELECTION
def base_map():
    # Initiate empty GeoJSON
    return dl.Map(
        [
            dl.TileLayer(id="basemap"),
            dl.FeatureGroup(id='edit_control',
                            children=[BASE_EDIT_CONTROL]),
            dl.LayerGroup(id="selected-rectangle-layer"),
            dl.LayerGroup(id="ship-layer")
            ],
        id="map",
        className="base-map",
        center=[30, 0],
        zoom = 3
        )


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
                        html.Span("""IMPORTANT ! Your area must not exceed 100,000,000 ha.""", className='initial-modal-important'),
                        html.Br(),
                        html.Span("""Equivalent to a rectangle drawn around France.""", className='initial-modal-sub-important'),
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
            dbc.ModalHeader("🚤 Valid area selected 🚤", close_button=False, className='confirmation-modal-header'),
            dbc.ModalBody(id="confirmation-popup-body", className='confirmation-modal-body'),
            dbc.ModalFooter([
                html.Div([
                    dbc.Button("OK", id="btn-ok", className='confirmation-modal-ok-button'),
                    dbc.Button("REDRAW", id="btn-redraw", className='confirmation-modal-redraw-button')
                ], className='confirmation-modal-button-div'),
                ], className='confirmation-modal-footer')
            ],
        id="confirmation-modal",
        is_open=False,
        backdrop="static",
        keyboard=False,
        centered=True,
        class_name='confirmation-modal'
        )

 
# ERROR POPUP
def error_popup():
    return dbc.Modal(
        [
            dbc.ModalHeader("🦈 Oops ... Too large Area ! 🦈", close_button=False, className='error-modal-header'),
            dbc.ModalBody(id="error-popup-body", className='error-modal-body'),
            dbc.ModalFooter([
                html.Div([
                    html.Span("--------------------------", className='error-button-span'),
                    dbc.Button(" REDRAW ", id="btn-error-redraw", className='error-modal-redraw-button'),
                    html.Span("--------------------------", className='error-button-span')
                    ], className='error-modal-button-div'),
            ], className='error-modal-footer')
            ],
        id="error-modal",
        is_open=False,
        backdrop="static",
        keyboard=False,
        centered=True,
        class_name='error-modal'
        )
