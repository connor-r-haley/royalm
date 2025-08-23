import json
import sys

def simplify_coordinates(coords, tolerance=0.1):
    """Simplify coordinates using Douglas-Peucker algorithm (simplified version)"""
    if len(coords) <= 2:
        return coords
    
    # Simple decimation - take every nth point
    step = max(1, len(coords) // 50)  # Keep max 50 points per polygon
    return coords[::step]

def optimize_geometry(geometry):
    """Optimize geometry by simplifying coordinates"""
    if geometry['type'] == 'Polygon':
        optimized_coords = []
        for ring in geometry['coordinates']:
            optimized_ring = simplify_coordinates(ring)
            optimized_coords.append(optimized_ring)
        return {
            'type': 'Polygon',
            'coordinates': optimized_coords
        }
    elif geometry['type'] == 'MultiPolygon':
        optimized_polygons = []
        for polygon in geometry['coordinates']:
            optimized_rings = []
            for ring in polygon:
                optimized_ring = simplify_coordinates(ring)
                optimized_rings.append(optimized_ring)
            optimized_polygons.append(optimized_rings)
        return {
            'type': 'MultiPolygon',
            'coordinates': optimized_polygons
        }
    else:
        return geometry

def optimize_countries():
    """Optimize the WWIII countries GeoJSON for web performance"""
    
    # Load the processed countries data
    with open('wwiii-countries.json', 'r') as f:
        countries_data = json.load(f)
    
    # Optimize each feature
    optimized_features = []
    
    for feature in countries_data['features']:
        optimized_feature = {
            "type": "Feature",
            "properties": feature['properties'],
            "geometry": optimize_geometry(feature['geometry'])
        }
        optimized_features.append(optimized_feature)
    
    # Create the optimized GeoJSON
    optimized_countries = {
        "type": "FeatureCollection",
        "features": optimized_features
    }
    
    # Save to file
    with open('wwiii-countries-optimized.json', 'w') as f:
        json.dump(optimized_countries, f, indent=2)
    
    print(f"Optimized {len(optimized_features)} countries")
    print("Saved to wwiii-countries-optimized.json")
    
    return optimized_countries

if __name__ == "__main__":
    optimize_countries() 