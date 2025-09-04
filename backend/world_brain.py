#!/usr/bin/env python3
"""
World Brain - Core Simulation Engine
Implements the World Brain architecture with rich data integration
"""

import logging
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from world_data_service import world_data_service
from world_leaders_service import world_leaders_service

logger = logging.getLogger(__name__)

@dataclass
class Country:
    """Represents a country in the simulation"""
    id: str
    name: str
    gdp: float
    population: int
    military_budget: float
    nuclear_warheads: int
    active_military: int
    cyber_capability: int
    space_capability: int
    energy_balance: float
    food_balance: float
    regime_type: str
    bloc: str
    alliances: List[str]
    major_cities: List[str]
    key_industries: List[str]
    influence_level: int = 50
    stability: int = 70
    morale: int = 70

@dataclass
class Doctrine:
    """Represents a country's strategic doctrine"""
    country_id: str
    name: str
    description: str
    aggression_level: int  # 0-100
    cooperation_level: int  # 0-100
    risk_tolerance: int  # 0-100

@dataclass
class Relation:
    """Represents relations between countries"""
    country_a: str
    country_b: str
    trust_level: int  # -100 to 100
    trade_volume: float
    military_cooperation: int  # 0-100
    diplomatic_relations: int  # 0-100
    historical_conflicts: List[str] = field(default_factory=list)
    cultural_affinity: int = 0

@dataclass
class Action:
    """Represents an action taken by a country"""
    id: str
    actor_id: str
    target_id: Optional[str]
    action_type: str  # diplomatic, military, economic, cyber
    description: str
    intensity: int  # 0-100
    timestamp: datetime
    success_probability: float

@dataclass
class Outcome:
    """Represents the outcome of an action"""
    action_id: str
    success: bool
    impact_magnitude: int  # 0-100
    casualties: int = 0
    economic_damage: float = 0.0
    diplomatic_impact: int = 0
    escalation_triggered: bool = False
    new_escalation_level: int = 0
    stat_changes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeneratedNews:
    """Represents a generated news article"""
    headline: str
    lede: str
    content: str
    country: str
    category: str  # politics, military, economy, technology
    severity: str  # low, medium, high, critical
    reliability: str  # confirmed, likely, uncertain, disputed
    source: str
    timestamp: datetime
    stat_changes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MapState:
    """Represents the current state of the world map"""
    timestamp: datetime
    country_states: Dict[str, Dict[str, Any]]
    bloc_distribution: Dict[str, int]
    global_tension: int  # 0-100
    active_conflicts: List[str]

@dataclass
class WorldState:
    """Represents the complete world state"""
    timestamp: datetime
    current_date: datetime  # Real calendar date
    week_number: int
    countries: Dict[str, Country]
    doctrines: Dict[str, Doctrine]
    relations: Dict[str, Relation]
    actions: List[Action]
    outcomes: List[Outcome]
    news: List[GeneratedNews]
    map_states: List[MapState]
    map_state: MapState  # Current map state
    global_indicators: Dict[str, Any]

