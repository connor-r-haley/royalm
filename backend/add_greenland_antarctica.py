import json
import math

def distance(p1, p2):
    """Calculate distance between two points"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def douglas_peucker(points, epsilon):
    """Douglas-Peucker line simplification algorithm"""
    if len(points) <= 2:
        return points
    
    # Find the point with the maximum distance
    max_dist = 0
    max_idx = 0
    
    for i in range(1, len(points) - 1):
        dist = point_to_line_distance(points[i], points[0], points[-1])
        if dist > max_dist:
            max_dist = dist
            max_idx = i
    
    # If max distance is greater than epsilon, recursively simplify
    if max_dist > epsilon:
        # Recursive call
        rec_results1 = douglas_peucker(points[:max_idx + 1], epsilon)
        rec_results2 = douglas_peucker(points[max_idx:], epsilon)
        
        # Combine the results
        return rec_results1[:-1] + rec_results2
    else:
        # All points in between are too close, so remove them
        return [points[0], points[-1]]

def point_to_line_distance(point, line_start, line_end):
    """Calculate distance from point to line segment"""
    if line_start == line_end:
        return distance(point, line_start)
    
    # Calculate the distance
    numerator = abs((line_end[1] - line_start[1]) * point[0] - 
                   (line_end[0] - line_start[0]) * point[1] + 
                   line_end[0] * line_start[1] - line_end[1] * line_start[0])
    denominator = distance(line_start, line_end)
    
    return numerator / denominator

def simplify_geometry_ultra_quality(geometry, tolerance=0.02):
    """Simplify geometry with ultra-high quality preservation"""
    if geometry['type'] == 'Polygon':
        simplified_coords = []
        for ring in geometry['coordinates']:
            if len(ring) > 2:
                simplified_ring = douglas_peucker(ring, tolerance)
                simplified_coords.append(simplified_ring)
            else:
                simplified_coords.append(ring)
        return {
            'type': 'Polygon',
            'coordinates': simplified_coords
        }
    elif geometry['type'] == 'MultiPolygon':
        simplified_polygons = []
        for polygon in geometry['coordinates']:
            simplified_polygon = []
            for ring in polygon:
                if len(ring) > 2:
                    simplified_ring = douglas_peucker(ring, tolerance)
                    simplified_polygon.append(simplified_ring)
                else:
                    simplified_polygon.append(ring)
            simplified_polygons.append(simplified_polygon)
        return {
            'type': 'MultiPolygon',
            'coordinates': simplified_polygons
        }
    return geometry

def get_faction_for_territory(territory_name, mother_country):
    """Assign faction based on mother country"""
    if mother_country in ['US', 'Canada', 'United Kingdom', 'France', 'Germany', 'Italy', 'Japan', 'South Korea', 'Australia', 'New Zealand']:
        return "US"
    elif mother_country in ['Russia', 'China', 'Iran', 'North Korea']:
        return "RU"
    else:
        return "NEUTRAL"

def add_greenland_antarctica():
    """Add Greenland and split Antarctica into territorial claims"""
    try:
        # Load the current all countries data
        with open('all-countries-fixed-codes.json', 'r') as f:
            data = json.load(f)
        
        print("Adding Greenland and Antarctica territories...")
        
        # Load the original world data to get Greenland and Antarctica
        with open('world-countries.json', 'r') as f:
            world_data = json.load(f)
        
        features = world_data.get("features", [])
        new_features = []
        
        # Find Greenland
        greenland_feature = None
        antarctica_features = []
        
        for feature in features:
            props = feature.get("properties", {})
            name = props.get("name", "").lower()
            
            if 'greenland' in name:
                greenland_feature = feature
            elif 'antarctica' in name or 'antarctic' in name:
                antarctica_features.append(feature)
        
        # Add Greenland
        if greenland_feature:
            simplified_geometry = simplify_geometry_ultra_quality(greenland_feature['geometry'], tolerance=0.02)
            greenland_new = {
                "type": "Feature",
                "properties": {
                    "id": "GL",
                    "name": "Greenland",
                    "faction": "US",  # Greenland is part of Denmark (NATO)
                    "morale": 0.7,
                    "mother_country": "Denmark"
                },
                "geometry": simplified_geometry
            }
            new_features.append(greenland_new)
            print("✓ Added Greenland")
        
        # Define Antarctica territorial claims
        antarctica_claims = [
            {
                "id": "AQ-AR",
                "name": "Argentine Antarctica",
                "mother_country": "Argentina",
                "faction": "NEUTRAL",
                "coordinates": [[-74, -60], [-25, -60], [-25, -90], [-74, -90], [-74, -60]]
            },
            {
                "id": "AQ-AU",
                "name": "Australian Antarctic Territory", 
                "mother_country": "Australia",
                "faction": "US",
                "coordinates": [[45, -60], [160, -60], [160, -90], [45, -90], [45, -60]]
            },
            {
                "id": "AQ-CH",
                "name": "Chilean Antarctic Territory",
                "mother_country": "Chile", 
                "faction": "NEUTRAL",
                "coordinates": [[-90, -60], [-53, -60], [-53, -90], [-90, -90], [-90, -60]]
            },
            {
                "id": "AQ-FR",
                "name": "Adélie Land",
                "mother_country": "France",
                "faction": "US",
                "coordinates": [[136, -60], [142, -60], [142, -90], [136, -90], [136, -60]]
            },
            {
                "id": "AQ-NZ",
                "name": "Ross Dependency",
                "mother_country": "New Zealand",
                "faction": "US",
                "coordinates": [[160, -60], [180, -60], [180, -90], [160, -90], [160, -60]]
            },
            {
                "id": "AQ-NO",
                "name": "Queen Maud Land",
                "mother_country": "Norway",
                "faction": "US",
                "coordinates": [[-20, -60], [45, -60], [45, -90], [-20, -90], [-20, -60]]
            },
            {
                "id": "AQ-UK",
                "name": "British Antarctic Territory",
                "mother_country": "United Kingdom",
                "faction": "US",
                "coordinates": [[-80, -60], [-20, -60], [-20, -90], [-80, -90], [-80, -60]]
            }
        ]
        
        # Add Antarctica territories
        for claim in antarctica_claims:
            antarctica_territory = {
                "type": "Feature",
                "properties": {
                    "id": claim["id"],
                    "name": claim["name"],
                    "faction": claim["faction"],
                    "morale": 0.6,  # Lower morale due to harsh conditions
                    "mother_country": claim["mother_country"]
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [claim["coordinates"]]
                }
            }
            new_features.append(antarctica_territory)
            print(f"✓ Added {claim['name']}")
        
        # Add new features to existing data
        data['features'].extend(new_features)
        
        # Save updated data
        with open('all-countries-with-territories.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nAdded {len(new_features)} new territories")
        print(f"Total countries/territories: {len(data['features'])}")
        print("Saved to: all-countries-with-territories.json")
        
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    add_greenland_antarctica() 