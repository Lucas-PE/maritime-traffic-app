
# Convert leaflet coordinates selection into bounding box
def polygon_to_bounding_box(nested_polygon_coords):
    """
    Converts [[[lon, lat], ...]] to [[[lat_min, lon_min], [lat_max, lon_max]]]
    """
    polygon_coords = nested_polygon_coords[0]  # extract inner list

    # Extract latitudes and longitudes separately
    lats = [coord[1] for coord in polygon_coords]
    lons = [coord[0] for coord in polygon_coords]

    lat_min = min(lats)
    lat_max = max(lats)
    lon_min = min(lons)
    lon_max = max(lons)

    return [[[lat_min, lon_min], [lat_max, lon_max]]]


# Get center from rectangle bbox
def get_center(confirmed_bbox):
    print(confirmed_bbox)
    
    bounds = confirmed_bbox
    
    center_lat = (bounds[0][0][0] + bounds[0][1][0]) / 2
    center_lon = (bounds[0][0][1] + bounds[0][1][1]) / 2
    center = [center_lat, center_lon]
    
    return center