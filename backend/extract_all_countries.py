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

def get_faction_for_country(country_name):
    """Assign faction based on country name"""
    country_lower = country_name.lower()
    
    # US Allies
    us_allies = [
        'united states', 'canada', 'united kingdom', 'france', 'germany', 'italy', 
        'japan', 'south korea', 'australia', 'new zealand', 'netherlands', 'belgium',
        'norway', 'denmark', 'sweden', 'finland', 'poland', 'czech', 'slovakia',
        'hungary', 'romania', 'bulgaria', 'greece', 'portugal', 'spain', 'ireland',
        'iceland', 'luxembourg', 'estonia', 'latvia', 'lithuania', 'slovenia',
        'croatia', 'montenegro', 'albania', 'north macedonia', 'kosovo', 'bosnia',
        'serbia', 'ukraine', 'moldova', 'georgia', 'armenia', 'azerbaijan'
    ]
    
    # Russia/China Allies
    ru_allies = [
        'russia', 'china', 'iran', 'north korea', 'cuba', 'venezuela', 'nicaragua',
        'belarus', 'kazakhstan', 'kyrgyzstan', 'tajikistan', 'uzbekistan', 'turkmenistan',
        'syria', 'iraq', 'yemen', 'libya', 'sudan', 'south sudan', 'central african republic',
        'mali', 'burkina faso', 'niger', 'chad', 'congo', 'angola', 'zimbabwe',
        'madagascar', 'comoros', 'seychelles', 'mauritius'
    ]
    
    # Check for matches
    for ally in us_allies:
        if ally in country_lower:
            return "US"
    
    for ally in ru_allies:
        if ally in country_lower:
            return "RU"
    
    # Default to neutral
    return "NEUTRAL"

def extract_all_countries():
    """Extract ALL world countries with ultra-high quality borders"""
    try:
        # Load the comprehensive world data
        with open('world-countries.json', 'r') as f:
            world_data = json.load(f)
        
        features = world_data.get("features", [])
        extracted_features = []
        
        print(f"Processing {len(features)} countries...")
        
        total_points_before = 0
        total_points_after = 0
        
        for i, feature in enumerate(features):
            if i % 50 == 0:
                print(f"Processing country {i+1}/{len(features)}...")
            
            props = feature.get("properties", {})
            country_name = props.get("name", "Unknown")
            
            # Skip territories and dependencies
            if any(skip in country_name.lower() for skip in [
                'territory', 'dependency', 'minor outlying', 'virgin islands',
                'french polynesia', 'new caledonia', 'greenland', 'faroe islands',
                'bermuda', 'cayman islands', 'british virgin islands', 'anguilla',
                'montserrat', 'turks and caicos', 'falkland islands', 'south georgia',
                'pitcairn islands', 'tokelau', 'niue', 'cook islands', 'american samoa',
                'guam', 'northern mariana islands', 'puerto rico', 'aruba', 'curacao',
                'sint maarten', 'saint martin', 'saint barthelemy', 'mayotte', 'reunion',
                'french guiana', 'martinique', 'guadeloupe', 'saint pierre and miquelon',
                'wallis and futuna', 'saint helena', 'ascension', 'tristan da cunha',
                'gibraltar', 'isle of man', 'jersey', 'guernsey', 'aland islands',
                'svalbard', 'jan mayen', 'bouvet island', 'heard island', 'mcdonald islands',
                'norfolk island', 'christmas island', 'cocos islands', 'ashmore and cartier',
                'coral sea islands', 'heard island', 'mcdonald islands', 'australian antarctic',
                'french southern', 'british indian ocean', 'south sandwich', 'south orkney',
                'south shetland', 'peter i island', 'queen maud land', 'ross dependency',
                'australian antarctic', 'chilean antarctic', 'argentine antarctic'
            ]):
                continue
            
            # Count original points
            original_geometry = feature['geometry']
            if original_geometry['type'] == 'Polygon':
                for ring in original_geometry['coordinates']:
                    total_points_before += len(ring)
            elif original_geometry['type'] == 'MultiPolygon':
                for polygon in original_geometry['coordinates']:
                    for ring in polygon:
                        total_points_before += len(ring)
            
            # Simplify with ultra-high quality
            simplified_geometry = simplify_geometry_ultra_quality(original_geometry, tolerance=0.02)
            
            # Count simplified points
            if simplified_geometry['type'] == 'Polygon':
                for ring in simplified_geometry['coordinates']:
                    total_points_after += len(ring)
            elif simplified_geometry['type'] == 'MultiPolygon':
                for polygon in simplified_geometry['coordinates']:
                    for ring in polygon:
                        total_points_after += len(ring)
            
            # Create country code (use first 2 letters of country name)
            country_code = country_name[:2].upper()
            if len(country_code) < 2:
                country_code = country_name[:3].upper()
            
            # Create new feature
            new_feature = {
                "type": "Feature",
                "properties": {
                    "id": country_code,
                    "name": country_name,
                    "faction": get_faction_for_country(country_name),
                    "morale": 0.7  # Default morale
                },
                "geometry": simplified_geometry
            }
            extracted_features.append(new_feature)
        
        # Create the final GeoJSON
        result = {
            "type": "FeatureCollection",
            "features": extracted_features
        }
        
        # Save to file
        with open('all-countries-ultra-quality.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nExtracted {len(extracted_features)} countries with ultra-high quality borders")
        print(f"Points before: {total_points_before:,}")
        print(f"Points after: {total_points_after:,}")
        print(f"Reduction: {((total_points_before - total_points_after) / total_points_before * 100):.1f}%")
        print(f"File size: {len(json.dumps(result)) / 1024 / 1024:.1f} MB")
        print("Saved to: all-countries-ultra-quality.json")
        
        return result
        
    except FileNotFoundError:
        print("Error: world-countries.json not found. Please download it first.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    extract_all_countries() 