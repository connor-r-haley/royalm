from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, date
from enum import Enum
import json
import uuid

# ============================================================================
# PSYCHOHISTORY CORE MODELS - THE WORLD BRAIN
# ============================================================================

class BlocType(str, Enum):
    NATO = "NATO"
    NATO_ALIGNED = "NATO_ALIGNED"
    RUSSIA_BLOC = "RUSSIA_BLOC"
    CHINA_BLOC = "CHINA_BLOC"
    SWING = "SWING"
    NEUTRAL = "NEUTRAL"

class RegimeType(str, Enum):
    DEMOCRACY = "democracy"
    AUTOCRACY = "autocracy"
    HYBRID = "hybrid"
    MILITARY = "military"
    THEOCRACY = "theocracy"

class EventType(str, Enum):
    DIPLOMATIC = "diplomatic"
    MILITARY = "military"
    ECONOMIC = "economic"
    CYBER = "cyber"
    ESPIONAGE = "espionage"
    PROTEST = "protest"
    ELECTION = "election"
    NATURAL_DISASTER = "natural_disaster"
    TERRORISM = "terrorism"
    NUCLEAR = "nuclear"

class ActionType(str, Enum):
    DIPLOMATIC_MEETING = "diplomatic_meeting"
    MILITARY_MOBILIZATION = "military_mobilization"
    ECONOMIC_SANCTIONS = "economic_sanctions"
    CYBER_ATTACK = "cyber_attack"
    ESPIONAGE_OPERATION = "espionage_operation"
    MILITARY_INVASION = "military_invasion"
    NUCLEAR_THREAT = "nuclear_threat"
    ALLIANCE_FORMATION = "alliance_formation"
    TRADE_AGREEMENT = "trade_agreement"
    PEACE_TALKS = "peace_talks"

class EscalationLevel(str, Enum):
    PEACE = "peace"
    TENSION = "tension"
    CRISIS = "crisis"
    CONFLICT = "conflict"
    WAR = "war"
    NUCLEAR_THREAT = "nuclear_threat"
    NUCLEAR_WAR = "nuclear_war"

# ============================================================================
# CORE ENTITIES
# ============================================================================

class Country(BaseModel):
    """Core country entity with all state information"""
    id: str = Field(description="ISO 3166-1 alpha-2 country code")
    name: str = Field(description="Country name")
    bloc: BlocType = Field(description="Current bloc alignment")
    regime_type: RegimeType = Field(description="Type of regime")
    
    # Economic indicators
    gdp: float = Field(description="GDP in trillions USD")
    population: int = Field(description="Population")
    energy_balance: float = Field(description="Energy self-sufficiency ratio")
    food_balance: float = Field(description="Food self-sufficiency ratio")
    
    # Military capabilities
    military_score: float = Field(description="Overall military strength (0-1)")
    nuclear_capability: int = Field(description="Number of nuclear warheads")
    cyber_capability: float = Field(description="Cyber warfare capability (0-1)")
    
    # Current state
    morale: float = Field(description="Public morale (0-1)")
    cohesion: float = Field(description="Internal cohesion (0-1)")
    stability: float = Field(description="Regime stability (0-1)")
    
    class Config:
        use_enum_values = True

class Doctrine(BaseModel):
    """Country's strategic doctrine and preferences"""
    country_id: str = Field(description="Country ID")
    grand_strategy: str = Field(description="Overall strategic approach")
    red_lines: List[str] = Field(description="Unacceptable actions that trigger response")
    preferred_tools: Dict[str, float] = Field(description="Preference weights for different action types")
    
    # Behavioral parameters
    escalation_bias: float = Field(description="Tendency to escalate (-1 to 1, negative is cautious)")
    first_strike_preference: float = Field(description="Willingness to strike first (0-1)")
    proxy_war_preference: float = Field(description="Preference for proxy conflicts (0-1)")
    bargaining_hardness: float = Field(description="Negotiation style (0-1, higher is harder)")

class Objectives(BaseModel):
    """Country's goals and victory conditions"""
    country_id: str = Field(description="Country ID")
    public_goals: List[str] = Field(description="Publicly stated objectives")
    secret_goals: List[str] = Field(description="Hidden objectives")
    weights: Dict[str, float] = Field(description="Goal importance weights")
    
    # Victory conditions
    victory_conditions: List[str] = Field(description="What constitutes victory")
    loss_conditions: List[str] = Field(description="What constitutes defeat")

