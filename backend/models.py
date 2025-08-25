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
    IRAN = "IR"
    ISRAEL = "IL"
    NORTH_KOREA = "KP"

class PlayableCountryType(str, Enum):
    MAJOR_POWER = "major_power"      # US, China, Russia, EU
    RISING_POWER = "rising_power"    # India
    REGIONAL_PLAYER = "regional_player"  # Iran, Israel, North Korea

class PlayableCountry(BaseModel):
    id: str = Field(description="ISO 3166-1 alpha-2 country code")
    name: str = Field(description="Country name")
    type: PlayableCountryType = Field(description="Type of playable country")
    faction: Faction = Field(description="Starting faction")
    
    # Starting conditions
    starting_morale: float = Field(default=0.7, ge=0.0, le=1.0)
    starting_economic_strength: float = Field(default=0.5, ge=0.0, le=1.0)
    starting_military_strength: float = Field(default=0.5, ge=0.0, le=1.0)
    starting_diplomatic_influence: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Unique characteristics
    special_abilities: List[str] = Field(default_factory=list, description="Special abilities/advantages")
    starting_units: List[str] = Field(default_factory=list, description="Starting military units")
    starting_bases: List[str] = Field(default_factory=list, description="Starting military bases")
    starting_allies: List[str] = Field(default_factory=list, description="Starting allies")
    starting_enemies: List[str] = Field(default_factory=list, description="Starting enemies")
    
    # Game balance
    victory_conditions: List[str] = Field(default_factory=list, description="Victory conditions for this country")
    unique_challenges: List[str] = Field(default_factory=list, description="Unique challenges/weaknesses")
    
    # Description
    description: str = Field(description="Country description and playstyle")
    playstyle_tips: List[str] = Field(default_factory=list, description="Tips for playing this country")
    
    class Config:
        use_enum_values = True

# ============================================================================
# PLAYABLE COUNTRIES CONFIGURATION
# ============================================================================

