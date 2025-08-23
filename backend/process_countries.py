import json
import sys

# Key countries for WWIII simulator
KEY_COUNTRIES = {
    "US": "United States",
    "RU": "Russia", 
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
    "SA": "Saudi Arabia",
    "EG": "Egypt",
    "NG": "Nigeria",
    "ZA": "South Africa",
    "MX": "Mexico",
    "AR": "Argentina",
    "CL": "Chile",
    "PE": "Peru",
    "CO": "Colombia",
    "VE": "Venezuela",
    "UA": "Ukraine",
    "PL": "Poland",
    "CZ": "Czech Republic",
    "HU": "Hungary",
    "RO": "Romania",
    "BG": "Bulgaria",
    "GR": "Greece",
    "ES": "Spain",
    "PT": "Portugal",
    "NL": "Netherlands",
    "BE": "Belgium",
    "CH": "Switzerland",
    "AT": "Austria",
    "SE": "Sweden",
    "NO": "Norway",
    "DK": "Denmark",
    "FI": "Finland",
    "IS": "Iceland",
    "IE": "Ireland",
    "IL": "Israel",
    "JO": "Jordan",
    "LB": "Lebanon",
    "SY": "Syria",
    "IQ": "Iraq",
    "KW": "Kuwait",
    "QA": "Qatar",
    "AE": "United Arab Emirates",
    "OM": "Oman",
    "YE": "Yemen",
    "PK": "Pakistan",
    "AF": "Afghanistan",
    "BD": "Bangladesh",
    "LK": "Sri Lanka",
    "NP": "Nepal",
    "BT": "Bhutan",
    "MM": "Myanmar",
    "TH": "Thailand",
    "VN": "Vietnam",
    "LA": "Laos",
    "KH": "Cambodia",
    "MY": "Malaysia",
    "SG": "Singapore",
    "ID": "Indonesia",
    "PH": "Philippines",
    "TW": "Taiwan",
    "MN": "Mongolia",
    "KZ": "Kazakhstan",
    "UZ": "Uzbekistan",
    "KG": "Kyrgyzstan",
    "TJ": "Tajikistan",
    "TM": "Turkmenistan",
    "AZ": "Azerbaijan",
    "GE": "Georgia",
    "AM": "Armenia",
    "BY": "Belarus",
    "LT": "Lithuania",
    "LV": "Latvia",
    "EE": "Estonia",
    "MD": "Moldova",
    "RS": "Serbia",
    "HR": "Croatia",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "BA": "Bosnia and Herzegovina",
    "ME": "Montenegro",
    "MK": "North Macedonia",
    "AL": "Albania",
    "XK": "Kosovo"
}

def process_countries():
    """Process the world countries GeoJSON and extract key countries for WWIII simulator"""
    
    # Load the full world countries data
    with open('world-countries.json', 'r') as f:
        world_data = json.load(f)
    
    # Extract key countries
    key_features = []
    
    for feature in world_data['features']:
        properties = feature.get('properties', {})
        
        # Try different property names for country codes
        country_code = None
        for code_field in ['ISO3166-1-Alpha-2', 'ISO_A2', 'iso_a2', 'ISO3166-1-Alpha-3', 'ISO_A3', 'iso_a3']:
            if code_field in properties:
                country_code = properties[code_field]
                break
        
        if country_code and country_code in KEY_COUNTRIES:
            # Create a simplified feature for the WWIII simulator
            simplified_feature = {
                "type": "Feature",
                "properties": {
                    "id": country_code,
                    "name": KEY_COUNTRIES[country_code],
                    "faction": "NEUTRAL",  # Default faction
                    "morale": 0.5,  # Default morale
                    "population": properties.get('POP_EST', 0),
                    "gdp": properties.get('GDP_MD_EST', 0)
                },
                "geometry": feature['geometry']
            }
            key_features.append(simplified_feature)
            print(f"Added {country_code}: {KEY_COUNTRIES[country_code]}")
    
    # Create the final GeoJSON
    wwiii_countries = {
        "type": "FeatureCollection",
        "features": key_features
    }
    
    # Save to file
    with open('wwiii-countries.json', 'w') as f:
        json.dump(wwiii_countries, f, indent=2)
    
    print(f"\nProcessed {len(key_features)} countries for WWIII simulator")
    print("Saved to wwiii-countries.json")
    
    return wwiii_countries

if __name__ == "__main__":
    process_countries() 