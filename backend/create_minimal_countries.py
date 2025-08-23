import json

# Minimal set of key countries for WWIII simulator with simple geometries
MINIMAL_COUNTRIES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "id": "US", "name": "United States", "faction": "US", "morale": 0.8
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-125, 25], [-125, 50], [-65, 50], [-65, 25], [-125, 25]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "RU", "name": "Russia", "faction": "RU", "morale": 0.7
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [20, 50], [20, 80], [180, 80], [180, 50], [20, 50]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "CN", "name": "China", "faction": "NEUTRAL", "morale": 0.6
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [73, 18], [73, 54], [135, 54], [135, 18], [73, 18]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "UA", "name": "Ukraine", "faction": "US", "morale": 0.6
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [22, 44], [22, 52], [40, 52], [40, 44], [22, 44]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "TR", "name": "Turkey", "faction": "NEUTRAL", "morale": 0.5
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [26, 36], [26, 42], [45, 42], [45, 36], [26, 36]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "IR", "name": "Iran", "faction": "NEUTRAL", "morale": 0.4
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [44, 25], [44, 40], [63, 40], [63, 25], [44, 25]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "GB", "name": "United Kingdom", "faction": "US", "morale": 0.7
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-8, 50], [-8, 59], [2, 59], [2, 50], [-8, 50]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "DE", "name": "Germany", "faction": "US", "morale": 0.7
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [6, 47], [6, 55], [15, 55], [15, 47], [6, 47]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "FR", "name": "France", "faction": "US", "morale": 0.7
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-5, 41], [-5, 51], [10, 51], [10, 41], [-5, 41]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "JP", "name": "Japan", "faction": "US", "morale": 0.6
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [129, 31], [129, 46], [146, 46], [146, 31], [129, 31]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "KR", "name": "South Korea", "faction": "US", "morale": 0.6
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [125, 33], [125, 38], [132, 38], [132, 33], [125, 33]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "IL", "name": "Israel", "faction": "US", "morale": 0.5
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [34, 29], [34, 33], [36, 33], [36, 29], [34, 29]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "SA", "name": "Saudi Arabia", "faction": "NEUTRAL", "morale": 0.4
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [35, 16], [35, 32], [55, 32], [55, 16], [35, 16]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "IN", "name": "India", "faction": "NEUTRAL", "morale": 0.5
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [68, 8], [68, 37], [97, 37], [97, 8], [68, 8]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "CA", "name": "Canada", "faction": "US", "morale": 0.7
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-141, 42], [-141, 84], [-52, 84], [-52, 42], [-141, 42]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "AU", "name": "Australia", "faction": "US", "morale": 0.6
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [113, -44], [113, -10], [154, -10], [154, -44], [113, -44]
                ]]
            }
        }
    ]
}

def create_minimal_countries():
    """Create a minimal set of countries for fast web loading"""
    
    # Save to file
    with open('wwiii-countries-minimal.json', 'w') as f:
        json.dump(MINIMAL_COUNTRIES, f, indent=2)
    
    print(f"Created minimal set with {len(MINIMAL_COUNTRIES['features'])} countries")
    print("Saved to wwiii-countries-minimal.json")
    
    return MINIMAL_COUNTRIES

if __name__ == "__main__":
    create_minimal_countries() 