PLAYABLE_COUNTRIES = {
    "US": PlayableCountry(
        id="US",
        name="United States",
        type=PlayableCountryType.MAJOR_POWER,
        faction=Faction.US,
        starting_morale=0.8,
        starting_economic_strength=0.9,
        starting_military_strength=0.9,
        starting_diplomatic_influence=0.8,
        special_abilities=[
            "Global Power Projection",
            "Advanced Technology",
            "Strong Alliances",
            "Economic Dominance",
            "Nuclear Arsenal"
        ],
        starting_units=["US-CVN-1", "US-AIR-1", "US-ARMY-1"],
        starting_bases=["US-BASE-1", "US-BASE-2"],
        starting_allies=["GB", "FR", "DE", "JP"],
        starting_enemies=["RU", "CN", "KP"],
        victory_conditions=[
            "Maintain global hegemony",
            "Prevent rival superpowers from gaining dominance",
            "Protect NATO allies",
            "Maintain economic leadership"
        ],
        unique_challenges=[
            "High expectations from allies",
            "Complex global commitments",
            "Public opinion sensitivity",
            "High maintenance costs"
        ],
        description="The world's sole superpower with unmatched military and economic might. Lead the free world against authoritarian regimes.",
        playstyle_tips=[
            "Use your global reach to project power",
            "Leverage your strong alliances",
            "Maintain technological superiority",
            "Balance multiple global commitments"
        ]
    ),
    
    "CN": PlayableCountry(
        id="CN",
        name="China",
        type=PlayableCountryType.MAJOR_POWER,
        faction=Faction.CN,
        starting_morale=0.7,
        starting_economic_strength=0.8,
        starting_military_strength=0.7,
        starting_diplomatic_influence=0.6,
        special_abilities=[
            "Belt and Road Initiative",
            "Manufacturing Powerhouse",
            "Regional Dominance",
            "Economic Leverage",
            "Cyber Warfare"
        ],
        starting_units=["CN-ARMY-1", "CN-AIR-1", "CN-NAVY-1"],
        starting_bases=["CN-BASE-1", "CN-BASE-2"],
        starting_allies=["KP", "IR"],
        starting_enemies=["US", "JP", "IN"],
        victory_conditions=[
            "Establish regional hegemony",
            "Expand economic influence globally",
            "Reunify Taiwan",
            "Challenge US dominance"
        ],
        unique_challenges=[
            "Resource dependency",
            "Regional tensions",
            "Economic transition challenges",
            "International scrutiny"
        ],
        description="A rising superpower seeking to challenge US dominance and establish itself as the preeminent power in Asia.",
        playstyle_tips=[
            "Expand your economic influence",
            "Build regional alliances",
            "Leverage your manufacturing power",
            "Use economic tools for political gain"
        ]
    ),
    
    "RU": PlayableCountry(
        id="RU",
        name="Russia",
        type=PlayableCountryType.MAJOR_POWER,
        faction=Faction.RU,
        starting_morale=0.6,
        starting_economic_strength=0.4,
        starting_military_strength=0.8,
        starting_diplomatic_influence=0.5,
        special_abilities=[
            "Energy Superpower",
            "Nuclear Arsenal",
            "Hybrid Warfare",
            "Regional Influence",
            "Strategic Depth"
        ],
        starting_units=["RU-ARMY-1", "RU-AIR-1", "RU-NAVY-1"],
        starting_bases=["RU-BASE-1", "RU-BASE-2"],
        starting_allies=["IR", "KP"],
        starting_enemies=["US", "EU", "GB"],
        victory_conditions=[
            "Restore Soviet sphere of influence",
            "Control energy supplies to Europe",
            "Prevent NATO expansion",
            "Maintain great power status"
        ],
        unique_challenges=[
            "Economic sanctions",
            "Demographic decline",
            "Technological lag",
            "International isolation"
        ],
        description="A resurgent power seeking to restore its former glory and challenge Western dominance through energy and military might.",
        playstyle_tips=[
            "Use energy as a weapon",
            "Leverage your nuclear deterrent",
            "Exploit Western divisions",
            "Focus on regional dominance"
        ]
    ),
    
    "EU": PlayableCountry(
        id="EU",
        name="European Union",
        type=PlayableCountryType.MAJOR_POWER,
        faction=Faction.EU,
        starting_morale=0.7,
        starting_economic_strength=0.8,
        starting_military_strength=0.6,
        starting_diplomatic_influence=0.7,
        special_abilities=[
            "Economic Union",
            "Soft Power",
            "Technological Innovation",
            "Regulatory Power",
            "Multilateral Leadership"
        ],
        starting_units=["EU-ARMY-1", "EU-AIR-1"],
        starting_bases=["EU-BASE-1"],
        starting_allies=["US", "GB"],
        starting_enemies=["RU"],
        victory_conditions=[
            "Maintain European unity",
            "Expand EU influence",
            "Promote democratic values",
            "Achieve strategic autonomy"
        ],
        unique_challenges=[
            "Internal divisions",
            "Dependency on US security",
            "Complex decision-making",
            "Economic disparities"
        ],
        description="A unique supranational entity representing the collective power of European nations, balancing between US and Russian influence.",
        playstyle_tips=[
            "Use economic and regulatory power",
            "Maintain unity among member states",
            "Leverage soft power and diplomacy",
            "Build strategic partnerships"
        ]
    ),
    
    "IN": PlayableCountry(
        id="IN",
        name="India",
        type=PlayableCountryType.RISING_POWER,
        faction=Faction.NEUTRAL,
        starting_morale=0.6,
        starting_economic_strength=0.6,
        starting_military_strength=0.5,
        starting_diplomatic_influence=0.4,
        special_abilities=[
            "Non-Aligned Movement",
            "Demographic Dividend",
            "IT Powerhouse",
            "Nuclear Power",
            "Strategic Location"
        ],
        starting_units=["IN-ARMY-1", "IN-AIR-1"],
        starting_bases=["IN-BASE-1"],
        starting_allies=[],
        starting_enemies=["CN"],
        victory_conditions=[
            "Achieve great power status",
            "Maintain strategic autonomy",
            "Resolve regional conflicts",
            "Economic development"
        ],
        unique_challenges=[
            "Poverty and inequality",
            "Regional tensions",
            "Infrastructure gaps",
            "Bureaucratic inefficiency"
        ],
        description="A rising democracy seeking to carve its own path between major powers while developing into a global force.",
        playstyle_tips=[
            "Stay non-aligned initially",
            "Leverage your demographic advantage",
            "Build regional influence",
            "Choose allies carefully"
        ]
    ),
    
    "IR": PlayableCountry(
        id="IR",
        name="Iran",
        type=PlayableCountryType.REGIONAL_PLAYER,
        faction=Faction.NEUTRAL,
        starting_morale=0.5,
        starting_economic_strength=0.3,
        starting_military_strength=0.4,
        starting_diplomatic_influence=0.3,
        special_abilities=[
            "Proxy Warfare",
            "Energy Resources",
            "Regional Influence",
            "Asymmetric Capabilities",
            "Religious Authority"
        ],
        starting_units=["IR-ARMY-1", "IR-AIR-1"],
        starting_bases=["IR-BASE-1"],
        starting_allies=["RU", "CN"],
        starting_enemies=["US", "IL"],
        victory_conditions=[
            "Establish regional dominance",
            "Resist Western influence",
            "Support proxy groups",
            "Achieve nuclear capability"
        ],
        unique_challenges=[
            "Economic sanctions",
            "International isolation",
            "Regional hostility",
            "Internal dissent"
        ],
        description="A regional power using asymmetric warfare and proxy conflicts to challenge US dominance in the Middle East.",
        playstyle_tips=[
            "Use proxy warfare effectively",
            "Leverage energy resources",
            "Build regional alliances",
            "Exploit Western vulnerabilities"
        ]
    ),
    
    "IL": PlayableCountry(
        id="IL",
        name="Israel",
        type=PlayableCountryType.REGIONAL_PLAYER,
        faction=Faction.NEUTRAL,
        starting_morale=0.7,
        starting_economic_strength=0.6,
        starting_military_strength=0.7,
        starting_diplomatic_influence=0.4,
        special_abilities=[
            "Military Technology",
            "Intelligence Services",
            "Nuclear Arsenal",
            "US Alliance",
            "Innovation Hub"
        ],
        starting_units=["IL-ARMY-1", "IL-AIR-1"],
        starting_bases=["IL-BASE-1"],
        starting_allies=["US"],
        starting_enemies=["IR"],
        victory_conditions=[
            "Ensure national security",
            "Maintain regional military superiority",
            "Strengthen US alliance",
            "Achieve regional recognition"
        ],
        unique_challenges=[
            "Regional hostility",
            "Small population",
            "Resource limitations",
            "International criticism"
        ],
        description="A small but technologically advanced nation surrounded by enemies, relying on superior military technology and US support.",
        playstyle_tips=[
            "Leverage your technological advantage",
            "Maintain US alliance",
            "Use intelligence effectively",
            "Punch above your weight"
        ]
    ),
    
    "KP": PlayableCountry(
        id="KP",
        name="North Korea",
        type=PlayableCountryType.REGIONAL_PLAYER,
        faction=Faction.NEUTRAL,
        starting_morale=0.4,
        starting_economic_strength=0.2,
        starting_military_strength=0.6,
        starting_diplomatic_influence=0.2,
        special_abilities=[
            "Nuclear Deterrent",
            "Asymmetric Warfare",
            "Cyber Capabilities",
            "Regime Survival",
            "Strategic Patience"
        ],
        starting_units=["KP-ARMY-1", "KP-AIR-1"],
        starting_bases=["KP-BASE-1"],
        starting_allies=["CN", "RU"],
        starting_enemies=["US", "JP", "KR"],
        victory_conditions=[
            "Ensure regime survival",
            "Achieve nuclear recognition",
            "Extract concessions from enemies",
            "Maintain independence"
        ],
        unique_challenges=[
            "Economic isolation",
            "Resource scarcity",
            "International sanctions",
            "Technological backwardness"
        ],
        description="A nuclear-armed pariah state using brinkmanship and nuclear threats to extract concessions and ensure regime survival.",
        playstyle_tips=[
            "Use nuclear threats strategically",
            "Leverage your allies",
            "Exploit enemy divisions",
            "Focus on regime survival"
        ]
    )
}

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
# GAME MODE & ROUND SYSTEM MODELS
# ============================================================================

