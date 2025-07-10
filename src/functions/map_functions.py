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
    State,
    get_asset_url
)
from components.tile_layers import tile_layers
from functions.utils import (
    polygon_to_bounding_box
)
import dash_leaflet as dl
import asyncio
import threading
import pandas as pd
import time
import os

ASSET_ICON_DIR = "src/assets/vessels_png"
DEFAULT_ICON = None
  
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
    Output("ship-layer-interval", "disabled"),
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
            weight=1,
            fillOpacity=0.05,
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
            draw_config, # Disable draw
            edit_config, # Disable delete
            viewport, # Zoom on bbox
            [rectangle], # Draw the rectangle
            False # Enable the ship layer interval
            )


# UPDATE THE SHIP LAYER EVERY 2 SECONDS
@callback(
    Output("ship-layer", "children"),
    Input("ship-layer-interval", "n_intervals"),
    prevent_initial_call = True
)
def update_ship_layer(n_intervals):
    
    start_time = time.time()
    
    # 1. Fetch the data
    df_position = pd.read_json("src/data/raw/ais_position.json")
    if df_position.empty:
        df_position = pd.DataFrame(columns=['timestamp', 'MMSI', 'ShipName', 'lat', 'lon', 'COG',
                                            'NavigationalStatus', 'RateOfTurn', 'SOG', 'Spare', 'UserID'])
        
    df_static = pd.read_json("src/data/raw/ais_static.json")
    if df_static.empty:
        df_static = pd.DataFrame(columns=['timestamp', 'MMSI', 'Destination', 'Dimension', 'Eta', 'Type'])
    
    df_types = pd.read_csv("src/data/raw/ais_ShipTypes.csv", sep=";")
    df_status = pd.read_csv("src/data/raw/ais_NavigationStatus.csv", sep=";")

    df_static['timestamp'] = pd.to_datetime(df_static['timestamp'].str.replace('UTC', ''), format='ISO8601').dt.floor('s')
    df_position['timestamp'] = pd.to_datetime(df_position['timestamp'].str.replace('UTC', ''), format='ISO8601').dt.floor('s')
    
    # 2. Transform data
    # Keep LATEST MMSI static data
    df_static_latest = df_static.sort_values("timestamp").drop_duplicates("MMSI", keep="last")
    # Add the Ship Type string
    df_static_latest = pd.merge(df_static_latest, df_types, on='Type', how='left')
    # Calculate Lenght and Width
    df_static_latest["Length"] = df_static_latest["Dimension"].apply(lambda x: x.get("A", 0) + x.get("B", 0))
    df_static_latest["Width"] = df_static_latest["Dimension"].apply(lambda x: x.get("C", 0) + x.get("D", 0))

    # Join Navigation Status to position
    df_position_final = pd.merge(df_position, df_status, on='NavigationalStatus', how='left')

    # final_df
    final_df = pd.merge(df_position_final, df_static_latest, on='MMSI', how='left', suffixes = ('_position', '_static'))
    
    # 3. Build markers & lines
    
    markers = []
    lines = []
    
    for key, group in final_df.groupby(['MMSI', 'ShipName']):
        group_sorted = group.sort_values('timestamp_position')

        # Create lines
        latlngs = group_sorted[['lat', 'lon']].values.tolist()
        lines.append(dl.Polyline(
            positions=latlngs,
            color='white',
            weight=2,
            children=[
                dl.Tooltip(f"{key[1]} (MMSI: {key[0]}) Track")
            ]
        ))

        # Create marker with popup
        for _, row in group_sorted.iterrows():
            # Get the png
            category = str(row.get("Category", "") or "").replace(" ", "_")
            status = str(row.get("Status Description", "") or "").replace(" ", "_")
            icon_filename = f"{category}_{status}.png"
            icon_path = os.path.join(ASSET_ICON_DIR, icon_filename)

            if os.path.exists(icon_path):
                icon_url = get_asset_url(f"vessels_png/{icon_filename}")
                icon = {
                    "iconUrl": icon_url,
                    "iconSize": [16, 16],  # Adjust as needed
                    "iconAnchor": [16, 16]
                }
            else:
                icon = DEFAULT_ICON
            
            tooltip_content = html.Div([
                html.B(f"{row['MMSI']} - {row['ShipName']}"), html.Br(),
                f"Category: {row['Category']}", html.Br(),
                f"Status: {row['Status Description']}", html.Br(),
                f"Destination: {row['Destination']}", html.Br(),
                f"Position at: {row['timestamp_position']}"
            ])
            markers.append(dl.Marker(
                position=(row['lat'], row['lon']),
                icon=icon,
                children=[
                    dl.Tooltip(tooltip_content)
                ]
            ))
    
    print("--- %s seconds ---" % (time.time() - start_time))
    
    return markers + lines
