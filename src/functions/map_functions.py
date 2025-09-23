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
    polygon_to_bounding_box, bounding_box_area_ha
)
import dash_leaflet as dl
import asyncio
import threading
import pandas as pd
import time
import os
import json
from filelock import FileLock

ASSET_ICON_DIR = "src/assets/colored_vessels_png"
DEFAULT_ICON = "src/assets/colored_vessels_png/Unknown_Not defined_(default).png"

# Display Header on confirmation
@callback(
    Output("header-div", "style"),
    Input("btn-ok", "n_clicks"),
    prevent_initial_call=True
)
def display_header(ok_click):
    return {'display':'flex'}

# Change map background on dropdown change
@callback(
    Output("basemap", "url"),
    Input("basemap-dropdown", "value"),
    Input("header-tile-dropdown", "value")
)
def change_basemap(layer_name_base, layer_name_live):
    if layer_name_live is None:
        return tile_layers[layer_name_base]
    else:
        return tile_layers[layer_name_live]


# SELECT LEAFLET "DRAW RECTANGLE" ON INITIAL SELECT AND REDRAW
clientside_callback(
    """
    function(counter) {
        // ignore initial call
        if (!counter) return window.dash_clientside.no_update;

        // store last counter to avoid repeated triggers
        if (!window._last_redraw_counter) window._last_redraw_counter = 0;
        if (counter <= window._last_redraw_counter) return window.dash_clientside.no_update;
        window._last_redraw_counter = counter;

        // wait a short time to avoid race with map updates / clearing shapes
        setTimeout(function() {
            var btn = document.querySelector('.leaflet-draw-draw-rectangle') ||
                      document.querySelector('[class*="leaflet-draw-draw-rectangle"]') ||
                      document.querySelector('.leaflet-control-draw .leaflet-draw-draw-rectangle');

            if (btn) {
                btn.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
                btn.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
                btn.click();
            }
        }, 50);  // 50ms delay

        return window.dash_clientside.no_update;
    }
    """,
    Output("dummy-confirmation", "data"),
    Input("redraw-trigger", "data")
)

# MODALS HANDLER
# INITIAL/CONFIRMATION/ERROR MODALS :
@callback(
    Output("initial-modal", "is_open"),
    Output("confirmation-modal", "is_open"),
    Output("confirmation-popup-body", "children"),
    Output("error-modal", "is_open"),
    Output("error-popup-body", "children"),
    Output("last-drawn-bbox", "data"),
    Output("confirmed-bbox", "data"),
    Output("redraw-trigger", "data"),
    Input("base_edit_control", "geojson"),
    Input("btn-select", "n_clicks"),    
    Input("btn-ok", "n_clicks"),
    Input("btn-redraw", "n_clicks"),
    Input("btn-error-redraw", "n_clicks"),
    State("last-drawn-bbox", "data"),
    State("redraw-trigger", "data"),
    prevent_initial_call=True,
)
def confirmation_popup(polygon_coords, select_click, ok_click, redraw_click, error_redraw_click, last_bbox, redraw_trigger_value):
    triggered = ctx.triggered_id

    if triggered == "base_edit_control":
        if not polygon_coords or not polygon_coords.get("features"):
            raise exceptions.PreventUpdate
        
        features = polygon_coords["features"]
        # Do not update if the polygon is empty !
        if not features or "geometry" not in features[-1]:
            raise exceptions.PreventUpdate
        
        coords = polygon_coords["features"][-1]["geometry"]["coordinates"]
        bbox = polygon_to_bounding_box(coords)
        bbox_area = bounding_box_area_ha(bbox)
        
        confirmation_body = html.Div([
            html.Span(f"You selected an area of {bbox_area:,} ha"),
            html.Br(),
            html.Br(),
            html.Span("Press OK to start real-time maritime traffic on your zone or REDRAW to select another area.")
        ])
        
        error_body = html.Div([
            html.Span(f"You selected an area of {bbox_area:,} ha"),
            html.Br(),
            html.Br(),
            html.Span("Please Redraw a rectangle of maximum 100,000,000 ha."),
            html.Br(),
            html.Br(),
            html.Img(src='assets/selection_example.png', className='error-modal-image')
        ])
        
        if bbox_area >= 100000000:
            return False, False, None, True, error_body, bbox, no_update, no_update
        
        elif bbox_area <= 100000000:
            return False, True, confirmation_body, False, None, bbox, no_update, no_update

    elif triggered in ("btn-select", "btn-error-redraw", "btn-redraw"):
        if redraw_trigger_value is None:
            redraw_trigger_value = 0
        return False, False, None, False, None, no_update, no_update, redraw_trigger_value+1

    elif triggered == "btn-ok":
        return False, False, None, False, None, no_update, last_bbox, no_update

    raise exceptions.PreventUpdate


