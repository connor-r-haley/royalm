#!/usr/bin/env python3
"""
World Leaders Service - Important People and Events Data
Provides detailed profiles of world leaders, influencers, and recent events
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WorldLeadersService:
    """Service providing detailed profiles of world leaders and important people"""
    
    def __init__(self):
        self.leaders = self._load_leaders_data()
        self.recent_events = self._load_recent_events()
        self.ongoing_storylines = self._load_ongoing_storylines()
        self.controversies = self._load_controversies()
        logger.info("World Leaders Service initialized with comprehensive leader data")
    
    def _load_leaders_data(self) -> Dict[str, Dict[str, Any]]:
        """Load detailed profiles of world leaders and important people"""
        return {
            "donald_trump": {
                "name": "Donald Trump",
                "title": "Former President of the United States",
                "country": "US",
                "party": "Republican",
                "personality_traits": ["combative", "transactional", "nationalist", "populist"],
                "key_policies": ["America First", "trade protectionism", "immigration restrictions", "energy independence"],
                "recent_actions": [
                    "Alaskan summit with Putin that went nowhere",
                    "Pressure on Ukraine to accept territorial concessions",
                    "Continued claims of 2020 election fraud",
                    "Legal battles in multiple states"
                ],
                "relationships": {
                    "vladimir_putin": "transactional partnership",
                    "xi_jinping": "trade war adversary",
                    "volodymyr_zelensky": "conditional support"
                },
                "current_status": "presidential candidate",
                "influence_level": 95,  # 0-100
                "controversy_level": 90,  # 0-100
                "media_presence": "high"
            },
            "vladimir_putin": {
                "name": "Vladimir Putin",
                "title": "President of Russia",
                "country": "RU",
                "party": "United Russia",
                "personality_traits": ["calculating", "authoritarian", "strategic", "ruthless"],
                "key_policies": ["Russian resurgence", "Eurasian integration", "energy dominance", "cyber warfare"],
                "recent_actions": [
                    "Alaskan summit with Trump seeking leverage",
                    "Continued Ukraine invasion",
                    "Nuclear threats to NATO",
                    "Expansion of BRICS influence"
                ],
                "relationships": {
                    "donald_trump": "transactional partnership",
                    "xi_jinping": "strategic ally",
                    "volodymyr_zelensky": "enemy"
                },
                "current_status": "president",
                "influence_level": 90,
                "controversy_level": 95,
                "media_presence": "high"
            },
            "xi_jinping": {
                "name": "Xi Jinping",
                "title": "President of China",
                "country": "CN",
                "party": "Chinese Communist Party",
                "personality_traits": ["authoritarian", "nationalist", "long-term planner", "centralizing"],
                "key_policies": ["Chinese Dream", "Belt and Road Initiative", "military modernization", "tech dominance"],
                "recent_actions": [
                    "Continued Taiwan pressure",
                    "South China Sea expansion",
                    "Belt and Road debt diplomacy",
                    "AI and quantum computing investment"
                ],
                "relationships": {
                    "vladimir_putin": "strategic ally",
                    "donald_trump": "trade war adversary",
                    "tsai_ing_wen": "adversary"
                },
                "current_status": "president",
                "influence_level": 95,
                "controversy_level": 85,
                "media_presence": "medium"
            },
            "volodymyr_zelensky": {
                "name": "Volodymyr Zelensky",
                "title": "President of Ukraine",
                "country": "UA",
                "party": "Servant of the People",
                "personality_traits": ["charismatic", "resilient", "media-savvy", "determined"],
                "key_policies": ["EU integration", "NATO membership", "democratic reform", "anti-corruption"],
                "recent_actions": [
                    "Resisting Russian invasion",
                    "Seeking Western military aid",
                    "Rejecting territorial concessions",
                    "International diplomacy tour"
                ],
                "relationships": {
                    "joe_biden": "ally",
                    "vladimir_putin": "enemy",
                    "donald_trump": "conditional support"
                },
                "current_status": "president",
                "influence_level": 80,
                "controversy_level": 60,
                "media_presence": "very high"
            },
            "joe_biden": {
                "name": "Joe Biden",
                "title": "President of the United States",
                "country": "US",
                "party": "Democratic",
                "personality_traits": ["diplomatic", "experienced", "centrist", "compassionate"],
                "key_policies": ["NATO unity", "climate action", "infrastructure investment", "democratic values"],
                "recent_actions": [
                    "Supporting Ukraine with military aid",
                    "NATO expansion to Finland and Sweden",
                    "Climate summit leadership",
                    "Economic sanctions on Russia"
                ],
                "relationships": {
                    "volodymyr_zelensky": "ally",
                    "vladimir_putin": "adversary",
                    "emmanuel_macron": "ally"
                },
                "current_status": "president",
                "influence_level": 90,
                "controversy_level": 70,
                "media_presence": "high"
            },
            "emmanuel_macron": {
                "name": "Emmanuel Macron",
                "title": "President of France",
                "country": "FR",
                "party": "La République En Marche!",
                "personality_traits": ["intellectual", "reformist", "Europeanist", "confident"],
                "key_policies": ["EU integration", "nuclear energy", "digital sovereignty", "strategic autonomy"],
                "recent_actions": [
                    "EU defense integration",
                    "Nuclear energy expansion",
                    "Mediation attempts with Putin",
                    "African diplomacy"
                ],
                "relationships": {
                    "joe_biden": "ally",
                    "vladimir_putin": "diplomatic contact",
                    "olaf_scholz": "EU partner"
                },
                "current_status": "president",
                "influence_level": 75,
                "controversy_level": 65,
                "media_presence": "medium"
            },
            "olaf_scholz": {
                "name": "Olaf Scholz",
                "title": "Chancellor of Germany",
                "country": "DE",
                "party": "Social Democratic Party",
                "personality_traits": ["cautious", "pragmatic", "consensus-builder", "reserved"],
                "key_policies": ["energy transition", "EU unity", "economic stability", "social democracy"],
                "recent_actions": [
                    "Ending Russian energy dependence",
                    "Military modernization",
                    "EU fiscal policy",
                    "Climate transition funding"
                ],
                "relationships": {
                    "joe_biden": "ally",
                    "emmanuel_macron": "EU partner",
                    "vladimir_putin": "former energy partner"
                },
                "current_status": "chancellor",
                "influence_level": 70,
                "controversy_level": 50,
                "media_presence": "medium"
            },
            "narendra_modi": {
                "name": "Narendra Modi",
                "title": "Prime Minister of India",
                "country": "IN",
                "party": "Bharatiya Janata Party",
                "personality_traits": ["nationalist", "charismatic", "reformist", "Hindu nationalist"],
                "key_policies": ["Make in India", "Digital India", "Act East Policy", "strategic autonomy"],
                "recent_actions": [
                    "Quad participation",
                    "BRICS leadership",
                    "Space program expansion",
                    "Economic reforms"
                ],
                "relationships": {
                    "joe_biden": "strategic partner",
                    "xi_jinping": "border tensions",
                    "vladimir_putin": "energy partner"
                },
                "current_status": "prime minister",
                "influence_level": 85,
                "controversy_level": 75,
                "media_presence": "high"
            },
            "fumio_kishida": {
                "name": "Fumio Kishida",
                "title": "Prime Minister of Japan",
                "country": "JP",
                "party": "Liberal Democratic Party",
                "personality_traits": ["diplomatic", "moderate", "consensus-builder", "experienced"],
                "key_policies": ["defense modernization", "economic revitalization", "Quad cooperation", "nuclear energy"],
                "recent_actions": [
                    "Military budget increase",
                    "Quad summit hosting",
                    "Nuclear energy restart",
                    "Economic stimulus packages"
                ],
                "relationships": {
                    "joe_biden": "ally",
                    "xi_jinping": "adversary",
                    "narendra_modi": "Quad partner"
                },
                "current_status": "prime minister",
                "influence_level": 70,
                "controversy_level": 40,
                "media_presence": "medium"
            }
        }
    
    def _load_recent_events(self) -> List[Dict[str, Any]]:
        """Load recent world events that should be referenced"""
        return [
            {
                "id": "trump_putin_alaska_summit",
                "title": "Trump-Putin Alaskan Summit",
                "date": "2024-01-15",
                "description": "Donald Trump and Vladimir Putin held a secret summit in Alaska that went nowhere, but elevated Putin's international standing and led to Trump pressuring Ukraine to accept territorial concessions.",
                "participants": ["donald_trump", "vladimir_putin"],
                "impact": "high",
                "ongoing_effects": ["Ukraine pressure", "Putin elevation", "US-Russia relations"]
            },
            {
                "id": "ukraine_counteroffensive_failure",
                "title": "Ukraine's Failed Counteroffensive",
                "date": "2024-06-01",
                "description": "Ukraine's much-anticipated counteroffensive failed to achieve significant gains, leading to war fatigue in the West and pressure for negotiations.",
                "participants": ["volodymyr_zelensky", "vladimir_putin"],
                "impact": "high",
                "ongoing_effects": ["Western war fatigue", "Negotiation pressure", "Military stalemate"]
            },
            {
                "id": "china_taiwan_pressure",
                "title": "China Increases Taiwan Pressure",
                "date": "2024-07-01",
                "description": "China has intensified military pressure around Taiwan, including increased air incursions and naval exercises.",
                "participants": ["xi_jinping", "tsai_ing_wen"],
                "impact": "medium",
                "ongoing_effects": ["Regional tension", "US response", "Taiwan defense"]
            },
            {
                "id": "nato_finland_sweden",
                "title": "Finland and Sweden Join NATO",
                "date": "2024-04-01",
                "description": "Finland and Sweden officially joined NATO, significantly expanding the alliance's northern flank against Russia.",
                "participants": ["joe_biden", "vladimir_putin"],
                "impact": "high",
                "ongoing_effects": ["NATO expansion", "Russian response", "Baltic security"]
            }
        ]
    
    def _load_ongoing_storylines(self) -> List[Dict[str, Any]]:
        """Load ongoing geopolitical storylines"""
        return [
            {
                "id": "ukraine_war",
                "title": "Ukraine-Russia War",
                "status": "active",
                "key_players": ["volodymyr_zelensky", "vladimir_putin", "joe_biden"],
                "current_phase": "stalemate",
                "potential_developments": ["peace talks", "escalation", "frozen conflict"]
            },
            {
                "id": "us_china_competition",
                "title": "US-China Great Power Competition",
                "status": "intensifying",
                "key_players": ["joe_biden", "xi_jinping", "donald_trump"],
                "current_phase": "economic and technological competition",
                "potential_developments": ["trade war escalation", "tech decoupling", "military confrontation"]
            },
            {
                "id": "energy_transition",
                "title": "Global Energy Transition",
                "status": "accelerating",
                "key_players": ["emmanuel_macron", "olaf_scholz", "joe_biden"],
                "current_phase": "renewable expansion",
                "potential_developments": ["nuclear renaissance", "fossil fuel decline", "energy security concerns"]
            },
            {
                "id": "ai_arms_race",
                "title": "AI and Quantum Computing Race",
                "status": "emerging",
                "key_players": ["xi_jinping", "joe_biden", "narendra_modi"],
                "current_phase": "research and development",
                "potential_developments": ["breakthroughs", "military applications", "economic disruption"]
            }
        ]
    
    def _load_controversies(self) -> List[Dict[str, Any]]:
        """Load current controversies and scandals"""
        return [
            {
                "id": "trump_legal_battles",
                "title": "Trump's Multiple Legal Battles",
                "involved": ["donald_trump"],
                "type": "legal",
                "severity": "high",
                "impact": "US politics",
                "description": "Multiple criminal and civil cases against Trump affecting his presidential campaign."
            },
            {
                "id": "putin_opposition_crackdown",
                "title": "Putin's Opposition Crackdown",
                "involved": ["vladimir_putin"],
                "type": "human rights",
                "severity": "high",
                "impact": "Russian politics",
                "description": "Continued suppression of political opposition and independent media in Russia."
            },
            {
                "id": "china_uyghur_controversy",
                "title": "China's Uyghur Treatment",
                "involved": ["xi_jinping"],
                "type": "human rights",
                "severity": "high",
                "impact": "China-West relations",
                "description": "Allegations of human rights abuses against Uyghur Muslims in Xinjiang."
            },
            {
                "id": "modi_hindu_nationalism",
                "title": "Modi's Hindu Nationalism",
                "involved": ["narendra_modi"],
                "type": "religious",
                "severity": "medium",
                "impact": "Indian society",
                "description": "Promotion of Hindu nationalist policies affecting religious minorities."
            }
        ]
    
    def get_leader(self, leader_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed profile of a specific leader"""
        return self.leaders.get(leader_id)
    
    def get_country_leaders(self, country_code: str) -> List[Dict[str, Any]]:
        """Get all leaders from a specific country"""
        return [
            leader for leader in self.leaders.values()
            if leader["country"] == country_code.upper()
        ]
    
    def get_recent_events(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get recent events within specified timeframe"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        return [
            event for event in self.recent_events
            if datetime.strptime(event["date"], "%Y-%m-%d") >= cutoff_date
        ]
    
    def get_ongoing_storylines(self) -> List[Dict[str, Any]]:
        """Get all active geopolitical storylines"""
        return [storyline for storyline in self.ongoing_storylines if storyline["status"] == "active"]
    
    def get_controversies(self, min_severity: str = "medium") -> List[Dict[str, Any]]:
        """Get controversies above specified severity level"""
        severity_levels = {"low": 1, "medium": 2, "high": 3}
        min_level = severity_levels.get(min_severity, 1)
        return [
            controversy for controversy in self.controversies
            if severity_levels.get(controversy["severity"], 1) >= min_level
        ]
    
    def get_leader_relationships(self, leader_id: str) -> Dict[str, str]:
        """Get relationships for a specific leader"""
        leader = self.get_leader(leader_id)
        return leader.get("relationships", {}) if leader else {}
    
    def get_related_events(self, leader_id: str) -> List[Dict[str, Any]]:
        """Get events related to a specific leader"""
        return [
            event for event in self.recent_events
            if leader_id in event.get("participants", [])
        ]

# Global instance
world_leaders_service = WorldLeadersService()

