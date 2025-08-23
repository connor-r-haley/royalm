from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
import json

# ============================================================================
# CORE GAME MODELS
# ============================================================================

class Faction(str, Enum):
    US = "US"
    RU = "RU" 
    CN = "CN"
    NEUTRAL = "NEUTRAL"
    EU = "EU"
    INDIA = "IN"
    JAPAN = "JP"
    UK = "GB"
    FRANCE = "FR"
    GERMANY = "DE"

class ResourceType(str, Enum):
    OIL = "oil"
    GAS = "gas"
    RARE_EARTHS = "rare_earths"
    FOOD = "food"
    WATER = "water"
    URANIUM = "uranium"
    COAL = "coal"
    IRON = "iron"
    ALUMINUM = "aluminum"
    COPPER = "copper"

class UnitType(str, Enum):
    CARRIER = "carrier"
    DESTROYER = "destroyer"
    SUBMARINE = "submarine"
    FIGHTER = "fighter"
    BOMBER = "bomber"
    TANK = "tank"
    INFANTRY = "infantry"
    MISSILE = "missile"
    SATELLITE = "satellite"
    DRONE = "drone"

class DiplomaticStatus(str, Enum):
    ALLY = "ally"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
    WAR = "war"
    TRADE_PARTNER = "trade_partner"
    MILITARY_PARTNER = "military_partner"

class EventType(str, Enum):
    DIPLOMATIC = "diplomatic"
    MILITARY = "military"
    ECONOMIC = "economic"
    POLITICAL = "political"
    NATURAL_DISASTER = "natural_disaster"
    TECHNOLOGICAL = "technological"
    INTELLIGENCE = "intelligence"

# ============================================================================
# COUNTRY & TERRITORY MODELS
# ============================================================================

class EconomicData(BaseModel):
    gdp_nominal: float = Field(description="Nominal GDP in USD")
    gdp_per_capita: float = Field(description="GDP per capita in USD")
    inflation_rate: float = Field(description="Annual inflation rate %")
    unemployment_rate: float = Field(description="Unemployment rate %")
    debt_to_gdp: float = Field(description="Government debt to GDP ratio %")
    trade_balance: float = Field(description="Trade balance in USD")
    foreign_reserves: float = Field(description="Foreign exchange reserves in USD")
    currency_strength: float = Field(description="Currency strength index 0-1")

class MilitaryData(BaseModel):
    active_personnel: int = Field(description="Active military personnel")
    reserve_personnel: int = Field(description="Reserve military personnel")
    defense_budget: float = Field(description="Annual defense budget in USD")
    nuclear_weapons: int = Field(description="Number of nuclear weapons")
    aircraft_carriers: int = Field(description="Number of aircraft carriers")
    submarines: int = Field(description="Number of submarines")
    tanks: int = Field(description="Number of main battle tanks")
    fighter_jets: int = Field(description="Number of fighter aircraft")
    military_technology_level: float = Field(description="Military tech level 0-1")

class PoliticalData(BaseModel):
    government_type: str = Field(description="Type of government")
    political_stability: float = Field(description="Political stability index 0-1")
    corruption_index: float = Field(description="Corruption perception index 0-1")
    press_freedom: float = Field(description="Press freedom index 0-1")
    democracy_index: float = Field(description="Democracy index 0-1")
    current_leader: str = Field(description="Current head of state/government")
    ruling_party: str = Field(description="Ruling political party")
    opposition_strength: float = Field(description="Opposition strength 0-1")

class SocialData(BaseModel):
    population: int = Field(description="Total population")
    population_growth: float = Field(description="Annual population growth rate %")
    median_age: float = Field(description="Median age")
    literacy_rate: float = Field(description="Literacy rate %")
    internet_penetration: float = Field(description="Internet penetration %")
    urbanization_rate: float = Field(description="Urbanization rate %")
    life_expectancy: float = Field(description="Life expectancy in years")
    social_unrest_index: float = Field(description="Social unrest index 0-1")

class ResourceReserves(BaseModel):
    oil_reserves: float = Field(description="Oil reserves in barrels")
    gas_reserves: float = Field(description="Gas reserves in cubic meters")
    coal_reserves: float = Field(description="Coal reserves in tons")
    uranium_reserves: float = Field(description="Uranium reserves in tons")
    rare_earth_reserves: float = Field(description="Rare earth reserves in tons")
    arable_land: float = Field(description="Arable land in hectares")
    fresh_water: float = Field(description="Fresh water resources in cubic km")

