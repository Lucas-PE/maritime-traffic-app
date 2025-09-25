from dash import (
    callback, 
    Output, 
    Input, 
    no_update, 
    html, 
    ctx,
    State,
    exceptions,
    clientside_callback,
    dcc,
    ALL
)
from components.tile_layers import tile_layers
from functions.utils import (
    polygon_to_bounding_box, bounding_box_area_ha
)
import pandas as pd
import plotly.express as px

# Display Header and Offcanvas button on confirmation
@callback(
    Output("header-div", "style"),
    Output("filter-button", "style"),
    Output("tooltips-button", "style"),
    Output("footer-div", "style"),
    Input("btn-ok", "n_clicks"),
    prevent_initial_call=True
)
def display_header(ok_click):
    return {'display':'flex'}, {'display':'flex'}, {'display':'flex'}, {'display':'flex'}


# Display OffCanvas on btn or vessel click
@callback(
    Output("clicked-vessel", "data"),
    Output("tooltips-offcanvas", "is_open"),
    Output("filter-offcanvas", "is_open"),
    Input("tooltips-button", "n_clicks"),
    Input("filter-button", "n_clicks"),
    Input({"type": "vessel-marker", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_offcanvas_and_marker(tooltip_click, filter_click, marker_clicks):
    # Normalize n_clicks list for markers (None -> 0)
    marker_clicks = [n if n is not None else 0 for n in marker_clicks]

    trig = ctx.triggered_id

    if isinstance(trig, dict) and trig.get("type") == "vessel-marker" and sum(marker_clicks) > 0:
        return trig, True, False

    if trig == "tooltips-button":
        return no_update, True, False

    if trig == "filter-button":
        return no_update, False, True

    return no_update, no_update, no_update


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

# checklist filter
@callback(
    Output("status-checklist", "options"),
    Output("type-checklist", "options"),
    Input("unique-status-categories", "data"),
    prevent_initial_call=True
)
def update_checklist_options(unique_pairs):
    from functions.filters_dict import status_images, category_images
    if not unique_pairs:
        return [], []
    all_statuses = sorted({row[0] for row in unique_pairs})
    all_types = sorted({row[1] for row in unique_pairs})
    
    status_options = [
        {
            "label": [
                html.Img(src=status_images.get(s, ""), style={"height": "20px", "width": "20px", "margin-left": "10px", "margin-top":"3px", "margin-bottom":"3px"}),
                html.Span(s, style={"padding-left": "10px", "font-size": 12})
            ],
            "value": s
        }
        for s in all_statuses
    ]
    
    category_options = [
        {
            "label": [
                html.Img(src=category_images.get(s, ""), style={"height": "20px", "width": "20px", "margin-left": "10px", "margin-top":"3px", "margin-bottom":"3px"}),
                html.Span(s, style={"padding-left": "10px", "font-size": 12})
            ],
            "value": s
        }
        for s in all_types
    ]

    return status_options, category_options


# Store the filters
@callback(
    Output('filtered-status', 'data'),
    Output('filtered-category', 'data'),
    Input("status-checklist", "value"),
    Input("type-checklist", "value"),
    prevent_initial_call=True
)
def store_filters(filtered_status, filtered_category):
    stored_status = []
    stored_category = []
    
    if filtered_status:
        stored_status.extend(filtered_status)
    
    if filtered_category:
        stored_category.extend(filtered_category)
    
    return stored_status, stored_category


# "Select all" filters
clientside_callback(
    """
    function(selectAllValue, allOptions) {
        // If 'Select All' is checked, return all options
        if (selectAllValue.includes("All")) {
            return allOptions.map(o => o.value);
        }
        // If not, return an empty list
        return [];
    }
    """,
    Output("status-checklist", "value"),
    Input("select-all-status", "value"),
    [State("status-checklist", "options")]
)

clientside_callback(
    """
    function(selectAllValue, allOptions) {
        // If 'Select All' is checked, return all options
        if (selectAllValue.includes("All")) {
            return allOptions.map(o => o.value);
        }
        // If not, return an empty list
        return [];
    }
    """,
    Output("type-checklist", "value"),
    Input("select-all-category", "value"),
    [State("type-checklist", "options")]
)


# GET AND DISPLAY DATA OF CLICKED VESSEL
@callback(
    Output("tooltips-offcanvas", "children"),
    Input("clicked-vessel", "data"),
    prevent_initial_call=True
)
def display_clicked_vessel(clicked_id):
    if clicked_id is None:
        return html.Span("Click on any vessel to display detailed information.")
    
    if clicked_id:
        # Get the MMSI in the ID
        MMSI = clicked_id.get('index').split('-')[1]
        MMSI = int(MMSI)
        
        # GET ALL ENTRIES FOR THE CLICKED MMSI
        try:
            df_position = pd.read_json("src/data/raw/ais_position.json")
        except:
            return no_update
        
        df_types = pd.read_csv("src/data/raw/ais_ShipTypes.csv", sep=";")
        df_status = pd.read_csv("src/data/raw/ais_NavigationStatus.csv", sep=";")
        
        clicked_df_position = df_position[df_position["MMSI"] == MMSI]

        df_static = pd.read_json("src/data/raw/ais_static.json")
        if df_static.empty:
            df_static = pd.DataFrame(columns=['timestamp', 'MMSI', 'Destination', 'Dimension', 'Eta', 'Type'])
        clicked_df_static = df_static[df_static["MMSI"] == MMSI]
        clicked_df_static = df_static.sort_values("timestamp").drop_duplicates("MMSI", keep="last")
        
        clicked_df_position['timestamp'] = pd.to_datetime(clicked_df_position['timestamp'].str.replace('UTC', ''), format='ISO8601').dt.floor('s')
        clicked_df_static['timestamp'] = pd.to_datetime(clicked_df_static['timestamp'].str.replace('UTC', ''), format='ISO8601').dt.floor('s')
        
        # Join Navigation Status to position
        clicked_df_position = pd.merge(clicked_df_position, df_status, on='NavigationalStatus', how='left')
        # Add the Ship Type string
        clicked_df_static = pd.merge(clicked_df_static, df_types, on='Type', how='left')
        # Calculate Lenght and Width
        clicked_df_static["Length"] = clicked_df_static["Dimension"].apply(lambda x: x.get("A", 0) + x.get("B", 0))
        clicked_df_static["Width"] = clicked_df_static["Dimension"].apply(lambda x: x.get("C", 0) + x.get("D", 0))
        
        final_clicked_mmsi = pd.merge(clicked_df_position, clicked_df_static, on='MMSI', how='left', suffixes = ('_position', '_static'))
        final_clicked_mmsi = final_clicked_mmsi.fillna('Unknown')
        
        latest_clicked_mmsi = final_clicked_mmsi.sort_values("timestamp_position").drop_duplicates("MMSI", keep="last")
        
        if latest_clicked_mmsi.Eta.iloc[0] == "Unknown":
            ETA = html.Span("Unknown", className="tooltip-displayed-info")
        else:
            ETA = html.Span(f"""
                            {latest_clicked_mmsi.Eta.iloc[0]['Month']} Month(s),
                            {latest_clicked_mmsi.Eta.iloc[0]['Day']} Day(s),
                            {latest_clicked_mmsi.Eta.iloc[0]['Hour']} Hour(s),
                            {latest_clicked_mmsi.Eta.iloc[0]['Minute']} Minute(s),""", 
                            className="tooltip-displayed-info")
        
        if latest_clicked_mmsi.SOG.iloc[0] == "Unknown":
            SOG = html.Span("Unknown", className="tooltip-displayed-info")
        if latest_clicked_mmsi.SOG.iloc[0] == 0:
            SOG = html.Span("Unknown", className="tooltip-displayed-info")
        else:
            SOG = dcc.Graph(
                id='sog-evolution',
                figure= px.bar(
                    final_clicked_mmsi,
                    x="timestamp_position", 
                    y="SOG",
                    title=None,
                    labels={"timestamp_position": "Time", "SOG": "Speed over Ground (knots)"},
                    height=350,
                    color_discrete_sequence=["#F2DDD0"]
                    ).update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    ),
                    className='sog-fig'
                )
        
        # BUILD THE DIV
        # Montrer sog evolution avec un graph
        displayed_tooltip = html.Div([
            html.Span("Additionnal information on vessels are sent every 6 minutes.", className='tooltip-info-italic'),
            html.Br(),
            html.Br(),           
            html.Span(f"{latest_clicked_mmsi.MMSI.iloc[0]} - {latest_clicked_mmsi.ShipName.iloc[0]}", className='tooltip-mmsi-name'),
            html.Br(), 
            html.Br(),             
            html.Span("Navigational Status", className="tooltip-sub-titles"),
            html.Span(latest_clicked_mmsi["Status Description"].iloc[0], className="tooltip-displayed-info"),
            html.Span("Category", className="tooltip-sub-titles"),
            html.Span(latest_clicked_mmsi.Category.iloc[0], className="tooltip-displayed-info"),
            html.Span("Destination", className="tooltip-sub-titles"),
            html.Span(latest_clicked_mmsi.Destination.iloc[0], className="tooltip-displayed-info"),
            html.Span("Estimated Time of Arrival", className="tooltip-sub-titles"),
            ETA,
            html.Span("Rate of Turn", className="tooltip-sub-titles"),
            html.Span(latest_clicked_mmsi.RateOfTurn.iloc[0], className="tooltip-displayed-info"),
            html.Span("Lenght - Width", className="tooltip-sub-titles"),
            html.Span(f"{latest_clicked_mmsi.Length.iloc[0]} m. - {latest_clicked_mmsi.Width.iloc[0]} m.", className="tooltip-displayed-info"),
            html.Span("(SOG) Speed Evolution", className="tooltip-sub-titles"),
            SOG
            ], className='clicked-tooltip-div')
        
        return displayed_tooltip
    

# Display footer kpis
@callback(
    Output('footer-counts', 'children'),
    Input('displayed-rows-count', 'data'),
    Input('df-unique-vessels', 'data')
)
def footer_kpis(total_rows, unique_vessels):
    return html.Div([
        html.Span(total_rows, className='footer-count'),
        html.Span("points displayed ---", className='footer-count-description'),
        html.Span(unique_vessels, className='footer-count'),
        html.Span("unique vessels", className='footer-count-description')
    ])   
