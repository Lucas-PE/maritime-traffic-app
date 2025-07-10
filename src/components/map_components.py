from dash import html
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
            dbc.ModalHeader("Rectangle Selection", close_button=False),
            dbc.ModalBody([
                html.P("First Choose your map layout :"),
                dbc.Select(
                    id="basemap-dropdown",
                    options=[{"label": name, "value": name} for name in tile_layers.keys()],
                    value="CartoDB Light"
                    ),
                html.P("Then click on select and draw a rectangle"),
                dbc.Button("Select", id="btn-select", color="primary"),
                ]),
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