class Country(BaseModel):
    id: str = Field(description="ISO 3166-1 alpha-2 country code")
    name: str = Field(description="Country name")
    faction: Faction = Field(default=Faction.NEUTRAL, description="Current faction alignment")
    morale: float = Field(default=0.5, ge=0.0, le=1.0, description="National morale 0-1")
    
    # Geographic data
    capital: Optional[str] = Field(description="Capital city")
    coordinates: Optional[List[float]] = Field(description="[longitude, latitude] of capital")
    area_km2: Optional[float] = Field(description="Land area in square kilometers")
    
    # Detailed data
    economic: Optional[EconomicData] = None
    military: Optional[MilitaryData] = None
    political: Optional[PoliticalData] = None
    social: Optional[SocialData] = None
    resources: Optional[ResourceReserves] = None
    
    # Game state
    is_territory: bool = Field(default=False, description="Whether this is a territory of another country")
    mother_country: Optional[str] = Field(description="Parent country if this is a territory")
    description: Optional[str] = Field(description="Description or notes")
    
    # Dynamic values
    current_gdp: Optional[float] = None
    current_morale: Optional[float] = None
    war_exhaustion: float = Field(default=0.0, ge=0.0, le=1.0)
    diplomatic_relations: Dict[str, DiplomaticStatus] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True

# ============================================================================
# MILITARY & UNITS
# ============================================================================

class Unit(BaseModel):
    id: str = Field(description="Unique unit identifier")
    type: UnitType = Field(description="Type of military unit")
    faction: Faction = Field(description="Owning faction")
    pos: List[float] = Field(description="[longitude, latitude] position")
    
    # Combat stats
    health: float = Field(default=1.0, ge=0.0, le=1.0)
    fuel: float = Field(default=1.0, ge=0.0, le=1.0)
    ammunition: float = Field(default=1.0, ge=0.0, le=1.0)
    morale: float = Field(default=0.8, ge=0.0, le=1.0)
    
    # Capabilities
    attack_power: float = Field(description="Attack strength")
    defense_power: float = Field(description="Defense strength")
    range_km: float = Field(description="Operational range in kilometers")
    speed_kmh: float = Field(description="Speed in km/h")
    
    # Status
    is_active: bool = Field(default=True)
    current_mission: Optional[str] = None
    target_id: Optional[str] = None
    
    class Config:
        use_enum_values = True

class MilitaryBase(BaseModel):
    id: str = Field(description="Unique base identifier")
    name: str = Field(description="Base name")
    faction: Faction = Field(description="Owning faction")
    pos: List[float] = Field(description="[longitude, latitude] position")
    
    # Base capabilities
    max_units: int = Field(description="Maximum units that can be stationed")
    current_units: List[str] = Field(default_factory=list, description="List of unit IDs")
    base_type: str = Field(description="Type of base (air, naval, army, etc.)")
    
    # Infrastructure
    runways: int = Field(default=0, description="Number of runways")
    docks: int = Field(default=0, description="Number of docks")
    barracks_capacity: int = Field(default=0, description="Barracks capacity")
    fuel_storage: float = Field(description="Fuel storage capacity")
    ammunition_storage: float = Field(description="Ammunition storage capacity")
    
    # Status
    is_operational: bool = Field(default=True)
    damage_level: float = Field(default=0.0, ge=0.0, le=1.0)
    
    class Config:
        use_enum_values = True

# ============================================================================
# DIPLOMATIC & ECONOMIC MODELS
# ============================================================================

class DiplomaticRelation(BaseModel):
    country_a: str = Field(description="First country code")
    country_b: str = Field(description="Second country code")
    status: DiplomaticStatus = Field(description="Current diplomatic status")
    trust_level: float = Field(default=0.5, ge=0.0, le=1.0, description="Trust level between countries")
    
    # Economic ties
    trade_volume: float = Field(default=0.0, description="Annual trade volume in USD")
    investment_flow: float = Field(default=0.0, description="Investment flow in USD")
    energy_dependence: float = Field(default=0.0, description="Energy dependence level 0-1")
    
    # Military cooperation
    military_alliance: bool = Field(default=False)
    joint_exercises: bool = Field(default=False)
    arms_sales: bool = Field(default=False)
    
    # Historical factors
    historical_conflicts: int = Field(default=0, description="Number of historical conflicts")
    years_of_relations: int = Field(default=0, description="Years of diplomatic relations")
    
    class Config:
        use_enum_values = True

