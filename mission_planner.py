import numpy as np

def generate_lawnmower_path(json_data):
    coords = json_data["polygon_coordinates"]
    alt = json_data["target_altitude_m"]
    
    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    lat_step = 0.0004 
    lon_step = 0.0005
    
    waypoints = []
    lat_range = np.arange(min_lat, max_lat, lat_step)
    lon_range = np.arange(min_lon, max_lon, lon_step)
    
    flip = False
    for lon in lon_range:
        current_lats = lat_range[::-1] if flip else lat_range
        for lat in current_lats:
            waypoints.append((lat, lon, alt))
        flip = not flip
        
    return waypoints
