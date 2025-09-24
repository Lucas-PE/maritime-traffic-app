from dash import (
    callback, 
    Output, 
    Input, 
    no_update, 
    html, 
    ctx,
    State,
    exceptions,
    clientside_callback
)
from components.tile_layers import tile_layers
from functions.utils import (
    polygon_to_bounding_box, bounding_box_area_ha
)
import pandas as pd

# Display Header and Offcanvas button on confirmation
@callback(
    Output("header-div", "style"),
    Output("filter-button", "style"),
    Output("tooltips-button", "style"),
    Input("btn-ok", "n_clicks"),
    prevent_initial_call=True
)
def display_header(ok_click):
    return {'display':'flex'}, {'display':'flex'}, {'display':'flex'}


# Display OffCanvas on btn click
@callback(
    Output('tooltips-offcanvas', 'is_open'),
    Output('filter-offcanvas', 'is_open'),
    Input("tooltips-button", "n_clicks"),
    Input("filter-button", "n_clicks")  
)
def open_offcanvas(tooltip_click, filter_click):
    if ctx.triggered_id == 'tooltips-button':
        return True, False
    if ctx.triggered_id == 'filter-button':
        return False, True
    else:
        return no_update, no_update


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
    from functions.filters_dict import status_images
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

    return status_options, all_types

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