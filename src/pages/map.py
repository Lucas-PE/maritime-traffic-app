import dash
from dash import html
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.tile_layers import tile_layers

dash.register_page(__name__, path='/map', name = "MAP")

def layout():
    return html.Div([
        dl.Map(
            [
                dl.TileLayer(id="basemap"),
                dl.FeatureGroup([
                    dl.EditControl(
                        id="edit_control",
                        draw={"rectangle": True, "polygon": False, "polyline": False,
                              "circle": False, "marker": False, "circlemarker": False},
                        edit={"edit": False}
                        )
                    ])
                ],
            id="map",
            className="base-map",
            center=[30, 0],
            zoom = 3
            ),
        
        # Initial popup
        dbc.Modal(
            [
                dbc.ModalHeader("Rectangle Selection"),
                dbc.ModalBody([
                    html.P("First Choose your map layout :"),
                    dbc.Select(
                            id="basemap-dropdown",
                            options=[{"label": name, "value": name} for name in tile_layers.keys()],
                            value="CartoDB Light"
                            ),
                    html.P("Then click on sleect and draw a rectangle"),
                    dbc.Button("Select", id="btn-select", color="primary", className="me-2"),
                ]),
                ],
            id="initial-modal",
            is_open=True,  # Open on app start
            backdrop="static",  # Prevent closing by clicking outside
            keyboard=False,     # Prevent closing by Esc key
            centered=True,
            class_name="initial-modal"
            ),
        
        # Confirmation Popup, after rectangle is drawn
        dbc.Modal(
            [
                dbc.ModalHeader("Rectangle Coordinates"),
                dbc.ModalBody(id="rectangle-coords-display"),
                dbc.ModalFooter([
                    dbc.Button("OK", id="btn-ok", color="success", className="me-2"),
                    dbc.Button("Redraw", id="btn-redraw", color="danger")
                    ])
                ],
            id="coords-modal",
            is_open=False,
            backdrop="static",
            keyboard=False,
            )
        ])
