#!/usr/bin/env python3
"""
Script to create clean Antarctica divisions without spider web effect
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

def create_clean_antarctica_territories() -> List[dict]:
    """Create clean Antarctica territories with simple wedge shapes"""
    
    # Define territory data
    territories = [
        {
            "id": "AQ-AR",
            "name": "Argentina Territory",
            "mother_country": "Argentina",
            "faction": "NEUTRAL",
            "description": "Argentine Antarctic Territory (claimed by Argentina)",
            "longitude_range": (-74, -25)
        },
        {
            "id": "AQ-CH", 
            "name": "Chile Territory",
            "mother_country": "Chile",
            "faction": "NEUTRAL",
            "description": "Chilean Antarctic Territory (claimed by Chile)",
            "longitude_range": (-90, -53)
        },
        {
            "id": "AQ-UK",
            "name": "UK Territory", 
            "mother_country": "United Kingdom",
            "faction": "NATO",
            "description": "British Antarctic Territory (claimed by UK)",
            "longitude_range": (-80, -20)
        },
        {
            "id": "AQ-NO",
            "name": "Norway Territory",
            "mother_country": "Norway", 
            "faction": "NATO",
            "description": "Queen Maud Land (claimed by Norway)",
            "longitude_range": (-20, 45)
        },
        {
            "id": "AQ-AU",
            "name": "Australia Territory",
            "mother_country": "Australia",
            "faction": "NATO", 
            "description": "Australian Antarctic Territory (claimed by Australia)",
            "longitude_range": (45, 160)
        },
        {
            "id": "AQ-FR",
            "name": "France Territory",
            "mother_country": "France",
            "faction": "NATO",
            "description": "Adélie Land (claimed by France)", 
            "longitude_range": (136, 142)
        },
        {
            "id": "AQ-NZ",
            "name": "New Zealand Territory",
            "mother_country": "New Zealand",
            "faction": "NATO",
            "description": "Ross Dependency (claimed by New Zealand)",
            "longitude_range": (160, -150)  # Wraps around
        }
    ]
    
    features = []
    
    for territory in territories:
        # Create a simple wedge shape for each territory
        min_lng, max_lng = territory["longitude_range"]
        
        # Create coordinates for a wedge shape
        coords = []
        
        # Handle wrapping for Ross Dependency
        if min_lng > max_lng:  # Wraps around
            # First part: min_lng to 180
            for lng in range(int(min_lng), 181, 5):
                coords.append([lng, -60])  # Coastline
            # Second part: -180 to max_lng  
            for lng in range(-180, int(max_lng) + 1, 5):
                coords.append([lng, -60])  # Coastline
            # Inner part
            for lng in range(int(max_lng), int(min_lng) - 1, -5):
                coords.append([lng, -85])  # Inner boundary
        else:
            # Regular territory
            for lng in range(int(min_lng), int(max_lng) + 1, 5):
                coords.append([lng, -60])  # Coastline
            for lng in range(int(max_lng), int(min_lng) - 1, -5):
                coords.append([lng, -85])  # Inner boundary
        
        # Close the polygon
        if coords:
            coords.append(coords[0])
        
        feature = {
            "type": "Feature",
            "properties": {
                "id": territory["id"],
                "name": territory["name"],
                "mother_country": territory["mother_country"],
                "faction": territory["faction"],
                "alliance": territory["faction"],
                "morale": 0.4,
                "nuclear_weapons": 0,
                "nuclear_status": "none",
                "description": territory["description"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }
        
        features.append(feature)
    
    return features

def main():
    """Main function to create clean Antarctica"""
    
    # Load the base data
    data = load_json_file('all-countries-ultra-quality.json')
    if not data:
        print("Could not load base data")
        return
    
    # Remove any existing Antarctica territories
    data['features'] = [f for f in data['features'] if not f['properties']['id'].startswith('AQ-')]
    
    # Create clean Antarctica territories
    antarctica_features = create_clean_antarctica_territories()
    data['features'].extend(antarctica_features)
    
    print(f"Created {len(antarctica_features)} clean Antarctica territories")
    
    # Save the result
    save_json_file(data, 'all-countries-antarctica-clean.json')
    
    # Also copy to frontend
    import shutil
    shutil.copy('all-countries-antarctica-clean.json', '../frontend/public/all-countries-antarctica-clean.json')
    print("Copied to frontend/public/")

if __name__ == "__main__":
    main()
