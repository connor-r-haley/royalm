#!/usr/bin/env python3
"""
Country mapping system to correctly match country IDs and names
"""

# Enhanced political data with ACTUAL country IDs from ultra-quality data
ENHANCED_COUNTRIES = {
    'UN': {  # United States of America
        'name': 'United States',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 5244,
        'nuclear_status': 'confirmed',
        'morale': 0.8,
        'description': 'NATO leader, nuclear superpower'
    },
    'RU': {  # Russia
        'name': 'Russia',
        'faction': 'RUSSIA_BLOC',
        'alliance': 'CSTO',
        'nuclear_weapons': 5977,
        'nuclear_status': 'confirmed',
        'morale': 0.7,
        'description': 'Nuclear superpower, CSTO leader'
    },
    'CH': {  # China
        'name': 'China',
        'faction': 'CHINA_BLOC',
        'alliance': 'SCO',
        'nuclear_weapons': 410,
        'nuclear_status': 'confirmed',
        'morale': 0.8,
        'description': 'Rising superpower, nuclear state'
    },
    'UN': {  # United Kingdom
        'name': 'United Kingdom',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 225,
        'nuclear_status': 'confirmed',
        'morale': 0.75,
        'description': 'NATO member, nuclear power'
    },
    'FR': {  # France
        'name': 'France',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 290,
        'nuclear_status': 'confirmed',
        'morale': 0.7,
        'description': 'NATO member, nuclear power'
    },
    'GE': {  # Germany
        'name': 'Germany',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.65,
        'description': 'NATO member, non-nuclear'
    },
    'IT': {  # Italy
        'name': 'Italy',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.6,
        'description': 'NATO member, non-nuclear'
    },
    'CA': {  # Canada
        'name': 'Canada',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.7,
        'description': 'NATO member, non-nuclear'
    },
    'PO': {  # Poland
        'name': 'Poland',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.8,
        'description': 'NATO member, non-nuclear'
    },
    'UK': {  # Ukraine
        'name': 'Ukraine',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.9,
        'description': 'NATO member, non-nuclear'
    },
    'BE': {  # Belarus
        'name': 'Belarus',
        'faction': 'RUSSIA_BLOC',
        'alliance': 'CSTO',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.6,
        'description': 'CSTO member, non-nuclear'
    },
    'KA': {  # Kazakhstan
        'name': 'Kazakhstan',
        'faction': 'RUSSIA_BLOC',
        'alliance': 'CSTO',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.5,
        'description': 'CSTO member, non-nuclear'
    },
    'IN': {  # India
        'name': 'India',
        'faction': 'SWING',
        'alliance': 'QUAD',
        'nuclear_weapons': 164,
        'nuclear_status': 'confirmed',
        'morale': 0.7,
        'description': 'Swing state, nuclear power'
    },
    'PA': {  # Pakistan
        'name': 'Pakistan',
        'faction': 'SWING',
        'alliance': 'none',
        'nuclear_weapons': 170,
        'nuclear_status': 'confirmed',
        'morale': 0.6,
        'description': 'Swing state, nuclear power'
    },
    'IS': {  # Israel
        'name': 'Israel',
        'faction': 'SWING',
        'alliance': 'none',
        'nuclear_weapons': 90,
        'nuclear_status': 'estimated',
        'morale': 0.8,
        'description': 'Swing state, nuclear power (estimated)'
    },
    'NO': {  # North Korea
        'name': 'North Korea',
        'faction': 'CHINA_BLOC',
        'alliance': 'none',
        'nuclear_weapons': 30,
        'nuclear_status': 'estimated',
        'morale': 0.7,
        'description': 'China ally, nuclear power (estimated)'
    },
    'IR': {  # Iran
        'name': 'Iran',
        'faction': 'CHINA_BLOC',
        'alliance': 'SCO',
        'nuclear_weapons': 0,
        'nuclear_status': 'suspected',
        'morale': 0.6,
        'description': 'China ally, suspected nuclear program'
    },
    'JA': {  # Japan
        'name': 'Japan',
        'faction': 'NATO',
        'alliance': 'QUAD',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.7,
        'description': 'US ally, non-nuclear'
    },
    'AU': {  # Australia
        'name': 'Australia',
        'faction': 'NATO',
        'alliance': 'QUAD',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.7,
        'description': 'US ally, non-nuclear'
    },
    'BR': {  # Brazil
        'name': 'Brazil',
        'faction': 'SWING',
        'alliance': 'BRICS',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.6,
        'description': 'Swing state, non-nuclear'
    },
    'SA': {  # Saudi Arabia
        'name': 'Saudi Arabia',
        'faction': 'SWING',
        'alliance': 'none',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.5,
        'description': 'Swing state, non-nuclear'
    },
    'TU': {  # Turkey
        'name': 'Turkey',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.6,
        'description': 'NATO member, non-nuclear'
    },
    'EG': {  # Egypt
        'name': 'Egypt',
        'faction': 'SWING',
        'alliance': 'none',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.5,
        'description': 'Swing state, non-nuclear'
    },
    'ME': {  # Mexico
        'name': 'Mexico',
        'faction': 'NATO',
        'alliance': 'NATO',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.6,
        'description': 'US ally, non-nuclear'
    },
    'AR': {  # Argentina
        'name': 'Argentina',
        'faction': 'SWING',
        'alliance': 'none',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.5,
        'description': 'Swing state, non-nuclear'
    },
    'SO': {  # South Africa
        'name': 'South Africa',
        'faction': 'SWING',
        'alliance': 'BRICS',
        'nuclear_weapons': 0,
        'nuclear_status': 'none',
        'morale': 0.5,
        'description': 'Swing state, non-nuclear'
    }
}

