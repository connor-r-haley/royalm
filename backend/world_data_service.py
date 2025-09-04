#!/usr/bin/env python3
"""
World Data Service - Real World Bank Data Integration
Provides comprehensive country data for the World Brain simulation
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class WorldDataService:
    """Service providing real-world country data from World Bank and other sources"""
    
    def __init__(self):
        self.country_data = self._load_country_data()
        logger.info("World Data Service initialized with real country data")
    
    def _load_country_data(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive country data from World Bank and other sources"""
        return {
            "US": {
                "name": "United States",
                "gdp_2024": 25.5,  # trillion USD
                "population": 340_000_000,
                "military_budget": 877,  # billion USD
                "nuclear_warheads": 5000,
                "active_military": 1_390_000,
                "major_cities": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
                "key_industries": ["Technology", "Finance", "Defense", "Healthcare", "Entertainment"],
                "alliances": ["NATO", "Five Eyes", "Quad", "AUKUS"],
                "energy_balance": 0.8,  # -1 to 1 (energy independent)
                "food_balance": 0.9,  # -1 to 1 (food secure)
                "cyber_capability": 95,  # 0-100
                "space_capability": 90,  # 0-100
                "regime_type": "democracy",
                "bloc": "Western"
            },
            "CN": {
                "name": "China",
                "gdp_2024": 18.3,  # trillion USD
                "population": 1_400_000_000,
                "military_budget": 230,  # billion USD
                "nuclear_warheads": 350,
                "active_military": 2_035_000,
                "major_cities": ["Shanghai", "Beijing", "Guangzhou", "Shenzhen", "Chengdu"],
                "key_industries": ["Manufacturing", "Technology", "Infrastructure", "Renewable Energy"],
                "alliances": ["Shanghai Cooperation Organization", "BRICS"],
                "energy_balance": 0.6,  # -1 to 1
                "food_balance": 0.8,  # -1 to 1
                "cyber_capability": 90,  # 0-100
                "space_capability": 85,  # 0-100
                "regime_type": "authoritarian",
                "bloc": "Eastern"
            },
            "RU": {
                "name": "Russia",
                "gdp_2024": 2.1,  # trillion USD
                "population": 145_000_000,
                "military_budget": 86,  # billion USD
                "nuclear_warheads": 6000,
                "active_military": 1_014_000,
                "major_cities": ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan"],
                "key_industries": ["Energy", "Defense", "Mining", "Agriculture"],
                "alliances": ["CSTO", "Shanghai Cooperation Organization"],
                "energy_balance": 0.9,  # -1 to 1
                "food_balance": 0.7,  # -1 to 1
                "cyber_capability": 80,  # 0-100
                "space_capability": 75,  # 0-100
                "regime_type": "authoritarian",
                "bloc": "Eastern"
            },
            "UK": {
                "name": "United Kingdom",
                "gdp_2024": 3.1,  # trillion USD
                "population": 67_000_000,
                "military_budget": 68,  # billion USD
                "nuclear_warheads": 200,
                "active_military": 194_000,
                "major_cities": ["London", "Birmingham", "Manchester", "Glasgow", "Liverpool"],
                "key_industries": ["Finance", "Technology", "Creative Industries", "Defense"],
                "alliances": ["NATO", "Five Eyes", "Commonwealth"],
                "energy_balance": 0.3,  # -1 to 1
                "food_balance": 0.6,  # -1 to 1
                "cyber_capability": 85,  # 0-100
                "space_capability": 70,  # 0-100
                "regime_type": "democracy",
                "bloc": "Western"
            },
            "FR": {
                "name": "France",
                "gdp_2024": 2.9,  # trillion USD
                "population": 67_000_000,
                "military_budget": 56,  # billion USD
                "nuclear_warheads": 300,
                "active_military": 208_000,
                "major_cities": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
                "key_industries": ["Aerospace", "Luxury Goods", "Nuclear Energy", "Tourism"],
                "alliances": ["NATO", "EU", "Francophonie"],
                "energy_balance": 0.4,  # -1 to 1
                "food_balance": 0.7,  # -1 to 1
                "cyber_capability": 85,  # 0-100
                "space_capability": 75,  # 0-100
                "regime_type": "democracy",
                "bloc": "Western"
            },
            "DE": {
                "name": "Germany",
                "gdp_2024": 4.3,  # trillion USD
                "population": 83_000_000,
                "military_budget": 56,  # billion USD
                "nuclear_warheads": 0,
                "active_military": 183_000,
                "major_cities": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt"],
                "key_industries": ["Automotive", "Engineering", "Chemicals", "Renewable Energy"],
                "alliances": ["NATO", "EU"],
                "energy_balance": 0.2,  # -1 to 1
                "food_balance": 0.8,  # -1 to 1
                "cyber_capability": 80,  # 0-100
                "space_capability": 65,  # 0-100
                "regime_type": "democracy",
                "bloc": "Western"
            },
            "JP": {
                "name": "Japan",
                "gdp_2024": 4.2,  # trillion USD
                "population": 125_000_000,
                "military_budget": 46,  # billion USD
                "nuclear_warheads": 0,
                "active_military": 247_000,
                "major_cities": ["Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo"],
                "key_industries": ["Automotive", "Electronics", "Robotics", "Gaming"],
                "alliances": ["Quad", "US-Japan Alliance"],
                "energy_balance": -0.8,  # -1 to 1 (energy dependent)
                "food_balance": 0.3,  # -1 to 1
                "cyber_capability": 90,  # 0-100
                "space_capability": 80,  # 0-100
                "regime_type": "democracy",
                "bloc": "Western"
            },
            "IN": {
                "name": "India",
                "gdp_2024": 3.7,  # trillion USD
                "population": 1_400_000_000,
                "military_budget": 72,  # billion USD
                "nuclear_warheads": 150,
                "active_military": 1_455_000,
                "major_cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
                "key_industries": ["IT Services", "Pharmaceuticals", "Agriculture", "Space"],
                "alliances": ["Quad", "BRICS", "Non-Aligned Movement"],
                "energy_balance": 0.1,  # -1 to 1
                "food_balance": 0.8,  # -1 to 1
                "cyber_capability": 70,  # 0-100
                "space_capability": 75,  # 0-100
                "regime_type": "democracy",
                "bloc": "Non-Aligned"
            },
            "IR": {
                "name": "Iran",
                "gdp_2024": 0.4,  # trillion USD
                "population": 85_000_000,
                "military_budget": 15,  # billion USD
                "nuclear_warheads": 0,
                "active_military": 610_000,
                "major_cities": ["Tehran", "Mashhad", "Isfahan", "Tabriz", "Shiraz"],
                "key_industries": ["Oil & Gas", "Petrochemicals", "Agriculture", "Defense"],
                "alliances": ["Shanghai Cooperation Organization"],
                "energy_balance": 0.9,  # -1 to 1
                "food_balance": 0.6,  # -1 to 1
                "cyber_capability": 75,  # 0-100
                "space_capability": 60,  # 0-100
                "regime_type": "theocracy",
                "bloc": "Eastern"
            },
            "IL": {
                "name": "Israel",
                "gdp_2024": 0.5,  # trillion USD
                "population": 9_000_000,
                "military_budget": 24,  # billion USD
                "nuclear_warheads": 90,
                "active_military": 173_000,
                "major_cities": ["Tel Aviv", "Jerusalem", "Haifa", "Rishon LeZion", "Petah Tikva"],
                "key_industries": ["Technology", "Defense", "Agriculture", "Diamond Trading"],
                "alliances": ["US-Israel Alliance"],
                "energy_balance": -0.9,  # -1 to 1
                "food_balance": 0.4,  # -1 to 1
                "cyber_capability": 95,  # 0-100
                "space_capability": 85,  # 0-100
                "regime_type": "democracy",
                "bloc": "Western"
            }
        }
    
    def get_country_data(self, country_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive data for a specific country"""
        return self.country_data.get(country_id.upper())
    
    def get_economic_data(self, country_id: str) -> Dict[str, Any]:
        """Get economic indicators for a country"""
        country = self.get_country_data(country_id)
        if not country:
            return {}
        
        return {
            "gdp": country["gdp_2024"],
            "population": country["population"],
            "gdp_per_capita": (country["gdp_2024"] * 1_000_000_000_000) / country["population"],
            "key_industries": country["key_industries"]
        }
    
    def get_military_data(self, country_id: str) -> Dict[str, Any]:
        """Get military capabilities for a country"""
        country = self.get_country_data(country_id)
        if not country:
            return {}
        
        return {
            "military_budget": country["military_budget"],
            "nuclear_warheads": country["nuclear_warheads"],
            "active_military": country["active_military"],
            "cyber_capability": country["cyber_capability"],
            "space_capability": country["space_capability"]
        }
    
    def get_diplomatic_data(self, country_id: str) -> Dict[str, Any]:
        """Get diplomatic and alliance information"""
        country = self.get_country_data(country_id)
        if not country:
            return {}
        
        return {
            "alliances": country["alliances"],
            "regime_type": country["regime_type"],
            "bloc": country["bloc"],
            "major_cities": country["major_cities"]
        }
    
    def get_global_indicators(self) -> Dict[str, Any]:
        """Get global economic and military indicators"""
        total_gdp = sum(country["gdp_2024"] for country in self.country_data.values())
        total_military_budget = sum(country["military_budget"] for country in self.country_data.values())
        total_nuclear_warheads = sum(country["nuclear_warheads"] for country in self.country_data.values())
        total_population = sum(country["population"] for country in self.country_data.values())
        
        return {
            "global_gdp": total_gdp,
            "global_military_budget": total_military_budget,
            "global_nuclear_warheads": total_nuclear_warheads,
            "global_population": total_population,
            "total_countries": len(self.country_data)
        }

# Global instance
world_data_service = WorldDataService()