class GameMode(str, Enum):
    SINGLE_PLAYER = "single_player"
    MULTIPLAYER = "multiplayer"

class RoundPhase(str, Enum):
    PLANNING = "planning"           # Players make decisions
    RESOLUTION = "resolution"       # Actions are processed
    EVENTS = "events"              # World events occur
    DIPLOMACY = "diplomacy"        # Diplomatic interactions
    ECONOMIC = "economic"          # Economic updates
    MILITARY = "military"          # Military movements/conflicts

class ActionType(str, Enum):
    # Diplomatic Actions
    FORM_ALLIANCE = "form_alliance"
    BREAK_ALLIANCE = "break_alliance"
    DECLARE_WAR = "declare_war"
    SIGN_TRADE_AGREEMENT = "sign_trade_agreement"
    IMPOSE_SANCTIONS = "impose_sanctions"
    
    # Military Actions
    MOVE_UNITS = "move_units"
    ATTACK_COUNTRY = "attack_country"
    BUILD_MILITARY = "build_military"
    DEPLOY_NUCLEAR = "deploy_nuclear"
    CONDUCT_ESPIONAGE = "conduct_espionage"
    
    # Economic Actions
    INVEST_IN_ECONOMY = "invest_in_economy"
    TRADE_RESOURCES = "trade_resources"
    BUILD_INFRASTRUCTURE = "build_infrastructure"
    MANIPULATE_CURRENCY = "manipulate_currency"
    
    # Political Actions
    INFLUENCE_ELECTIONS = "influence_elections"
    SUPPORT_REBELS = "support_rebels"
    MEDIA_CAMPAIGN = "media_campaign"
    DIPLOMATIC_VISIT = "diplomatic_visit"

