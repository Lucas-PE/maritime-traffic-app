from dash import Output, Input, callback, html, exceptions, callback_context, no_update
from components.tile_layers import tile_layers

# Change map background on dropdown change
@callback(
    Output("basemap", "url"),
    Input("basemap-dropdown", "value"),
)
def change_basemap(layer_name):
    return tile_layers[layer_name]


# Close initial modal on select
@callback(
    Output("initial-modal", "is_open"),
    Input("btn-select", "n_clicks"),
    prevent_initial_call=True,
)
def close_initial_modal(_):
    return False


# Handle rectangle drawn: show coords modal
@callback(
    Output("coords-modal", "is_open"),
    Output("rectangle-coords-display", "children"),
    Input("edit_control", "geojson"),
    prevent_initial_call=True,
)
def display_rectangle_coords(geojson):
    if not geojson or not geojson.get("features"):
        raise exceptions.PreventUpdate
    coords = geojson["features"][-1]["geometry"]["coordinates"]
    return True, html.Pre(str(coords))


# Handle "OK" and "Redraw" buttons on coords modal
@callback(
    Output("edit_control", "geojson"),
    Input("btn-ok", "n_clicks"),
    Input("btn-redraw", "n_clicks"),
    prevent_initial_call=True,
)
def handle_coords_modal(btn_ok, btn_redraw):
    triggered = callback_context.triggered_id
    if triggered == "btn-ok":
        return no_update
    elif triggered == "btn-redraw":
        # Clear drawn shapes by setting empty geojson
        return {"type": "FeatureCollection", "features": []}
    raise exceptions.PreventUpdate