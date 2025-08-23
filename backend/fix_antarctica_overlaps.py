import json
import math

def fix_antarctica_overlaps():
    """Fix overlapping Antarctica territories by creating non-overlapping slices"""
    
    # Load the original world data to get the real Antarctica geometry
    try:
        with open('world-countries.json', 'r') as f:
            world_data = json.load(f)
    except FileNotFoundError:
        print("Error: world-countries.json not found")
        return None
    
    # Find Antarctica in the original data
    antarctica_feature = None
    for feature in world_data.get("features", []):
        props = feature.get("properties", {})
        name = props.get("name", "").lower()
        if 'antarctica' in name:
            antarctica_feature = feature
            break
    
    if not antarctica_feature:
        print("Error: Antarctica not found in world data")
        return None
    
    print("Found real Antarctica geometry")
    
    # Load current data
    try:
        with open('all-countries-antarctica-real.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: all-countries-antarctica-real.json not found")
        return None
    
    # Remove old Antarctica territories
    data['features'] = [f for f in data['features'] if not f['properties']['id'].startswith('AQ-')]
    
    print("Removed old overlapping Antarctica territories")
    
    # Get the real Antarctica geometry
    antarctica_geometry = antarctica_feature['geometry']
    
    # Define NON-OVERLAPPING territorial claims as longitude ranges
    # Resolving disputes by giving priority to first claimants and creating clear boundaries
    territorial_claims = [
        {
            "id": "AQ-CH",
            "name": "Chilean Antarctic Territory", 
            "mother_country": "Chile",
            "faction": "NEUTRAL",
            "description": "Chilean Antarctic Territory (claimed by Chile)",
            "longitude_range": [-90, -74]  # 74°W to 90°W (Chile gets the tip)
        },
        {
            "id": "AQ-AR",
            "name": "Argentine Antarctica",
            "mother_country": "Argentina",
            "faction": "NEUTRAL",
            "description": "Argentine Antarctic Territory (claimed by Argentina)",
            "longitude_range": [-74, -25]  # 25°W to 74°W (Argentina gets the main peninsula)
        },
        {
            "id": "AQ-UK",
            "name": "British Antarctic Territory",
            "mother_country": "United Kingdom",
            "faction": "US",
            "description": "British Antarctic Territory (claimed by UK)",
            "longitude_range": [-25, -20]  # 20°W to 25°W (UK gets small slice)
        },
        {
            "id": "AQ-NO",
            "name": "Queen Maud Land",
            "mother_country": "Norway",
            "faction": "US",
            "description": "Queen Maud Land (claimed by Norway)",
            "longitude_range": [-20, 45]  # 20°W to 45°E (Norway gets Atlantic sector)
        },
        {
            "id": "AQ-AU", 
            "name": "Australian Antarctic Territory",
            "mother_country": "Australia",
            "faction": "US",
            "description": "Australian Antarctic Territory (claimed by Australia)",
            "longitude_range": [45, 136]  # 45°E to 136°E (Australia gets Indian Ocean sector)
        },
        {
            "id": "AQ-FR",
            "name": "Adélie Land",
            "mother_country": "France",
            "faction": "US",
            "description": "Adélie Land (claimed by France)",
            "longitude_range": [136, 142]  # 136°E to 142°E (France gets small slice)
        },
        {
            "id": "AQ-NZ",
            "name": "Ross Dependency",
            "mother_country": "New Zealand",
            "faction": "US",
            "description": "Ross Dependency (claimed by New Zealand)",
            "longitude_range": [142, 180]  # 142°E to 180°E (NZ gets Pacific sector)
        }
    ]
    
    def clip_geometry_to_longitude_range(geometry, min_lon, max_lon):
        """Clip Antarctica geometry to a specific longitude range"""
        if geometry['type'] == 'Polygon':
            clipped_coords = []
            for ring in geometry['coordinates']:
                clipped_ring = []
                for point in ring:
                    lon, lat = point
                    if min_lon <= lon <= max_lon:
                        clipped_ring.append(point)
                
                if len(clipped_ring) >= 3:
                    clipped_coords.append(clipped_ring)
            
            if clipped_coords:
                return {
                    'type': 'Polygon',
                    'coordinates': clipped_coords
                }
        
        elif geometry['type'] == 'MultiPolygon':
            clipped_polygons = []
            for polygon in geometry['coordinates']:
                clipped_polygon = []
                for ring in polygon:
                    clipped_ring = []
                    for point in ring:
                        lon, lat = point
                        if min_lon <= lon <= max_lon:
                            clipped_ring.append(point)
                    
                    if len(clipped_ring) >= 3:
                        clipped_polygon.append(clipped_ring)
                
                if clipped_polygon:
                    clipped_polygons.append(clipped_polygon)
            
            if clipped_polygons:
                return {
                    'type': 'MultiPolygon',
                    'coordinates': clipped_polygons
                }
        
        return None
    
    # Create territories by clipping Antarctica to longitude ranges
    for claim in territorial_claims:
        min_lon, max_lon = claim['longitude_range']
        clipped_geometry = clip_geometry_to_longitude_range(antarctica_geometry, min_lon, max_lon)
        
        if clipped_geometry:
            antarctica_territory = {
                "type": "Feature",
                "properties": {
                    "id": claim["id"],
                    "name": claim["name"],
                    "faction": claim["faction"],
                    "morale": 0.6,
                    "mother_country": claim["mother_country"],
                    "description": claim["description"]
                },
                "geometry": clipped_geometry
            }
            
            data['features'].append(antarctica_territory)
            print(f"✓ Added {claim['name']} (longitude {min_lon}° to {max_lon}°)")
        else:
            print(f"⚠ No geometry found for {claim['name']}")
    
    # Save updated data
    with open('all-countries-antarctica-fixed.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nFixed Antarctica territories - no overlaps!")
    print(f"Total countries/territories: {len(data['features'])}")
    print("Saved to: all-countries-antarctica-fixed.json")
    
    return data

if __name__ == "__main__":
    fix_antarctica_overlaps() 