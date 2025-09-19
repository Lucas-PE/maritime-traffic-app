import math

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


# Get the bbox area
def bounding_box_area_ha(bbox):
    
    (lat_min, lon_min), (lat_max, lon_max) = bbox[0]

    # Height in km
    height_km = (lat_max - lat_min) * 111.0

    # Width in km (adjusted for latitude)
    mean_lat = (lat_max + lat_min) / 2.0
    width_km = (lon_max - lon_min) * 111.0 * math.cos(math.radians(mean_lat))

    # Area in km²
    area_km2 = height_km * width_km

    # Convert to hectares
    area_ha = area_km2 * 100  # 1 km² = 100 ha

    return f"{round(area_ha, 2):,} ha"


# Get center from rectangle bbox
def get_center(confirmed_bbox):
    print(confirmed_bbox)
    
    bounds = confirmed_bbox
    
    center_lat = (bounds[0][0][0] + bounds[0][1][0]) / 2
    center_lon = (bounds[0][0][1] + bounds[0][1][1]) / 2
    center = [center_lat, center_lon]
    
    return center