class Relations(BaseModel):
    """Bilateral relations between countries"""
    country_a: str = Field(description="First country ID")
    country_b: str = Field(description="Second country ID")
    attitude: float = Field(description="Attitude (-100 to 100)")
    alliance_level: float = Field(description="Alliance strength (0-1)")
    trade_dependency: float = Field(description="Trade dependency (0-1)")
    security_dilemma: float = Field(description="Security dilemma intensity (0-1)")
    border_dispute: bool = Field(description="Active border dispute")
    
    # Historical factors
    historical_conflicts: List[str] = Field(default_factory=list, description="Past conflicts")
    cultural_affinity: float = Field(default=0.5, description="Cultural similarity (0-1)")

class Posture(BaseModel):
    """Current military and political posture"""
    country_id: str = Field(description="Country ID")
    mobilization: float = Field(description="Mobilization level (0-1)")
    readiness: float = Field(description="Military readiness (0-1)")
    alert_level: EscalationLevel = Field(description="Current alert level")
    morale: float = Field(description="Military morale (0-1)")
    cohesion: float = Field(description="Alliance cohesion (0-1)")

class Capabilities(BaseModel):
    """Detailed military capabilities"""
    country_id: str = Field(description="Country ID")
    land_power: float = Field(description="Land forces strength (0-1)")
    air_power: float = Field(description="Air forces strength (0-1)")
    naval_power: float = Field(description="Naval forces strength (0-1)")
    cyber: float = Field(description="Cyber warfare capability (0-1)")
    space: float = Field(description="Space capabilities (0-1)")
    logistics: float = Field(description="Logistical capacity (0-1)")
    isr: float = Field(description="Intelligence, Surveillance, Reconnaissance (0-1)")

# ============================================================================
# EVENTS AND ACTIONS
# ============================================================================

class WorldEvent(BaseModel):
    """Raw event from news or other sources"""
    timestamp: datetime = Field(description="When the event occurred")
    source: str = Field(description="Source of the event")
    text: str = Field(description="Raw event text")
    metadata: Dict[str, Any] = Field(description="Additional metadata")
    
    # Parsed information
    event_type: Optional[EventType] = Field(default=None, description="Type of event")
    actors: List[str] = Field(default_factory=list, description="Countries involved")
    location: Optional[str] = Field(default=None, description="Location of event")
    severity: float = Field(default=0.5, description="Event severity (0-1)")
    reliability: float = Field(default=0.8, description="Information reliability (0-1)")
    linked_evidence: List[str] = Field(default_factory=list, description="Related evidence IDs")

class Action(BaseModel):
    """Action taken by a country"""
    timestamp: datetime = Field(description="When action was taken")
    actor_id: str = Field(description="Country taking action")
    action_type: ActionType = Field(description="Type of action")
    parameters: Dict[str, Any] = Field(description="Action parameters")
    origin_mode: str = Field(description="Game mode that generated this action")
    risk_estimate: Dict[str, float] = Field(description="Risk assessment")
    seed: int = Field(description="Random seed for reproducibility")
    
    # Target information
    target_countries: List[str] = Field(description="Target countries")
    target_regions: List[str] = Field(description="Target regions")

class Outcome(BaseModel):
    """Result of an action"""
    timestamp: datetime = Field(description="When outcome occurred")
    action_id: str = Field(description="Related action ID")
    result: Dict[str, Any] = Field(description="Outcome details")
    losses: Dict[str, Any] = Field(description="Losses incurred")
    territory_changes: Dict[str, Any] = Field(description="Territorial changes")
    diplomatic_changes: Dict[str, Any] = Field(description="Diplomatic impact")
    
    # Escalation effects
    escalation_triggered: bool = Field(description="Whether escalation occurred")
    new_escalation_level: Optional[EscalationLevel] = Field(description="New escalation level")

# ============================================================================
# NARRATIVE AND OUTPUT
# ============================================================================

class GeneratedNews(BaseModel):
    """AI-generated news article"""
    timestamp: datetime = Field(description="When article was generated")
    headline: str = Field(description="Article headline")
    lede: str = Field(description="Article lede")
    body: str = Field(description="Article body")
    citations: List[str] = Field(description="Cited evidence IDs")
    visibility: float = Field(description="Article visibility/impact (0-1)")
    
    # Metadata
    author: str = Field(default="Psychohistory Engine", description="Article author")
    category: str = Field(description="News category")
    severity: float = Field(default=0.5, description="Event severity (0-1)")
    reliability: float = Field(default=0.9, description="Article reliability (0-1)")
    source: str = Field(default="World Brain", description="News source")

class MapState(BaseModel):
    """Current state of the world map"""
    timestamp: datetime = Field(description="When state was captured")
    regions: Dict[str, Dict[str, Any]] = Field(description="Region states")
    
    # Global indicators
    global_tension: float = Field(description="Global tension level (0-1)")
    nuclear_threat_level: float = Field(description="Nuclear threat level (0-1)")
    economic_stability: float = Field(description="Global economic stability (0-1)")