class PlayerAction(BaseModel):
    action_id: str = Field(description="Unique action identifier")
    player_country: str = Field(description="Country performing the action")
    action_type: ActionType = Field(description="Type of action")
    target_country: Optional[str] = Field(description="Target country (if applicable)")
    
    # Action parameters
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action-specific parameters")
    
    # Timing
    round_number: int = Field(description="Round when action was submitted")
    phase: RoundPhase = Field(description="Phase when action was submitted")
    
    # Status
    status: str = Field(default="pending", description="Action status: pending, resolved, failed")
    result: Optional[Dict[str, Any]] = Field(description="Action result")
    
    # Secrecy
    is_secret: bool = Field(default=False, description="Whether this action is hidden from other players")
    revealed_round: Optional[int] = Field(description="Round when secret action is revealed")
    
    class Config:
        use_enum_values = True

class Round(BaseModel):
    round_number: int = Field(description="Round number")
    phase: RoundPhase = Field(description="Current phase")
    start_time: datetime = Field(description="When the round started")
    end_time: Optional[datetime] = Field(description="When the round ended")
    
    # Round events
    world_events: List[WorldEvent] = Field(default_factory=list, description="Events that occurred this round")
    player_actions: List[PlayerAction] = Field(default_factory=list, description="All actions submitted this round")
    diplomatic_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Diplomatic relation changes")
    economic_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Economic changes")
    military_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Military changes")
    
    # Round summary
    summary: Optional[str] = Field(description="Round summary for players")
    highlights: List[str] = Field(default_factory=list, description="Key highlights of the round")
    
    class Config:
        use_enum_values = True

class GameSession(BaseModel):
    session_id: str = Field(description="Unique session identifier")
    game_mode: GameMode = Field(description="Single-player or multiplayer")
    
    # Players
    host_player: str = Field(description="Host player country")
    players: Dict[str, str] = Field(default_factory=dict, description="Player ID -> Country mapping")
    max_players: int = Field(default=8, description="Maximum number of players")
    
    # Game state
    current_round: int = Field(default=1, description="Current round number")
    current_phase: RoundPhase = Field(default=RoundPhase.PLANNING, description="Current phase")
    rounds: List[Round] = Field(default_factory=list, description="All rounds")
    
    # World state
    countries: Dict[str, Country] = Field(default_factory=dict, description="All countries in the world")
    ai_controlled_countries: List[str] = Field(default_factory=list, description="Countries controlled by AI")
    
    # Game settings
    round_duration_minutes: int = Field(default=5, description="Duration of planning phase in minutes")
    max_actions_per_round: int = Field(default=3, description="Maximum actions per player per round")
    
    # Status
    is_active: bool = Field(default=True, description="Whether the game is active")
    start_date: datetime = Field(description="When the game started")
    end_date: Optional[datetime] = Field(description="When the game ended")
    
    class Config:
        use_enum_values = True

