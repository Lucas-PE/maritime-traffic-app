from dash import (
    Output, 
    Input, 
    callback, 
    html, 
    exceptions, 
    callback_context, 
    no_update, 
    clientside_callback,
    ctx,
    State
)
from components.tile_layers import tile_layers
from functions.utils import (
    polygon_to_bounding_box
)
import dash_leaflet as dl
import asyncio
import threading

  
# 1. INITIAL POPUP
# Change map background on dropdown change
@callback(
    Output("basemap", "url"),
    Input("basemap-dropdown", "value"),
)
def change_basemap(layer_name):
    return tile_layers[layer_name]


# Close initial modal on select + select DRAW RECTANGLE
clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) {
            return [window.dash_clientside.no_update, ""];
        }

        var rectBtn = document.querySelector('.leaflet-draw-draw-rectangle');
        if (rectBtn) {
            rectBtn.click();
        }

        return [false, ""];  // close modal and dummy output
    }
    """,
    [Output("initial-modal", "is_open"), Output("dummy-initial", "data")],
    Input("btn-select", "n_clicks"),
)

# 2. CONFIRMATION POPUP
# CONFIRMATION POPUP :
@callback(
    Output("confirmation-modal", "is_open"),
    Output("rectangle-coords-display", "children"),
    Output("last-drawn-bbox", "data"),
    Output("confirmed-bbox", "data"),
    Input("edit_control", "geojson"),
    Input("btn-ok", "n_clicks"),
    Input("btn-redraw", "n_clicks"),
    State("last-drawn-bbox", "data"),
    prevent_initial_call=True,
)
def confirmation_popup(polygon_coords, ok_click, redraw_click, last_bbox):
    triggered = ctx.triggered_id

    if triggered == "edit_control":
        if not polygon_coords or not polygon_coords.get("features"):
            raise exceptions.PreventUpdate
        
        features = polygon_coords["features"]
        # Do not update if the polygon is empty !
        if not features or "geometry" not in features[-1]:
            raise exceptions.PreventUpdate
        
        coords = polygon_coords["features"][-1]["geometry"]["coordinates"]
        bbox = polygon_to_bounding_box(coords)
        return True, html.Pre(str(bbox)), bbox, no_update

    elif triggered == "btn-redraw":
        return False, no_update, None, None

    elif triggered == "btn-ok":
        return False, no_update, no_update, last_bbox

    raise exceptions.PreventUpdate


# Clear the selected rectangle on Redraw click and on confirmation !
@callback(
    Output("edit_control", "editToolbar"),
    Input("btn-redraw", "n_clicks"),
    Input("confirmed-bbox", "data"),
    prevent_initial_call=True
)
def clear_all_shapes(n, bbox):
    return dict(mode="remove", action="clear all", n_clicks=n)


# REAL TIME MAP
@callback(
    Output("edit_control", "draw"),
    Output("edit_control", "edit"),
    Output("map", "viewport"),
    Output("selected-rectangle-layer", "children"),
    Input("confirmed-bbox", "data"),
    prevent_initial_call=True
)
def update_map(bbox):
    from functions.ais_streamer import (clear_json,
                                        stream_ais_position,
                                        stream_ais_static,
                                        stop_event
                                        )
    if bbox == None:
        raise exceptions.PreventUpdate
    
    if bbox != None:
        
        # SET ALL DRAW AND EDIT TO FALSE
        draw_config = {
            "rectangle": False,
            "polygon": False,
            "polyline": False,
            "circle": False,
            "marker": False,
            "circlemarker": False
            }
        
        edit_config = {
            "edit": False,
            "remove": False
            }
        
        # DRAW THE SELECTED RECTANGLE
        rectangle = dl.Rectangle(
            bounds=bbox,
            color="blue",
            weight=2,
            fillOpacity=0.1,
            fillColor="blue"
            )
        
        # FLY TO THE SELECTED RECTANGLE
        viewport = {
            "bounds": bbox,
            "transition": "flyToBounds",
            "options": {
                "animate": True,
                "duration": 1.8,
                "padding": [20, 20]
                }
            }
        
        # WEBSOCKET PROCESS :
        POSITION_JSON_PATH = "src/data/raw/ais_position.json"
        STATIC_JSON_PATH = "src/data/raw/ais_static.json"
        
        async def run_websockets_loop():
            await asyncio.gather(
                stream_ais_position(bbox=bbox, position_json_path=POSITION_JSON_PATH),
                stream_ais_static(bbox=bbox, static_json_path=STATIC_JSON_PATH)
                )
            
        def run_loop():
            asyncio.run(run_websockets_loop())
        
        try:
        # 1 : clear JSON
            clear_json(STATIC_JSON_PATH, POSITION_JSON_PATH)
            print("WebSocket thread started. Collecting data...")
        
        # 2. Start the WebSocket listener in background thread
            stop_event.clear()
            t = threading.Thread(target=run_loop, daemon=True)
            t.start()
        
    
        except KeyboardInterrupt:
            print("Interrupted. Shutting down.")
        
        return (
            draw_config,
            edit_config,
            viewport, 
            [rectangle]
            )

# UPDATE THE SHIP LAYER EVERY 2 SECONDS