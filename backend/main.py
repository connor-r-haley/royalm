# pip install fastapi uvicorn "pydantic<3" starlette
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio, uuid, json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- In-memory state (one unit to move) ---
SESSIONS: Dict[str, Dict[str, Any]] = {}
ACTIONS: Dict[str, List[Dict[str, Any]]] = {}
WS_CLIENTS: Dict[str, List[WebSocket]] = {}

SEED_STATE = {
    "tick": 0,
    "factions": ["US","RU"],
    "units": [
        {"id":"US-CVN-1","type":"carrier","faction":"US","pos":[28.0, 35.0], "supply":1.00} # lon, lat
    ],
    "headlines": []
}

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

class Action(BaseModel):
    player_id: str
    type: str               # "MOVE_NE" only for Step 0
    payload: Dict[str, Any] = {}

def snapshot(session_id: str) -> Dict[str, Any]:
    return SESSIONS[session_id]

async def broadcast(session_id: str, message: Dict[str, Any]):
    for ws in WS_CLIENTS.get(session_id, []):
        try:
            await ws.send_json(message)
        except:
            pass

@app.post("/sessions")
def create_session():
    sid = str(uuid.uuid4())[:8]
    SESSIONS[sid] = {k: (v.copy() if isinstance(v, list) else v) for k, v in SEED_STATE.copy().items()}
    ACTIONS[sid] = []
    WS_CLIENTS[sid] = []
    return {"session_id": sid, "state": SESSIONS[sid]}

@app.get("/sessions/{sid}/snapshot")
def get_snapshot(sid: str):
    return snapshot(sid)

@app.post("/sessions/{sid}/actions")
def submit_action(sid: str, action: Action):
    ACTIONS[sid].append(action.dict())
    return {"ok": True, "queued": action.dict()}

@app.post("/sessions/{sid}/commit")
async def commit_turn(sid: str):
    state = SESSIONS[sid]
    # For Step 0: if any MOVE_NE action exists, nudge the carrier NE & make a headline
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
    await ws.accept()
    WS_CLIENTS[sid].append(ws)
    try:
        await ws.send_json({"type":"CONNECTED","tick": SESSIONS[sid]["tick"]})
        while True:
            # We don’t expect client -> server messages for Step 0; keep alive
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        pass
    finally:
        WS_CLIENTS[sid].remove(ws)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "WWIII Simulator Backend Running"}

# Borders are now served statically from frontend/public/borders.json
# Only PATCH endpoint is needed for updates

@app.patch("/borders/{country_id}")
async def patch_border(country_id: str, payload: dict = Body(...)):
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
    
    # Note: Static file updates removed - borders are now managed locally by frontend
    # Changes are broadcast via WebSocket for real-time updates across clients
    
    # Broadcast border update to all connected clients
    border_update = {
        "type": "BORDER_UPDATE",
        "country_id": country_id,
        "updates": payload
    }
    
    # Broadcast to all sessions (you might want to scope this differently)
    for session_id in WS_CLIENTS:
        await broadcast(session_id, border_update)
    
    return {"ok": True}