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

def create_ultra_quality_borders():
    """Create ultra-high quality borders with minimal simplification"""
    try:
        # Load the real borders
        with open('wwiii-countries-real.json', 'r') as f:
            data = json.load(f)
        
        print("Creating ultra-high quality borders...")
        
        ultra_quality_features = []
        total_points_before = 0
        total_points_after = 0
        
        for feature in data['features']:
            original_geometry = feature['geometry']
            
            # Count original points
            if original_geometry['type'] == 'Polygon':
                for ring in original_geometry['coordinates']:
                    total_points_before += len(ring)
            elif original_geometry['type'] == 'MultiPolygon':
                for polygon in original_geometry['coordinates']:
                    for ring in polygon:
                        total_points_before += len(ring)
            
            # Simplify with ultra-high quality (very small tolerance)
            ultra_quality_geometry = simplify_geometry_ultra_quality(original_geometry, tolerance=0.02)
            
            # Count ultra-quality points
            if ultra_quality_geometry['type'] == 'Polygon':
                for ring in ultra_quality_geometry['coordinates']:
                    total_points_after += len(ring)
            elif ultra_quality_geometry['type'] == 'MultiPolygon':
                for polygon in ultra_quality_geometry['coordinates']:
                    for ring in polygon:
                        total_points_after += len(ring)
            
            # Create ultra-quality feature
            ultra_quality_feature = {
                'type': 'Feature',
                'properties': feature['properties'],
                'geometry': ultra_quality_geometry
            }
            ultra_quality_features.append(ultra_quality_feature)
        
        # Create ultra-quality GeoJSON
        ultra_quality_data = {
            'type': 'FeatureCollection',
            'features': ultra_quality_features
        }
        
        # Save ultra-quality version
        with open('wwiii-countries-ultra-quality.json', 'w') as f:
            json.dump(ultra_quality_data, f, indent=2)
        
        print(f"Ultra-high quality borders created!")
        print(f"Points before: {total_points_before:,}")
        print(f"Points after: {total_points_after:,}")
        print(f"Reduction: {((total_points_before - total_points_after) / total_points_before * 100):.1f}%")
        print(f"File size: {len(json.dumps(ultra_quality_data)) / 1024 / 1024:.1f} MB")
        
        return ultra_quality_data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    create_ultra_quality_borders() 