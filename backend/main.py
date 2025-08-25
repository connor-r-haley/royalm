# pip install fastapi uvicorn "pydantic<3" starlette
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio, uuid, json
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Import our new models (optional - simplified)
try:
    from models import (
        # Core models
        GameSession, Country, Faction, WorldEvent, NewsHeadline, EventType, DiplomaticStatus,
        PlayableCountry, PLAYABLE_COUNTRIES, PlayerAction, Round, AICountry, GameServer, Player,
        
        # Enums
        GameMode, RoundPhase, ActionType, AIStrategy, PlayableCountryType,
        
        # API models
        SessionCreateRequest, SessionCreateResponse, ActionRequest, ActionResponse, 
        RoundUpdateResponse, GameServerCreateRequest, GameServerJoinRequest
    )
    MODELS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Models not available: {e}")
    MODELS_AVAILABLE = False

# Services (optional - now enabled with requests instead of aiohttp)
try:
    from chatgpt_service import ChatGPTService, get_chatgpt_service
    from realtime_data_service import RealTimeDataService, get_realtime_service
    SERVICES_AVAILABLE = True
    chatgpt_service = None
    realtime_service = None
except ImportError as e:
    logging.warning(f"Services not available: {e}")
    SERVICES_AVAILABLE = False
    chatgpt_service = None
    realtime_service = None

# Import predictive simulation service
try:
    from predictive_simulation_service import predictive_service
    PREDICTIVE_SERVICE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Predictive simulation service not available: {e}")
    PREDICTIVE_SERVICE_AVAILABLE = False

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- In-memory state for the enhanced simulator ---
SESSIONS: Dict[str, Dict[str, Any]] = {}
ACTIONS: Dict[str, List[Dict[str, Any]]] = {}
WS_CLIENTS: Dict[str, List[WebSocket]] = {}

# --- New round-based gameplay state ---
GAME_SESSIONS: Dict[str, Any] = {}
GAME_SERVERS: Dict[str, Any] = {}
PLAYERS: Dict[str, Any] = {}
AI_CONTROLLERS: Dict[str, Any] = {}
ROUND_TIMERS: Dict[str, asyncio.Task] = {}

# Initialize services on startup (optional)
@app.on_event("startup")
async def startup_event():
    global chatgpt_service, realtime_service, SERVICES_AVAILABLE
    if SERVICES_AVAILABLE:
        try:
            # Check if API keys are available
            openai_key = os.getenv("OPENAI_API_KEY")
            news_key = os.getenv("NEWS_API_KEY")
            
            if openai_key and openai_key != "sk-test-placeholder-key":
                chatgpt_service = await get_chatgpt_service()
                logger.info("ChatGPT service initialized successfully")
            else:
                logger.warning("OpenAI API key not configured, ChatGPT service disabled")
                
            if news_key and news_key != "test-news-api-key":
                realtime_service = await get_realtime_service()
                logger.info("Real-time data service initialized successfully")
            else:
                logger.warning("News API key not configured, real-time service disabled")
                
            # Update SERVICES_AVAILABLE based on actual service availability
            SERVICES_AVAILABLE = chatgpt_service is not None or realtime_service is not None
            
        except Exception as e:
            logger.warning(f"Failed to initialize services: {e}")
            SERVICES_AVAILABLE = False
    else:
        logger.info("Running in basic mode without advanced services")

@app.on_event("shutdown")
async def shutdown_event():
    global chatgpt_service, realtime_service
    if chatgpt_service:
        try:
            # await chatgpt_service.__aexit__(None, None, None) # Original line commented out
            pass
        except:
            pass
    if realtime_service:
        try:
            # await realtime_service.__aexit__(None, None, None) # Original line commented out
            pass
        except:
            pass
    logger.info("Services shut down successfully")

# Load real world country borders data
def load_countries():
    try:
        with open('all-countries-antarctica-fixed.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to simplified data if file not found
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"id": "RU", "name": "Russia", "faction": "RU", "morale": 0.7},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [20.0, 60.0], [40.0, 60.0], [40.0, 50.0], [20.0, 50.0], [20.0, 60.0]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {"id": "UA", "name": "Ukraine", "faction": "US", "morale": 0.6},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [22.0, 52.0], [32.0, 52.0], [32.0, 44.0], [22.0, 44.0], [22.0, 52.0]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {"id": "TR", "name": "Turkey", "faction": "US", "morale": 0.55},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [26.0, 42.0], [36.0, 42.0], [36.0, 36.0], [26.0, 36.0], [26.0, 42.0]
                        ]]
                    }
                }
            ]
        }

