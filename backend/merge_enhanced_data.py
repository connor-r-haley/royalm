#!/usr/bin/env python3
"""
Script to merge enhanced political data with original detailed country borders
"""

import json
import os
from country_mapping_fixed import ENHANCED_COUNTRIES
from country_mapping import get_default_faction

def load_json_file(filepath):
    """Load a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_json_file(data, filepath):
    """Save data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Saved to {filepath}")
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

def get_default_faction(country_id, country_name):
    """Assign default factions for countries not in enhanced data"""
    
    # NATO and US allies
    nato_countries = {
        'NL', 'BE', 'DK', 'NO', 'SE', 'FI', 'ES', 'PT', 'GR', 'CZ', 'SK', 'HU', 'RO', 'BG', 'HR', 'SI', 'EE', 'LV', 'LT', 'ME', 'AL', 'MK', 'RS', 'BA', 'XK', 'MD', 'GE', 'AM', 'AZ', 'KG', 'TJ', 'UZ', 'TM', 'MN', 'KR', 'TW', 'PH', 'TH', 'SG', 'MY', 'ID', 'VN', 'NZ', 'FJ', 'PG', 'NC', 'PF', 'TO', 'WS', 'KI', 'VU', 'SB', 'NR', 'TV', 'PW', 'MH', 'FM', 'CK', 'NU', 'TK', 'AS', 'GU', 'MP', 'VI', 'PR', 'GT', 'BZ', 'SV', 'HN', 'NI', 'CR', 'PA', 'CO', 'VE', 'GY', 'SR', 'GF', 'EC', 'PE', 'BO', 'CL', 'PY', 'UY', 'FK', 'GS', 'IO', 'CC', 'CX', 'NF', 'AU-ACT', 'AU-NSW', 'AU-NT', 'AU-QLD', 'AU-SA', 'AU-TAS', 'AU-VIC', 'AU-WA'
    }
    
    # Russia bloc allies
    russia_bloc = {
        'AM', 'AZ', 'BY', 'KZ', 'KG', 'TJ', 'UZ', 'TM', 'MD', 'GE', 'AB', 'SO', 'SS', 'RU-ALT', 'RU-AMU', 'RU-ARK', 'RU-AST', 'RU-BEL', 'RU-BRY', 'RU-CHE', 'RU-CHU', 'RU-CU', 'RU-DA', 'RU-IN', 'RU-IRK', 'RU-IVA', 'RU-KAM', 'RU-KDA', 'RU-KEM', 'RU-KHA', 'RU-KIR', 'RU-KOS', 'RU-KRS', 'RU-LEN', 'RU-LIP', 'RU-MAG', 'RU-MOS', 'RU-MUR', 'RU-NEN', 'RU-NGR', 'RU-NIZ', 'RU-NVS', 'RU-OMS', 'RU-ORE', 'RU-ORL', 'RU-PNZ', 'RU-PRI', 'RU-PSK', 'RU-ROS', 'RU-RYA', 'RU-SAK', 'RU-SAM', 'RU-SAR', 'RU-SMO', 'RU-SPE', 'RU-STA', 'RU-SVE', 'RU-TAM', 'RU-TOM', 'RU-TUL', 'RU-TVE', 'RU-TYU', 'RU-UD', 'RU-ULY', 'RU-VGG', 'RU-VLA', 'RU-VLG', 'RU-VOR', 'RU-YAN', 'RU-YAR', 'RU-YEV', 'RU-ZAB'
    }
    
    # China bloc allies
    china_bloc = {
        'KP', 'IR', 'SY', 'LB', 'JO', 'IQ', 'KW', 'QA', 'AE', 'OM', 'YE', 'BH', 'LA', 'MM', 'KH', 'BD', 'NP', 'LK', 'MV', 'BT', 'CN-11', 'CN-12', 'CN-13', 'CN-14', 'CN-15', 'CN-21', 'CN-22', 'CN-23', 'CN-31', 'CN-32', 'CN-33', 'CN-34', 'CN-35', 'CN-36', 'CN-37', 'CN-41', 'CN-42', 'CN-43', 'CN-44', 'CN-45', 'CN-46', 'CN-50', 'CN-51', 'CN-52', 'CN-53', 'CN-54', 'CN-61', 'CN-62', 'CN-63', 'CN-64', 'CN-65', 'CN-71', 'CN-81', 'CN-82', 'CN-91', 'CN-92', 'CN-93', 'CN-94', 'CN-95', 'CN-96', 'CN-97', 'CN-98', 'CN-99'
    }
    
    # Swing states
    swing_states = {
        'IN', 'PK', 'IL', 'BR', 'SA', 'EG', 'AR', 'ZA', 'NG', 'KE', 'ET', 'TZ', 'UG', 'GH', 'CI', 'SN', 'ML', 'BF', 'NE', 'TD', 'SD', 'ER', 'DJ', 'SO', 'CM', 'CF', 'CG', 'CD', 'AO', 'ZM', 'ZW', 'BW', 'NA', 'LS', 'SZ', 'MG', 'MU', 'SC', 'KM', 'YT', 'RE', 'MW', 'MZ', 'ZW', 'BW', 'NA', 'LS', 'SZ', 'MG', 'MU', 'SC', 'KM', 'YT', 'RE', 'MW', 'MZ'
    }
    
    # Antarctica territories (gray)
    antarctica_territories = {
        'AQ-ADL', 'AQ-CLA', 'AQ-COA', 'AQ-EAS', 'AQ-GRA', 'AQ-MAR', 'AQ-PAL', 'AQ-QUE', 'AQ-ROS', 'AQ-TER', 'AQ-VIC', 'AQ-WIL', 'AQ-ANT'
    }
    
    if country_id in nato_countries:
        return "NATO"
    elif country_id in russia_bloc:
        return "RUSSIA_BLOC"
    elif country_id in china_bloc:
        return "CHINA_BLOC"
    elif country_id in swing_states:
        return "SWING"
    elif country_id in antarctica_territories:
        return "NEUTRAL"  # Gray for Antarctica
    else:
        return "NEUTRAL"  # Default gray for unknown/less important

