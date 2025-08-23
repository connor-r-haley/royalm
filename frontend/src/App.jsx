import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import BorderManager from "./borderManager";

const API = "http://localhost:8000";
const MAPTILER_KEY = "A4684uteIMrjertm4Tjw";
const STYLES = {
   // Aquarelle:        `https://api.maptiler.com/maps/aquarelle/style.json?key=${MAPTILER_KEY}`,
  // Backdrop:         `https://api.maptiler.com/maps/backdrop/style.json?key=${MAPTILER_KEY}`,
  // Basic:            `https://api.maptiler.com/maps/basic-v2/style.json?key=${MAPTILER_KEY}`,
  // Bright:           `https://api.maptiler.com/maps/bright-v2/style.json?key=${MAPTILER_KEY}`,
  // Dataviz:          `https://api.maptiler.com/maps/dataviz/style.json?key=${MAPTILER_KEY}`,
  Main:        `https://api.maptiler.com/maps/landscape/style.json?key=${MAPTILER_KEY}`,
  // Ocean:            `https://api.maptiler.com/maps/ocean/style.json?key=${MAPTILER_KEY}`,
  // OpenStreetMap:    `https://api.maptiler.com/maps/openstreetmap/style.json?key=${MAPTILER_KEY}`,
  SatelliteMain:        `https://api.maptiler.com/maps/satellite/style.json?key=${MAPTILER_KEY}`,          // imagery only
  ModernPolitical:          `https://api.maptiler.com/maps/outdoor-v2/style.json?key=${MAPTILER_KEY}`,
  SatellitePolitical:  `https://api.maptiler.com/maps/hybrid/style.json?key=${MAPTILER_KEY}`,             // imagery + labels
  // Streets:          `https://api.maptiler.com/maps/streets-v2/style.json?key=${MAPTILER_KEY}`,
  GreyscalePolitical:            `https://api.maptiler.com/maps/toner-v2/style.json?key=${MAPTILER_KEY}`,           // black & white
  // Topo:             `https://api.maptiler.com/maps/topo/style.json?key=${MAPTILER_KEY}`,
  // Winter:           `https://api.maptiler.com/maps/winter/style.json?key=${MAPTILER_KEY}`,
  Landscape:        `https://api.maptiler.com/maps/landscape/style.json?key=${MAPTILER_KEY}`, // default (minimal borders)
  TonerBW:          `https://api.maptiler.com/maps/toner-v2/style.json?key=${MAPTILER_KEY}`,   // high contrast
  SatelliteHybrid:  `https://api.maptiler.com/maps/hybrid/style.json?key=${MAPTILER_KEY}`,     // imagery + labels
};