BORDERS = load_countries()

# Simple session state for basic mode
SEED_STATE = {
    "tick": 0,
    "factions": ["US","RU"],
    "units": [
        {"id":"US-CVN-1","type":"carrier","faction":"US","pos":[28.0, 35.0], "supply":1.00} # lon, lat
    ],
    "headlines": []
}

async def broadcast(session_id: str, message: Dict[str, Any]):
    """Broadcast message to all WebSocket clients in a session."""
    for ws in WS_CLIENTS.get(session_id, []):
        try:
            await ws.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to WebSocket: {e}")

@app.post("/sessions")
async def create_session():
    """Create a new simulation session."""
    sid = str(uuid.uuid4())[:8]
    
    # Use simple state for now
    SESSIONS[sid] = {k: (v.copy() if isinstance(v, list) else v) for k, v in SEED_STATE.copy().items()}
    ACTIONS[sid] = []
    WS_CLIENTS[sid] = []
    
    return {
        "session_id": sid, 
        "state": SESSIONS[sid],
        "message": f"Session created successfully. Services available: {SERVICES_AVAILABLE}"
    }

@app.get("/sessions/{sid}/snapshot")
def get_snapshot(sid: str):
    """Get current snapshot of a session."""
    if sid not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    return SESSIONS[sid]

@app.post("/sessions/{sid}/actions")
async def submit_action(sid: str, action: Dict[str, Any] = Body(...)):
    """Submit an action for a session."""
    if sid not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    ACTIONS[sid].append(action)
    
    return {
        "action_id": str(uuid.uuid4()),
        "status": "queued",
        "message": f"Action {action.get('type', 'unknown')} queued successfully"
    }

@app.post("/sessions/{sid}/commit")
async def commit_turn(sid: str):
    """Commit the current turn and advance the simulation."""
    if sid not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[sid]
    
    # Process pending actions
    moved = False
    for a in ACTIONS[sid]:
        if a["type"] == "MOVE_NE":
            for u in state["units"]:
                if u["id"] == "US-CVN-1":
                    # Move ~200–250 km NE (roughly ~2 deg lon, ~1.5 deg lat at this latitude)
                    u["pos"] = [u["pos"][0] + 2.0, u["pos"][1] + 1.5]
                    u["supply"] = round(max(0, u["supply"] - 0.06), 2)
                    moved = True
    
    ACTIONS[sid].clear()
    state["tick"] += 1

    diff = {
        "type": "WORLD_DIFF",
        "tick": state["tick"],
        "entities": [{"id":"US-CVN-1","delta":{"pos": state["units"][0]["pos"], "supply": state["units"][0]["supply"]}}],
        "headlines": (["US carrier group advances northeast (-6% supply)"] if moved else ["No movement this turn"])
    }
    
    # Push to clients
    await broadcast(sid, diff)
    return {"ok": True, "diff": diff, "state": state}

@app.websocket("/ws/sessions/{sid}")
async def ws_session(ws: WebSocket, sid: str):
    """WebSocket endpoint for real-time session updates."""
    await ws.accept()
    if sid not in WS_CLIENTS:
        WS_CLIENTS[sid] = []
    WS_CLIENTS[sid].append(ws)
    
    try:
        # Send initial session state
        if sid in SESSIONS:
            await ws.send_json({
                "type": "SESSION_STATE",
                "session": SESSIONS[sid]
            }, cls=DateTimeEncoder)
        
        while True:
            data = await ws.receive_text()
            # Handle incoming WebSocket messages
            try:
                message = json.loads(data)
                # Basic message handling
                if message.get("type") == "GET_SESSION_STATE" and sid in SESSIONS:
                    await ws.send_json({
                        "type": "SESSION_STATE",
                        "session": SESSIONS[sid]
                    }, cls=DateTimeEncoder)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in WebSocket message: {data}")
    
    except WebSocketDisconnect:
        if sid in WS_CLIENTS and ws in WS_CLIENTS[sid]:
            WS_CLIENTS[sid].remove(ws)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if sid in WS_CLIENTS and ws in WS_CLIENTS[sid]:
            WS_CLIENTS[sid].remove(ws)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "WWIII Simulator Backend Running"}

