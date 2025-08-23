import json
import sys

def aggressive_simplify(coords, max_points=20):
    """Aggressively simplify coordinates - keep only max_points"""
    if len(coords) <= max_points:
        return coords
    
    # Take evenly spaced points
    step = len(coords) // max_points
    simplified = []
    for i in range(0, len(coords), step):
        simplified.append(coords[i])
        if len(simplified) >= max_points:
            break
    
    # Always include the last point to close the polygon
    if simplified[-1] != coords[-1]:
        simplified.append(coords[-1])
    
    return simplified

def optimize_geometry_aggressive(geometry):
    """Aggressively optimize geometry by drastically reducing coordinates"""
    if geometry['type'] == 'Polygon':
        optimized_coords = []
        for ring in geometry['coordinates']:
            optimized_ring = aggressive_simplify(ring, max_points=15)
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
                optimized_ring = aggressive_simplify(ring, max_points=15)
                optimized_rings.append(optimized_ring)
            optimized_polygons.append(optimized_rings)
        return {
            'type': 'MultiPolygon',
            'coordinates': optimized_polygons
        }
    else:
        return geometry

def aggressive_optimize():
    """Aggressively optimize the WWIII countries GeoJSON for web performance"""
    
    # Load the processed countries data
    with open('wwiii-countries.json', 'r') as f:
        countries_data = json.load(f)
    
    # Optimize each feature
    optimized_features = []
    
    for feature in countries_data['features']:
        optimized_feature = {
            "type": "Feature",
            "properties": feature['properties'],
            "geometry": optimize_geometry_aggressive(feature['geometry'])
        }
        optimized_features.append(optimized_feature)
    
    # Create the optimized GeoJSON
    optimized_countries = {
        "type": "FeatureCollection",
        "features": optimized_features
    }
    
    # Save to file
    with open('wwiii-countries-web.json', 'w') as f:
        json.dump(optimized_countries, f, indent=2)
    
    print(f"Aggressively optimized {len(optimized_features)} countries")
    print("Saved to wwiii-countries-web.json")
    
    return optimized_countries

if __name__ == "__main__":
    aggressive_optimize() 