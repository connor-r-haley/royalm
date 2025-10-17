#!/usr/bin/env python3
"""
World Data Service - Real World Bank Data Integration
Provides comprehensive country data for the World Brain simulation
"""

import logging
from typing import Dict, Any, List, Optional
import json
import os

logger = logging.getLogger(__name__)

class WorldDataService:
    """Service providing real-world country data from World Bank and other sources"""
    
    def __init__(self):
        self.country_data = self._load_country_data()
        self.complete_country_data = self._build_complete_dataset()
        logger.info("World Data Service initialized with real country data")
    
    def _load_country_data(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive country data.

        Priority:
        1) If world-countries.json exists (large canonical dataset), load and normalize it to our schema
        2) Fall back to the compact, curated in-file dictionary below
        """
        file_path = os.path.join(os.path.dirname(__file__), "world-countries.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                normalized: Dict[str, Dict[str, Any]] = {}

                def get_first(d: Dict[str, Any], keys: List[str], default=None):
                    for k in keys:
                        if k in d and d[k] not in (None, ""):
                            return d[k]
                    return default

                def to_num(v, default=0):
                    try:
                        if isinstance(v, (int, float)):
                            return v
                        if isinstance(v, str):
                            return float(v.replace(",", "").strip())
                    except Exception:
                        return default
                    return default

                # Handle common shapes: FeatureCollection or array/dict of country records
                features = None
                if isinstance(raw, dict) and isinstance(raw.get("features"), list):
                    features = raw["features"]
                if features is not None:
                    for feat in features:
                        if not isinstance(feat, dict):
                            continue
                        props = feat.get("properties") or {}
                        # IDs from ISO codes or fallback to name
                        cid = get_first(props, [
                            "ISO3166-1-Alpha-3", "iso_a3", "alpha3", "cca3", "id"
                        ])
                        name = get_first(props, ["name", "NAME", "NAME_EN", "official"]) or None
                        if not cid and name:
                            cid = name
                        if not cid:
                            continue
                        cid = str(cid).upper()

                        normalized[cid] = {
                            "name": name or cid,
                            # economic fields will be overlaid later (WB/live)
                            "gdp_2024": 0,
                            "population": 0,
                            "military_budget": 0,
                            "nuclear_warheads": 0,
                            "regime_type": "Unknown",
                            "bloc": "Unknown",
                        }
                else:
                    # Raw may be a list or dict of simple records
                    items = raw.items() if isinstance(raw, dict) else enumerate(raw)
                    for _, rec in items:
                        if not isinstance(rec, dict):
                            continue
                        # Try a variety of common id/name/iso fields
                        cid = get_first(
                            rec,
                            [
                                "country_id", "id", "iso", "ISO", "code", "cca3", "cca2",
                                "alpha3", "alpha2", "iso_a3", "iso_a2"
                            ],
                            None,
                        )
                        name = get_first(rec, ["name", "country", "Country", "official"], None)
                        if not cid and name:
                            cid = name
                        if not cid:
                            continue
                        cid = str(cid).upper()

                        gdp = to_num(get_first(rec, ["gdp_2024", "gdp", "GDP"]))
                        pop = int(to_num(get_first(rec, ["population", "Population"])) or 0)
                        nukes = int(to_num(get_first(rec, ["nuclear_warheads", "nukes", "nuclear"])) or 0)
                        mil = to_num(get_first(rec, ["military_budget", "military", "defense_budget"]))
                        regime = get_first(rec, ["regime_type", "regime", "government"], "Unknown")
                        bloc = get_first(rec, ["bloc", "alliance", "alignment"], "Unknown")

                        normalized[cid] = {
                            "name": name or cid,
                            "gdp_2024": gdp,
                            "population": pop,
                            "military_budget": mil,
                            "nuclear_warheads": nukes,
                            "regime_type": regime,
                            "bloc": bloc,
                        }

                if len(normalized) > 10:
                    logger.info("Loaded %d countries from world-countries.json", len(normalized))
                    return normalized
                else:
                    logger.warning("world-countries.json loaded but contained <10 entries; using fallback")
            except Exception as e:
                logger.warning("Failed to parse world-countries.json; using fallback: %s", e)

        # Fallback curated set (ensures app works without the large dataset present)
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

    def _build_complete_dataset(self) -> Dict[str, Dict[str, Any]]:
        """Build a comprehensive dataset by merging a baseline borders file with curated data.

        - Baseline: backend/borders-enhanced-detailed.json (provides ~200 countries)
        - Overlay: self.country_data (adds richer fields for known countries)
        """
        baseline: Dict[str, Dict[str, Any]] = {}
        borders_path = os.path.join(os.path.dirname(__file__), "borders-enhanced-detailed.json")
        try:
            with open(borders_path, "r", encoding="utf-8") as f:
                gj = json.load(f)
            for feat in (gj.get("features") or []):
                props = feat.get("properties") or {}
                iso3_code = props.get("ISO3166-1-Alpha-3") or props.get("iso_a3") or props.get("alpha3")
                iso3_code = str(iso3_code).upper() if iso3_code else None
                if iso3_code and (len(iso3_code) != 3 or not iso3_code.isalpha()):
                    iso3_code = None
                cid = (
                    str(
                        (iso3_code)
                        or props.get("id")
                        or props.get("iso_a2")
                        or props.get("name")
                        or ""
                    ).upper()
                )
                if not cid:
                    continue
                name = props.get("name") or cid
                if cid not in baseline:
                    baseline[cid] = {
                        "name": name,
                        "gdp_2024": 0,
                        "population": 0,
                        "military_budget": 0,
                        "nuclear_warheads": 0,
                        "regime_type": "Unknown",
                        "bloc": "Unknown",
                        "iso3": iso3_code,
                    }
        except Exception as e:
            logger.warning("Failed to read borders file for baseline: %s", e)

        # Helper to overlay an entry
        def overlay(cid: str, src: Dict[str, Any]):
            if not cid:
                return
            if cid not in baseline:
                baseline[cid] = {
                    "name": src.get("name", cid),
                    "gdp_2024": 0,
                    "population": 0,
                    "military_budget": 0,
                    "nuclear_warheads": 0,
                    "regime_type": "Unknown",
                    "bloc": "Unknown",
                }
            dst = baseline[cid]
            dst["name"] = src.get("name", dst["name"]) or dst["name"]
            if src.get("gdp_2024") is not None:
                dst["gdp_2024"] = src.get("gdp_2024")
            if src.get("population") is not None:
                dst["population"] = src.get("population")
            if src.get("military_budget") is not None:
                dst["military_budget"] = src.get("military_budget")
            if src.get("nuclear_warheads") is not None:
                dst["nuclear_warheads"] = src.get("nuclear_warheads")
            if src.get("regime_type"):
                dst["regime_type"] = src.get("regime_type")
            if src.get("bloc"):
                dst["bloc"] = src.get("bloc")

        # Overlay curated data onto baseline using several key strategies
        for cid, rec in self.country_data.items():
            overlay(cid.upper(), rec)

        # Also attempt overlay by country name if IDs differ
        name_to_id = { (v.get("name") or k).upper(): k for k, v in baseline.items() }
        for cid, rec in self.country_data.items():
            nm = (rec.get("name") or cid).upper()
            if nm in name_to_id:
                overlay(name_to_id[nm], rec)

        logger.info("Complete country dataset built with %d entries", len(baseline))
        return baseline

    def get_all_countries(self) -> Dict[str, Dict[str, Any]]:
        return self.complete_country_data

# Global instance
world_data_service = WorldDataService()