def get_default_faction(country_id, country_name):
    """Assign default factions for countries not in enhanced data"""
    
    # NATO and US allies (Western democracies and allies)
    nato_countries = {
        'Netherlands', 'Belgium', 'Denmark', 'Norway', 'Sweden', 'Finland', 'Spain', 'Portugal', 'Greece', 'Czechia', 'Slovakia', 'Hungary', 'Romania', 'Bulgaria', 'Croatia', 'Slovenia', 'Estonia', 'Latvia', 'Lithuania', 'Montenegro', 'Albania', 'North Macedonia', 'Serbia', 'Bosnia and Herzegovina', 'Kosovo', 'Moldova', 'Georgia', 'Armenia', 'Azerbaijan', 'Kyrgyzstan', 'Tajikistan', 'Uzbekistan', 'Turkmenistan', 'Mongolia', 'South Korea', 'Taiwan', 'Philippines', 'Thailand', 'Singapore', 'Malaysia', 'Indonesia', 'Vietnam', 'New Zealand', 'Fiji', 'Papua New Guinea', 'New Caledonia', 'French Polynesia', 'Tonga', 'Samoa', 'Kiribati', 'Vanuatu', 'Solomon Islands', 'Nauru', 'Tuvalu', 'Palau', 'Marshall Islands', 'Micronesia', 'Cook Islands', 'Niue', 'Tokelau', 'American Samoa', 'Guam', 'Northern Mariana Islands', 'U.S. Virgin Islands', 'Puerto Rico', 'Guatemala', 'Belize', 'El Salvador', 'Honduras', 'Nicaragua', 'Costa Rica', 'Panama', 'Colombia', 'Venezuela', 'Guyana', 'Suriname', 'French Guiana', 'Ecuador', 'Peru', 'Bolivia', 'Chile', 'Paraguay', 'Uruguay', 'Falkland Islands', 'South Georgia and South Sandwich Islands', 'British Indian Ocean Territory', 'Cocos (Keeling) Islands', 'Christmas Island', 'Norfolk Island', 'Iceland', 'Seychelles', 'Trinidad and Tobago', 'Grenada', 'Saint Vincent and the Grenadines', 'Barbados', 'Saint Lucia', 'Dominica', 'Antigua and Barbuda', 'Saint Kitts and Nevis', 'Jamaica', 'Mauritius', 'Comoros', 'São Tomé and Principe', 'Cabo Verde', 'Malta', 'Aland', 'Indian Ocean Territories', 'Iceland', 'Bahrain', 'Spratly Islands', 'Clipperton Island', 'Macao S.A.R', 'Bajo Nuevo Bank (Petrel Is.)', 'Serranilla Bank', 'Scarborough Reef'
    }
    
    # Russia bloc allies (CSTO and Russian allies)
    russia_bloc = {
        'Armenia', 'Azerbaijan', 'Belarus', 'Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'Uzbekistan', 'Turkmenistan', 'Moldova', 'Georgia'
    }
    
    # China bloc allies (SCO and Chinese allies)
    china_bloc = {
        'North Korea', 'Iran', 'Syria', 'Lebanon', 'Jordan', 'Iraq', 'Kuwait', 'Qatar', 'United Arab Emirates', 'Oman', 'Yemen', 'Bahrain', 'Laos', 'Myanmar', 'Cambodia', 'Bangladesh', 'Nepal', 'Sri Lanka', 'Maldives', 'Bhutan'
    }
    
    # Swing states (strategically neutral or non-aligned)
    swing_states = {
        'India', 'Pakistan', 'Israel', 'Brazil', 'Saudi Arabia', 'Egypt', 'Argentina', 'South Africa', 'Nigeria', 'Kenya', 'Ethiopia', 'United Republic of Tanzania', 'Uganda', 'Ghana', 'Ivory Coast', 'Senegal', 'Mali', 'Burkina Faso', 'Niger', 'Chad', 'Sudan', 'Eritrea', 'Djibouti', 'Somalia', 'Cameroon', 'Central African Republic', 'Republic of the Congo', 'Democratic Republic of the Congo', 'Angola', 'Zambia', 'Zimbabwe', 'Botswana', 'Namibia', 'Lesotho', 'eSwatini', 'Madagascar', 'Mauritius', 'Seychelles', 'Comoros', 'Mayotte', 'Réunion', 'Malawi', 'Mozambique'
    }
    
    # Antarctica territories (gray)
    antarctica_territories = {
        'Antarctica'
    }
    
    if country_name in nato_countries:
        return "NATO"
    elif country_name in russia_bloc:
        return "RUSSIA_BLOC"
    elif country_name in china_bloc:
        return "CHINA_BLOC"
    elif country_name in swing_states:
        return "SWING"
    elif country_name in antarctica_territories:
        return "NEUTRAL"  # Gray for Antarctica
    else:
        return "NEUTRAL"  # Default gray for unknown/less important