@app.get("/borders")
def get_borders():
    """Get current border data."""
    return BORDERS

@app.patch("/borders/{country_id}")
async def patch_border(country_id: str, payload: dict = Body(...)):
    """Update country border properties."""
    # Update in-memory data
    for f in BORDERS["features"]:
        if f["properties"]["id"] == country_id:
            if "geometry" in payload:
                f["geometry"] = payload["geometry"]
            if "faction" in payload:
                f["properties"]["faction"] = payload["faction"]
            if "morale" in payload:
                f["properties"]["morale"] = payload["morale"]
            break
    
    # Broadcast border update to all connected clients
    border_update = {
        "type": "BORDER_UPDATE",
        "country_id": country_id,
        "updates": payload
    }
    
    # Broadcast to all sessions
    for session_id in WS_CLIENTS:
        await broadcast(session_id, border_update)
    
    return {"ok": True}

# New API endpoints for enhanced features (basic versions)

@app.get("/sessions/{sid}/events")
def get_session_events(sid: str, limit: int = 20):
    """Get recent events for a session."""
    if sid not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Return basic events for now
    return {
        "events": [
            {
                "id": "event_1",
                "title": "Simulation Started",
                "description": "WWIII simulation session initiated",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "total": 1
    }

@app.get("/sessions/{sid}/news")
def get_session_news(sid: str, limit: int = 10):
    """Get recent news headlines for a session."""
    if sid not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Return basic news for now
    return {
        "headlines": [
            {
                "id": "news_1",
                "title": "WWIII Simulator Active",
                "summary": "Geopolitical simulation is running",
                "source": "Simulator",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "total": 1
    }

@app.get("/sessions/{sid}/stats")
def get_session_stats(sid: str):
    """Get session statistics and usage information."""
    if sid not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = SESSIONS[sid]
    
    return {
        "session_id": sid,
        "current_tick": session["tick"],
        "total_units": len(session["units"]),
        "services_available": SERVICES_AVAILABLE,
        "message": "Basic simulation mode active"
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    services_status = {
        "chatgpt_service": chatgpt_service is not None,
        "realtime_service": realtime_service is not None,
        "sessions_count": len(SESSIONS),
        "active_websockets": sum(len(clients) for clients in WS_CLIENTS.values()),
        "services_available": SERVICES_AVAILABLE
    }
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "services": services_status,
        "mode": "basic" if not SERVICES_AVAILABLE else "enhanced"
    }

@app.get("/costs")
def get_cost_info():
    """Get current cost information and usage statistics."""
    if not SERVICES_AVAILABLE or not chatgpt_service:
        return {
            "status": "services_not_available",
            "message": "Advanced services not enabled",
            "estimated_monthly_cost": "$0.00"
        }
    
    try:
        usage = chatgpt_service.get_usage_stats()
        
        # Calculate estimated monthly cost
        daily_cost = usage.get("total_cost", 0)
        monthly_cost = daily_cost * 30
        
        return {
            "status": "ok",
            "current_usage": usage,
            "pricing": {
                "model": "gpt-4o-mini",
                "input_per_1m_tokens": "$0.15",
                "output_per_1m_tokens": "$0.60",
                "cached_input_per_1m_tokens": "$0.075"
            },
            "cost_estimates": {
                "daily": f"${daily_cost:.2f}",
                "monthly": f"${monthly_cost:.2f}",
                "hourly_gameplay": "$0.09"
            },
            "recommendations": [
                "Use cached responses when possible (50% cost reduction)",
                "Limit real-time updates to important events",
                "Batch similar requests together",
                "Set daily cost limits if needed"
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not retrieve cost info: {str(e)}"
        }

# ============================================================================
# ROUND-BASED GAMEPLAY ENDPOINTS
# ============================================================================

@app.post("/game/create-session")
async def create_game_session(request: dict):
    """Create a new round-based game session."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    session_id = str(uuid.uuid4())
    
    # Create new game session
    session = {
        "session_id": session_id,
        "game_mode": request.get("game_mode", "single_player"),
        "host_player": request.get("host_country"),
        "players": {session_id: request.get("host_country")},  # Host is first player
        "max_players": request.get("max_players", 8),
        "round_duration_minutes": request.get("round_duration_minutes", 5),
        "start_date": datetime.now().isoformat(),
        "countries": {},  # Will be populated with all world countries
        "ai_controlled_countries": [],  # Will be populated with non-player countries
        "current_round": 1,
        "current_phase": "planning",
        "rounds": [],
        "max_actions_per_round": 3,
        "is_active": True
    }
    
    # Initialize world with all countries
    await initialize_world_countries(session)
    
    # Set up AI controllers for non-player countries
    await setup_ai_controllers(session)
    
    GAME_SESSIONS[session_id] = session
    
    return {
        "session_id": session_id,
        "game_mode": request.get("game_mode", "single_player"),
        "message": f"Game session created successfully. Mode: {request.get('game_mode', 'single_player')}"
    }

@app.post("/game/{session_id}/join")
async def join_game_session(session_id: str, request: dict):
    """Join an existing game session."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    if session_id not in GAME_SESSIONS:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = GAME_SESSIONS[session_id]
    
    # Check if session is full
    if len(session["players"]) >= session["max_players"]:
        raise HTTPException(status_code=400, detail="Game session is full")
    
    # Check if country is already taken
    if request.get("selected_country") in session["players"].values():
        raise HTTPException(status_code=400, detail="Country already selected")
    
    # Add player to session
    player_id = str(uuid.uuid4())
    session["players"][player_id] = request.get("selected_country")
    
    # Create player object
    player = {
        "player_id": player_id,
        "username": request.get("username"),
        "selected_country": request.get("selected_country"),
        "last_seen": datetime.now().isoformat(),
        "is_connected": True,
        "is_ready": False,
        "actions_submitted": 0
    }
    PLAYERS[player_id] = player
    
    return {
        "player_id": player_id,
        "session_id": session_id,
        "message": f"Successfully joined as {request.get('selected_country')}"
    }

@app.post("/game/{session_id}/actions")
async def submit_action(session_id: str, request: dict):
    """Submit an action for the current round."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    if session_id not in GAME_SESSIONS:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = GAME_SESSIONS[session_id]
    
    # Check if it's planning phase
    if session["current_phase"] != "planning":
        raise HTTPException(status_code=400, detail="Actions can only be submitted during planning phase")
    
    # Check if player has actions remaining
    current_round = session["rounds"][-1] if session["rounds"] else None
    if not current_round:
        # Create first round if it doesn't exist
        current_round = {
            "round_number": 1,
            "phase": "planning",
            "start_time": datetime.now().isoformat(),
            "player_actions": [],
            "world_events": [],
            "diplomatic_changes": [],
            "economic_changes": [],
            "military_changes": []
        }
        session["rounds"].append(current_round)
    
    player_actions_this_round = len([
        action for action in current_round["player_actions"] 
        if action["player_country"] == request.get("player_country")
    ])
    
    if player_actions_this_round >= session["max_actions_per_round"]:
        raise HTTPException(status_code=400, detail="Maximum actions per round reached")
    
    # Create action
    action = {
        "action_id": str(uuid.uuid4()),
        "player_country": request.get("player_country"),
        "action_type": request.get("action_type"),
        "target_country": request.get("target_country"),
        "parameters": request.get("parameters", {}),
        "round_number": session["current_round"],
        "phase": session["current_phase"],
        "is_secret": request.get("is_secret", False),
        "status": "pending"
    }
    
    # Add action to current round
    current_round["player_actions"].append(action)
    
    return {
        "action_id": action["action_id"],
        "status": "submitted",
        "message": f"Action {request.get('action_type')} submitted successfully",
        "round_number": session["current_round"]
    }

@app.get("/game/{session_id}/status")
async def get_game_status(session_id: str):
    """Get current game status and round information."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    if session_id not in GAME_SESSIONS:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = GAME_SESSIONS[session_id]
    
    # Calculate time remaining in current phase
    current_round = session["rounds"][-1] if session["rounds"] else None
    time_remaining = 0
    
    if current_round and session["current_phase"] == "planning":
        start_time = datetime.fromisoformat(current_round["start_time"])
        elapsed = (datetime.now() - start_time).total_seconds()
        time_remaining = max(0, (session["round_duration_minutes"] * 60) - elapsed)
    
    return {
        "session_id": session_id,
        "round_number": session["current_round"],
        "phase": session["current_phase"],
        "time_remaining": int(time_remaining),
        "actions_submitted": len(current_round["player_actions"]) if current_round else 0,
        "max_actions": session["max_actions_per_round"],
        "world_events": current_round.get("world_events", []) if current_round else [],
        "round_summary": current_round.get("summary") if current_round else None
    }

@app.post("/game/{session_id}/start")
async def start_game(session_id: str):
    """Start the game and begin the first round."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    if session_id not in GAME_SESSIONS:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = GAME_SESSIONS[session_id]
    
    # Create first round
    round_obj = {
        "round_number": 1,
        "phase": "planning",
        "start_time": datetime.now().isoformat(),
        "player_actions": [],
        "world_events": [],
        "diplomatic_changes": [],
        "economic_changes": [],
        "military_changes": []
    }
    session["rounds"].append(round_obj)
    
    # Start round timer
    await start_round_timer(session_id)
    
    return {
        "session_id": session_id,
        "message": "Game started! Round 1 planning phase has begun.",
        "round_number": 1,
        "phase": "planning",
        "duration_minutes": session["round_duration_minutes"]
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def initialize_world_countries(session):
    """Initialize the world with all countries."""
    # Load all countries from the borders data
    try:
        with open("borders-enhanced-detailed.json", "r") as f:
            borders_data = json.load(f)
        
        for feature in borders_data["features"]:
            props = feature["properties"]
            country = {
                "id": props.get("id", ""),
                "name": props.get("name", ""),
                "faction": "NEUTRAL",
                "morale": 0.5,
                "capital": props.get("capital"),
                "coordinates": props.get("coordinates"),
                "area_km2": props.get("area_km2"),
                "description": props.get("description")
            }
            session["countries"][country["id"]] = country
            
    except Exception as e:
        logger.error(f"Error loading world countries: {e}")
        # Fallback: create basic countries
        for country_id in ["US", "CN", "RU", "EU", "IN", "IR", "IL", "KP"]:
            session["countries"][country_id] = {
                "id": country_id,
                "name": country_id,
                "faction": "NEUTRAL",
                "morale": 0.5
            }

async def setup_ai_controllers(session):
    """Set up AI controllers for non-player countries."""
    player_countries = set(session["players"].values())
    
    for country_id, country in session["countries"].items():
        if country_id not in player_countries:
            session["ai_controlled_countries"].append(country_id)
            
            # Create AI controller
            ai_controller = {
                "country_id": country_id,
                "strategy": "NEUTRAL",
                "personality_traits": ["balanced"],
                "risk_tolerance": 0.5,
                "aggression_level": 0.3,
                "diplomatic_approach": 0.7
            }
            AI_CONTROLLERS[country_id] = ai_controller

async def start_round_timer(session_id: str):
    """Start a timer for the current round."""
    if session_id in ROUND_TIMERS:
        ROUND_TIMERS[session_id].cancel()
    
    session = GAME_SESSIONS[session_id]
    
    async def round_timer():
        await asyncio.sleep(session["round_duration_minutes"] * 60)
        await end_planning_phase(session_id)
    
    ROUND_TIMERS[session_id] = asyncio.create_task(round_timer())

async def end_planning_phase(session_id: str):
    """End the planning phase and process all actions."""
    if session_id not in GAME_SESSIONS:
        return
    
    session = GAME_SESSIONS[session_id]
    current_round = session["rounds"][-1]
    
    # End planning phase
    current_round["end_time"] = datetime.now().isoformat()
    current_round["phase"] = "resolution"
    
    # Process all actions
    await process_round_actions(session_id)
    
    # Generate round summary
    await generate_round_summary(session_id)
    
    # Start next round
    session["current_round"] += 1
    new_round = {
        "round_number": session["current_round"],
        "phase": "planning",
        "start_time": datetime.now().isoformat()
    }
    session["rounds"].append(new_round)
    
    # Start timer for new round
    await start_round_timer(session_id)
    
    # Broadcast round update to all connected clients
    await broadcast_round_update(session_id)

async def process_round_actions(session_id: str):
    """Process all actions submitted during the planning phase."""
    session = GAME_SESSIONS[session_id]
    current_round = session["rounds"][-1]
    
    for action in current_round["player_actions"]:
        # Process each action based on type
        result = await execute_action(action, session)
        action["result"] = result
        action["status"] = "resolved"

async def execute_action(action, session):
    """Execute a single action and return the result."""
    # This is a simplified action execution system
    # In a full implementation, this would be much more complex
    
    result = {
        "success": True,
        "message": f"Action {action['action_type']} executed successfully",
        "effects": {}
    }
    
    if action["action_type"] == "form_alliance":
        result["message"] = f"{action['player_country']} formed an alliance with {action['target_country']}"
    elif action["action_type"] == "declare_war":
        result["message"] = f"{action['player_country']} declared war on {action['target_country']}"
    elif action["action_type"] == "invest_in_economy":
        result["message"] = f"{action['player_country']} invested in economic development"
    
    return result

async def generate_round_summary(session_id: str):
    """Generate a summary of the round for players."""
    session = GAME_SESSIONS[session_id]
    current_round = session["rounds"][-1]
    
    summary_parts = []
    
    # Add action summaries
    for action in current_round["player_actions"]:
        if not action.get("is_secret", False):
            summary_parts.append(action["result"]["message"])
    
    # Add world events
    for event in current_round.get("world_events", []):
        summary_parts.append(f"World Event: {event['title']}")
    
    current_round["summary"] = " | ".join(summary_parts) if summary_parts else "A quiet round with no major developments."

async def broadcast_round_update(session_id: str):
    """Broadcast round update to all connected WebSocket clients."""
    if session_id not in WS_CLIENTS:
        return
    
    session = GAME_SESSIONS[session_id]
    current_round = session["rounds"][-1]
    
    update = {
        "type": "ROUND_UPDATE",
        "session_id": session_id,
        "round_number": session["current_round"],
        "phase": session["current_phase"],
        "summary": current_round["summary"],
        "highlights": current_round.get("highlights", [])
    }
    
    for client in WS_CLIENTS[session_id]:
        try:
            await client.send_json(update, cls=DateTimeEncoder)
        except Exception as e:
            logger.error(f"Error broadcasting to client: {e}")

# ============================================================================
# PLAYABLE COUNTRIES ENDPOINTS
# ============================================================================

@app.get("/playable-countries")
def get_playable_countries():
    """Get all available playable countries."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    return {
        "countries": list(PLAYABLE_COUNTRIES.keys()),
        "total": len(PLAYABLE_COUNTRIES),
        "categories": {
            "major_powers": ["US", "CN", "RU", "EU"],
            "rising_powers": ["IN"],
            "regional_players": ["IR", "IL", "KP"]
        }
    }

@app.get("/playable-countries/{country_id}")
def get_playable_country(country_id: str):
    """Get detailed information about a specific playable country."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    if country_id not in PLAYABLE_COUNTRIES:
        raise HTTPException(status_code=404, detail="Country not found")
    
    country = PLAYABLE_COUNTRIES[country_id]
    return country

@app.get("/playable-countries/{country_id}/setup")
def get_country_setup(country_id: str):
    """Get starting setup information for a playable country."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    if country_id not in PLAYABLE_COUNTRIES:
        raise HTTPException(status_code=404, detail="Country not found")
    
    country = PLAYABLE_COUNTRIES[country_id]
    
    return {
        "country_id": country_id,
        "name": country.name,
        "type": country.type,
        "starting_faction": country.faction,
        "starting_conditions": {
            "morale": country.starting_morale,
            "economic_strength": country.starting_economic_strength,
            "military_strength": country.starting_military_strength,
            "diplomatic_influence": country.starting_diplomatic_influence
        },
        "special_abilities": country.special_abilities,
        "starting_units": country.starting_units,
        "starting_bases": country.starting_bases,
        "starting_allies": country.starting_allies,
        "starting_enemies": country.starting_enemies,
        "victory_conditions": country.victory_conditions,
        "unique_challenges": country.unique_challenges,
        "description": country.description,
        "playstyle_tips": country.playstyle_tips
    }

@app.post("/playable-countries/{country_id}/start-game")
def start_game_with_country(country_id: str):
    """Start a new game session with a specific playable country."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    if country_id not in PLAYABLE_COUNTRIES:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Create a new session with the selected country
    session_id = str(uuid.uuid4())
    country = PLAYABLE_COUNTRIES[country_id]
    
    # Initialize session with country-specific starting conditions
    session = {
        "session_id": session_id,
        "start_date": datetime.now(),
        "current_date": datetime.now(),
        "game_speed": 1.0,
        "tick": 0,
        "turn_number": 0,
        "phase": "planning",
        "selected_country": country_id,
        "countries": {},
        "units": {},
        "bases": {},
        "diplomatic_relations": {},
        "trade_routes": {},
        "sanctions": {},
        "world_events": {},
        "news_headlines": [],
        "pending_actions": [],
        "action_history": [],
        "ai_enabled": True,
        "real_time_events": True,
        "difficulty_level": "medium"
    }
    
    # Add the selected country to the session
    session["countries"][country_id] = {
        "id": country_id,
        "name": country.name,
        "faction": country.faction,
        "morale": country.starting_morale,
        "type": country.type,
        "special_abilities": country.special_abilities,
        "starting_conditions": {
            "economic_strength": country.starting_economic_strength,
            "military_strength": country.starting_military_strength,
            "diplomatic_influence": country.starting_diplomatic_influence
        }
    }
    
    # Add starting units and bases
    for unit_id in country.starting_units:
        session["units"][unit_id] = {
            "id": unit_id,
            "type": "carrier" if "CVN" in unit_id else "army" if "ARMY" in unit_id else "air",
            "faction": country.faction,
            "pos": [0, 0],  # Will be set based on country location
            "health": 1.0,
            "fuel": 1.0,
            "ammunition": 1.0,
            "morale": 0.8,
            "is_active": True
        }
    
    for base_id in country.starting_bases:
        session["bases"][base_id] = {
            "id": base_id,
            "name": f"{country.name} Base",
            "faction": country.faction,
            "pos": [0, 0],  # Will be set based on country location
            "max_units": 10,
            "current_units": [],
            "base_type": "multi",
            "is_operational": True,
            "damage_level": 0.0
        }
    
    SESSIONS[session_id] = session
    ACTIONS[session_id] = []
    WS_CLIENTS[session_id] = []
    
    return {
        "session_id": session_id,
        "country_id": country_id,
        "country_name": country.name,
        "message": f"Game started with {country.name}",
        "session": session
    }

@app.get("/playable-countries/compare")
def compare_playable_countries():
    """Compare all playable countries side by side."""
    if not MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Models not available")
    
    comparison = {}
    
    for country_id, country in PLAYABLE_COUNTRIES.items():
        comparison[country_id] = {
            "name": country.name,
            "type": country.type,
            "faction": country.faction,
            "starting_stats": {
                "morale": country.starting_morale,
                "economic": country.starting_economic_strength,
                "military": country.starting_military_strength,
                "diplomatic": country.starting_diplomatic_influence
            },
            "special_abilities_count": len(country.special_abilities),
            "starting_units_count": len(country.starting_units),
            "starting_allies_count": len(country.starting_allies),
            "starting_enemies_count": len(country.starting_enemies),
            "difficulty": "Easy" if country.type == "major_power" else "Medium" if country.type == "rising_power" else "Hard"
        }
    
    return {
        "comparison": comparison,
        "summary": {
            "total_countries": len(PLAYABLE_COUNTRIES),
            "major_powers": len([c for c in PLAYABLE_COUNTRIES.values() if c.type == "major_power"]),
            "rising_powers": len([c for c in PLAYABLE_COUNTRIES.values() if c.type == "rising_power"]),
            "regional_players": len([c for c in PLAYABLE_COUNTRIES.values() if c.type == "regional_player"])
        }
    }

# ============================================================================
# OBSERVE THE END - PREDICTIVE SIMULATION ENDPOINTS
# ============================================================================

@app.post("/observe-the-end/create")
async def create_observe_the_end_simulation():
    """Create a new 'Observe the End' predictive simulation"""
    if not PREDICTIVE_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Predictive simulation service not available")
    
    try:
        simulation = await predictive_service.create_observe_the_end_simulation()
        
        return {
            "simulation_id": simulation.simulation_id,
            "start_date": simulation.start_date.isoformat(),
            "mode": simulation.mode,
            "message": "Predictive simulation started. Timeline will be generated automatically.",
            "status": "running"
        }
    except Exception as e:
        logger.error(f"Error creating predictive simulation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create simulation")

@app.get("/observe-the-end/{simulation_id}/timeline")
async def get_simulation_timeline(simulation_id: str):
    """Get the complete timeline of events for a simulation"""
    if not PREDICTIVE_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Predictive simulation service not available")
    
    try:
        timeline = await predictive_service.get_simulation_timeline(simulation_id)
        
        return {
            "simulation_id": simulation_id,
            "events": [
                {
                    "event_id": event.event_id,
                    "date": event.date.isoformat(),
                    "event_type": event.event_type,
                    "title": event.title,
                    "description": event.description,
                    "affected_countries": event.affected_countries,
                    "historical_pattern": event.historical_pattern,
                    "probability": event.probability,
                    "impact_magnitude": event.impact_magnitude,
                    "ai_reasoning": event.ai_reasoning
                }
                for event in timeline
            ],
            "total_events": len(timeline)
        }
    except Exception as e:
        logger.error(f"Error getting simulation timeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to get timeline")

@app.get("/observe-the-end/{simulation_id}/world-state/{date}")
async def get_world_state_at_date(simulation_id: str, date: str):
    """Get world state at a specific date"""
    if not PREDICTIVE_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Predictive simulation service not available")
    
    try:
        # Parse date string
        target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        world_state = await predictive_service.get_world_state_at_date(simulation_id, target_date)
        
        if not world_state:
            raise HTTPException(status_code=404, detail="World state not found for date")
        
        return {
            "simulation_id": simulation_id,
            "date": world_state.date.isoformat(),
            "countries": world_state.countries,
            "alliances": world_state.alliances,
            "conflicts": world_state.conflicts,
            "economic_indicators": world_state.economic_indicators,
            "world_stability_index": world_state.world_stability_index,
            "nuclear_threat_level": world_state.nuclear_threat_level
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    except Exception as e:
        logger.error(f"Error getting world state: {e}")
        raise HTTPException(status_code=500, detail="Failed to get world state")

@app.get("/observe-the-end/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get current status of a simulation"""
    if not PREDICTIVE_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Predictive simulation service not available")
    
    try:
        if simulation_id not in predictive_service.active_simulations:
            raise HTTPException(status_code=404, detail="Simulation not found")
        
        simulation = predictive_service.active_simulations[simulation_id]
        
        return {
            "simulation_id": simulation_id,
            "mode": simulation.mode,
            "start_date": simulation.start_date.isoformat(),
            "predicted_end_date": simulation.predicted_end_date.isoformat() if simulation.predicted_end_date else None,
            "end_scenario": simulation.end_scenario,
            "total_events": len(simulation.timeline_events),
            "total_world_states": len(simulation.world_states),
            "status": "completed" if simulation.predicted_end_date else "running"
        }
    except Exception as e:
        logger.error(f"Error getting simulation status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")

@app.get("/observe-the-end/patterns")
async def get_historical_patterns():
    """Get available historical patterns for analysis"""
    if not PREDICTIVE_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Predictive simulation service not available")
    
    try:
        patterns = predictive_service.historical_patterns
        
        return {
            "patterns": [
                {
                    "pattern": pattern.value,
                    "description": config["description"],
                    "modern_parallel": config["modern_parallel"],
                    "indicators": config["indicators"],
                    "timeline": config["timeline"],
                    "confidence": config["confidence"]
                }
                for pattern, config in patterns.items()
            ],
            "total_patterns": len(patterns)
        }
    except Exception as e:
        logger.error(f"Error getting historical patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patterns")

@app.get("/observe-the-end/news-sources")
async def get_news_sources():
    """Get available news sources for real-time data"""
    if not PREDICTIVE_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Predictive simulation service not available")
    
    try:
        sources = predictive_service.news_sources
        
        return {
            "sources": [
                {
                    "source_id": source.source_id,
                    "name": source.name,
                    "url": source.url,
                    "region": source.region,
                    "bias_level": source.bias_level,
                    "reliability_score": source.reliability_score,
                    "update_frequency": source.update_frequency
                }
                for source in sources
            ],
            "total_sources": len(sources)
        }
    except Exception as e:
        logger.error(f"Error getting news sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to get news sources")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)