export default function App() {
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const wsRef = useRef(null);

  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState("Not connected");
  const [queued, setQueued] = useState(false);
  const [headlines, setHeadlines] = useState([]);
  const [currentStyle, setCurrentStyle] = useState(localStorage.getItem("style") || "Landscape");
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [servicesStatus, setServicesStatus] = useState({
    chatgpt: false,
    news: false,
    loading: true
  });
  const [costInfo, setCostInfo] = useState(null);
  const [recentNews, setRecentNews] = useState([]);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const borderManagerRef = useRef(new BorderManager());

  // Check services status and fetch data
  const checkServicesStatus = async () => {
    try {
      console.log("Checking services status...");
      
      // Check health endpoint
      const healthResponse = await fetch(`${API}/health`);
      if (!healthResponse.ok) {
        throw new Error(`Health check failed: ${healthResponse.status}`);
      }
      const healthData = await healthResponse.json();
      console.log("Health data:", healthData);
      
      // Check cost info
      const costResponse = await fetch(`${API}/costs`);
      const costData = await costResponse.json();
      
      const servicesAvailable = healthData.services?.chatgpt_service && healthData.services?.realtime_service;
      
      setServicesStatus({
        chatgpt: healthData.services?.chatgpt_service || false,
        news: healthData.services?.realtime_service || false,
        loading: false
      });
      
      setCostInfo(costData);
      
      // If services are available, fetch some data
      if (servicesAvailable && healthData.mode === "enhanced") {
        console.log("Services available, fetching data...");
        await fetchRecentNews();
        await fetchAiAnalysis();
      } else {
        console.log("Services not available, using demo data");
        // Set demo data even if services aren't available
        setRecentNews([
          { title: "Global tensions rise in Eastern Europe", source: "Demo News", published_at: new Date().toISOString() },
          { title: "Economic sanctions impact global markets", source: "Demo News", published_at: new Date().toISOString() },
          { title: "Diplomatic talks continue in Geneva", source: "Demo News", published_at: new Date().toISOString() }
        ]);
        setAiAnalysis([
          { type: "diplomatic", title: "AI Analysis: Regional tensions escalating", description: "Analysis suggests increased military activity in the region", timestamp: new Date().toISOString() },
          { type: "economic", title: "AI Analysis: Economic indicators shifting", description: "Market analysis predicts currency fluctuations", timestamp: new Date().toISOString() }
        ]);
      }
    } catch (error) {
      console.error("Error checking services:", error);
      setServicesStatus({
        chatgpt: false,
        news: false,
        loading: false
      });
      // Set demo data on error
      setRecentNews([
        { title: "Global tensions rise in Eastern Europe", source: "Demo News", published_at: new Date().toISOString() },
        { title: "Economic sanctions impact global markets", source: "Demo News", published_at: new Date().toISOString() },
        { title: "Diplomatic talks continue in Geneva", source: "Demo News", published_at: new Date().toISOString() }
      ]);
      setAiAnalysis([
        { type: "diplomatic", title: "AI Analysis: Regional tensions escalating", description: "Analysis suggests increased military activity in the region", timestamp: new Date().toISOString() },
        { type: "economic", title: "AI Analysis: Economic indicators shifting", description: "Market analysis predicts currency fluctuations", timestamp: new Date().toISOString() }
      ]);
    }
  };

  const fetchRecentNews = async () => {
    try {
      // Create a temporary session for demo data
      const sessionResponse = await fetch(`${API}/sessions`, { method: "POST" });
      const sessionData = await sessionResponse.json();
      const sessionId = sessionData.session_id;
      
      const response = await fetch(`${API}/sessions/${sessionId}/news?limit=3`);
      const data = await response.json();
      if (data.headlines) {
        setRecentNews(data.headlines);
      }
    } catch (error) {
      console.error("Error fetching news:", error);
      // Set some demo data if API fails
      setRecentNews([
        { title: "Global tensions rise in Eastern Europe", source: "Demo News", published_at: new Date().toISOString() },
        { title: "Economic sanctions impact global markets", source: "Demo News", published_at: new Date().toISOString() },
        { title: "Diplomatic talks continue in Geneva", source: "Demo News", published_at: new Date().toISOString() }
      ]);
    }
  };

  const fetchAiAnalysis = async () => {
    try {
      // Create a temporary session for demo data
      const sessionResponse = await fetch(`${API}/sessions`, { method: "POST" });
      const sessionData = await sessionResponse.json();
      const sessionId = sessionData.session_id;
      
      const response = await fetch(`${API}/sessions/${sessionId}/events?limit=2`);
      const data = await response.json();
      if (data.events) {
        setAiAnalysis(data.events);
      }
    } catch (error) {
      console.error("Error fetching AI analysis:", error);
      // Set some demo data if API fails
      setAiAnalysis([
        { type: "diplomatic", title: "AI Analysis: Regional tensions escalating", description: "Analysis suggests increased military activity in the region", timestamp: new Date().toISOString() },
        { type: "economic", title: "AI Analysis: Economic indicators shifting", description: "Market analysis predicts currency fluctuations", timestamp: new Date().toISOString() }
      ]);
    }
  };

  useEffect(() => {
    const map = new maplibregl.Map({
      container: "map",
      style: STYLES[currentStyle],   // <-- your chosen MapTiler style
      center: [28.0, 35.0],
      zoom: 4.5,
    });
    mapRef.current = map;

    map.on("load", async () => {
      // 1. turn off unwanted built-in layers (optional)
      if (map.getLayer("country-label")) {
        map.setLayoutProperty("country-label", "visibility", "none");
      }
      if (map.getLayer("admin-1-boundary")) {
        map.setLayoutProperty("admin-1-boundary", "visibility", "none");
      }

      // 2. re-add your custom overlays (units, control zones, etc.)
      addGameLayers(map);

      // 3. load nation boundaries using border manager
      map.addSource("borders", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      await borderManagerRef.current.initialize(map);

      // 4. fill layer (color by faction/morale)
      map.addLayer({
        id: "borders-fill",
        type: "fill",
        source: "borders",
        paint: {
          "fill-color": [
            "match", ["get", "faction"],
            "US", "#2563eb",
            "RU", "#dc2626",
            /* else */ "#9ca3af"
          ],
          "fill-opacity": [
            "interpolate", ["linear"], ["get", "morale"],
            0, 0.20, 1, 0.55
          ]
        }
      });

      // 5. outline layer (with hover highlight)
      map.addLayer({
        id: "borders-outline",
        type: "line",
        source: "borders",
        paint: {
          "line-color": "#ffffff",
          "line-width": [
            "case",
            ["boolean", ["feature-state", "hover"], false], 3.0,
            1.5
          ]
        }
      });

      // 6. hover highlight logic
      let hoverId = null;
      map.on("mousemove", "borders-fill", (e) => {
        if (!e.features?.length) return;
        const id = e.features[0].properties.id;
        if (hoverId && hoverId !== id) {
          map.setFeatureState({ source: "borders", id: hoverId }, { hover: false });
        }
        hoverId = id;
        map.setFeatureState({ source: "borders", id }, { hover: true });
      });
      map.on("mouseleave", "borders-fill", () => {
        if (hoverId) {
          map.setFeatureState({ source: "borders", id: hoverId }, { hover: false });
        }
        hoverId = null;
      });

      // 7. Click select (opens side panel)
      map.on("click", "borders-fill", (e) => {
        const f = e.features?.[0];
        if (!f) return;
        setSelectedCountry({
          id: f.properties.id,
          name: f.properties.name,
          faction: f.properties.faction,
          morale: Number(f.properties.morale ?? 0.5),
          mother_country: f.properties.mother_country,
          description: f.properties.description
        });
      });

      // Check services status after map loads
      checkServicesStatus();
    });

    return () => map.remove();
  }, [currentStyle]);   // 👈 add currentStyle as dependency so it re-runs when you change basemap

  function pushHeadline(h) {
    setHeadlines((prev) => [h, ...prev].slice(0, 12));
  }

  async function newSession() {
    const r = await fetch(`${API}/sessions`, { method: "POST" });
    const j = await r.json();
    setSessionId(j.session_id);
    setStatus(`Session ${j.session_id} | Tick ${j.state.tick}`);
    const [lon, lat] = j.state.units[0].pos;

    if (!markerRef.current) {
      markerRef.current = new maplibregl.Marker({ color: "#1e90ff" }).setLngLat([lon, lat]).addTo(mapRef.current);
      mapRef.current.flyTo({ center: [lon, lat], zoom: 5, speed: 0.8 });
    } else {
      markerRef.current.setLngLat([lon, lat]);
    }
    openWS(j.session_id);
    pushHeadline("New session created. Fleet awaiting orders.");
  }

  function openWS(sid) {
    if (wsRef.current) try { wsRef.current.close(); } catch {}
    const ws = new WebSocket(`ws://localhost:8000/ws/sessions/${sid}`);
    wsRef.current = ws;
    ws.onopen = () => setStatus(`Session ${sid} | WS connected`);
    ws.onmessage = (evt) => {
      const msg = JSON.parse(evt.data);
      if (msg.type === "WORLD_DIFF") {
        const ent = msg.entities.find((e) => e.id === "US-CVN-1");
        if (ent && markerRef.current) {
          const [lon, lat] = ent.delta.pos;
          drawPulseLine([lon - 2.0, lat - 1.5], [lon, lat]);
          markerRef.current.setLngLat([lon, lat]);
        }
        (msg.headlines || []).forEach(pushHeadline);
        setStatus(`Session ${sid} | Tick ${msg.tick}`);
        setQueued(false);
      } else if (msg.type === "BORDER_UPDATE") {
        // Apply border update locally
        borderManagerRef.current.applyUpdate(msg.country_id, msg.updates);
      }
    };
  }

  async function queueMove() {
    if (!sessionId || queued) return;
    await fetch(`${API}/sessions/${sessionId}/actions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_id: "P1", type: "MOVE_NE", payload: {} }),
    });
    setQueued(true);
    pushHeadline("Order queued: Move Fleet NE");
  }

  async function commitTurn() {
    if (!sessionId) return;
    const r = await fetch(`${API}/sessions/${sessionId}/commit`, { method: "POST" });
    const j = await r.json();
    (j.diff?.headlines || []).forEach(pushHeadline);
  }

  function drawPulseLine(start, end) {
    const idSrc = "pulse-src";
    const idLine = "pulse-line";
    const fc = {
      type: "FeatureCollection",
      features: [{ type: "Feature", geometry: { type: "LineString", coordinates: [start, end] } }],
    };
    const map = mapRef.current;
    if (!map) return;
    if (map.getSource(idSrc)) map.getSource(idSrc).setData(fc);
    else map.addSource(idSrc, { type: "geojson", data: fc });
    if (!map.getLayer(idLine)) {
      map.addLayer({ id: idLine, type: "line", source: idSrc, paint: { "line-width": 4, "line-opacity": 0.9 } });
    }
    setTimeout(() => map.setPaintProperty(idLine, "line-opacity", 0.0), 700);
    setTimeout(() => {
      if (map.getLayer(idLine)) map.removeLayer(idLine);
      if (map.getSource(idSrc)) map.removeSource(idSrc);
    }, 1200);
  }

  function switchStyle(name) {
    if (!mapRef.current) return;
    setCurrentStyle(name);
    localStorage.setItem("style", name);
    const state = snapshotGameSources();          // capture current overlay data
    mapRef.current.setStyle(STYLES[name]);        // swap basemap
    mapRef.current.once("style.load", () => {
      addGameLayers(mapRef.current, state);       // restore overlays
      // re-add borders from captured state, if present
      if (!mapRef.current.getSource("borders")) {
        mapRef.current.addSource("borders", { type: "geojson", data: state.borders || emptyFC() });
        mapRef.current.addLayer({
          id: "borders-fill", type: "fill", source: "borders",
          paint: {
            "fill-color": ["match", ["get","faction"], "US","#2563eb","RU","#dc2626","#9ca3af"],
            "fill-opacity": ["interpolate", ["linear"], ["get","morale"], 0,0.20, 1,0.55]
          }
        });
        mapRef.current.addLayer({
          id: "borders-outline", type: "line", source: "borders",
          paint: { "line-color":"#fff", "line-width":[ "case", ["boolean",["feature-state","hover"],false], 3.0, 1.5 ] }
        });
      } else {
        mapRef.current.getSource("borders").setData(state.borders || emptyFC());
      }
    });
  }

  function snapshotGameSources() {
    const map = mapRef.current;
    const getData = (id) => (map?.getSource(id) && map.getSource(id)._data) || emptyFC();
    return {
      borders: getData("borders"),
      control: getData("control"),
      // units: getData("units"), a2ad: getData("a2ad"), etc. (add later)
    };
  }

  function addGameLayers(map, state = {}) {
    if (!map.getSource("control")) {
      map.addSource("control", { type: "geojson", data: state.control || emptyFC() });
    }
    if (!map.getLayer("control-fill")) {
      map.addLayer({
        id: "control-fill",
        type: "fill",
        source: "control",
        paint: {
          "fill-color": [
            "match",
            ["get", "faction"],
            "US", "#2563eb",
            "RU", "#dc2626",
            /* else */ "#9ca3af",
          ],
          "fill-opacity": ["interpolate", ["linear"], ["get", "morale"], 0, 0.25, 1, 0.65],
        },
      });
    }
    if (!map.getLayer("control-outline")) {
      map.addLayer({
        id: "control-outline",
        type: "line",
        source: "control",
        paint: { "line-color": "#fff", "line-width": 1.5, "line-blur": 2 },
      });
    }
  }

  const emptyFC = () => ({ type: "FeatureCollection", features: [] });

  function assignFaction(faction) {
    // Apply update locally first
    borderManagerRef.current.applyUpdate(selectedCountry.id, { faction });
    
    // Persist to backend
    fetch(`${API}/borders/${selectedCountry.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ faction })
    }).catch(console.error);
  }

  return (
    <div style={{ height: "100vh", width: "100vw" }}>
      <div id="map" style={{ position: "absolute", inset: 0 }} />

      <div
        style={{
          position: "absolute",
          right: 12,
          top: 12,
          width: 300,
          background: "#fff",
          padding: 12,
          borderRadius: 12,
          boxShadow: "0 8px 20px rgba(0,0,0,.15)",
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 8 }}>Step 0 Controls</div>
        <div style={{ fontSize: 12, color: "#555", marginBottom: 8 }}>{status}</div>

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button onClick={newSession}>New Session</button>
          <button onClick={queueMove} disabled={!sessionId || queued}>
            Queue: Move Fleet NE
          </button>
          <button onClick={commitTurn} disabled={!sessionId}>Commit Turn</button>
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 10 }}>
          <span style={{ fontSize: 12, color: "#555" }}>Basemap:</span>
          <select
            value={currentStyle}
            onChange={(e) => switchStyle(e.target.value)}
            style={{ padding: 6, borderRadius: 8 }}
          >
            {Object.keys(STYLES).map((k) => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>
        </div>

        <div style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
          Goal: click Move → Commit → watch carrier move & headline update.
        </div>

        {selectedCountry && (
          <div style={{marginTop:10, padding:8, border:"1px solid #e5e7eb", borderRadius:8}}>
            <div style={{fontWeight:600}}>{selectedCountry.name} ({selectedCountry.id})</div>
            {selectedCountry.mother_country && (
              <div style={{fontSize:12, color:"#666", marginTop:2}}>
                Territory of: {selectedCountry.mother_country}
              </div>
            )}
            {selectedCountry.description && (
              <div style={{fontSize:11, color:"#888", marginTop:1}}>
                {selectedCountry.description}
              </div>
            )}
            <div style={{display:"flex", gap:6, marginTop:6}}>
              <button onClick={() => assignFaction("US")}>Assign US</button>
              <button onClick={() => assignFaction("RU")}>Assign RU</button>
            </div>
          </div>
        )}
      </div>

      {/* Services Status Panel */}
      <div
        style={{
          position: "absolute",
          left: 12,
          top: 12,
          width: 350,
          background: "#fff",
          padding: 16,
          borderRadius: 12,
          boxShadow: "0 8px 20px rgba(0,0,0,.15)",
          maxHeight: "80vh",
          overflowY: "auto"
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 12, fontSize: 16 }}>
          🚀 Enhanced Services Status
        </div>

        {/* Services Status */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontWeight: 500, marginBottom: 8 }}>Service Status:</div>
          {servicesStatus.loading ? (
            <div style={{ color: "#666", fontSize: 14 }}>Loading services...</div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ 
                  width: 12, 
                  height: 12, 
                  borderRadius: "50%", 
                  backgroundColor: servicesStatus.chatgpt ? "#10b981" : "#ef4444" 
                }}></span>
                <span style={{ fontSize: 14 }}>
                  🤖 OpenAI GPT-4o-mini: {servicesStatus.chatgpt ? "✅ Active" : "❌ Inactive"}
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ 
                  width: 12, 
                  height: 12, 
                  borderRadius: "50%", 
                  backgroundColor: servicesStatus.news ? "#10b981" : "#ef4444" 
                }}></span>
                <span style={{ fontSize: 14 }}>
                  📰 News API: {servicesStatus.news ? "✅ Active" : "❌ Inactive"}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Cost Information */}
        {costInfo && (
          <div style={{ marginBottom: 16, padding: 12, background: "#f8fafc", borderRadius: 8 }}>
            <div style={{ fontWeight: 500, marginBottom: 8 }}>💰 Cost Info:</div>
            <div style={{ fontSize: 12, color: "#666" }}>
              <div>Model: {costInfo.pricing?.model || "N/A"}</div>
              <div>Input: {costInfo.pricing?.input_per_1m_tokens || "N/A"}</div>
              <div>Output: {costInfo.pricing?.output_per_1m_tokens || "N/A"}</div>
              {costInfo.cost_estimates && (
                <div style={{ marginTop: 4 }}>
                  <div>Hourly: {costInfo.cost_estimates.hourly_gameplay}</div>
                  <div>Monthly: {costInfo.cost_estimates.monthly}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Recent News */}
        {recentNews.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontWeight: 500, marginBottom: 8 }}>📰 Recent News:</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {recentNews.map((news, index) => (
                <div key={index} style={{ 
                  padding: 8, 
                  background: "#f8fafc", 
                  borderRadius: 6,
                  fontSize: 12 
                }}>
                  <div style={{ fontWeight: 500, marginBottom: 4 }}>{news.title}</div>
                  <div style={{ color: "#666", fontSize: 11 }}>{news.summary}</div>
                  <div style={{ color: "#888", fontSize: 10, marginTop: 4 }}>
                    Source: {news.source} • {new Date(news.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Analysis */}
        {aiAnalysis && aiAnalysis.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontWeight: 500, marginBottom: 8 }}>🤖 AI Analysis:</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {aiAnalysis.map((event, index) => (
                <div key={index} style={{ 
                  padding: 8, 
                  background: "#f0f9ff", 
                  borderRadius: 6,
                  fontSize: 12 
                }}>
                  <div style={{ fontWeight: 500, marginBottom: 4 }}>{event.title}</div>
                  <div style={{ color: "#666", fontSize: 11 }}>{event.description}</div>
                  <div style={{ color: "#888", fontSize: 10, marginTop: 4 }}>
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Refresh Button */}
        <button 
          onClick={checkServicesStatus}
          style={{
            padding: "8px 16px",
            background: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            fontSize: 12
          }}
        >
          🔄 Refresh Status
        </button>
      </div>

      <div
        id="ticker"
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          background: "#111",
          color: "#fff",
          padding: "10px 14px",
          fontSize: 14,
          display: "flex",
          gap: 16,
          overflow: "auto",
          whiteSpace: "nowrap",
        }}
      >
        {headlines.map((h, i) => (
          <span key={i}>• {h}</span>
        ))}
      </div>
    </div>
  );
}