# ============================================================================
# AI CONTROLLER MODELS
# ============================================================================

class AIStrategy(str, Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    ECONOMIC = "economic"
    DIPLOMATIC = "diplomatic"
    ISOLATIONIST = "isolationist"
    EXPANSIONIST = "expansionist"

class AICountry(BaseModel):
    country_id: str = Field(description="Country being controlled by AI")
    strategy: AIStrategy = Field(description="AI strategy for this country")
    personality_traits: List[str] = Field(default_factory=list, description="AI personality traits")
    
    # AI decision making
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0, description="Risk tolerance 0-1")
    aggression_level: float = Field(default=0.5, ge=0.0, le=1.0, description="Aggression level 0-1")
    diplomatic_approach: float = Field(default=0.5, ge=0.0, le=1.0, description="Diplomatic vs military approach 0-1")
    
    # Relationships with other countries
    trusted_allies: List[str] = Field(default_factory=list, description="Countries this AI trusts")
    enemies: List[str] = Field(default_factory=list, description="Countries this AI considers enemies")
    neutral_countries: List[str] = Field(default_factory=list, description="Countries this AI is neutral toward")
    
    # Goals and objectives
    primary_goals: List[str] = Field(default_factory=list, description="Primary AI goals")
    secondary_goals: List[str] = Field(default_factory=list, description="Secondary AI goals")
    
    class Config:
        use_enum_values = True

# ============================================================================
# MULTIPLAYER SERVER MODELS
# ============================================================================

class GameServer(BaseModel):
    server_id: str = Field(description="Unique server identifier")
    name: str = Field(description="Server name")
    game_mode: GameMode = Field(description="Game mode")
    
    # Server settings
    max_players: int = Field(description="Maximum players")
    current_players: int = Field(default=0, description="Current number of players")
    is_public: bool = Field(default=True, description="Whether server is public")
    password: Optional[str] = Field(description="Server password if private")
    
    # Game settings
    round_duration: int = Field(default=5, description="Round duration in minutes")
    starting_countries: List[str] = Field(default_factory=list, description="Available starting countries")
    
    # Status
    status: str = Field(default="waiting", description="Server status: waiting, starting, active, finished")
    created_at: datetime = Field(description="When server was created")
    
    class Config:
        use_enum_values = True

class Player(BaseModel):
    player_id: str = Field(description="Unique player identifier")
    username: str = Field(description="Player username")
    selected_country: Optional[str] = Field(description="Selected country")
    
    # Connection info
    is_connected: bool = Field(default=True, description="Whether player is connected")
    last_seen: datetime = Field(description="Last time player was active")
    
    # Game state
    is_ready: bool = Field(default=False, description="Whether player is ready to start")
    actions_submitted: int = Field(default=0, description="Number of actions submitted this round")
    
    class Config:
        use_enum_values = True

# ============================================================================
# WORLD EVENT MODELS (Enhanced)
# ============================================================================

