import os
import json
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import logging
from dataclasses import dataclass
from models import (
    WorldEvent, NewsHeadline, Country, DiplomaticStatus, EventType,
    EconomicData, MilitaryData, PoliticalData, SocialData, ResourceReserves
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Represents a data source for real-time information."""
    name: str
    url: str
    api_key: Optional[str] = None
    rate_limit: int = 100  # Requests per hour
    last_update: Optional[datetime] = None
    is_active: bool = True

class RealTimeDataService:
    """
    Efficient real-time data service for geopolitical simulation.
    
    Features:
    - Multiple data source integration
    - Intelligent caching and rate limiting
    - Cost optimization through smart data management
    - Real-time event detection and analysis
    """
    
    def __init__(self, news_api_key: Optional[str] = None):
        # Data sources configuration
        self.data_sources: Dict[str, DataSource] = {
            "newsapi": DataSource(
                name="NewsAPI",
                url="https://newsapi.org/v2/everything",
                api_key=news_api_key,
                rate_limit=100
            ),
            "openweather": DataSource(
                name="OpenWeather",
                url="https://api.openweathermap.org/data/2.5/weather",
                api_key=os.getenv("OPENWEATHER_API_KEY"),
                rate_limit=1000
            ),
            "currencyapi": DataSource(
                name="CurrencyAPI",
                url="https://api.exchangerate-api.com/v4/latest/USD",
                rate_limit=1000
            )
        }
        
        # Caching system
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        
        # Rate limiting
        self.request_counts: Dict[str, int] = {}
        self.last_reset = datetime.now()
        
        # Session for HTTP requests
        self.session: Optional[requests.Session] = None
        
        # Event tracking
        self.tracked_events: Set[str] = set()
        self.event_history: List[WorldEvent] = []
        
        # Country data cache
        self.country_data_cache: Dict[str, Dict[str, Any]] = {}
        
    async def __aenter__(self):
        self.session = requests.Session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
    
    def _get_cache_key(self, source: str, params: Dict[str, Any]) -> str:
        """Generate a cache key for the request."""
        cache_data = {
            "source": source,
            "params": params,
            "timestamp": datetime.now().strftime("%Y%m%d_%H")
        }
        return json.dumps(cache_data, sort_keys=True)
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if a cache entry is still valid."""
        cached_time = datetime.fromisoformat(cache_entry["timestamp"])
        return datetime.now() - cached_time < self.cache_duration
    
    def _check_rate_limit(self, source: str) -> bool:
        """Check if we're within rate limits for a data source."""
        # Reset counters if it's been an hour
        if datetime.now() - self.last_reset > timedelta(hours=1):
            self.request_counts.clear()
            self.last_reset = datetime.now()
        
        current_count = self.request_counts.get(source, 0)
        max_requests = self.data_sources[source].rate_limit
        
        return current_count < max_requests
    
    def _increment_request_count(self, source: str):
        """Increment the request count for a data source."""
        self.request_counts[source] = self.request_counts.get(source, 0) + 1
    
    async def _make_request(self, source: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to a data source."""
        if not self._check_rate_limit(source):
            logger.warning(f"Rate limit exceeded for {source}")
            return {}
        
        data_source = self.data_sources[source]
        if not data_source.is_active:
            logger.warning(f"Data source {source} is not active")
            return {}
        
        headers = {"User-Agent": "WWIII-Simulator/1.0"}
        if data_source.api_key:
            params["apiKey"] = data_source.api_key
        
        try:
            response = self.session.get(data_source.url, params=params, headers=headers)
            response.raise_for_status() # Raise an exception for HTTP errors
            
            data = response.json()
            self._increment_request_count(source)
            data_source.last_update = datetime.now()
            
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {source}: {e}")
            return {}
    
    async def get_current_news(self, countries: List[str], keywords: List[str] = None) -> List[NewsHeadline]:
        """Get current news for specified countries."""
        if not self.data_sources["newsapi"].api_key:
            logger.warning("NewsAPI key not configured, using simulated news")
            return await self._generate_simulated_news(countries)
        
        cache_key = self._get_cache_key("newsapi", {"countries": countries, "keywords": keywords})
        
        # Check cache first
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]["data"]
        
        # Build query
        query_parts = []
        for country in countries:
            query_parts.append(f'"{country}"')
        
        if keywords:
            for keyword in keywords:
                query_parts.append(keyword)
        
        query = " OR ".join(query_parts)
        
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 20
        }
        
        data = await self._make_request("newsapi", params)
        
        headlines = []
        if "articles" in data:
            for article in data["articles"]:
                headline = NewsHeadline(
                    id=f"news_{len(headlines)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    title=article.get("title", ""),
                    summary=article.get("description", ""),
                    source=article.get("source", {}).get("name", "Unknown"),
                    url=article.get("url"),
                    content=article.get("content", ""),
                    sentiment=0.0,  # Would need sentiment analysis
                    relevant_countries=countries,
                    published_date=datetime.fromisoformat(article.get("publishedAt", datetime.now().isoformat())),
                    relevance_score=0.8
                )
                headlines.append(headline)
        
        # Cache the result
        self.cache[cache_key] = {
            "data": headlines,
            "timestamp": datetime.now().isoformat()
        }
        
        return headlines
    
    async def get_country_economic_data(self, country_code: str) -> Optional[EconomicData]:
        """Get current economic data for a country."""
        cache_key = f"economic_{country_code}_{datetime.now().strftime('%Y%m%d')}"
        
        if cache_key in self.country_data_cache:
            return EconomicData(**self.country_data_cache[cache_key])
        
        # In a real implementation, you'd fetch from economic APIs
        # For now, return simulated data based on country
        economic_data = self._get_simulated_economic_data(country_code)
        
        if economic_data:
            self.country_data_cache[cache_key] = economic_data.dict()
        
        return economic_data
    
    async def get_country_military_data(self, country_code: str) -> Optional[MilitaryData]:
        """Get current military data for a country."""
        cache_key = f"military_{country_code}_{datetime.now().strftime('%Y%m%d')}"
        
        if cache_key in self.country_data_cache:
            return MilitaryData(**self.country_data_cache[cache_key])
        
        # In a real implementation, you'd fetch from military databases
        # For now, return simulated data
        military_data = self._get_simulated_military_data(country_code)
        
        if military_data:
            self.country_data_cache[cache_key] = military_data.dict()
        
        return military_data
    
    async def get_country_political_data(self, country_code: str) -> Optional[PoliticalData]:
        """Get current political data for a country."""
        cache_key = f"political_{country_code}_{datetime.now().strftime('%Y%m%d')}"
        
        if cache_key in self.country_data_cache:
            return PoliticalData(**self.country_data_cache[cache_key])
        
        # In a real implementation, you'd fetch from political databases
        # For now, return simulated data
        political_data = self._get_simulated_political_data(country_code)
        
        if political_data:
            self.country_data_cache[cache_key] = political_data.dict()
        
        return political_data
    
    async def get_country_social_data(self, country_code: str) -> Optional[SocialData]:
        """Get current social data for a country."""
        cache_key = f"social_{country_code}_{datetime.now().strftime('%Y%m%d')}"
        
        if cache_key in self.country_data_cache:
            return SocialData(**self.country_data_cache[cache_key])
        
        # In a real implementation, you'd fetch from social databases
        # For now, return simulated data
        social_data = self._get_simulated_social_data(country_code)
        
        if social_data:
            self.country_data_cache[cache_key] = social_data.dict()
        
        return social_data
    
    async def get_country_resources(self, country_code: str) -> Optional[ResourceReserves]:
        """Get current resource data for a country."""
        cache_key = f"resources_{country_code}_{datetime.now().strftime('%Y%m%d')}"
        
        if cache_key in self.country_data_cache:
            return ResourceReserves(**self.country_data_cache[cache_key])
        
        # In a real implementation, you'd fetch from resource databases
        # For now, return simulated data
        resource_data = self._get_simulated_resource_data(country_code)
        
        if resource_data:
            self.country_data_cache[cache_key] = resource_data.dict()
        
        return resource_data
    
    async def detect_real_time_events(self, countries: List[str]) -> List[WorldEvent]:
        """Detect real-time events that might affect the simulation."""
        events = []
        
        # Get current news
        news = await self.get_current_news(countries)
        
        # Analyze news for significant events
        for headline in news:
            event = self._analyze_headline_for_events(headline, countries)
            if event:
                events.append(event)
        
        # Check for new events (not already tracked)
        new_events = [event for event in events if event.id not in self.tracked_events]
        
        # Add to tracked events
        for event in new_events:
            self.tracked_events.add(event.id)
            self.event_history.append(event)
        
        return new_events
    
    def _analyze_headline_for_events(self, headline: NewsHeadline, countries: List[str]) -> Optional[WorldEvent]:
        """Analyze a news headline to extract significant events."""
        title_lower = headline.title.lower()
        
        # Define event triggers
        event_triggers = {
            EventType.DIPLOMATIC: ["meeting", "summit", "talks", "agreement", "treaty", "diplomatic"],
            EventType.MILITARY: ["military", "defense", "weapons", "deployment", "exercise", "drill"],
            EventType.ECONOMIC: ["economic", "trade", "sanctions", "market", "gdp", "inflation"],
            EventType.POLITICAL: ["election", "government", "parliament", "vote", "protest"],
            EventType.NATURAL_DISASTER: ["earthquake", "flood", "hurricane", "drought", "disaster"],
            EventType.TECHNOLOGICAL: ["technology", "cyber", "hack", "digital", "innovation"],
            EventType.INTELLIGENCE: ["intelligence", "spy", "surveillance", "security"]
        }
        
        # Determine event type
        event_type = EventType.DIPLOMATIC  # Default
        for trigger_type, triggers in event_triggers.items():
            if any(trigger in title_lower for trigger in triggers):
                event_type = trigger_type
                break
        
        # Calculate impact scores based on keywords and sentiment
        geopolitical_impact = 0.3
        economic_impact = 0.2
        military_impact = 0.2
        social_impact = 0.2
        
        if event_type == EventType.MILITARY:
            military_impact = 0.6
        elif event_type == EventType.ECONOMIC:
            economic_impact = 0.6
        elif event_type == EventType.POLITICAL:
            social_impact = 0.6
        
        # Boost impact if multiple countries are involved
        if len(headline.relevant_countries) > 1:
            geopolitical_impact += 0.2
        
        return WorldEvent(
            id=f"event_{len(self.event_history)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            event_type=event_type,
            title=headline.title,
            description=headline.summary,
            affected_countries=headline.relevant_countries,
            primary_actors=headline.relevant_countries[:2],
            start_date=headline.published_date,
            geopolitical_impact=geopolitical_impact,
            economic_impact=economic_impact,
            military_impact=military_impact,
            social_impact=social_impact,
            source=headline.source,
            confidence_level=0.7,
            tags=[event_type.value]
        )
    
    async def _generate_simulated_news(self, countries: List[str]) -> List[NewsHeadline]:
        """Generate simulated news when real APIs are not available."""
        simulated_headlines = [
            {
                "title": f"Diplomatic tensions rise between {countries[0]} and {countries[1]}",
                "summary": "Recent developments have increased diplomatic tensions between the two nations.",
                "source": "Simulated News",
                "sentiment": -0.3
            },
            {
                "title": f"Economic cooperation agreement signed by {countries[0]}",
                "summary": "New trade agreement expected to boost economic relations.",
                "source": "Simulated News",
                "sentiment": 0.4
            },
            {
                "title": f"Military exercise conducted by {countries[1]}",
                "summary": "Large-scale military exercise demonstrates defense capabilities.",
                "source": "Simulated News",
                "sentiment": 0.1
            }
        ]
        
        headlines = []
        for i, headline_data in enumerate(simulated_headlines):
            headline = NewsHeadline(
                id=f"sim_news_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=headline_data["title"],
                summary=headline_data["summary"],
                source=headline_data["source"],
                content=headline_data["summary"],
                sentiment=headline_data["sentiment"],
                relevant_countries=countries,
                published_date=datetime.now(),
                relevance_score=0.8
            )
            headlines.append(headline)
        
        return headlines
    
    def _get_simulated_economic_data(self, country_code: str) -> Optional[EconomicData]:
        """Get simulated economic data for a country."""
        # This would be replaced with real API calls in production
        base_data = {
            "US": {"gdp": 25.5e12, "per_capita": 77000, "inflation": 3.2},
            "CN": {"gdp": 17.7e12, "per_capita": 12500, "inflation": 2.1},
            "RU": {"gdp": 2.1e12, "per_capita": 14500, "inflation": 7.4},
            "DE": {"gdp": 4.4e12, "per_capita": 53000, "inflation": 2.9},
            "JP": {"gdp": 4.2e12, "per_capita": 33500, "inflation": 0.5},
            "GB": {"gdp": 3.1e12, "per_capita": 46000, "inflation": 4.0}
        }
        
        if country_code not in base_data:
            return None
        
        data = base_data[country_code]
        return EconomicData(
            gdp_nominal=data["gdp"],
            gdp_per_capita=data["per_capita"],
            inflation_rate=data["inflation"],
            unemployment_rate=5.0,
            debt_to_gdp=80.0,
            trade_balance=0.0,
            foreign_reserves=100e9,
            currency_strength=0.7
        )
    
    def _get_simulated_military_data(self, country_code: str) -> Optional[MilitaryData]:
        """Get simulated military data for a country."""
        base_data = {
            "US": {"active": 1400000, "budget": 800e9, "nuclear": 5800},
            "CN": {"active": 2000000, "budget": 250e9, "nuclear": 350},
            "RU": {"active": 900000, "budget": 65e9, "nuclear": 6000},
            "DE": {"active": 180000, "budget": 55e9, "nuclear": 0},
            "JP": {"active": 250000, "budget": 50e9, "nuclear": 0},
            "GB": {"active": 150000, "budget": 60e9, "nuclear": 225}
        }
        
        if country_code not in base_data:
            return None
        
        data = base_data[country_code]
        return MilitaryData(
            active_personnel=data["active"],
            reserve_personnel=data["active"] * 2,
            defense_budget=data["budget"],
            nuclear_weapons=data["nuclear"],
            aircraft_carriers=2 if country_code == "US" else 0,
            submarines=10,
            tanks=1000,
            fighter_jets=500,
            military_technology_level=0.8
        )
    
    def _get_simulated_political_data(self, country_code: str) -> Optional[PoliticalData]:
        """Get simulated political data for a country."""
        base_data = {
            "US": {"stability": 0.7, "democracy": 0.8, "leader": "President Biden"},
            "CN": {"stability": 0.8, "democracy": 0.2, "leader": "President Xi"},
            "RU": {"stability": 0.6, "democracy": 0.3, "leader": "President Putin"},
            "DE": {"stability": 0.8, "democracy": 0.9, "leader": "Chancellor Scholz"},
            "JP": {"stability": 0.9, "democracy": 0.8, "leader": "Prime Minister Kishida"},
            "GB": {"stability": 0.7, "democracy": 0.8, "leader": "Prime Minister Sunak"}
        }
        
        if country_code not in base_data:
            return None
        
        data = base_data[country_code]
        return PoliticalData(
            government_type="Democratic" if data["democracy"] > 0.5 else "Authoritarian",
            political_stability=data["stability"],
            corruption_index=0.3,
            press_freedom=0.7,
            democracy_index=data["democracy"],
            current_leader=data["leader"],
            ruling_party="Various",
            opposition_strength=0.4
        )
    
    def _get_simulated_social_data(self, country_code: str) -> Optional[SocialData]:
        """Get simulated social data for a country."""
        base_data = {
            "US": {"population": 330e6, "life_expectancy": 78.9},
            "CN": {"population": 1400e6, "life_expectancy": 76.9},
            "RU": {"population": 144e6, "life_expectancy": 72.6},
            "DE": {"population": 83e6, "life_expectancy": 81.3},
            "JP": {"population": 126e6, "life_expectancy": 84.6},
            "GB": {"population": 67e6, "life_expectancy": 81.2}
        }
        
        if country_code not in base_data:
            return None
        
        data = base_data[country_code]
        return SocialData(
            population=int(data["population"]),
            population_growth=0.5,
            median_age=40.0,
            literacy_rate=95.0,
            internet_penetration=85.0,
            urbanization_rate=80.0,
            life_expectancy=data["life_expectancy"],
            social_unrest_index=0.3
        )
    
    def _get_simulated_resource_data(self, country_code: str) -> Optional[ResourceReserves]:
        """Get simulated resource data for a country."""
        base_data = {
            "US": {"oil": 50e9, "gas": 10e12, "coal": 250e9},
            "CN": {"oil": 25e9, "gas": 5e12, "coal": 140e9},
            "RU": {"oil": 80e9, "gas": 50e12, "coal": 160e9},
            "DE": {"oil": 0.2e9, "gas": 0.1e12, "coal": 40e9},
            "JP": {"oil": 0.05e9, "gas": 0.02e12, "coal": 0.3e9},
            "GB": {"oil": 2e9, "gas": 0.2e12, "coal": 0.2e9}
        }
        
        if country_code not in base_data:
            return None
        
        data = base_data[country_code]
        return ResourceReserves(
            oil_reserves=data["oil"],
            gas_reserves=data["gas"],
            coal_reserves=data["coal"],
            uranium_reserves=100e3,
            rare_earth_reserves=1e6,
            arable_land=50e6,
            fresh_water=1000
        )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for monitoring."""
        return {
            "request_counts": self.request_counts,
            "cache_size": len(self.cache),
            "tracked_events": len(self.tracked_events),
            "event_history_size": len(self.event_history),
            "country_data_cache_size": len(self.country_data_cache)
        }
    
    def clear_cache(self):
        """Clear all caches."""
        self.cache.clear()
        self.country_data_cache.clear()
        logger.info("Real-time data service cache cleared")

# Singleton instance
_realtime_service: Optional[RealTimeDataService] = None

async def get_realtime_service() -> RealTimeDataService:
    """Get or create realtime data service instance."""
    global _realtime_service
    if _realtime_service is None:
        news_api_key = os.getenv("NEWS_API_KEY")
        if not news_api_key:
            raise ValueError("News API key is required. Set NEWS_API_KEY environment variable.")
        
        _realtime_service = RealTimeDataService(news_api_key)
        await _realtime_service.__aenter__()
        logger.info("Realtime data service initialized successfully")
    return _realtime_service

async def close_realtime_service():
    """Close the real-time data service."""
    global _realtime_service
    if _realtime_service:
        await _realtime_service.__aexit__(None, None, None)
        _realtime_service = None 