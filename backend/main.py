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

# Import our new models (optional - simplified)
try:
    from models import (
        GameSession, GameAction, SessionCreateRequest, SessionCreateResponse,
        ActionRequest, ActionResponse, WorldUpdateResponse, Country, Faction,
        WorldEvent, NewsHeadline, EventType, DiplomaticStatus
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

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- In-memory state for the enhanced simulator ---
SESSIONS: Dict[str, Dict[str, Any]] = {}
ACTIONS: Dict[str, List[Dict[str, Any]]] = {}
WS_CLIENTS: Dict[str, List[WebSocket]] = {}

# Initialize services on startup (optional)
@app.on_event("startup")
async def startup_event():
    global chatgpt_service, realtime_service, SERVICES_AVAILABLE
    if SERVICES_AVAILABLE:
        try:
            chatgpt_service = await get_chatgpt_service()
            realtime_service = await get_realtime_service()
            logger.info("Services initialized successfully")
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
            })
        
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
                    })
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