class TradeRoute(BaseModel):
    id: str = Field(description="Unique trade route identifier")
    origin_country: str = Field(description="Origin country code")
    destination_country: str = Field(description="Destination country code")
    
    # Trade details
    goods_type: List[str] = Field(description="Types of goods traded")
    annual_volume: float = Field(description="Annual trade volume in USD")
    route_type: str = Field(description="Type of route (sea, land, air, pipeline)")
    
    # Route path
    waypoints: List[List[float]] = Field(description="Route waypoints [lon, lat]")
    
    # Status
    is_active: bool = Field(default=True)
    security_level: float = Field(default=1.0, ge=0.0, le=1.0)
    efficiency: float = Field(default=1.0, ge=0.0, le=1.0)

class EconomicSanction(BaseModel):
    id: str = Field(description="Unique sanction identifier")
    imposing_country: str = Field(description="Country imposing sanctions")
    target_country: str = Field(description="Target country")
    
    # Sanction details
    sanction_type: List[str] = Field(description="Types of sanctions")
    severity: float = Field(description="Sanction severity 0-1")
    start_date: datetime = Field(description="When sanctions began")
    end_date: Optional[datetime] = Field(description="When sanctions end (if applicable)")
    
    # Economic impact
    estimated_impact: float = Field(description="Estimated economic impact in USD")
    sectors_affected: List[str] = Field(description="Economic sectors affected")
    
    # Status
    is_active: bool = Field(default=True)
    compliance_level: float = Field(default=0.0, ge=0.0, le=1.0)

# ============================================================================
# EVENTS & NEWS MODELS
# ============================================================================

class WorldEvent(BaseModel):
    id: str = Field(description="Unique event identifier")
    event_type: EventType = Field(description="Type of event")
    title: str = Field(description="Event title")
    description: str = Field(description="Event description")
    
    # Location and participants
    location: Optional[List[float]] = Field(description="[longitude, latitude] of event")
    affected_countries: List[str] = Field(description="Countries affected by this event")
    primary_actors: List[str] = Field(description="Primary actors involved")
    
    # Timing
    start_date: datetime = Field(description="When the event started")
    end_date: Optional[datetime] = Field(description="When the event ended")
    duration_days: Optional[int] = Field(description="Duration in days")
    
    # Impact assessment
    geopolitical_impact: float = Field(description="Geopolitical impact score 0-1")
    economic_impact: float = Field(description="Economic impact score 0-1")
    military_impact: float = Field(description="Military impact score 0-1")
    social_impact: float = Field(description="Social impact score 0-1")
    
    # Game effects
    morale_effects: Dict[str, float] = Field(default_factory=dict, description="Morale changes by country")
    diplomatic_effects: List[Dict[str, Any]] = Field(default_factory=list, description="Diplomatic relation changes")
    economic_effects: Dict[str, float] = Field(default_factory=dict, description="Economic changes by country")
    
    # Metadata
    source: str = Field(description="Source of the event data")
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in event accuracy")
    tags: List[str] = Field(default_factory=list, description="Event tags for categorization")
    
    class Config:
        use_enum_values = True

class NewsHeadline(BaseModel):
    id: str = Field(description="Unique headline identifier")
    title: str = Field(description="News headline")
    summary: str = Field(description="Brief summary")
    source: str = Field(description="News source")
    url: Optional[str] = Field(description="Source URL")
    
    # Content
    content: str = Field(description="Full news content")
    sentiment: float = Field(description="Sentiment score -1 to 1")
    
    # Geographic relevance
    relevant_countries: List[str] = Field(description="Countries mentioned/relevant")
    location: Optional[List[float]] = Field(description="[longitude, latitude] if location-specific")
    
    # Timing
    published_date: datetime = Field(description="When the news was published")
    relevance_score: float = Field(description="Relevance to simulation 0-1")
    
    # Game impact
    morale_impact: Dict[str, float] = Field(default_factory=dict, description="Morale impact by country")
    diplomatic_impact: List[Dict[str, Any]] = Field(default_factory=list, description="Diplomatic impacts")

# ============================================================================
# GAME STATE MODELS
# ============================================================================