# Clear the selected rectangle on Redraw buttons and on confirmation !
@callback(
    Output("base_edit_control", "editToolbar"),
    Input("btn-redraw", "n_clicks"),
    Input("btn-error-redraw", "n_clicks"),
    Input("confirmed-bbox", "data"),
    prevent_initial_call=True
)
def clear_all_shapes(n, nn, bbox):
    return dict(mode="remove", action="clear all", n_clicks=n)


# REAL TIME MAP
@callback(
    Output("edit_control", "children"),
    Output("map", "viewport"),
    Output("selected-rectangle-layer", "children"),
    Output("ship-layer-interval", "disabled"),
    Input("confirmed-bbox", "data"),
    Input("header-center-button", "n_clicks"),
    prevent_initial_call=True
)
def update_map(bbox, center_button):
    from functions.ais_streamer import (clear_json,
                                        stream_ais_position,
                                        stream_ais_static,
                                        stop_event
                                        )
    from components.map_components import LIVE_EDIT_CONTROL, LIVE_MEASURE_CONTROL
    
    if bbox == None:
        raise exceptions.PreventUpdate
    
    if bbox != None:
        
        # DRAW THE SELECTED RECTANGLE
        rectangle = dl.Rectangle(
            bounds=bbox,
            color="#103A53",
            weight=1,
            fillOpacity=0.05,
            fillColor="#25A1A9"
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
        
        # CASE OF Header Center Button triggered
        if ctx.triggered_id == "header-center-button":
            return (
                no_update,
                viewport,
                no_update,
                no_update
            )
        
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
            [LIVE_EDIT_CONTROL, LIVE_MEASURE_CONTROL], # Disable draw and delete + activate measures
            viewport, # Zoom on bbox
            [rectangle], # Draw the rectangle
            False # Enable the ship layer interval
            )


