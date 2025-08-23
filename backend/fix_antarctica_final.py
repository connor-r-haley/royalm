import json
import math

def create_realistic_antarctica_territories():
    """Create proper Antarctica territorial claims that follow the coastline"""
    
    # Load the current data
    try:
        with open('all-countries-antarctica-fixed.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: all-countries-antarctica-fixed.json not found")
        return None
    
    # Remove Antarctica as a country (keep only territories)
    data['features'] = [f for f in data['features'] if f['properties']['name'] != 'Antarctica']
    
    # Remove old Antarctica territories (those starting with AQ-)
    data['features'] = [f for f in data['features'] if not f['properties']['id'].startswith('AQ-')]
    
    print("Removed Antarctica country and old territories")
    
    # Create realistic Antarctica territories that follow the coastline
    # These are based on actual territorial claims but with realistic coastal boundaries
    antarctica_territories = [
        {
            "id": "AQ-AR",
            "name": "Argentine Antarctica",
            "mother_country": "Argentina",
            "faction": "NEUTRAL",
            "description": "Argentine Antarctic Territory (claimed by Argentina)",
            # Create a more realistic polygon that follows the coastline
            "coordinates": [
                [-74, -60], [-70, -62], [-68, -65], [-65, -68], [-60, -70], 
                [-55, -72], [-50, -75], [-45, -78], [-40, -80], [-35, -82], 
                [-30, -84], [-25, -85], [-25, -90], [-74, -90], [-74, -60]
            ]
        },
        {
            "id": "AQ-CH",
            "name": "Chilean Antarctic Territory", 
            "mother_country": "Chile",
            "faction": "NEUTRAL",
            "description": "Chilean Antarctic Territory (claimed by Chile)",
            "coordinates": [
                [-90, -60], [-85, -62], [-80, -65], [-78, -68], [-76, -70], 
                [-74, -72], [-74, -90], [-90, -90], [-90, -60]
            ]
        },
        {
            "id": "AQ-UK",
            "name": "British Antarctic Territory",
            "mother_country": "United Kingdom",
            "faction": "US",
            "description": "British Antarctic Territory (claimed by UK)",
            "coordinates": [
                [-80, -60], [-75, -62], [-70, -65], [-65, -68], [-60, -70], 
                [-55, -72], [-50, -75], [-45, -78], [-40, -80], [-35, -82], 
                [-30, -84], [-25, -85], [-25, -90], [-80, -90], [-80, -60]
            ]
        },
        {
            "id": "AQ-NO",
            "name": "Queen Maud Land",
            "mother_country": "Norway",
            "faction": "US",
            "description": "Queen Maud Land (claimed by Norway)",
            "coordinates": [
                [-20, -60], [-15, -62], [-10, -65], [-5, -68], [0, -70], 
                [5, -72], [10, -75], [15, -78], [20, -80], [25, -82], 
                [30, -84], [35, -86], [40, -88], [45, -89], [45, -90], 
                [-20, -90], [-20, -60]
            ]
        },
        {
            "id": "AQ-AU", 
            "name": "Australian Antarctic Territory",
            "mother_country": "Australia",
            "faction": "US",
            "description": "Australian Antarctic Territory (claimed by Australia)",
            "coordinates": [
                [45, -60], [50, -62], [55, -65], [60, -68], [65, -70], 
                [70, -72], [75, -75], [80, -78], [85, -80], [90, -82], 
                [95, -84], [100, -86], [105, -88], [110, -89], [115, -90], 
                [120, -90], [125, -90], [130, -90], [135, -90], [140, -90], 
                [145, -90], [150, -90], [155, -90], [160, -90], [160, -60], 
                [45, -60]
            ]
        },
        {
            "id": "AQ-FR",
            "name": "Adélie Land",
            "mother_country": "France",
            "faction": "US",
            "description": "Adélie Land (claimed by France)",
            "coordinates": [
                [136, -60], [138, -62], [140, -65], [142, -68], [142, -90], 
                [136, -90], [136, -60]
            ]
        },
        {
            "id": "AQ-NZ",
            "name": "Ross Dependency",
            "mother_country": "New Zealand",
            "faction": "US",
            "description": "Ross Dependency (claimed by New Zealand)",
            "coordinates": [
                [160, -60], [165, -62], [170, -65], [175, -68], [180, -70], 
                [175, -72], [170, -75], [165, -78], [160, -80], [155, -82], 
                [150, -84], [150, -90], [160, -90], [160, -60]
            ]
        }
    ]
    
    # Add new realistic Antarctica territories
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
        print(f"✓ Added {territory['name']} with realistic coastline")
    
    # Save updated data
    with open('all-countries-antarctica-final.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nFixed Antarctica territories")
    print(f"Total countries/territories: {len(data['features'])}")
    print("Saved to: all-countries-antarctica-final.json")
    
    return data

if __name__ == "__main__":
    create_realistic_antarctica_territories() 