class GameSession(BaseModel):
    session_id: str = Field(description="Unique session identifier")
    start_date: datetime = Field(description="When the session started")
    current_date: datetime = Field(description="Current game date")
    game_speed: float = Field(default=1.0, description="Game time speed multiplier")
    
    # World state
    countries: Dict[str, Country] = Field(default_factory=dict, description="All countries in the game")
    units: Dict[str, Unit] = Field(default_factory=dict, description="All military units")
    bases: Dict[str, MilitaryBase] = Field(default_factory=dict, description="All military bases")
    
    # Diplomatic state
    diplomatic_relations: Dict[str, DiplomaticRelation] = Field(default_factory=dict, description="All diplomatic relations")
    trade_routes: Dict[str, TradeRoute] = Field(default_factory=dict, description="All trade routes")
    sanctions: Dict[str, EconomicSanction] = Field(default_factory=dict, description="Active sanctions")
    
    # Events and news
    world_events: Dict[str, WorldEvent] = Field(default_factory=dict, description="All world events")
    news_headlines: List[NewsHeadline] = Field(default_factory=list, description="Recent news headlines")
    
    # Game mechanics
    tick: int = Field(default=0, description="Game tick counter")
    turn_number: int = Field(default=0, description="Current turn number")
    phase: str = Field(default="planning", description="Current game phase")
    
    # Player actions
    pending_actions: List[Dict[str, Any]] = Field(default_factory=list, description="Pending player actions")
    action_history: List[Dict[str, Any]] = Field(default_factory=list, description="Action history")
    
    # Settings
    ai_enabled: bool = Field(default=True, description="Whether AI opponents are enabled")
    real_time_events: bool = Field(default=True, description="Whether real-time events are enabled")
    difficulty_level: str = Field(default="medium", description="Game difficulty level")

class GameAction(BaseModel):
    action_id: str = Field(description="Unique action identifier")
    player_id: str = Field(description="Player who initiated the action")
    action_type: str = Field(description="Type of action")
    timestamp: datetime = Field(description="When the action was initiated")
    
    # Action details
    target_id: Optional[str] = Field(description="Target of the action")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    
    # Status
    status: str = Field(default="pending", description="Action status")
    execution_time: Optional[datetime] = Field(description="When the action was executed")
    result: Optional[Dict[str, Any]] = Field(description="Action result")

# ============================================================================
# API MODELS
# ============================================================================

class SessionCreateRequest(BaseModel):
    start_date: Optional[datetime] = Field(description="Starting date for the simulation")
    ai_enabled: bool = Field(default=True)
    real_time_events: bool = Field(default=True)
    difficulty_level: str = Field(default="medium")

class SessionCreateResponse(BaseModel):
    session_id: str
    state: GameSession
    message: str = "Session created successfully"

class ActionRequest(BaseModel):
    player_id: str
    action_type: str
    target_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ActionResponse(BaseModel):
    action_id: str
    status: str
    message: str
    estimated_completion: Optional[datetime] = None

class WorldUpdateResponse(BaseModel):
    session_id: str
    tick: int
    current_date: datetime
    changes: Dict[str, Any]
    new_events: List[WorldEvent]
    new_headlines: List[NewsHeadline]
    morale_updates: Dict[str, float]
    diplomatic_updates: List[Dict[str, Any]]

# ============================================================================
# CHATGPT INTEGRATION MODELS
# ============================================================================

class ChatGPTRequest(BaseModel):
    prompt: str = Field(description="The prompt to send to ChatGPT")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    max_tokens: int = Field(default=1000, description="Maximum tokens for response")
    temperature: float = Field(default=0.7, description="Response creativity 0-1")

class ChatGPTResponse(BaseModel):
    response: str = Field(description="ChatGPT's response")
    usage: Dict[str, int] = Field(description="Token usage information")
    model: str = Field(description="Model used for response")

class EventAnalysisRequest(BaseModel):
    date: datetime = Field(description="Date to analyze events for")
    countries_of_interest: List[str] = Field(description="Countries to focus on")
    event_types: List[EventType] = Field(description="Types of events to analyze")
    include_historical_context: bool = Field(default=True, description="Include historical context")

class EventAnalysisResponse(BaseModel):
    events: List[WorldEvent]
    analysis: str = Field(description="AI analysis of the events")
    predictions: List[Dict[str, Any]] = Field(description="AI predictions based on events")
    confidence_scores: Dict[str, float] = Field(description="Confidence scores for predictions")

class GeopoliticalUpdateRequest(BaseModel):
    current_date: datetime = Field(description="Current date for the update")
    focus_areas: List[str] = Field(description="Geographic areas to focus on")
    update_type: str = Field(description="Type of update (diplomatic, military, economic, etc.)")

class GeopoliticalUpdateResponse(BaseModel):
    updates: List[Dict[str, Any]] = Field(description="Geopolitical updates")
    new_events: List[WorldEvent]
    diplomatic_changes: List[Dict[str, Any]]
    economic_changes: List[Dict[str, Any]]
    military_changes: List[Dict[str, Any]]
    analysis: str = Field(description="AI analysis of the updates")