class WorldEventTrigger(BaseModel):
    trigger_type: str = Field(description="Type of trigger")
    conditions: Dict[str, Any] = Field(description="Conditions that must be met")
    probability: float = Field(default=1.0, ge=0.0, le=1.0, description="Probability of event occurring")
    
    class Config:
        use_enum_values = True

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
    round_triggered: Optional[int] = Field(description="Round when event was triggered")
    
    # Impact assessment
    geopolitical_impact: float = Field(description="Geopolitical impact score 0-1")
    economic_impact: float = Field(description="Economic impact score 0-1")
    military_impact: float = Field(description="Military impact score 0-1")
    social_impact: float = Field(description="Social impact score 0-1")
    
    # Game effects
    morale_effects: Dict[str, float] = Field(default_factory=dict, description="Morale changes by country")
    diplomatic_effects: List[Dict[str, Any]] = Field(default_factory=list, description="Diplomatic relation changes")
    economic_effects: Dict[str, float] = Field(default_factory=dict, description="Economic changes by country")
    
    # Event triggers and chains
    triggers: List[WorldEventTrigger] = Field(default_factory=list, description="What triggered this event")
    chain_events: List[str] = Field(default_factory=list, description="Events that may be triggered by this one")
    
    # Metadata
    source: str = Field(description="Source of the event data")
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in event accuracy")
    tags: List[str] = Field(default_factory=list, description="Event tags for categorization")
    
    class Config:
        use_enum_values = True

# ============================================================================
# PREDICTIVE SIMULATION MODELS
# ============================================================================

class SimulationMode(str, Enum):
    SINGLE_PLAYER = "single_player"
    MULTIPLAYER = "multiplayer"
    OBSERVE_THE_END = "observe_the_end"

class HistoricalPattern(str, Enum):
    ROMAN_DECLINE = "roman_decline"
    PERSIAN_EXPANSION = "persian_expansion"
    BYZANTINE_DIPLOMACY = "byzantine_diplomacy"
    MONGOL_CONQUEST = "mongol_conquest"
    OTTOMAN_DECLINE = "ottoman_decline"
    COLD_WAR_ESCALATION = "cold_war_escalation"
    NAPOLEONIC_WARS = "napoleonic_wars"
    WORLD_WAR_ESCALATION = "world_war_escalation"

class WorldEventType(str, Enum):
    DIPLOMATIC_CRISIS = "diplomatic_crisis"
    MILITARY_ESCALATION = "military_escalation"
    ECONOMIC_COLLAPSE = "economic_collapse"
    ALLIANCE_SHIFT = "alliance_shift"
    REGIME_CHANGE = "regime_change"
    NUCLEAR_THREAT = "nuclear_threat"
    TERRITORIAL_CONQUEST = "territorial_conquest"
    ECONOMIC_SANCTIONS = "economic_sanctions"
    CIVIL_WAR = "civil_war"
    NATURAL_DISASTER = "natural_disaster"
    TECHNOLOGICAL_BREAKTHROUGH = "technological_breakthrough"
    INTELLIGENCE_REVELATION = "intelligence_revelation"

class TimelineEvent(BaseModel):
    """A single event in the predictive timeline"""
    event_id: str = Field(description="Unique event identifier")
    date: datetime = Field(description="When this event occurs")
    event_type: WorldEventType = Field(description="Type of event")
    title: str = Field(description="Event headline")
    description: str = Field(description="Detailed description")
    affected_countries: List[str] = Field(default_factory=list, description="Countries involved")
    historical_pattern: Optional[HistoricalPattern] = Field(default=None, description="Historical pattern this follows")
    probability: float = Field(default=0.5, ge=0.0, le=1.0, description="Probability of this event occurring")
    impact_magnitude: float = Field(default=0.5, ge=0.0, le=1.0, description="Impact on world stability")
    triggers: List[str] = Field(default_factory=list, description="Events that trigger this")
    consequences: List[str] = Field(default_factory=list, description="Events this triggers")
    ai_reasoning: str = Field(description="AI explanation for why this event occurs")
    
    class Config:
        use_enum_values = True

class WorldState(BaseModel):
    """Current state of the world at a given date"""
    date: datetime = Field(description="Current simulation date")
    countries: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Country states")
    alliances: Dict[str, List[str]] = Field(default_factory=dict, description="Current alliances")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Active conflicts")
    economic_indicators: Dict[str, float] = Field(default_factory=dict, description="Economic data")
    military_deployments: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict, description="Military positions")
    diplomatic_relations: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Relations between countries")
    world_stability_index: float = Field(default=0.7, ge=0.0, le=1.0, description="Overall world stability")
    nuclear_threat_level: float = Field(default=0.3, ge=0.0, le=1.0, description="Nuclear war probability")
    
    class Config:
        use_enum_values = True

