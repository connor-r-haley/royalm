#!/usr/bin/env python3
"""
FastAPI Backend for World Brain Simulation
"""

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import uuid
from datetime import datetime

from .world_brain import get_world_brain, WorldState, GeneratedNews

# Get singleton instance
world_brain = get_world_brain()
from .world_data_service import world_data_service
from .world_leaders_service import world_leaders_service
from .historical_news_service import get_historical_news_service
from .refdata.router import router as ref_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="World Brain API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reference data router
app.include_router(ref_router, prefix="/ref", tags=["refdata"])

# Pydantic models for API requests/responses
class SimulationCreateRequest(BaseModel):
    seed: Optional[int] = None
    start_month: int
    start_year: int
    use_present: bool = True  # If True, use World Brain, if False use historical news

class SimulationResponse(BaseModel):
    id: str
    status: str
    current_date: str
    countries: Dict[str, Any]
    news: List[Dict[str, Any]]
    map_state: Dict[str, Any]
    global_indicators: Dict[str, Any]

class NewsArticle(BaseModel):
    title: str
    content: str
    country: str
    category: str
    severity: str
    reliability: str
    source: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    world_brain_available: bool
    world_data_available: bool
    world_leaders_available: bool
    chatgpt_available: bool

class GameSessionRequest(BaseModel):
    game_mode: str
    host_country: str
    round_duration_minutes: int = 5
    max_players: int = 1

class GameSessionResponse(BaseModel):
    session_id: str
    game_mode: str
    host_country: str
    status: str
    round_number: int = 0

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check ChatGPT service availability
    chatgpt_available = False
    try:
        from chatgpt_service import get_chatgpt_service
        chatgpt_service = await get_chatgpt_service()
        chatgpt_available = chatgpt_service.client is not None
        print(f"ChatGPT Service Debug - API Key exists: {bool(chatgpt_service.api_key)}")
        print(f"ChatGPT Service Debug - Client exists: {chatgpt_service.client is not None}")
        if not chatgpt_available:
            print("ChatGPT Service Debug - Client is None")
    except Exception as e:
        print(f"ChatGPT Service Debug - Error: {str(e)}")
        chatgpt_available = False
    
    return HealthResponse(
        status="healthy",
        world_brain_available=True,
        world_data_available=len(world_data_service.country_data) > 0,
        world_leaders_available=len(world_leaders_service.leaders) > 0,
        chatgpt_available=chatgpt_available
    )

# Game session storage (in-memory for now)
game_sessions = {}

@app.post("/game/create-session", response_model=GameSessionResponse)
async def create_game_session(request: GameSessionRequest):
    """Create a new game session"""
    session_id = str(uuid.uuid4())
    
    game_sessions[session_id] = {
        "session_id": session_id,
        "game_mode": request.game_mode,
        "host_country": request.host_country,
        "status": "active",
        "round_number": 0,
        "round_duration_minutes": request.round_duration_minutes,
        "max_players": request.max_players,
        "created_at": datetime.now()
    }
    
    logger.info(f"Created game session: {session_id}, mode: {request.game_mode}, country: {request.host_country}")
    
    return GameSessionResponse(
        session_id=session_id,
        game_mode=request.game_mode,
        host_country=request.host_country,
        status="active",
        round_number=0
    )

