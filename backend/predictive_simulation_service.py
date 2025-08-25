"""
Predictive Simulation Service
Combines real-world news, historical patterns, and AI logic to predict WWIII scenarios
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random
import uuid
import os

from models import (
    PredictiveSimulation, TimelineEvent, WorldState, WorldEventType, 
    HistoricalPattern, SimulationMode, NewsSource, PredictiveHistoryTranscript
)

logger = logging.getLogger(__name__)

class PredictiveSimulationService:
    """Service for running predictive WWIII simulations"""
    
    def __init__(self):
        self.active_simulations: Dict[str, PredictiveSimulation] = {}
        self.news_sources: List[NewsSource] = self._initialize_news_sources()
        self.historical_patterns: Dict[HistoricalPattern, Dict[str, Any]] = self._initialize_historical_patterns()
        self.predictive_transcripts: List[PredictiveHistoryTranscript] = []
        self.chatgpt_service = None
        
        # Load Predictive History transcripts
        self._load_predictive_history_transcripts()
        
    def _initialize_news_sources(self) -> List[NewsSource]:
        """Initialize real-world news sources"""
        return [
            NewsSource(
                source_id="reuters",
                name="Reuters",
                url="https://www.reuters.com",
                region="global",
                bias_level=0.0,
                reliability_score=0.9,
                update_frequency="hourly"
            ),
            NewsSource(
                source_id="ap",
                name="Associated Press",
                url="https://apnews.com",
                region="global",
                bias_level=0.0,
                reliability_score=0.9,
                update_frequency="hourly"
            ),
            NewsSource(
                source_id="bbc_world",
                name="BBC World",
                url="https://www.bbc.com/news/world",
                region="global",
                bias_level=0.1,
                reliability_score=0.85,
                update_frequency="hourly"
            ),
            NewsSource(
                source_id="xinhua",
                name="Xinhua News",
                url="http://www.xinhuanet.com/english",
                region="china",
                bias_level=0.3,
                reliability_score=0.7,
                update_frequency="hourly"
            ),
            NewsSource(
                source_id="rt",
                name="RT News",
                url="https://www.rt.com",
                region="russia",
                bias_level=0.4,
                reliability_score=0.6,
                update_frequency="hourly"
            )
        ]
    
    def _initialize_historical_patterns(self) -> Dict[HistoricalPattern, Dict[str, Any]]:
        """Initialize historical patterns for predictive analysis"""
        return {
            HistoricalPattern.ROMAN_DECLINE: {
                "description": "Pattern of imperial overreach, internal decay, and external pressure",
                "modern_parallel": "US global hegemony facing challenges from rising powers",
                "indicators": ["military overextension", "economic decline", "internal division", "external threats"],
                "timeline": "5-15 years",
                "confidence": 0.8
            },
            HistoricalPattern.PERSIAN_EXPANSION: {
                "description": "Regional power expanding influence through proxy wars and alliances",
                "modern_parallel": "Iran's regional ambitions and proxy network",
                "indicators": ["proxy warfare", "alliance building", "regional influence", "nuclear ambitions"],
                "timeline": "2-8 years",
                "confidence": 0.7
            },
            HistoricalPattern.BYZANTINE_DIPLOMACY: {
                "description": "Complex diplomatic balancing between multiple powers",
                "modern_parallel": "EU's balancing act between US, Russia, and China",
                "indicators": ["diplomatic complexity", "multiple alliances", "economic interdependence", "strategic ambiguity"],
                "timeline": "3-10 years",
                "confidence": 0.6
            },
            HistoricalPattern.MONGOL_CONQUEST: {
                "description": "Rapid expansion through superior technology and organization",
                "modern_parallel": "China's Belt and Road Initiative and technological advancement",
                "indicators": ["economic expansion", "technological superiority", "infrastructure projects", "military modernization"],
                "timeline": "10-25 years",
                "confidence": 0.7
            },
            HistoricalPattern.OTTOMAN_DECLINE: {
                "description": "Gradual decline of empire through internal weakness and external pressure",
                "modern_parallel": "Russia's current trajectory and internal challenges",
                "indicators": ["economic stagnation", "military overreach", "internal corruption", "external isolation"],
                "timeline": "5-20 years",
                "confidence": 0.6
            },
            HistoricalPattern.COLD_WAR_ESCALATION: {
                "description": "Nuclear standoff between superpowers with proxy conflicts",
                "modern_parallel": "US-China-Russia nuclear triangle",
                "indicators": ["nuclear posturing", "proxy conflicts", "ideological competition", "arms race"],
                "timeline": "1-5 years",
                "confidence": 0.8
            }
        }
    
    def _load_predictive_history_transcripts(self):
        """Load and parse Predictive History transcripts"""
        try:
            transcript_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'predictive_history_transcripts.jsonl')
            
            if not os.path.exists(transcript_file):
                logger.warning(f"Predictive History transcripts file not found: {transcript_file}")
                return
            
            with open(transcript_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        if line.strip():
                            data = json.loads(line.strip())
                            
                            # Extract key information from transcript
                            transcript = PredictiveHistoryTranscript(
                                transcript_id=f"transcript_{line_num}",
                                date=datetime.now(),  # We don't have actual dates in the data
                                topic=data.get('title', 'Unknown Topic'),
                                historical_pattern=self._extract_historical_pattern(data.get('text', '')),
                                modern_parallel=self._extract_modern_parallel(data.get('text', '')),
                                prediction=self._extract_prediction(data.get('text', '')),
                                confidence=0.7,  # Default confidence
                                reasoning=data.get('text', '')[:1000],  # First 1000 chars as reasoning
                                applicable_countries=self._extract_applicable_countries(data.get('text', ''))
                            )
                            
                            self.predictive_transcripts.append(transcript)
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse transcript line {line_num}: {e}")
                    except Exception as e:
                        logger.warning(f"Error processing transcript line {line_num}: {e}")
            
            logger.info(f"Loaded {len(self.predictive_transcripts)} Predictive History transcripts")
            
        except Exception as e:
            logger.error(f"Error loading Predictive History transcripts: {e}")
    
    def _extract_historical_pattern(self, text: str) -> HistoricalPattern:
        """Extract historical pattern from transcript text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['roman', 'rome', 'empire', 'decline']):
            return HistoricalPattern.ROMAN_DECLINE
        elif any(word in text_lower for word in ['persian', 'iran', 'expansion', 'proxy']):
            return HistoricalPattern.PERSIAN_EXPANSION
        elif any(word in text_lower for word in ['byzantine', 'diplomacy', 'balancing']):
            return HistoricalPattern.BYZANTINE_DIPLOMACY
        elif any(word in text_lower for word in ['mongol', 'conquest', 'expansion']):
            return HistoricalPattern.MONGOL_CONQUEST
        elif any(word in text_lower for word in ['ottoman', 'decline', 'stagnation']):
            return HistoricalPattern.OTTOMAN_DECLINE
        elif any(word in text_lower for word in ['cold war', 'nuclear', 'escalation']):
            return HistoricalPattern.COLD_WAR_ESCALATION
        elif any(word in text_lower for word in ['napoleonic', 'napoleon', 'wars']):
            return HistoricalPattern.NAPOLEONIC_WARS
        elif any(word in text_lower for word in ['world war', 'wwi', 'wwii']):
            return HistoricalPattern.WORLD_WAR_ESCALATION
        else:
            return HistoricalPattern.ROMAN_DECLINE  # Default
    
    def _extract_modern_parallel(self, text: str) -> str:
        """Extract modern parallel from transcript text"""
        # Look for patterns that suggest modern parallels
        text_lower = text.lower()
        
        if 'united states' in text_lower or 'us' in text_lower:
            return "United States global hegemony and challenges"
        elif 'china' in text_lower or 'chinese' in text_lower:
            return "China's rise and Belt & Road Initiative"
        elif 'russia' in text_lower or 'russian' in text_lower:
            return "Russia's regional ambitions and challenges"
        elif 'europe' in text_lower or 'eu' in text_lower:
            return "European Union's diplomatic balancing"
        elif 'iran' in text_lower or 'persian' in text_lower:
            return "Iran's regional proxy network"
        else:
            return "Modern geopolitical dynamics"
    
    def _extract_prediction(self, text: str) -> str:
        """Extract prediction from transcript text"""
        # Look for predictive language
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['will', 'going to', 'likely', 'probably', 'inevitable']):
            # Extract sentence containing prediction
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['will', 'going to', 'likely', 'probably', 'inevitable']):
                    return sentence.strip()
        
        return "Historical patterns suggest continued geopolitical evolution"
    
    def _extract_applicable_countries(self, text: str) -> List[str]:
        """Extract applicable countries from transcript text"""
        countries = []
        text_lower = text.lower()
        
        country_mappings = {
            'united states': 'US', 'us': 'US', 'america': 'US',
            'china': 'CN', 'chinese': 'CN',
            'russia': 'RU', 'russian': 'RU',
            'europe': 'EU', 'european': 'EU',
            'iran': 'IR', 'persian': 'IR',
            'israel': 'IL', 'israeli': 'IL',
            'north korea': 'KP', 'korea': 'KP',
            'india': 'IN', 'indian': 'IN'
        }
        
        for country_name, country_code in country_mappings.items():
            if country_name in text_lower:
                countries.append(country_code)
        
        return list(set(countries))  # Remove duplicates
    
    def set_chatgpt_service(self, chatgpt_service):
        """Set ChatGPT service for enhanced AI logic"""
        self.chatgpt_service = chatgpt_service
        logger.info("ChatGPT service integrated with predictive simulation")
    
    async def _get_chatgpt_analysis(self, world_state: WorldState, current_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get ChatGPT analysis for current world state and patterns"""
        if not self.chatgpt_service:
            return {"analysis": "ChatGPT service not available", "confidence": 0.5}
        
        try:
            # Prepare context for ChatGPT
            context = f"""
            Current World State Analysis:
            - World Stability Index: {world_state.world_stability_index}
            - Nuclear Threat Level: {world_state.nuclear_threat_level}
            - Active Conflicts: {len(world_state.conflicts)}
            - Economic Indicators: {world_state.economic_indicators}
            
            Active Historical Patterns:
            {[f"- {p['pattern'].value}: {p['config']['description']}" for p in current_patterns]}
            
            Predictive History Insights:
            {[f"- {t.topic}: {t.prediction}" for t in self.predictive_transcripts[:5]]}
            
            Based on this analysis, what is the most likely next major geopolitical event?
            Consider historical patterns, current tensions, and predictive insights.
            """
            
            response = await self.chatgpt_service.analyze_geopolitical_situation(context)
            
            return {
                "analysis": response.get("analysis", "No analysis available"),
                "confidence": response.get("confidence", 0.5),
                "recommended_action": response.get("recommended_action", "Continue monitoring"),
                "timeframe": response.get("timeframe", "3-6 months")
            }
            
        except Exception as e:
            logger.error(f"Error getting ChatGPT analysis: {e}")
            return {"analysis": "Analysis failed", "confidence": 0.3}
    
    async def create_observe_the_end_simulation(self) -> PredictiveSimulation:
        """Create a new 'Observe the End' simulation"""
        simulation_id = str(uuid.uuid4())
        start_date = datetime.now()
        
        # Initialize world state with current real-world conditions
        initial_world_state = await self._get_current_world_state()
        
        simulation = PredictiveSimulation(
            simulation_id=simulation_id,
            mode=SimulationMode.OBSERVE_THE_END,
            start_date=start_date,
            world_states=[initial_world_state]
        )
        
        self.active_simulations[simulation_id] = simulation
        
        # Start the predictive simulation
        asyncio.create_task(self._run_predictive_simulation(simulation_id))
        
        return simulation
    
    async def _get_current_world_state(self) -> WorldState:
        """Get current real-world state based on latest news and data"""
        current_date = datetime.now()
        
        # This would integrate with real news APIs
        # For now, using realistic starting conditions
        return WorldState(
            date=current_date,
            countries={
                "US": {
                    "faction": "US",
                    "morale": 0.7,
                    "economic_strength": 0.8,
                    "military_strength": 0.9,
                    "diplomatic_influence": 0.8,
                    "nuclear_capability": True,
                    "allies": ["GB", "FR", "DE", "JP", "CA", "AU"]
                },
                "CN": {
                    "faction": "CN", 
                    "morale": 0.8,
                    "economic_strength": 0.9,
                    "military_strength": 0.7,
                    "diplomatic_influence": 0.6,
                    "nuclear_capability": True,
                    "allies": ["RU", "KP", "PK"]
                },
                "RU": {
                    "faction": "RU",
                    "morale": 0.6,
                    "economic_strength": 0.4,
                    "military_strength": 0.8,
                    "diplomatic_influence": 0.5,
                    "nuclear_capability": True,
                    "allies": ["CN", "IR", "BY"]
                },
                "EU": {
                    "faction": "EU",
                    "morale": 0.7,
                    "economic_strength": 0.8,
                    "military_strength": 0.6,
                    "diplomatic_influence": 0.7,
                    "nuclear_capability": False,
                    "allies": ["US", "GB", "CA"]
                },
                "IR": {
                    "faction": "IR",
                    "morale": 0.6,
                    "economic_strength": 0.3,
                    "military_strength": 0.5,
                    "diplomatic_influence": 0.4,
                    "nuclear_capability": True,
                    "allies": ["RU", "SY", "YE"]
                },
                "IL": {
                    "faction": "IL",
                    "morale": 0.8,
                    "economic_strength": 0.7,
                    "military_strength": 0.8,
                    "diplomatic_influence": 0.5,
                    "nuclear_capability": True,
                    "allies": ["US", "GB"]
                },
                "KP": {
                    "faction": "KP",
                    "morale": 0.5,
                    "economic_strength": 0.2,
                    "military_strength": 0.6,
                    "diplomatic_influence": 0.2,
                    "nuclear_capability": True,
                    "allies": ["CN", "RU"]
                }
            },
            alliances={
                "NATO": ["US", "GB", "FR", "DE", "CA", "IT", "ES", "PL"],
                "SCO": ["CN", "RU", "IN", "PK", "UZ", "KG"],
                "BRICS": ["CN", "RU", "IN", "BR", "ZA"],
                "OPEC+": ["RU", "SA", "IR", "IQ", "AE"]
            },
            conflicts=[
                {
                    "type": "proxy_war",
                    "location": "Ukraine",
                    "participants": ["RU", "US", "EU"],
                    "intensity": 0.7,
                    "start_date": "2022-02-24"
                },
                {
                    "type": "diplomatic_crisis",
                    "location": "Taiwan Strait",
                    "participants": ["CN", "US", "TW"],
                    "intensity": 0.6,
                    "start_date": "2022-08-01"
                }
            ],
            economic_indicators={
                "global_gdp_growth": 0.03,
                "inflation_rate": 0.05,
                "oil_price": 85.0,
                "usd_strength": 0.8,
                "cny_strength": 0.7
            },
            world_stability_index=0.6,
            nuclear_threat_level=0.4
        )
    
    async def _run_predictive_simulation(self, simulation_id: str):
        """Run the predictive simulation to generate timeline"""
        simulation = self.active_simulations[simulation_id]
        current_date = simulation.start_date
        
        # Generate timeline of events
        timeline_events = []
        world_states = [simulation.world_states[0]]
        
        # Simulate for up to 10 years
        end_date = current_date + timedelta(days=3650)
        
        while current_date < end_date:
            # Generate next event based on current world state
            next_event = await self._generate_next_event(current_date, world_states[-1])
            
            if next_event:
                timeline_events.append(next_event)
                
                # Update world state based on event
                new_world_state = await self._update_world_state(world_states[-1], next_event)
                world_states.append(new_world_state)
                
                # Check for end conditions
                if await self._check_end_conditions(new_world_state):
                    simulation.predicted_end_date = current_date
                    simulation.end_scenario = await self._determine_end_scenario(new_world_state)
                    break
            
            # Advance time (variable intervals based on event intensity)
            days_advance = random.randint(1, 30) if timeline_events else 1
            current_date += timedelta(days=days_advance)
        
        # Update simulation with results
        simulation.timeline_events = timeline_events
        simulation.world_states = world_states
        
        logger.info(f"Simulation {simulation_id} completed. Predicted end: {simulation.predicted_end_date}")
    
    async def _generate_next_event(self, date: datetime, world_state: WorldState) -> Optional[TimelineEvent]:
        """Generate the next logical event based on current world state"""
        # Analyze current conditions and apply historical patterns
        patterns = await self._identify_active_patterns(world_state)
        
        if not patterns:
            return None
        
        # Select most likely pattern to trigger next
        selected_pattern = max(patterns, key=lambda p: p["probability"])
        
        # Generate event based on pattern
        event = await self._create_event_from_pattern(date, selected_pattern, world_state)
        
        return event
    
    async def _identify_active_patterns(self, world_state: WorldState) -> List[Dict[str, Any]]:
        """Identify which historical patterns are currently active"""
        active_patterns = []
        
        # Check each pattern against current conditions
        for pattern, config in self.historical_patterns.items():
            probability = await self._calculate_pattern_probability(pattern, world_state)
            
            if probability > 0.3:  # Only consider patterns with >30% probability
                active_patterns.append({
                    "pattern": pattern,
                    "probability": probability,
                    "config": config
                })
        
        return active_patterns
    
    async def _calculate_pattern_probability(self, pattern: HistoricalPattern, world_state: WorldState) -> float:
        """Calculate probability of a historical pattern being active"""
        base_probability = 0.5
        
        if pattern == HistoricalPattern.ROMAN_DECLINE:
            # US decline indicators
            us_state = world_state.countries.get("US", {})
            if us_state.get("economic_strength", 0.8) < 0.7:
                base_probability += 0.2
            if us_state.get("military_strength", 0.9) < 0.8:
                base_probability += 0.1
            if world_state.world_stability_index < 0.6:
                base_probability += 0.2
                
        elif pattern == HistoricalPattern.COLD_WAR_ESCALATION:
            # Nuclear threat indicators
            if world_state.nuclear_threat_level > 0.5:
                base_probability += 0.3
            if len([c for c in world_state.countries.values() if c.get("nuclear_capability")]) >= 3:
                base_probability += 0.2
                
        elif pattern == HistoricalPattern.PERSIAN_EXPANSION:
            # Iran expansion indicators
            ir_state = world_state.countries.get("IR", {})
            if ir_state.get("diplomatic_influence", 0.4) > 0.5:
                base_probability += 0.2
            if "IR" in world_state.alliances.get("SCO", []):
                base_probability += 0.2
        
        return min(base_probability, 1.0)
    
    async def _create_event_from_pattern(self, date: datetime, pattern_data: Dict[str, Any], world_state: WorldState) -> TimelineEvent:
        """Create a timeline event based on a historical pattern"""
        pattern = pattern_data["pattern"]
        config = pattern_data["config"]
        
        # Generate event based on pattern type
        if pattern == HistoricalPattern.ROMAN_DECLINE:
            return await self._create_roman_decline_event(date, world_state)
        elif pattern == HistoricalPattern.COLD_WAR_ESCALATION:
            return await self._create_cold_war_event(date, world_state)
        elif pattern == HistoricalPattern.PERSIAN_EXPANSION:
            return await self._create_persian_expansion_event(date, world_state)
        else:
            return await self._create_generic_event(date, pattern, world_state)
    
    async def _create_roman_decline_event(self, date: datetime, world_state: WorldState) -> TimelineEvent:
        """Create event based on Roman decline pattern"""
        event_types = [
            WorldEventType.ECONOMIC_COLLAPSE,
            WorldEventType.MILITARY_ESCALATION,
            WorldEventType.DIPLOMATIC_CRISIS,
            WorldEventType.ALLIANCE_SHIFT
        ]
        
        event_type = random.choice(event_types)
        
        if event_type == WorldEventType.ECONOMIC_COLLAPSE:
            return TimelineEvent(
                event_id=str(uuid.uuid4()),
                date=date,
                event_type=event_type,
                title="US Dollar Crisis: Global Reserve Currency Under Threat",
                description="China and Russia announce new BRICS currency initiative, challenging US dollar dominance. Major economies begin diversifying reserves.",
                affected_countries=["US", "CN", "RU", "EU"],
                historical_pattern=HistoricalPattern.ROMAN_DECLINE,
                probability=0.7,
                impact_magnitude=0.8,
                ai_reasoning="Following Roman pattern: economic decline precedes military weakness. US dollar dominance mirrors Roman currency system."
            )
        elif event_type == WorldEventType.MILITARY_ESCALATION:
            return TimelineEvent(
                event_id=str(uuid.uuid4()),
                date=date,
                event_type=event_type,
                title="NATO Expansion Crisis: Finland and Sweden Join Amid Russian Threats",
                description="Russia threatens nuclear response as Finland and Sweden officially join NATO, creating new flashpoint in Baltic region.",
                affected_countries=["RU", "US", "EU", "FI", "SE"],
                historical_pattern=HistoricalPattern.ROMAN_DECLINE,
                probability=0.6,
                impact_magnitude=0.7,
                ai_reasoning="Roman pattern: overextension of military commitments leads to strategic vulnerability."
            )
    
    async def _create_cold_war_event(self, date: datetime, world_state: WorldState) -> TimelineEvent:
        """Create event based on Cold War escalation pattern"""
        return TimelineEvent(
            event_id=str(uuid.uuid4()),
            date=date,
            event_type=WorldEventType.NUCLEAR_THREAT,
            title="Nuclear Posturing Escalates: Russia Conducts Strategic Bomber Flights",
            description="Russia conducts nuclear-capable bomber flights near NATO borders, while US deploys additional missile defense systems to Eastern Europe.",
            affected_countries=["RU", "US", "EU"],
            historical_pattern=HistoricalPattern.COLD_WAR_ESCALATION,
            probability=0.8,
            impact_magnitude=0.9,
            ai_reasoning="Cold War pattern: nuclear posturing and missile defense deployment creates dangerous escalation cycle."
        )
    
    async def _create_persian_expansion_event(self, date: datetime, world_state: WorldState) -> TimelineEvent:
        """Create event based on Persian expansion pattern"""
        return TimelineEvent(
            event_id=str(uuid.uuid4()),
            date=date,
            event_type=WorldEventType.TERRITORIAL_CONQUEST,
            title="Iran Expands Regional Influence: Proxy Forces Advance in Yemen",
            description="Iran-backed Houthi forces gain significant territory in Yemen, establishing control over key shipping lanes in Red Sea.",
            affected_countries=["IR", "SA", "US", "YE"],
            historical_pattern=HistoricalPattern.PERSIAN_EXPANSION,
            probability=0.6,
            impact_magnitude=0.6,
            ai_reasoning="Persian pattern: regional expansion through proxy warfare and strategic positioning."
        )
    
    async def _create_generic_event(self, date: datetime, pattern: HistoricalPattern, world_state: WorldState) -> TimelineEvent:
        """Create a generic event based on pattern"""
        return TimelineEvent(
            event_id=str(uuid.uuid4()),
            date=date,
            event_type=WorldEventType.DIPLOMATIC_CRISIS,
            title=f"Diplomatic Crisis: {pattern.value.replace('_', ' ').title()} Pattern Emerges",
            description=f"Historical {pattern.value} pattern manifests in modern geopolitics, creating new diplomatic challenges.",
            affected_countries=list(world_state.countries.keys())[:3],
            historical_pattern=pattern,
            probability=0.5,
            impact_magnitude=0.5,
            ai_reasoning=f"Historical pattern {pattern.value} indicates this type of event is likely at this stage."
        )
    
    async def _update_world_state(self, current_state: WorldState, event: TimelineEvent) -> WorldState:
        """Update world state based on new event"""
        new_state = WorldState(
            date=event.date,
            countries=current_state.countries.copy(),
            alliances=current_state.alliances.copy(),
            conflicts=current_state.conflicts.copy(),
            economic_indicators=current_state.economic_indicators.copy(),
            world_stability_index=current_state.world_stability_index,
            nuclear_threat_level=current_state.nuclear_threat_level
        )
        
        # Apply event effects
        if event.event_type == WorldEventType.NUCLEAR_THREAT:
            new_state.nuclear_threat_level = min(1.0, new_state.nuclear_threat_level + 0.2)
            new_state.world_stability_index = max(0.0, new_state.world_stability_index - 0.1)
            
        elif event.event_type == WorldEventType.ECONOMIC_COLLAPSE:
            new_state.economic_indicators["global_gdp_growth"] = max(-0.05, new_state.economic_indicators["global_gdp_growth"] - 0.02)
            new_state.world_stability_index = max(0.0, new_state.world_stability_index - 0.15)
            
        elif event.event_type == WorldEventType.MILITARY_ESCALATION:
            new_state.world_stability_index = max(0.0, new_state.world_stability_index - 0.1)
            new_state.nuclear_threat_level = min(1.0, new_state.nuclear_threat_level + 0.1)
        
        return new_state
    
    async def _check_end_conditions(self, world_state: WorldState) -> bool:
        """Check if simulation should end"""
        # Nuclear war threshold
        if world_state.nuclear_threat_level > 0.9:
            return True
        
        # Complete economic collapse
        if world_state.economic_indicators.get("global_gdp_growth", 0) < -0.1:
            return True
        
        # World stability collapse
        if world_state.world_stability_index < 0.1:
            return True
        
        return False
    
    async def _determine_end_scenario(self, final_state: WorldState) -> str:
        """Determine how the world ends"""
        if final_state.nuclear_threat_level > 0.9:
            return "Nuclear War: Multiple nuclear exchanges between major powers lead to global devastation"
        elif final_state.economic_indicators.get("global_gdp_growth", 0) < -0.1:
            return "Economic Collapse: Global economic system collapses, leading to widespread chaos and conflict"
        elif final_state.world_stability_index < 0.1:
            return "Global Chaos: Complete breakdown of international order leads to widespread conflict"
        else:
            return "Unknown End: Simulation ended under unclear circumstances"
    
    async def get_simulation_timeline(self, simulation_id: str) -> List[TimelineEvent]:
        """Get timeline events for a simulation"""
        if simulation_id not in self.active_simulations:
            return []
        
        simulation = self.active_simulations[simulation_id]
        return simulation.timeline_events
    
    async def get_world_state_at_date(self, simulation_id: str, date: datetime) -> Optional[WorldState]:
        """Get world state at a specific date"""
        if simulation_id not in self.active_simulations:
            return None
        
        simulation = self.active_simulations[simulation_id]
        
        # Find closest world state to requested date
        closest_state = None
        min_diff = timedelta.max
        
        for state in simulation.world_states:
            diff = abs(state.date - date)
            if diff < min_diff:
                min_diff = diff
                closest_state = state
        
        return closest_state

# Global instance
predictive_service = PredictiveSimulationService()
