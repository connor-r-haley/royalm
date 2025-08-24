#!/usr/bin/env python3
"""
Script to mathematically divide Antarctica using actual coastline points
"""

import json
import math
from typing import List, Tuple, Dict

def load_json_file(filepath: str) -> dict:
    """Load a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_json_file(data: dict, filepath: str):
    """Save data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Saved to {filepath}")
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

def get_antarctica_coordinates(data: dict) -> List[Tuple[float, float]]:
    """Extract all coordinates from Antarctica geometry"""
    coordinates = []
    
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        name = props.get("name", "").lower()
        
        if 'antarctica' in name and 'territory' not in name:
            geometry = feature.get("geometry", {})
            if geometry.get("type") == "Polygon":
                coords = geometry["coordinates"][0]  # First ring
                coordinates.extend(coords)
            elif geometry.get("type") == "MultiPolygon":
                for polygon in geometry["coordinates"]:
                    coords = polygon[0]  # First ring of each polygon
                    coordinates.extend(coords)
            break
    
    return coordinates

def divide_antarctica_by_longitude(coordinates: List[Tuple[float, float]]) -> Dict[str, List[Tuple[float, float]]]:
    """Divide Antarctica into territorial claims based on longitude ranges"""
    
    # Define territorial claims with longitude ranges
    territories = {
        "Argentine Antarctica": {"range": (-74, -25), "coords": []},
        "Chilean Antarctic Territory": {"range": (-90, -53), "coords": []},
        "British Antarctic Territory": {"range": (-80, -20), "coords": []},
        "Queen Maud Land": {"range": (-20, 45), "coords": []},
        "Australian Antarctic Territory": {"range": (45, 160), "coords": []},
        "Adélie Land": {"range": (136, 142), "coords": []},
        "Ross Dependency": {"range": (160, -150), "coords": []}  # Wraps around
    }
    
    # Sort coordinates into territories
    for coord in coordinates:
        lng, lat = coord
        
        # Handle longitude wrapping for Ross Dependency
        if lng > 160 or lng < -150:
            territories["Ross Dependency"]["coords"].append(coord)
        else:
            # Check each territory's longitude range
            for name, territory in territories.items():
                if name != "Ross Dependency":
                    min_lng, max_lng = territory["range"]
                    if min_lng <= lng <= max_lng:
                        territory["coords"].append(coord)
                        break
    
    return territories

def create_territory_features(territories: Dict) -> List[dict]:
    """Create GeoJSON features for each territory"""
    features = []
    
    territory_data = {
        "Argentine Antarctica": {
            "id": "AQ-AR",
            "name": "Argentina Territory",
            "mother_country": "Argentina",
            "faction": "NEUTRAL",
            "description": "Argentine Antarctic Territory (claimed by Argentina)"
        },
        "Chilean Antarctic Territory": {
            "id": "AQ-CH", 
            "name": "Chile Territory",
            "mother_country": "Chile",
            "faction": "NEUTRAL",
            "description": "Chilean Antarctic Territory (claimed by Chile)"
        },
        "British Antarctic Territory": {
            "id": "AQ-UK",
            "name": "UK Territory", 
            "mother_country": "United Kingdom",
            "faction": "NATO",
            "description": "British Antarctic Territory (claimed by UK)"
        },
        "Queen Maud Land": {
            "id": "AQ-NO",
            "name": "Norway Territory",
            "mother_country": "Norway", 
            "faction": "NATO",
            "description": "Queen Maud Land (claimed by Norway)"
        },
        "Australian Antarctic Territory": {
            "id": "AQ-AU",
            "name": "Australia Territory",
            "mother_country": "Australia",
            "faction": "NATO", 
            "description": "Australian Antarctic Territory (claimed by Australia)"
        },
        "Adélie Land": {
            "id": "AQ-FR",
            "name": "France Territory",
            "mother_country": "France",
            "faction": "NATO",
            "description": "Adélie Land (claimed by France)"
        },
        "Ross Dependency": {
            "id": "AQ-NZ",
            "name": "New Zealand Territory",
            "mother_country": "New Zealand",
            "faction": "NATO",
            "description": "Ross Dependency (claimed by New Zealand)"
        }
    }
    
    for territory_name, coords in territories.items():
        if coords["coords"]:
            # Create a polygon from the coordinates
            # For simplicity, we'll create a convex hull or use the coordinates directly
            feature = {
                "type": "Feature",
                "properties": territory_data[territory_name],
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords["coords"]]
                }
            }
            features.append(feature)
    
    return features

def main():
    """Main function to divide Antarctica mathematically"""
    
    # Load the base data
    data = load_json_file('all-countries-ultra-quality.json')
    if not data:
        print("Could not load base data")
        return
    
    # Get Antarctica coordinates
    antarctica_coords = get_antarctica_coordinates(data)
    if not antarctica_coords:
        print("Could not find Antarctica coordinates")
        return
    
    print(f"Found {len(antarctica_coords)} Antarctica coordinates")
    
    # Divide Antarctica by longitude
    territories = divide_antarctica_by_longitude(antarctica_coords)
    
    # Create territory features
    territory_features = create_territory_features(territories)
    
    # Remove old Antarctica territories and add new ones
    data['features'] = [f for f in data['features'] if not f['properties']['id'].startswith('AQ-')]
    data['features'].extend(territory_features)
    
    print(f"Created {len(territory_features)} Antarctica territories")
    
    # Save the result
    save_json_file(data, 'all-countries-antarctica-math.json')
    
    # Also copy to frontend
    import shutil
    shutil.copy('all-countries-antarctica-math.json', '../frontend/public/all-countries-antarctica-math.json')
    print("Copied to frontend/public/")

if __name__ == "__main__":
    main()