@app.get("/game/{session_id}/status")
async def get_game_status(session_id: str):
    """Get game session status"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return game_sessions[session_id]

@app.post("/worldbrain/create", response_model=SimulationResponse)
async def create_world_brain_simulation(request: SimulationCreateRequest, response: Response):
    """Create a new World Brain simulation"""
    # Add cache-busting headers
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        simulation_id = str(uuid.uuid4())
        
        # Check if the requested date is in the past
        current_date = datetime.now()
        requested_date = datetime(request.start_year, request.start_month, 1)
        is_historical = requested_date < current_date and not request.use_present
        
        if is_historical:
            # Use historical news service for past dates
            historical_service = await get_historical_news_service()
            historical_news = await historical_service.get_historical_news(
                request.start_year,
                request.start_month
            )
            
            # Create a basic map state for historical view using world_brain's MapState
            from world_brain import MapState
            historical_map_state = MapState(
                timestamp=datetime.now(),
                country_states={"Global": {"status": "historical", "tension": 50}},
                bloc_distribution={"Historical": 1},
                global_tension=50,  # Default moderate tension (0-100 scale)
                active_conflicts=[]
            )
            
            # Create a simplified world state for historical view
            world_state = WorldState(
                timestamp=datetime.now(),
                current_date=requested_date,
                week_number=1,
                countries={},  # Empty since we're just showing news
                doctrines={},
                relations={},
                actions=[],
                outcomes=[],
                news=[GeneratedNews(
                    headline=article["title"],
                    lede=article["content"],
                    content=article["content"],
                    country=article["country"],
                    category=article["category"],
                    severity=article["severity"],
                    reliability=article["reliability"],
                    source=article["source"],
                    timestamp=datetime.fromisoformat(article["timestamp"].replace('Z', '+00:00')) if article.get("timestamp") else datetime.now(),
                    stat_changes={"url": article["url"]}
                ) for article in historical_news],
                map_states=[historical_map_state],
                map_state=historical_map_state,
                global_indicators={}
            )
        else:
            # Use World Brain for present/future dates
            world_state = await world_brain.initialize_world(
                simulation_id, 
                request.seed,
                request.start_month,
                request.start_year
            )
        
        # Format news for frontend
        formatted_news = []
        for news_item in world_state.news:
            news_data = {
                "title": news_item.headline,
                "content": news_item.content,  # Use full content instead of just lede
                "country": news_item.country,
                "category": news_item.category,
                "severity": news_item.severity,
                "reliability": news_item.reliability,
                "source": news_item.source,
                "timestamp": news_item.timestamp.isoformat()
            }
            
            # Add URL if available (for real news articles)
            if "url" in news_item.stat_changes:
                news_data["url"] = news_item.stat_changes["url"]
            
            formatted_news.append(news_data)
        
        # Format countries for frontend
        formatted_countries = {}
        for country_id, country_data in world_state.countries.items():
            formatted_countries[country_id] = {
                "name": country_data.name,
                "gdp": country_data.gdp,
                "population": country_data.population,
                "military_budget": country_data.military_budget,
                "nuclear_warheads": country_data.nuclear_warheads,
                "regime_type": country_data.regime_type,
                "bloc": country_data.bloc,
                "alliances": country_data.alliances,
                "stability": country_data.stability,
                "morale": country_data.morale,
                "influence_level": country_data.influence_level
            }
        
        # Format map state for frontend
        formatted_map_state = {
            "global_tension": world_state.map_state.global_tension,
            "bloc_distribution": world_state.map_state.bloc_distribution,
            "active_conflicts": world_state.map_state.active_conflicts,
            "country_states": world_state.map_state.country_states
        }
        
        return SimulationResponse(
            id=simulation_id,
            status="simulation_active",
            current_date=world_state.current_date.strftime("%m/%d/%Y"),
            countries=formatted_countries,
            news=formatted_news,
            map_state=formatted_map_state,
            global_indicators=world_state.global_indicators
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/worldbrain/{simulation_id}/advance-month")
async def advance_world_brain_month(simulation_id: str, response: Response):
    """Advance the simulation by one month"""
    # Add cache-busting headers
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        result = await world_brain.advance_month(simulation_id)
        
        # Format news for frontend
        formatted_news = []
        for news_item in result["news"]:
            news_data = {
                "title": news_item.headline,
                "content": news_item.content,
                "country": news_item.country,
                "category": news_item.category,
                "severity": news_item.severity,
                "reliability": news_item.reliability,
                "source": news_item.source,
                "timestamp": news_item.timestamp.isoformat()
            }
            
            # Add URL if available (for real news articles)
            if "url" in news_item.stat_changes:
                news_data["url"] = news_item.stat_changes["url"]
            
            formatted_news.append(news_data)
        
        return {
            "simulation_id": simulation_id,
            "current_date": result["current_date"].strftime("%m/%d/%Y"),
            "news": formatted_news,
            "map_state": result["map_state"],
            "global_indicators": result["global_indicators"],
            "use_historical_news": result["use_historical_news"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error advancing month: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/worldbrain/{simulation_id}/status", response_model=SimulationResponse)
async def get_world_brain_status(simulation_id: str):
    """Get current status of a simulation"""
    try:
        if simulation_id not in world_brain.simulations:
            raise HTTPException(status_code=404, detail="Simulation not found")
        
        world_state = world_brain.simulations[simulation_id]
        
        # Format news for frontend
        formatted_news = []
        for news_item in world_state.news:
            formatted_news.append({
                "title": news_item.headline,
                "content": news_item.lede,
                "country": news_item.country,
                "category": news_item.category,
                "severity": news_item.severity,
                "reliability": news_item.reliability,
                "source": news_item.source,
                "timestamp": news_item.timestamp.isoformat()
            })
        
        # Format countries for frontend
        formatted_countries = {}
        for country_id, country in world_state.countries.items():
            formatted_countries[country_id] = {
                "name": country.name,
                "gdp": country.gdp,
                "population": country.population,
                "military_budget": country.military_budget,
                "nuclear_warheads": country.nuclear_warheads,
                "regime_type": country.regime_type,
                "bloc": country.bloc,
                "alliances": country.alliances,
                "stability": country.stability,
                "morale": country.morale,
                "influence_level": country.influence_level
            }
        
        # Format map state
        current_map_state = world_state.map_states[-1] if world_state.map_states else None
        formatted_map_state = {
            "global_tension": current_map_state.global_tension if current_map_state else 0,
            "bloc_distribution": current_map_state.bloc_distribution if current_map_state else {},
            "active_conflicts": current_map_state.active_conflicts if current_map_state else [],
            "country_states": current_map_state.country_states if current_map_state else {}
        }
        
        return SimulationResponse(
            id=simulation_id,
            status="simulation_active",
            current_date=world_state.current_date.strftime("%m/%d/%Y"),
            countries=formatted_countries,
            news=formatted_news,
            map_state=formatted_map_state,
            global_indicators=world_state.global_indicators
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting simulation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/worlddata/countries")
async def get_countries():
    """Get all country data"""
    # Return the complete merged dataset (covers ~200+ countries)
    return world_data_service.get_all_countries()

@app.get("/worlddata/countries/{country_id}")
async def get_country(country_id: str):
    """Get specific country data"""
    country_data = world_data_service.get_country_data(country_id)
    if not country_data:
        raise HTTPException(status_code=404, detail="Country not found")
    return country_data

@app.get("/worldleaders/leaders")
async def get_leaders():
    """Get all leader data"""
    return world_leaders_service.leaders

@app.get("/worldleaders/leaders/{leader_id}")
async def get_leader(leader_id: str):
    """Get specific leader data"""
    leader_data = world_leaders_service.get_leader(leader_id)
    if not leader_data:
        raise HTTPException(status_code=404, detail="Leader not found")
    return leader_data

@app.get("/worldleaders/events")
async def get_recent_events():
    """Get recent world events"""
    return world_leaders_service.get_recent_events()

@app.get("/worldleaders/storylines")
async def get_ongoing_storylines():
    """Get ongoing geopolitical storylines"""
    return world_leaders_service.get_ongoing_storylines()

@app.get("/worldleaders/controversies")
async def get_controversies():
    """Get current controversies"""
    return world_leaders_service.get_controversies()

@app.get("/costs")
async def get_costs():
    """Get OpenAI API cost information"""
    return {
        "pricing": {
            "model": "gpt-4",
            "input_per_1m_tokens": "$0.03",
            "output_per_1m_tokens": "$0.06"
        },
        "cost_estimates": {
            "hourly_gameplay": "$0.50 - $2.00",
            "monthly": "$10 - $40 (based on 20 hours/month)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)