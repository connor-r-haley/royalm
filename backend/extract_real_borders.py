import json
import sys

# The 16 key countries we want with real borders
KEY_COUNTRIES = {
    "US": "United States of America",
    "RU": "Russian Federation", 
    "CN": "China",
    "GB": "United Kingdom",
    "FR": "France",
    "DE": "Germany",
    "IT": "Italy",
    "JP": "Japan",
    "IN": "India",
    "BR": "Brazil",
    "CA": "Canada",
    "AU": "Australia",
    "KR": "South Korea",
    "IR": "Iran",
    "TR": "Turkey",
    "SA": "Saudi Arabia"
}

def find_country_by_name(features, country_name):
    """Find country by name with fuzzy matching"""
    for feature in features:
        props = feature.get("properties", {})
        name = props.get("name", "").lower()
        if country_name.lower() in name or name in country_name.lower():
            return feature
    return None

def extract_real_borders():
    """Extract real borders for key countries"""
    try:
        # Load the comprehensive world data
        with open('world-countries.json', 'r') as f:
            world_data = json.load(f)
        
        features = world_data.get("features", [])
        extracted_features = []
        
        print("Extracting real borders for key countries...")
        
        for country_id, country_name in KEY_COUNTRIES.items():
            feature = find_country_by_name(features, country_name)
            if feature:
                # Create new feature with our properties
                new_feature = {
                    "type": "Feature",
                    "properties": {
                        "id": country_id,
                        "name": country_name,
                        "faction": "US" if country_id in ["US", "GB", "FR", "DE", "IT", "JP", "CA", "AU", "KR"] else "RU" if country_id in ["RU", "CN", "IR"] else "NEUTRAL",
                        "morale": 0.7  # Default morale
                    },
                    "geometry": feature["geometry"]
                }
                extracted_features.append(new_feature)
                print(f"✓ Found: {country_name} ({country_id})")
            else:
                print(f"✗ Not found: {country_name} ({country_id})")
        
        # Create the final GeoJSON
        result = {
            "type": "FeatureCollection",
            "features": extracted_features
        }
        
        # Save to file
        with open('wwiii-countries-real.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nExtracted {len(extracted_features)} countries with real borders")
        print("Saved to: wwiii-countries-real.json")
        
        return result
        
    except FileNotFoundError:
        print("Error: world-countries.json not found. Please download it first.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    extract_real_borders() 