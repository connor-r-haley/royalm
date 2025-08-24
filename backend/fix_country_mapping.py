#!/usr/bin/env python3
"""
Fix country mapping by matching actual country names
"""

import json

def load_json_file(filepath):
    """Load a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def create_proper_mapping():
    """Create proper country mapping based on actual names"""
    
    # Load the ultra-quality data
    data = load_json_file('all-countries-ultra-quality.json')
    if not data:
        return
    
    # Create mapping based on EXACT country names as keys
    country_mapping = {}
    
    # Enhanced political data with exact country names as keys
    enhanced_data = {
        'United States of America': {
            'name': 'United States',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 5244,
            'nuclear_status': 'confirmed',
            'morale': 0.8,
            'description': 'NATO leader, nuclear superpower'
        },
        'Russia': {
            'name': 'Russia',
            'faction': 'RUSSIA_BLOC',
            'alliance': 'CSTO',
            'nuclear_weapons': 5977,
            'nuclear_status': 'confirmed',
            'morale': 0.7,
            'description': 'Nuclear superpower, CSTO leader'
        },
        'China': {
            'name': 'China',
            'faction': 'CHINA_BLOC',
            'alliance': 'SCO',
            'nuclear_weapons': 410,
            'nuclear_status': 'confirmed',
            'morale': 0.8,
            'description': 'Rising superpower, nuclear state'
        },
        'United Kingdom': {
            'name': 'United Kingdom',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 225,
            'nuclear_status': 'confirmed',
            'morale': 0.75,
            'description': 'NATO member, nuclear power'
        },
        'France': {
            'name': 'France',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 290,
            'nuclear_status': 'confirmed',
            'morale': 0.7,
            'description': 'NATO member, nuclear power'
        },
        'Germany': {
            'name': 'Germany',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.65,
            'description': 'NATO member, non-nuclear'
        },
        'Italy': {
            'name': 'Italy',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.6,
            'description': 'NATO member, non-nuclear'
        },
        'Canada': {
            'name': 'Canada',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.7,
            'description': 'NATO member, non-nuclear'
        },
        'Poland': {
            'name': 'Poland',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.8,
            'description': 'NATO member, non-nuclear'
        },
        'Ukraine': {
            'name': 'Ukraine',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.9,
            'description': 'NATO member, non-nuclear'
        },
        'Belarus': {
            'name': 'Belarus',
            'faction': 'RUSSIA_BLOC',
            'alliance': 'CSTO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.6,
            'description': 'CSTO member, non-nuclear'
        },
        'Kazakhstan': {
            'name': 'Kazakhstan',
            'faction': 'RUSSIA_BLOC',
            'alliance': 'CSTO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.5,
            'description': 'CSTO member, non-nuclear'
        },
        'India': {
            'name': 'India',
            'faction': 'SWING',
            'alliance': 'QUAD',
            'nuclear_weapons': 164,
            'nuclear_status': 'confirmed',
            'morale': 0.7,
            'description': 'Swing state, nuclear power'
        },
        'Pakistan': {
            'name': 'Pakistan',
            'faction': 'SWING',
            'alliance': 'none',
            'nuclear_weapons': 170,
            'nuclear_status': 'confirmed',
            'morale': 0.6,
            'description': 'Swing state, nuclear power'
        },
        'Israel': {
            'name': 'Israel',
            'faction': 'SWING',
            'alliance': 'none',
            'nuclear_weapons': 90,
            'nuclear_status': 'estimated',
            'morale': 0.8,
            'description': 'Swing state, nuclear power (estimated)'
        },
        'North Korea': {
            'name': 'North Korea',
            'faction': 'CHINA_BLOC',
            'alliance': 'none',
            'nuclear_weapons': 30,
            'nuclear_status': 'estimated',
            'morale': 0.7,
            'description': 'China ally, nuclear power (estimated)'
        },
        'Iran': {
            'name': 'Iran',
            'faction': 'CHINA_BLOC',
            'alliance': 'SCO',
            'nuclear_weapons': 0,
            'nuclear_status': 'suspected',
            'morale': 0.6,
            'description': 'China ally, suspected nuclear program'
        },
        'Japan': {
            'name': 'Japan',
            'faction': 'NATO',
            'alliance': 'QUAD',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.7,
            'description': 'US ally, non-nuclear'
        },
        'Ireland': {
            'name': 'Ireland',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.7,
            'description': 'NATO member, non-nuclear'
        },
        'Australia': {
            'name': 'Australia',
            'faction': 'NATO',
            'alliance': 'QUAD',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.7,
            'description': 'US ally, non-nuclear'
        },
        'Brazil': {
            'name': 'Brazil',
            'faction': 'SWING',
            'alliance': 'BRICS',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.6,
            'description': 'Swing state, non-nuclear'
        },
        'Saudi Arabia': {
            'name': 'Saudi Arabia',
            'faction': 'SWING',
            'alliance': 'none',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.5,
            'description': 'Swing state, non-nuclear'
        },
        'Turkey': {
            'name': 'Turkey',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.6,
            'description': 'NATO member, non-nuclear'
        },
        'Egypt': {
            'name': 'Egypt',
            'faction': 'SWING',
            'alliance': 'none',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.5,
            'description': 'Swing state, non-nuclear'
        },
        'Mexico': {
            'name': 'Mexico',
            'faction': 'NATO',
            'alliance': 'NATO',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.6,
            'description': 'US ally, non-nuclear'
        },
        'Argentina': {
            'name': 'Argentina',
            'faction': 'SWING',
            'alliance': 'none',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.5,
            'description': 'Swing state, non-nuclear'
        },
        'South Africa': {
            'name': 'South Africa',
            'faction': 'SWING',
            'alliance': 'BRICS',
            'nuclear_weapons': 0,
            'nuclear_status': 'none',
            'morale': 0.5,
            'description': 'Swing state, non-nuclear'
        }
    }
    
    # Create mapping from country names to enhanced data
    for feature in data['features']:
        country_name = feature['properties']['name']
        if country_name in enhanced_data:
            country_mapping[country_name] = enhanced_data[country_name]
    
    # Save the mapping
    with open('country_mapping_fixed.py', 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""Fixed country mapping based on actual names"""\n\n')
        f.write('ENHANCED_COUNTRIES = {\n')
        for country_name, data in country_mapping.items():
            f.write(f"    '{country_name}': {{\n")
            for key, value in data.items():
                if isinstance(value, str):
                    f.write(f"        '{key}': '{value}',\n")
                else:
                    f.write(f"        '{key}': {value},\n")
            f.write('    },\n')
        f.write('}\n')
    
    print(f"Created mapping for {len(country_mapping)} countries")
    for country_name, data in country_mapping.items():
        print(f"  {country_name}: {data['faction']}")

if __name__ == "__main__":
    create_proper_mapping()