class WorldBrain:
    """Core World Brain simulation engine"""
    
    def __init__(self):
        # Initialize ChatGPT service only when needed
        self.chatgpt_service = None
        self.simulations: Dict[str, WorldState] = {}
        self.current_week = 0
        logger.info("World Brain initialized")
    
    async def initialize_world(self, simulation_id: str, seed: Optional[int] = None, start_month: Optional[int] = None, start_year: Optional[int] = None) -> WorldState:
        """Initialize a new world simulation"""
        if seed:
            random.seed(seed)
        
        logger.info(f"Initializing world simulation {simulation_id}")
        
        # Use provided start date or current date
        if start_month and start_year:
            start_date = datetime(year=start_year, month=start_month, day=1)
        else:
            start_date = datetime.now()
        
        # Load real country data
        countries = {}
        for country_id, data in world_data_service.country_data.items():
            countries[country_id] = Country(
                id=country_id,
                name=data["name"],
                gdp=data["gdp_2024"],
                population=data["population"],
                military_budget=data["military_budget"],
                nuclear_warheads=data["nuclear_warheads"],
                active_military=data["active_military"],
                cyber_capability=data["cyber_capability"],
                space_capability=data["space_capability"],
                energy_balance=data["energy_balance"],
                food_balance=data["food_balance"],
                regime_type=data["regime_type"],
                bloc=data["bloc"],
                alliances=data["alliances"],
                major_cities=data["major_cities"],
                key_industries=data["key_industries"]
            )
        
        # Initialize doctrines based on real leaders
        doctrines = {}
        for leader_id, leader_data in world_leaders_service.leaders.items():
            country_id = leader_data["country"]
            if country_id in countries:
                doctrines[country_id] = Doctrine(
                    country_id=country_id,
                    name=f"{leader_data['name']} Doctrine",
                    description=f"Strategic doctrine under {leader_data['name']}",
                    aggression_level=self._calculate_aggression(leader_data),
                    cooperation_level=self._calculate_cooperation(leader_data),
                    risk_tolerance=self._calculate_risk_tolerance(leader_data)
                )
        
        # Initialize relations based on real alliances and conflicts
        relations = {}
        for country_a in countries:
            for country_b in countries:
                if country_a < country_b:  # Avoid duplicates
                    relation = self._initialize_relation(countries[country_a], countries[country_b])
                    relations[f"{country_a}_{country_b}"] = relation
        
        # Create initial map state
        initial_map_state = self._create_map_state(countries, relations)
        
        # Create initial world state
        world_state = WorldState(
            timestamp=datetime.now(),
            current_date=start_date,
            week_number=1,
            countries=countries,
            doctrines=doctrines,
            relations=relations,
            actions=[],
            outcomes=[],
            news=[],
            map_states=[initial_map_state],
            map_state=initial_map_state,  # Set current map state
            global_indicators=world_data_service.get_global_indicators()
        )
        
        # Generate initial news based on recent events
        initial_news = await self._generate_initial_psychohistorical_news(world_state)
        world_state.news = initial_news
        
        
        self.simulations[simulation_id] = world_state
        logger.info(f"World simulation {simulation_id} initialized with {len(countries)} countries")
        
        return world_state
    
    async def tick(self, simulation_id: str) -> WorldState:
        """Advance the simulation by one week"""
        if simulation_id not in self.simulations:
            raise ValueError(f"Simulation {simulation_id} not found")
        
        world_state = self.simulations[simulation_id]
        self.current_week += 1
        
        # Advance the real date by one week
        world_state.current_date += timedelta(weeks=1)
        world_state.week_number += 1
        
        logger.info(f"Advancing simulation {simulation_id} to week {self.current_week} ({world_state.current_date.strftime('%m/%d/%Y')})")
        
        # Generate actions for each country
        new_actions = self._generate_actions(world_state)
        world_state.actions.extend(new_actions)
        
        # Process actions and generate outcomes
        new_outcomes = self._process_actions(new_actions, world_state)
        world_state.outcomes.extend(new_outcomes)
        
        # Update world state based on outcomes
        self._update_world_state(world_state, new_outcomes)
        
        # Generate news based on actions and outcomes (only important ones)
        new_news = await self._generate_news(world_state, new_actions, new_outcomes)
        world_state.news.extend(new_news)
        
        # Update map state
        new_map_state = self._create_map_state(world_state)
        world_state.map_states.append(new_map_state)
        
        # Update timestamp
        world_state.timestamp = datetime.now()
        
        logger.info(f"Simulation {simulation_id} advanced. Generated {len(new_actions)} actions, {len(new_outcomes)} outcomes, {len(new_news)} news articles")
        
        return world_state
    
    def _calculate_aggression(self, leader_data: Dict[str, Any]) -> int:
        """Calculate aggression level based on leader personality and policies"""
        base_aggression = 50
        
        # Adjust based on personality traits
        if "combative" in leader_data.get("personality_traits", []):
            base_aggression += 20
        if "authoritarian" in leader_data.get("personality_traits", []):
            base_aggression += 15
        if "nationalist" in leader_data.get("personality_traits", []):
            base_aggression += 10
        
        # Adjust based on recent actions
        recent_actions = leader_data.get("recent_actions", [])
        if any("invasion" in action.lower() for action in recent_actions):
            base_aggression += 25
        if any("pressure" in action.lower() for action in recent_actions):
            base_aggression += 15
        
        return min(100, max(0, base_aggression))
    
    def _calculate_cooperation(self, leader_data: Dict[str, Any]) -> int:
        """Calculate cooperation level based on leader personality and policies"""
        base_cooperation = 50
        
        # Adjust based on personality traits
        if "diplomatic" in leader_data.get("personality_traits", []):
            base_cooperation += 20
        if "consensus-builder" in leader_data.get("personality_traits", []):
            base_cooperation += 15
        if "transactional" in leader_data.get("personality_traits", []):
            base_cooperation += 10
        
        # Adjust based on relationships
        relationships = leader_data.get("relationships", {})
        ally_count = sum(1 for rel in relationships.values() if "ally" in rel.lower())
        base_cooperation += ally_count * 5
        
        return min(100, max(0, base_cooperation))
    
    def _calculate_risk_tolerance(self, leader_data: Dict[str, Any]) -> int:
        """Calculate risk tolerance based on leader personality and recent actions"""
        base_risk = 50
        
        # Adjust based on personality traits
        if "ruthless" in leader_data.get("personality_traits", []):
            base_risk += 20
        if "strategic" in leader_data.get("personality_traits", []):
            base_risk += 10
        if "cautious" in leader_data.get("personality_traits", []):
            base_risk -= 15
        
        # Adjust based on controversy level
        controversy = leader_data.get("controversy_level", 50)
        base_risk += (controversy - 50) * 0.3
        
        return min(100, max(0, int(base_risk)))
    
    def _initialize_relation(self, country_a: Country, country_b: Country) -> Relation:
        """Initialize relations between two countries"""
        # Check if they're in the same bloc
        same_bloc = country_a.bloc == country_b.bloc
        
        # Check for alliance overlap
        alliance_overlap = len(set(country_a.alliances) & set(country_b.alliances))
        
        # Base trust level
        if same_bloc:
            base_trust = 60
        elif alliance_overlap > 0:
            base_trust = 40
        else:
            base_trust = 0
        
        # Adjust based on regime type compatibility
        if country_a.regime_type == country_b.regime_type:
            base_trust += 20
        elif (country_a.regime_type == "democracy" and country_b.regime_type == "authoritarian") or \
             (country_a.regime_type == "authoritarian" and country_b.regime_type == "democracy"):
            base_trust -= 30
        
        return Relation(
            country_a=country_a.id,
            country_b=country_b.id,
            trust_level=base_trust,
            trade_volume=0.0,  # Will be calculated based on GDP
            military_cooperation=alliance_overlap * 20,
            diplomatic_relations=base_trust
        )
    
    def _generate_initial_news(self, world_state: WorldState) -> List[GeneratedNews]:
        """Generate initial news based on real recent events from the past 1-3 months"""
        initial_news = []
        
        # Get current date for reference
        current_date = datetime.now()
        
        # Create realistic recent news articles from the past 1-3 months
        recent_articles = [
            {
                "headline": "Trump-Putin Alaska Summit Ends Without Breakthrough",
                "content": "The highly anticipated summit between former US President Donald Trump and Russian President Vladimir Putin in Alaska concluded without significant agreements. The meeting, which lasted several hours, focused on Ukraine, trade relations, and regional security concerns. Analysts note the summit elevated Putin's international standing while Trump continues to pressure Ukraine for territorial concessions.",
                "country": "Global",
                "category": "diplomatic",
                "severity": "high",
                "reliability": "confirmed",
                "source": "Reuters",
                "days_ago": 45
            },
            {
                "headline": "Ukraine's Counteroffensive Fails to Achieve Strategic Gains",
                "content": "Ukraine's much-anticipated summer counteroffensive has failed to achieve significant territorial gains against Russian forces. Military analysts report that despite heavy casualties, Ukrainian forces have been unable to break through heavily fortified Russian defensive lines. The failure has led to increased war fatigue in Western nations and growing pressure for peace negotiations.",
                "country": "Global",
                "category": "military",
                "severity": "high",
                "reliability": "confirmed",
                "source": "Associated Press",
                "days_ago": 30
            },
            {
                "headline": "China Intensifies Military Pressure Around Taiwan",
                "content": "China has significantly increased military activities around Taiwan, including large-scale air incursions and naval exercises. The People's Liberation Army has conducted multiple drills simulating blockade scenarios, raising concerns about potential escalation. Taiwan's defense ministry reports detecting over 100 Chinese military aircraft in the region this month.",
                "country": "Global",
                "category": "military",
                "severity": "high",
                "reliability": "confirmed",
                "source": "BBC News",
                "days_ago": 25
            },
            {
                "headline": "US-China Trade Tensions Escalate Over Technology Restrictions",
                "content": "Trade tensions between the United States and China have intensified as the US implements new restrictions on advanced technology exports to China. The measures target semiconductors, artificial intelligence, and quantum computing technologies. China has vowed to retaliate with its own export controls, raising concerns about a new phase in the economic rivalry between the world's two largest economies.",
                "country": "Global",
                "category": "economic",
                "severity": "high",
                "reliability": "confirmed",
                "source": "CNN International",
                "days_ago": 60
            },
            {
                "headline": "Global Markets Volatile Amid Economic Policy Uncertainty",
                "content": "International financial markets have experienced significant volatility as major economies implement conflicting economic policies. The US Federal Reserve's continued interest rate hikes, combined with China's stimulus measures and Europe's energy transition policies, have created uncertainty in global trade and investment flows.",
                "country": "Global",
                "category": "economic",
                "severity": "medium",
                "reliability": "confirmed",
                "source": "Financial Times",
                "days_ago": 20
            },
            {
                "headline": "Cybersecurity Threats Escalate Globally",
                "content": "Government agencies worldwide report a dramatic increase in sophisticated cyber attacks targeting critical infrastructure. Security experts warn that state-sponsored hacking groups have become more aggressive, with attacks on energy grids, financial systems, and government networks reaching unprecedented levels.",
                "country": "Global",
                "category": "cyber",
                "severity": "high",
                "reliability": "likely",
                "source": "The New York Times",
                "days_ago": 15
            }
        ]
        
        for article in recent_articles:
            # Calculate the actual date based on days ago from current date
            article_date = current_date - timedelta(days=article["days_ago"])
            
            news = GeneratedNews(
                headline=article["headline"],
                lede=article["content"],
                content=article["content"],
                country=article["country"],
                category=article["category"],
                severity=article["severity"],
                reliability=article["reliability"],
                source=article["source"],
                timestamp=article_date,
                stat_changes={}  # Real news doesn't have simulation stat changes
            )
            initial_news.append(news)
        
        return initial_news
    
    def _generate_actions(self, world_state: WorldState) -> List[Action]:
        """Generate actions for each country based on their doctrines and current situation"""
        actions = []
        
        for country_id, country in world_state.countries.items():
            doctrine = world_state.doctrines.get(country_id)
            if not doctrine:
                continue
            
            # Determine if country should take action based on doctrine
            if random.random() < (doctrine.aggression_level / 100.0):
                action = self._create_action(country, doctrine, world_state)
                if action:
                    actions.append(action)
        
        return actions
    
    def _create_action(self, country: Country, doctrine: Doctrine, world_state: WorldState) -> Optional[Action]:
        """Create a specific action for a country"""
        action_types = ["diplomatic", "military", "economic", "cyber"]
        action_type = random.choice(action_types)
        
        # Find potential targets
        potential_targets = [
            c for c in world_state.countries.values()
            if c.id != country.id
        ]
        
        if not potential_targets:
            return None
        
        target = random.choice(potential_targets)
        
        # Determine action intensity based on doctrine
        intensity = min(100, doctrine.aggression_level + random.randint(-20, 20))
        intensity = max(0, intensity)
        
        # Create action description
        descriptions = {
            "diplomatic": f"{country.name} engages in diplomatic {random.choice(['pressure', 'negotiations', 'threats', 'overtures'])} with {target.name}",
            "military": f"{country.name} conducts military {random.choice(['exercises', 'deployments', 'threats', 'operations'])} near {target.name}",
            "economic": f"{country.name} implements economic {random.choice(['sanctions', 'trade restrictions', 'incentives', 'agreements'])} with {target.name}",
            "cyber": f"{country.name} conducts cyber {random.choice(['operations', 'espionage', 'attacks', 'defense'])} against {target.name}"
        }
        
        return Action(
            id=f"action_{len(world_state.actions)}_{country.id}",
            actor_id=country.id,
            target_id=target.id,
            action_type=action_type,
            description=descriptions[action_type],
            intensity=intensity,
            timestamp=world_state.timestamp,
            success_probability=0.7
        )
    
    def _process_actions(self, actions: List[Action], world_state: WorldState) -> List[Outcome]:
        """Process actions and generate outcomes"""
        outcomes = []
        
        for action in actions:
            # Determine success based on probability and random factors
            success = random.random() < action.success_probability
            
            # Calculate impact magnitude
            impact_magnitude = action.intensity
            if not success:
                impact_magnitude = impact_magnitude // 2
            
            # Add some randomness
            impact_magnitude += random.randint(-10, 10)
            impact_magnitude = max(0, min(100, impact_magnitude))
            
            outcome = Outcome(
                action_id=action.id,
                success=success,
                impact_magnitude=impact_magnitude,
                casualties=random.randint(0, impact_magnitude * 100) if action.action_type == "military" else 0,
                economic_damage=impact_magnitude * 1000000 if action.action_type == "economic" else 0.0,
                diplomatic_impact=impact_magnitude if action.action_type == "diplomatic" else 0,
                escalation_triggered=impact_magnitude > 70
            )
            
            outcomes.append(outcome)
        
        return outcomes
    
    def _update_world_state(self, world_state: WorldState, outcomes: List[Outcome]):
        """Update world state based on outcomes"""
        for outcome in outcomes:
            # Find the corresponding action
            action = next((a for a in world_state.actions if a.id == outcome.action_id), None)
            if not action:
                continue
            
            # Update relations between countries
            relation_key = f"{action.actor_id}_{action.target_id}"
            if relation_key in world_state.relations:
                relation = world_state.relations[relation_key]
                if outcome.success:
                    relation.trust_level += outcome.diplomatic_impact
                else:
                    relation.trust_level -= outcome.diplomatic_impact
                relation.trust_level = max(-100, min(100, relation.trust_level))
    
    async def _generate_news(self, world_state: WorldState, actions: List[Action], outcomes: List[Outcome]) -> List[GeneratedNews]:
        """Generate psychohistorically accurate news articles based on actions and outcomes"""
        news_articles = []
        
        # Generate news for important actions only (higher threshold)
        for action, outcome in zip(actions, outcomes):
            if outcome.impact_magnitude > 50:  # Only report important events
                news = await self._create_psychohistorical_news_article(action, outcome, world_state)
                if news:
                    news_articles.append(news)
        
        # Generate occasional world news (reduced frequency)
        if random.random() < 0.2:  # 20% chance of additional news
            additional_news = await self._generate_additional_psychohistorical_news(world_state)
            news_articles.extend(additional_news)
        
        return news_articles
    
    def _create_news_article(self, action: Action, outcome: Outcome, world_state: WorldState) -> Optional[GeneratedNews]:
        """Create a news article for a specific action and outcome"""
        actor = world_state.countries.get(action.actor_id)
        target = world_state.countries.get(action.target_id) if action.target_id else None
        
        if not actor:
            return None
        
        # Calculate stat changes based on outcome
        stat_changes = self._calculate_stat_changes(action, outcome, actor, target)
        
        # Create realistic public-facing headlines and content
        if outcome.success:
            if action.action_type == "diplomatic":
                headline = f"{actor.name} Issues Diplomatic Statement to {target.name}"
                content = f"The {actor.name} government has issued a formal diplomatic communication to {target.name}. "
                if outcome.impact_magnitude > 70:
                    content += f"International observers note the unusually strong language used in the statement."
                else:
                    content += f"Diplomatic sources describe the tone as standard protocol."
            elif action.action_type == "military":
                headline = f"{actor.name} Conducts Military Exercises Near {target.name}"
                content = f"{actor.name} has announced military exercises in the region near {target.name}. "
                if outcome.impact_magnitude > 70:
                    content += f"The scale and timing of these exercises have raised concerns among regional analysts."
                else:
                    content += f"Military officials describe these as routine training operations."
            elif action.action_type == "economic":
                headline = f"{actor.name} Announces New Economic Measures Affecting {target.name}"
                content = f"{actor.name} has implemented new economic policies that will impact trade relations with {target.name}. "
                if outcome.impact_magnitude > 70:
                    content += f"Economic experts warn these measures could significantly affect bilateral trade."
                else:
                    content += f"Trade analysts expect minimal disruption to existing economic ties."
            elif action.action_type == "cyber":
                headline = f"Cybersecurity Incident Reported in {target.name}"
                content = f"Authorities in {target.name} have reported a cybersecurity incident affecting government systems. "
                if outcome.impact_magnitude > 70:
                    content += f"Security experts describe this as a sophisticated attack requiring significant resources."
                else:
                    content += f"Officials indicate the incident has been contained with minimal disruption."
            
            severity = "high" if outcome.impact_magnitude > 70 else "medium"
        else:
            if action.action_type == "diplomatic":
                headline = f"{actor.name} Diplomatic Initiative with {target.name} Shows Limited Progress"
                content = f"Recent diplomatic efforts between {actor.name} and {target.name} have not achieved their stated objectives. "
                content += f"Both sides continue to express commitment to dialogue."
            elif action.action_type == "military":
                headline = f"{actor.name} Military Operations Face Challenges"
                content = f"Recent military activities by {actor.name} have encountered operational difficulties. "
                content += f"Defense officials emphasize the importance of learning from these experiences."
            elif action.action_type == "economic":
                headline = f"{actor.name} Economic Policy Implementation Delayed"
                content = f"Planned economic measures by {actor.name} have faced implementation challenges. "
                content += f"Government officials indicate they are reviewing the policy approach."
            elif action.action_type == "cyber":
                headline = f"Cybersecurity Measures in {actor.name} Prove Effective"
                content = f"Recent cybersecurity incidents targeting {actor.name} have been successfully defended against. "
                content += f"Security experts credit improved defensive capabilities."
            
            severity = "low"
        
        # Add escalation warning for high-impact actions
        if outcome.escalation_triggered:
            content += " Regional tensions have increased following these developments."
        
        # Add stat change information to content
        if stat_changes:
            content += f" Impact: {self._format_stat_changes(stat_changes)}"
        
        # Create realistic timestamp within the current week (simulation date)
        days_ago = random.randint(0, 6)  # Within the past week
        article_date = world_state.current_date - timedelta(days=days_ago)
        
        # Determine reliability based on action type and outcome
        if action.action_type == "cyber":
            reliability = "uncertain"  # Cyber incidents are often unclear
        elif outcome.impact_magnitude > 80:
            reliability = "confirmed"  # High-impact events are usually well-documented
        else:
            reliability = "likely"  # Standard reliability for most events
        
        # Create realistic source names
        sources = [
            "Reuters", "Associated Press", "Agence France-Presse", 
            "BBC News", "CNN International", "Al Jazeera",
            "The New York Times", "The Guardian", "Le Monde",
            "Der Spiegel", "Asahi Shimbun", "The Times of India"
        ]
        source = random.choice(sources)
        
        return GeneratedNews(
            headline=headline,
            lede=content[:200] + "..." if len(content) > 200 else content,
            content=content,
            country=actor.id,
            category=action.action_type,
            severity=severity,
            reliability=reliability,
            source=source,
            timestamp=article_date,
            stat_changes=stat_changes
        )
    
    def _generate_additional_news(self, world_state: WorldState) -> List[GeneratedNews]:
        """Generate additional world news based on current situation"""
        additional_news = []
        
        # Generate occasional world news updates
        if random.random() < 0.3:  # 30% chance of additional news
            world_news_templates = [
                {
                    "headline": "International Trade Talks Continue",
                    "content": "Representatives from major trading nations continue negotiations on economic cooperation agreements. Observers note the complexity of balancing national interests with global economic stability.",
                    "category": "economic",
                    "severity": "medium",
                    "reliability": "likely",
                    "source": "Reuters"
                },
                {
                    "headline": "Regional Security Discussions Intensify",
                    "content": "Security officials from multiple regions have increased coordination efforts. The discussions focus on addressing shared security challenges and improving response capabilities.",
                    "category": "military",
                    "severity": "medium",
                    "reliability": "confirmed",
                    "source": "Associated Press"
                },
                {
                    "headline": "Technology Sector Faces Regulatory Changes",
                    "content": "Governments worldwide are implementing new regulations affecting the technology sector. Industry leaders express concerns about the impact on innovation and global competitiveness.",
                    "category": "cyber",
                    "severity": "low",
                    "reliability": "likely",
                    "source": "BBC News"
                }
            ]
            
            template = random.choice(world_news_templates)
            days_ago = random.randint(0, 3)
            article_date = world_state.timestamp - timedelta(days=days_ago)
            
            news = GeneratedNews(
                headline=template["headline"],
                lede=template["content"],
                content=template["content"],
                country="Global",
                category=template["category"],
                severity=template["severity"],
                reliability=template["reliability"],
                source=template["source"],
                timestamp=article_date
            )
            additional_news.append(news)
        
        return additional_news
    
    def _calculate_stat_changes(self, action: Action, outcome: Outcome, actor: Country, target: Optional[Country]) -> Dict[str, Any]:
        """Calculate stat changes based on action outcome"""
        changes = {}
        
        # Calculate impact magnitude as percentage
        impact_pct = outcome.impact_magnitude / 100.0
        
        if action.action_type == "diplomatic":
            if outcome.success:
                changes["diplomatic_relations"] = f"+{int(impact_pct * 10)}"
                if target:
                    changes["trust_level"] = f"+{int(impact_pct * 15)}"
            else:
                changes["diplomatic_relations"] = f"-{int(impact_pct * 5)}"
                if target:
                    changes["trust_level"] = f"-{int(impact_pct * 10)}"
        
        elif action.action_type == "military":
            if outcome.success:
                changes["military_readiness"] = f"+{int(impact_pct * 8)}"
                changes["regional_tension"] = f"+{int(impact_pct * 12)}"
            else:
                changes["military_readiness"] = f"-{int(impact_pct * 3)}"
                changes["morale"] = f"-{int(impact_pct * 5)}"
        
        elif action.action_type == "economic":
            if outcome.success:
                changes["economic_growth"] = f"+{int(impact_pct * 6)}%"
                changes["trade_volume"] = f"+{int(impact_pct * 8)}%"
            else:
                changes["economic_growth"] = f"-{int(impact_pct * 2)}%"
                changes["market_confidence"] = f"-{int(impact_pct * 4)}"
        
        elif action.action_type == "cyber":
            if outcome.success:
                changes["cyber_capability"] = f"+{int(impact_pct * 5)}"
                changes["intelligence_gathering"] = f"+{int(impact_pct * 7)}"
            else:
                changes["cyber_defense"] = f"+{int(impact_pct * 3)}"
                changes["security_awareness"] = f"+{int(impact_pct * 4)}"
        
        # Add escalation effects
        if outcome.escalation_triggered:
            changes["global_tension"] = f"+{int(impact_pct * 15)}"
            changes["nuclear_threat"] = f"+{int(impact_pct * 8)}"
        
        return changes
    
    def _format_stat_changes(self, stat_changes: Dict[str, Any]) -> str:
        """Format stat changes for display in news articles"""
        if not stat_changes:
            return "Minimal impact"
        
        formatted_changes = []
        for stat, change in stat_changes.items():
            stat_name = stat.replace("_", " ").title()
            formatted_changes.append(f"{stat_name}: {change}")
        
        return ", ".join(formatted_changes[:3])  # Limit to 3 most important changes
    
    def _create_map_state(self, countries: Dict[str, Country], relations: Dict[str, Relation]) -> MapState:
        """Create current map state"""
        country_states = {}
        for country_id, country in countries.items():
            country_states[country_id] = {
                "stability": country.stability,
                "morale": country.morale,
                "influence": country.influence_level,
                "bloc": country.bloc
            }
        
        # Calculate bloc distribution
        bloc_distribution = {}
        for country in countries.values():
            bloc_distribution[country.bloc] = bloc_distribution.get(country.bloc, 0) + 1
        
        # Calculate initial global tension based on relations
        total_tension = 0
        relation_count = 0
        for relation in relations.values():
            tension = max(0, -relation.trust_level)  # Convert negative trust to tension
            total_tension += tension
            relation_count += 1
        
        global_tension = min(100, total_tension // (relation_count or 1))
        
        # Identify active conflicts based on relations
        active_conflicts = []
        for relation_key, relation in relations.items():
            if relation.trust_level < -50:  # High distrust indicates potential conflict
                active_conflicts.append(relation_key)
        
        return MapState(
            timestamp=datetime.now(),
            country_states=country_states,
            bloc_distribution=bloc_distribution,
            global_tension=global_tension,
            active_conflicts=active_conflicts
        )
    
    async def _create_psychohistorical_news_article(self, action: Action, outcome: Outcome, world_state: WorldState) -> Optional[GeneratedNews]:
        """Create a psychohistorically accurate news article using ChatGPT"""
        try:
            from chatgpt_service import get_chatgpt_service
            
            chatgpt_service = await get_chatgpt_service()
            
            # Convert world state to dict for ChatGPT
            world_state_dict = {
                "global_tension": self._calculate_global_tension(world_state),
                "active_conflicts": len([r for r in world_state.relations.values() if r.trust_level < -50]),
                "major_powers": [c.name for c in world_state.countries.values() if c.gdp > 2000000],
                "economic_indicators": {
                    "total_gdp": sum(c.gdp for c in world_state.countries.values()),
                    "average_stability": sum(c.stability for c in world_state.countries.values()) / len(world_state.countries)
                }
            }
            
            # Get country name for the actor
            actor_country = world_state.countries.get(action.actor_id)
            if not actor_country:
                return None
            
            # Generate news using ChatGPT
            news_data = await chatgpt_service.generate_psychohistorical_news(
                world_state_dict,
                actor_country.name,
                action.action_type,
                outcome.impact_magnitude
            )
            
            # Create timestamp within current week
            days_ago = random.randint(0, 6)
            article_date = world_state.current_date - timedelta(days=days_ago)
            
            # Create GeneratedNews object
            news = GeneratedNews(
                headline=news_data["headline"],
                lede=news_data["content"],
                content=news_data["content"],
                country=actor_country.name,
                category=action.action_type,
                severity=news_data["severity"],
                reliability=news_data["reliability"],
                source=news_data["source"],
                timestamp=article_date,
                stat_changes=news_data.get("stat_changes", {})
            )
            
            return news
            
        except Exception as e:
            print(f"Error generating psychohistorical news: {e}")
            # Fallback to basic news generation
            return self._create_news_article(action, outcome, world_state)
    
    async def _generate_additional_psychohistorical_news(self, world_state: WorldState) -> List[GeneratedNews]:
        """Generate additional psychohistorical world news using ChatGPT"""
        try:
            from chatgpt_service import get_chatgpt_service
            
            chatgpt_service = await get_chatgpt_service()
            
            # Convert world state to dict
            world_state_dict = {
                "global_tension": self._calculate_global_tension(world_state),
                "active_conflicts": len([r for r in world_state.relations.values() if r.tension_level > 70]),
                "major_powers": [c.name for c in world_state.countries.values() if c.gdp > 2000000],
                "economic_indicators": {
                    "total_gdp": sum(c.gdp for c in world_state.countries.values()),
                    "average_stability": sum(c.stability for c in world_state.countries.values()) / len(world_state.countries)
                }
            }
            
            # Select a random country for world news
            random_country = random.choice(list(world_state.countries.values()))
            
            # Generate world news using ChatGPT
            news_data = await chatgpt_service.generate_psychohistorical_news(
                world_state_dict,
                random_country.name,
                "world_event",
                60  # Medium impact for world news
            )
            
            # Create timestamp within current week
            days_ago = random.randint(0, 6)
            article_date = world_state.current_date - timedelta(days=days_ago)
            
            # Create GeneratedNews object
            news = GeneratedNews(
                headline=news_data["headline"],
                lede=news_data["content"],
                content=news_data["content"],
                country="Global",
                category="world_event",
                severity=news_data["severity"],
                reliability=news_data["reliability"],
                source=news_data["source"],
                timestamp=article_date,
                stat_changes=news_data.get("stat_changes", {})
            )
            
            return [news]
            
        except Exception as e:
            print(f"Error generating additional psychohistorical news: {e}")
            # Fallback to basic additional news generation
            return self._generate_additional_news(world_state)
    
    def _calculate_global_tension(self, world_state: WorldState) -> int:
        """Calculate global tension level"""
        total_tension = 0
        relation_count = 0
        
        for relation in world_state.relations.values():
            # Convert trust_level to tension (negative trust = high tension)
            tension = max(0, -relation.trust_level)
            total_tension += tension
            relation_count += 1
        
        if relation_count == 0:
            return 0
        
        return total_tension // relation_count
    
    async def _generate_initial_psychohistorical_news(self, world_state: WorldState) -> List[GeneratedNews]:
        """Generate initial psychohistorical news using ChatGPT"""
        try:
            from chatgpt_service import get_chatgpt_service
            
            chatgpt_service = await get_chatgpt_service()
            
            # Convert world state to dict
            world_state_dict = {
                "global_tension": self._calculate_global_tension(world_state),
                "active_conflicts": len([r for r in world_state.relations.values() if r.trust_level < -50]),
                "major_powers": [c.name for c in world_state.countries.values() if c.gdp > 2000000],
                "economic_indicators": {
                    "total_gdp": sum(c.gdp for c in world_state.countries.values()),
                    "average_stability": sum(c.stability for c in world_state.countries.values()) / len(world_state.countries)
                }
            }
            
            initial_news = []
            
            # Generate 3-5 initial news articles about recent world events
            recent_events = [
                ("United States", "diplomatic", 85),
                ("Russia", "military", 90),
                ("China", "economic", 75),
                ("Ukraine", "military", 80),
                ("India", "economic", 70)
            ]
            
            for country, event_type, impact in recent_events[:4]:  # Generate 4 articles
                news_data = await chatgpt_service.generate_psychohistorical_news(
                    world_state_dict,
                    country,
                    event_type,
                    impact
                )
                
                # Create timestamp for recent past (1-3 months ago)
                days_ago = random.randint(30, 90)
                article_date = world_state.current_date - timedelta(days=days_ago)
                
                # Create GeneratedNews object
                news = GeneratedNews(
                    headline=news_data["headline"],
                    lede=news_data["content"],
                    content=news_data["content"],
                    country=country,
                    category=event_type,
                    severity=news_data["severity"],
                    reliability=news_data["reliability"],
                    source=news_data["source"],
                    timestamp=article_date,
                    stat_changes=news_data.get("stat_changes", {})
                )
                
                initial_news.append(news)
            
            return initial_news
            
        except Exception as e:
            print(f"Error generating initial psychohistorical news: {e}")
            # Fallback to basic initial news generation
            return self._generate_initial_news(world_state)

# Global instance with singleton pattern
_world_brain_instance = None

def get_world_brain():
    global _world_brain_instance
    if _world_brain_instance is None:
        _world_brain_instance = WorldBrain()
    return _world_brain_instance

world_brain = get_world_brain()