def merge_enhanced_data():
    """Merge enhanced political data with original borders"""
    
    # Load the original detailed borders - use world-countries with proper geometry
    original_borders = load_json_file('world-countries.json')
    if not original_borders:
        print("Could not load Antarctica borders, trying ultra quality...")
        original_borders = load_json_file('all-countries-ultra-quality.json')
        if not original_borders:
            print("Could not load ultra quality borders, trying fallback...")
            original_borders = load_json_file('wwiii-countries-web.json')
            if not original_borders:
                print("Could not load original borders")
                return
    
    # Use the enhanced countries mapping
    enhanced_lookup = ENHANCED_COUNTRIES
    
    # Merge the data
    merged_features = []
    for feature in original_borders['features']:
        country_id = feature['properties'].get('id')
        country_name = feature['properties'].get('name', 'Unknown')
        
        if country_name in enhanced_lookup:
            # Merge enhanced data with original geometry
            merged_properties = {
                **feature['properties'],  # Keep original properties
                **enhanced_lookup[country_name]  # Override with enhanced data
            }
        else:
            # Add default faction for countries not in enhanced data
            default_faction = get_default_faction(country_id, country_name)
            merged_properties = {
                **feature['properties'],
                'faction': default_faction,
                'alliance': 'none',
                'nuclear_weapons': 0,
                'nuclear_status': 'none',
                'morale': 0.5,
                'description': f'{country_name} - {default_faction.lower().replace("_", " ")}'
            }
            
        merged_feature = {
            'type': 'Feature',
            'properties': merged_properties,
            'geometry': feature['geometry']  # Keep original detailed geometry
        }
        merged_features.append(merged_feature)
    
    # Create merged result
    merged_result = {
        'type': 'FeatureCollection',
        'features': merged_features
    }
    
    # Save the merged result
    save_json_file(merged_result, 'borders-enhanced-detailed.json')
    
    # Also copy to frontend
    frontend_path = '../frontend/public/borders-enhanced-detailed.json'
    save_json_file(merged_result, frontend_path)
    
    print(f"Successfully merged {len(merged_features)} countries")
    print(f"Enhanced countries: {len(enhanced_lookup)}")
    
    # Count factions
    faction_counts = {}
    for feature in merged_features:
        faction = feature['properties'].get('faction', 'UNKNOWN')
        faction_counts[faction] = faction_counts.get(faction, 0) + 1
    
    print("Faction distribution:")
    for faction, count in faction_counts.items():
        print(f"  {faction}: {count} countries")

if __name__ == "__main__":
    merge_enhanced_data()
