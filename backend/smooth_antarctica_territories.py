import json
import math

def create_smooth_antarctica_territories():
    """Create smooth, natural-looking Antarctica territorial claims"""
    
    # Load the current data
    try:
        with open('all-countries-antarctica-final.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: all-countries-antarctica-final.json not found")
        return None
    
    # Remove old Antarctica territories (those starting with AQ-)
    data['features'] = [f for f in data['features'] if not f['properties']['id'].startswith('AQ-')]
    
    print("Removed old jagged Antarctica territories")
    
    # Create smooth, natural-looking Antarctica territories
    # These follow realistic coastlines with smooth curves
    antarctica_territories = [
        {
            "id": "AQ-AR",
            "name": "Argentine Antarctica",
            "mother_country": "Argentina",
            "faction": "NEUTRAL",
            "description": "Argentine Antarctic Territory (claimed by Argentina)",
            # Smooth coastline following the Weddell Sea
            "coordinates": [
                [-74, -60], [-72, -61], [-70, -62.5], [-68, -64], [-66, -65.5], 
                [-64, -67], [-62, -68.5], [-60, -70], [-58, -71.5], [-56, -73], 
                [-54, -74.5], [-52, -76], [-50, -77.5], [-48, -79], [-46, -80.5], 
                [-44, -82], [-42, -83.5], [-40, -85], [-38, -86.5], [-36, -88], 
                [-34, -89], [-32, -90], [-74, -90], [-74, -60]
            ]
        },
        {
            "id": "AQ-CH",
            "name": "Chilean Antarctic Territory", 
            "mother_country": "Chile",
            "faction": "NEUTRAL",
            "description": "Chilean Antarctic Territory (claimed by Chile)",
            # Smooth coastline following the Antarctic Peninsula
            "coordinates": [
                [-90, -60], [-88, -61], [-86, -62.5], [-84, -64], [-82, -65.5], 
                [-80, -67], [-78, -68.5], [-76, -70], [-74, -71.5], [-74, -90], 
                [-90, -90], [-90, -60]
            ]
        },
        {
            "id": "AQ-UK",
            "name": "British Antarctic Territory",
            "mother_country": "United Kingdom",
            "faction": "US",
            "description": "British Antarctic Territory (claimed by UK)",
            # Smooth coastline following the Bellingshausen Sea
            "coordinates": [
                [-80, -60], [-78, -61], [-76, -62.5], [-74, -64], [-72, -65.5], 
                [-70, -67], [-68, -68.5], [-66, -70], [-64, -71.5], [-62, -73], 
                [-60, -74.5], [-58, -76], [-56, -77.5], [-54, -79], [-52, -80.5], 
                [-50, -82], [-48, -83.5], [-46, -85], [-44, -86.5], [-42, -88], 
                [-40, -89], [-38, -90], [-80, -90], [-80, -60]
            ]
        },
        {
            "id": "AQ-NO",
            "name": "Queen Maud Land",
            "mother_country": "Norway",
            "faction": "US",
            "description": "Queen Maud Land (claimed by Norway)",
            # Smooth coastline following the Atlantic sector
            "coordinates": [
                [-20, -60], [-18, -61], [-16, -62.5], [-14, -64], [-12, -65.5], 
                [-10, -67], [-8, -68.5], [-6, -70], [-4, -71.5], [-2, -73], 
                [0, -74.5], [2, -76], [4, -77.5], [6, -79], [8, -80.5], 
                [10, -82], [12, -83.5], [14, -85], [16, -86.5], [18, -88], 
                [20, -89], [22, -90], [24, -90], [26, -90], [28, -90], 
                [30, -90], [32, -90], [34, -90], [36, -90], [38, -90], 
                [40, -90], [42, -90], [44, -90], [45, -90], [45, -60], 
                [-20, -60]
            ]
        },
        {
            "id": "AQ-AU", 
            "name": "Australian Antarctic Territory",
            "mother_country": "Australia",
            "faction": "US",
            "description": "Australian Antarctic Territory (claimed by Australia)",
            # Smooth coastline following the Indian Ocean sector
            "coordinates": [
                [45, -60], [47, -61], [49, -62.5], [51, -64], [53, -65.5], 
                [55, -67], [57, -68.5], [59, -70], [61, -71.5], [63, -73], 
                [65, -74.5], [67, -76], [69, -77.5], [71, -79], [73, -80.5], 
                [75, -82], [77, -83.5], [79, -85], [81, -86.5], [83, -88], 
                [85, -89], [87, -90], [89, -90], [91, -90], [93, -90], 
                [95, -90], [97, -90], [99, -90], [101, -90], [103, -90], 
                [105, -90], [107, -90], [109, -90], [111, -90], [113, -90], 
                [115, -90], [117, -90], [119, -90], [121, -90], [123, -90], 
                [125, -90], [127, -90], [129, -90], [131, -90], [133, -90], 
                [135, -90], [137, -90], [139, -90], [141, -90], [143, -90], 
                [145, -90], [147, -90], [149, -90], [151, -90], [153, -90], 
                [155, -90], [157, -90], [159, -90], [160, -90], [160, -60], 
                [45, -60]
            ]
        },
        {
            "id": "AQ-FR",
            "name": "Adélie Land",
            "mother_country": "France",
            "faction": "US",
            "description": "Adélie Land (claimed by France)",
            # Smooth coastline for French claim
            "coordinates": [
                [136, -60], [137, -61], [138, -62.5], [139, -64], [140, -65.5], 
                [141, -67], [142, -68.5], [142, -90], [136, -90], [136, -60]
            ]
        },
        {
            "id": "AQ-NZ",
            "name": "Ross Dependency",
            "mother_country": "New Zealand",
            "faction": "US",
            "description": "Ross Dependency (claimed by New Zealand)",
            # Smooth coastline following the Ross Sea
            "coordinates": [
                [160, -60], [162, -61], [164, -62.5], [166, -64], [168, -65.5], 
                [170, -67], [172, -68.5], [174, -70], [176, -71.5], [178, -73], 
                [180, -74.5], [178, -76], [176, -77.5], [174, -79], [172, -80.5], 
                [170, -82], [168, -83.5], [166, -85], [164, -86.5], [162, -88], 
                [160, -89], [158, -90], [156, -90], [154, -90], [152, -90], 
                [150, -90], [150, -60], [160, -60]
            ]
        }
    ]
    
    # Add new smooth Antarctica territories
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
        print(f"✓ Added {territory['name']} with smooth coastline")
    
    # Save updated data
    with open('all-countries-antarctica-smooth.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nCreated smooth Antarctica territories")
    print(f"Total countries/territories: {len(data['features'])}")
    print("Saved to: all-countries-antarctica-smooth.json")
    
    return data

if __name__ == "__main__":
    create_smooth_antarctica_territories() 