# ============================================================================
# PSYCHOHISTORY SIMULATION
# ============================================================================

class PsychohistorySimulation(BaseModel):
    """Complete psychohistory simulation state"""
    simulation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(description="Simulation name")
    description: str = Field(description="Simulation description")
    
    # World state
    countries: Dict[str, Country] = Field(default_factory=dict, description="All countries")
    doctrines: Dict[str, Doctrine] = Field(default_factory=dict, description="Country doctrines")
    objectives: Dict[str, Objectives] = Field(default_factory=dict, description="Country objectives")
    relations: List[Relations] = Field(default_factory=list, description="Bilateral relations")
    postures: Dict[str, Posture] = Field(default_factory=dict, description="Country postures")
    capabilities: Dict[str, Capabilities] = Field(default_factory=dict, description="Country capabilities")
    
    # Events and actions
    events: List[WorldEvent] = Field(default_factory=list, description="World events")
    actions: List[Action] = Field(default_factory=list, description="Actions taken")
    outcomes: List[Outcome] = Field(default_factory=list, description="Action outcomes")
    
    # Output
    news: List[GeneratedNews] = Field(default_factory=list, description="Generated news")
    map_states: List[MapState] = Field(default_factory=list, description="Map state history")
    
    # Simulation metadata
    current_tick: int = Field(description="Current simulation tick")
    start_date: datetime = Field(description="Simulation start date")
    current_date: datetime = Field(description="Current simulation date")
    seed: int = Field(description="Random seed for reproducibility")
    
    # Configuration
    tick_frequency: str = Field(default="weekly", description="How often ticks occur")
    max_ticks: int = Field(default=52, description="Maximum number of ticks")

class SimulationRequest(BaseModel):
    """Request to create a new psychohistory simulation"""
    name: str = Field(description="Simulation name")
    description: str = Field(description="Simulation description")
    start_date: datetime = Field(description="Start date")
    duration_weeks: int = Field(description="Duration in weeks")
    seed: Optional[int] = Field(description="Random seed for reproducibility")
    
    # Configuration options
    include_news_ingestion: bool = Field(default=True, description="Include real news")
    include_predictive_history: bool = Field(default=True, description="Include Predictive History data")
    include_sociological_factors: bool = Field(default=True, description="Include human factors")

class SimulationResponse(BaseModel):
    """Response from psychohistory simulation"""
    simulation_id: str = Field(description="Simulation ID")
    status: str = Field(description="Simulation status")
    current_tick: int = Field(description="Current tick")
    total_ticks: int = Field(description="Total ticks")
    latest_news: List[GeneratedNews] = Field(description="Latest generated news")
    map_state: MapState = Field(description="Current map state")
    recent_events: List[WorldEvent] = Field(description="Recent world events")

# ============================================================================
# UTILITY MODELS
# ============================================================================

class RiskProfile(BaseModel):
    """Risk assessment for an action"""
    operational_risk: float = Field(description="Tactical failure risk (0-1)")
    escalation_risk: float = Field(description="Escalation risk (0-1)")
    economic_risk: float = Field(description="Economic impact risk (0-1)")
    political_risk: float = Field(description="Political fallout risk (0-1)")
    nuclear_risk: float = Field(description="Nuclear escalation risk (0-1)")
    
    # Detailed breakdown
    risk_factors: Dict[str, float] = Field(default_factory=dict, description="Individual risk factors")
    mitigation_options: List[str] = Field(default_factory=list, description="Possible risk mitigations")

class UtilityFunction(BaseModel):
    """Country's utility function for decision making"""
    country_id: str = Field(description="Country ID")
    weights: Dict[str, float] = Field(description="Goal weights")
    
    # Core goals
    security_weight: float = Field(description="Security importance")
    economy_weight: float = Field(description="Economic importance")
    prestige_weight: float = Field(description="Prestige importance")
    stability_weight: float = Field(description="Domestic stability importance")
    
    # Time preferences
    short_term_bias: float = Field(description="Short-term vs long-term bias")
    risk_tolerance: float = Field(description="Risk tolerance level")

class ActionOption(BaseModel):
    """Possible action for a country"""
    action_type: ActionType = Field(description="Type of action")
    description: str = Field(description="Action description")
    parameters: Dict[str, Any] = Field(description="Action parameters")
    expected_utility: float = Field(description="Expected utility gain")
    risk_profile: RiskProfile = Field(description="Risk assessment")
    feasibility: float = Field(description="Feasibility score (0-1)")
    
    # Requirements
    required_capabilities: List[str] = Field(description="Required capabilities")
    required_resources: Dict[str, float] = Field(description="Required resources")
    diplomatic_cost: float = Field(description="Diplomatic cost")
