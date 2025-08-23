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

def create_antarctica_territories():
    """Create proper Antarctica territorial claims based on real boundaries"""
    
    # Real Antarctica territorial claims with proper boundaries
    # These are based on actual territorial claims and the Antarctic Treaty
    # Note: Some claims overlap, but we'll create non-overlapping divisions
    antarctica_territories = [
        {
            "id": "AQ-AR",
            "name": "Argentine Antarctica",
            "mother_country": "Argentina",
            "faction": "NEUTRAL",
            "description": "Argentine Antarctic Territory (claimed by Argentina)",
            # Argentine claim: 25°W to 74°W, south of 60°S
            "coordinates": [
                [-74, -60], [-25, -60], [-25, -90], [-74, -90], [-74, -60]
            ]
        },
        {
            "id": "AQ-CH",
            "name": "Chilean Antarctic Territory", 
            "mother_country": "Chile",
            "faction": "NEUTRAL",
            "description": "Chilean Antarctic Territory (claimed by Chile)",
            # Chilean claim: 53°W to 90°W, south of 60°S
            "coordinates": [
                [-90, -60], [-74, -60], [-74, -90], [-90, -90], [-90, -60]
            ]
        },
        {
            "id": "AQ-UK",
            "name": "British Antarctic Territory",
            "mother_country": "United Kingdom",
            "faction": "US",
            "description": "British Antarctic Territory (claimed by UK)",
            # British claim: 20°W to 80°W, south of 60°S
            "coordinates": [
                [-80, -60], [-25, -60], [-25, -90], [-80, -90], [-80, -60]
            ]
        },
        {
            "id": "AQ-NO",
            "name": "Queen Maud Land",
            "mother_country": "Norway",
            "faction": "US",
            "description": "Queen Maud Land (claimed by Norway)",
            # Norwegian claim: 20°W to 45°E, south of 60°S
            "coordinates": [
                [-20, -60], [45, -60], [45, -90], [-20, -90], [-20, -60]
            ]
        },
        {
            "id": "AQ-AU", 
            "name": "Australian Antarctic Territory",
            "mother_country": "Australia",
            "faction": "US",
            "description": "Australian Antarctic Territory (claimed by Australia)",
            # Australian claim: 45°E to 160°E, south of 60°S
            "coordinates": [
                [45, -60], [160, -60], [160, -90], [45, -90], [45, -60]
            ]
        },
        {
            "id": "AQ-FR",
            "name": "Adélie Land",
            "mother_country": "France",
            "faction": "US",
            "description": "Adélie Land (claimed by France)",
            # French claim: 136°E to 142°E, south of 60°S
            "coordinates": [
                [136, -60], [142, -60], [142, -90], [136, -90], [136, -60]
            ]
        },
        {
            "id": "AQ-NZ",
            "name": "Ross Dependency",
            "mother_country": "New Zealand",
            "faction": "US",
            "description": "Ross Dependency (claimed by New Zealand)",
            # New Zealand claim: 160°E to 150°W, south of 60°S
            "coordinates": [
                [160, -60], [180, -60], [180, -90], [150, -90], [150, -60], [160, -60]
            ]
        }
    ]
    
    # Load the current data
    try:
        with open('all-countries-with-territories.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: all-countries-with-territories.json not found")
        return None
    
    # Remove old Antarctica territories (those starting with AQ-)
    data['features'] = [f for f in data['features'] if not f['properties']['id'].startswith('AQ-')]
    
    print("Removed old Antarctica territories")
    
    # Add new properly divided Antarctica territories
    for territory in antarctica_territories:
        antarctica_territory = {
            "type": "Feature",
            "properties": {
                "id": territory["id"],
                "name": territory["name"],
                "faction": territory["faction"],
                "morale": 0.6,  # Lower morale due to harsh conditions
                "mother_country": territory["mother_country"],
                "description": territory["description"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [territory["coordinates"]]
            }
        }
        
        data['features'].append(antarctica_territory)
        print(f"✓ Added {territory['name']}")
    
    # Save updated data
    with open('all-countries-antarctica-fixed.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nUpdated Antarctica territories")
    print(f"Total countries/territories: {len(data['features'])}")
    print("Saved to: all-countries-antarctica-fixed.json")
    
    return data

if __name__ == "__main__":
    create_antarctica_territories() 