class PredictiveSimulation(BaseModel):
    """Complete predictive simulation session"""
    simulation_id: str = Field(description="Unique simulation identifier")
    mode: SimulationMode = Field(default=SimulationMode.OBSERVE_THE_END, description="Simulation mode")
    start_date: datetime = Field(description="Starting date (current real-world date)")
    predicted_end_date: Optional[datetime] = Field(default=None, description="Predicted end date")
    end_scenario: Optional[str] = Field(default=None, description="How the world ends")
    timeline_events: List[TimelineEvent] = Field(default_factory=list, description="All predicted events")
    world_states: List[WorldState] = Field(default_factory=list, description="World state at each date")
    historical_patterns_applied: List[HistoricalPattern] = Field(default_factory=list, description="Patterns used")
    ai_reasoning_log: List[str] = Field(default_factory=list, description="AI decision explanations")
    accuracy_metrics: Dict[str, float] = Field(default_factory=dict, description="Simulation accuracy scores")
    
    class Config:
        use_enum_values = True

class NewsSource(BaseModel):
    """News source for real-time data"""
    source_id: str = Field(description="Source identifier")
    name: str = Field(description="Source name")
    url: str = Field(description="Source URL")
    region: str = Field(description="Geographic region")
    bias_level: float = Field(default=0.5, ge=-1.0, le=1.0, description="Political bias (-1 to 1)")
    reliability_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Reliability score")
    update_frequency: str = Field(default="hourly", description="How often to check")
    
    class Config:
        use_enum_values = True

class PredictiveHistoryTranscript(BaseModel):
    """Transcript from Predictive History analysis"""
    transcript_id: str = Field(description="Transcript identifier")
    date: datetime = Field(description="When this analysis was made")
    topic: str = Field(description="Topic analyzed")
    historical_pattern: HistoricalPattern = Field(description="Pattern identified")
    modern_parallel: str = Field(description="Modern equivalent")
    prediction: str = Field(description="Predicted outcome")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence in prediction")
    reasoning: str = Field(description="Detailed reasoning")
    applicable_countries: List[str] = Field(default_factory=list, description="Countries this applies to")
    
    class Config:
        use_enum_values = True

# ============================================================================
# API MODELS
# ============================================================================

class SessionCreateRequest(BaseModel):
    game_mode: GameMode = Field(description="Single-player or multiplayer")
    host_country: str = Field(description="Host player's selected country")
    round_duration_minutes: int = Field(default=5, description="Round duration")
    max_players: int = Field(default=8, description="Maximum players")

class SessionCreateResponse(BaseModel):
    session_id: str
    game_mode: GameMode
    message: str = "Session created successfully"

class ActionRequest(BaseModel):
    player_country: str = Field(description="Country performing the action")
    action_type: ActionType = Field(description="Type of action")
    target_country: Optional[str] = Field(description="Target country")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    is_secret: bool = Field(default=False, description="Whether action is secret")

class ActionResponse(BaseModel):
    action_id: str
    status: str
    message: str
    round_number: int

class RoundUpdateResponse(BaseModel):
    session_id: str
    round_number: int
    phase: RoundPhase
    time_remaining: int = Field(description="Seconds remaining in current phase")
    actions_submitted: int = Field(description="Number of actions submitted by player")
    max_actions: int = Field(description="Maximum actions allowed")
    world_events: List[WorldEvent] = Field(default_factory=list)
    round_summary: Optional[str] = Field(description="Summary of previous round")

class GameServerCreateRequest(BaseModel):
    name: str = Field(description="Server name")
    game_mode: GameMode = Field(description="Game mode")
    max_players: int = Field(description="Maximum players")
    round_duration: int = Field(default=5, description="Round duration in minutes")
    is_public: bool = Field(default=True, description="Whether server is public")
    password: Optional[str] = Field(description="Server password")

class GameServerJoinRequest(BaseModel):
    server_id: str = Field(description="Server to join")
    username: str = Field(description="Player username")
    selected_country: str = Field(description="Selected country")
    password: Optional[str] = Field(description="Server password if private")

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
