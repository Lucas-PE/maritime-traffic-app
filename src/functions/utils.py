
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