# UPDATE THE SHIP LAYER EVERY 2 SECONDS
@callback(
    Output("ship-layer", "children"),
    Output("df-build-time", "data"),
    Output("df-rows-count", "data"),
    Input("ship-layer-interval", "n_intervals"),
    prevent_initial_call = True
)
def update_ship_layer(n_intervals):
    
    start_time = time.time()
    
    # 1. Fetch the data
    try:
        df_position = pd.read_json("src/data/raw/ais_position.json")
    except:
        return no_update

    if df_position.empty:
        df_position = pd.DataFrame(columns=['timestamp', 'MMSI', 'ShipName', 'lat', 'lon', 'COG',
                                            'NavigationalStatus', 'RateOfTurn', 'SOG', 'Spare', 'UserID', "Heading"])
        
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
    final_df = final_df.fillna('Unknown')
    
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
        
        # --- IMPORTANT --> ONLY DISPLAY LATEST VESSEL POSITION ---
        latest_row = group_sorted.iloc[-1]
        
        heading = latest_row.get("Heading", 0)
        # Mirror & adjust heading
        adjusted_heading = (heading - 90) % 360

        if 90 < adjusted_heading < 270:
            flip = "scaleX(-1)"
            rotated_heading = (180 - adjusted_heading) % 360
        else:
            flip = ""
            rotated_heading = adjusted_heading

        # Create marker with popup
        # Get the png
        category = str(latest_row.get("Category", "") or "").replace(" ", "_")
        status = str(latest_row.get("Status Description", "") or "").replace(" ", "_")
        icon_filename = f"{category}_{status}.png"
        icon_path = os.path.join(ASSET_ICON_DIR, icon_filename)

        if os.path.exists(icon_path):
            icon_url = get_asset_url(f"colored_vessels_png/{icon_filename}")
        else:
            icon_url = get_asset_url(f"colored_vessels_png/Unknown_Not_defined_(default).png")
        
        icon_html = f"""
            <div style="width: 21px; height: 21px; display: flex; align-items: center; justify-content: center;">
                <img src="{icon_url}" 
                    style="transform: {flip} rotate({rotated_heading}deg);
                        transform-origin: center;
                        width: 21px; height: 21px;">
            </div>
        """
        
        icon = dict(
            html=icon_html,
            className="",
            iconSize=[21, 21],
            iconAnchor=[12, 12]
            )
            
        tooltip_content = html.Div([
            html.B(f"{latest_row['MMSI']} - {latest_row['ShipName']}"), html.Br(),
            f"Category: {latest_row['Category']}", html.Br(),
            f"Status: {latest_row['Status Description']}", html.Br(),
            f"Destination: {latest_row['Destination']}", html.Br(),
            f"Position at: {latest_row['timestamp_position']}"
            ])

        markers.append(
            dl.DivMarker(
                id=f"marker-{latest_row['MMSI']}-{icon_filename}",
                position=(latest_row['lat'], latest_row['lon']),
                iconOptions=icon,
                children=[
                    dl.Tooltip(tooltip_content, className='vessel-tooltip')
                    ]
                ))
    
    # RETURN THE BUILD TIME
    build_time = round(time.time() - start_time, 2)
    
    # RETURN THE DF SIZE FOR AUTO CLEANING IF > 1,500 rows
    row_count = final_df.shape[0]
    if row_count >= 1500:
        returned_rows_count = row_count
    else:
        returned_rows_count = no_update
    
    return markers + lines, build_time, returned_rows_count


# JSON AUTO CLEAN TO DO !
@callback(
    Input("df-rows-count", "data"),
    prevent_initial_call=True
)
def json_auto_clean(df_row_count):

    json_path = "src/data/raw/ais_position.json"
    lock_path = "src/data/raw/ais_position.json.lock"
    tmp_path = json_path + ".tmp"

    with FileLock(lock_path):

        try:
            # Load JSON
            with open(json_path, "r") as f:
                records = json.load(f)

            if not isinstance(records, list) or len(records) == 0:
                no_update

            df = pd.DataFrame(records)

            # Ensure required columns exist
            required_cols = {"timestamp", "MMSI", "ShipName"}
            if not required_cols.issubset(df.columns):
                no_update

            # Keep original timestamp
            df['timestamp_orig'] = df['timestamp']

            # Convert for sorting/cleaning (remove 'UTC')
            df["timestamp"] = pd.to_datetime(
                df['timestamp'].str.replace('UTC','').str.strip(),
                errors='coerce'
            ).dt.floor('s')

            df.dropna(subset=['timestamp'], inplace=True)
            if df.empty:
                no_update

            # Sort by group and timestamp
            df.sort_values(['MMSI', 'ShipName', 'timestamp'], inplace=True)

            # Drop oldest row per group if group has more than 1 row
            cleaned_df = (
                df.groupby(['MMSI', 'ShipName'], group_keys=False)
                  .apply(lambda g: g.iloc[1:] if len(g) > 1 else g)
                  .reset_index(drop=True)
            )

            # Restore original timestamp strings
            cleaned_df['timestamp'] = cleaned_df['timestamp_orig']
            cleaned_df = cleaned_df.drop(columns=['timestamp_orig'])

            print(f"Cleaned JSON → {cleaned_df.shape[0]} rows remaining")

            # --- Atomic write ---
            with open(tmp_path, "w") as f:
                json.dump(cleaned_df.to_dict(orient='records'), f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            # Replace original JSON with temp file
            os.replace(tmp_path, json_path)

        except (json.JSONDecodeError, FileNotFoundError) as e:
            no_update
        except Exception as e:
            no_update
        finally:
            # Ensure tmp file is removed if it still exists
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
