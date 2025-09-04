import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import BorderManager from "./borderManager";

const API = "http://localhost:8001";
const MAPTILER_KEY = "A4684uteIMrjertm4Tjw";
const STYLES = {
  Main:        `https://api.maptiler.com/maps/landscape/style.json?key=${MAPTILER_KEY}`,
  SatelliteMain:        `https://api.maptiler.com/maps/satellite/style.json?key=${MAPTILER_KEY}`,
  ModernPolitical:          `https://api.maptiler.com/maps/outdoor-v2/style.json?key=${MAPTILER_KEY}`,
  SatellitePolitical:  `https://api.maptiler.com/maps/hybrid/style.json?key=${MAPTILER_KEY}`,
  GreyscalePolitical:            `https://api.maptiler.com/maps/toner-v2/style.json?key=${MAPTILER_KEY}`,
  Landscape:        `https://api.maptiler.com/maps/landscape/style.json?key=${MAPTILER_KEY}`,
  TonerBW:          `https://api.maptiler.com/maps/toner-v2/style.json?key=${MAPTILER_KEY}`,
  SatelliteHybrid:  `https://api.maptiler.com/maps/hybrid/style.json?key=${MAPTILER_KEY}`,
};

export default function App() {
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const wsRef = useRef(null);

  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState("Ready to select your game mode");
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
  const borderManagerRef = useRef(new BorderManager());
  const [showCountrySelection, setShowCountrySelection] = useState(false);
  const [playableCountries, setPlayableCountries] = useState([]);
  const [selectedPlayableCountry, setSelectedPlayableCountry] = useState(null);
  const [countryComparison, setCountryComparison] = useState(null);
  const [gameMode, setGameMode] = useState(null);
  const [currentGameSession, setCurrentGameSession] = useState(null);
  const [currentRound, setCurrentRound] = useState(null);
  const [gamePhase, setGamePhase] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [playerActions, setPlayerActions] = useState([]);
  const [availableActions, setAvailableActions] = useState([]);
  const [roundSummary, setRoundSummary] = useState(null);

  
  // Psychohistory state
  const [psychohistorySimulation, setPsychohistorySimulation] = useState(null);
  const [psychohistoryNews, setPsychohistoryNews] = useState([]);
  const [psychohistoryMapState, setPsychohistoryMapState] = useState(null);
  const [psychohistoryTick, setPsychohistoryTick] = useState(0);
  const [psychohistoryStatus, setPsychohistoryStatus] = useState('idle');
  const [selectedGameMode, setSelectedGameMode] = useState(null);
  const [showMainMenu, setShowMainMenu] = useState(true);
  const [newsLoading, setNewsLoading] = useState(false);
  const [selectedStartDate, setSelectedStartDate] = useState(() => {
    const today = new Date();
    return {
      month: today.getMonth() + 1,
      year: today.getFullYear(),
      usePresent: true
    };
  });

  useEffect(() => {
    const map = new maplibregl.Map({
      container: "map",
      style: STYLES[currentStyle],
      center: [28.0, 35.0],
      zoom: 4.5,
    });
    mapRef.current = map;

    map.on("load", async () => {
      if (map.getLayer("country-label")) {
        map.setLayoutProperty("country-label", "visibility", "none");
      }
      if (map.getLayer("admin-1-boundary")) {
        map.setLayoutProperty("admin-1-boundary", "visibility", "none");
      }

      addGameLayers(map);

      map.addSource("borders", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      await borderManagerRef.current.initialize(map);

      map.addLayer({
        id: "borders-fill",
        type: "fill",
        source: "borders",
        paint: {
          "fill-color": [
            "case",
            ["==", ["get", "faction"], "NATO"], "#2563eb",
            ["==", ["get", "faction"], "NATO_ALIGNED"], "#06b6d4",
            ["==", ["get", "faction"], "RUSSIA_BLOC"], "#dc2626",
            ["==", ["get", "faction"], "CHINA_BLOC"], "#16a34a",
            ["==", ["get", "faction"], "SWING"], "#eab308",
            "#9ca3af"
          ],
          "fill-opacity": [
            "interpolate", ["linear"], ["get", "morale"],
            0, 0.20, 1, 0.55
          ]
        }
      });

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

      const nuclearData = {
        type: "FeatureCollection",
        features: []
      };
      
      map.addSource("nuclear-indicators", { type: "geojson", data: nuclearData });
      map.addLayer({
        id: "nuclear-indicators",
        type: "circle",
        source: "nuclear-indicators",
        layout: {
          "circle-radius": [
            "interpolate", ["linear"], ["get", "nuclear_weapons"],
            0, 4, 100, 6, 1000, 8, 6000, 12
          ],
          "circle-allow-overlap": true,
          "circle-ignore-placement": true
        },
        paint: {
          "circle-color": [
            "match", ["get", "nuclear_status"],
            "confirmed", "#dc2626",
            "estimated", "#16a34a",
            "suspected", "#8b5cf6",
            "#6b7280"
          ],
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 1,
          "circle-opacity": 0.9
        }
      });

      let hoverId = null;
      let tooltip = null;

      const createTooltip = () => {
        const div = document.createElement('div');
        div.className = 'country-tooltip';
        div.style.cssText = `
          position: absolute;
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 12px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          pointer-events: none;
          z-index: 1000;
          max-width: 250px;
          white-space: nowrap;
        `;
        return div;
      };

      map.on("mousemove", "borders-fill", (e) => {
        if (!e.features?.length) return;
        const feature = e.features[0];
        const id = feature.properties.id;
        
        if (hoverId && hoverId !== id) {
          map.setFeatureState({ source: "borders", id: hoverId }, { hover: false });
        }
        hoverId = id;
        map.setFeatureState({ source: "borders", id }, { hover: true });

        if (!tooltip) {
          tooltip = createTooltip();
          document.body.appendChild(tooltip);
        }

        const props = feature.properties;
        let tooltipContent = `<strong>${props.name}</strong><br>`;
        tooltipContent += `Faction: ${props.faction}<br>`;
        tooltipContent += `Alliance: ${props.alliance || 'None'}<br>`;
        tooltipContent += `Morale: ${Math.round(props.morale * 100)}%`;
        
        if (props.nuclear_weapons > 0) {
          const statusText = props.nuclear_status === 'confirmed' ? 'Confirmed' : 
                           props.nuclear_status === 'estimated' ? 'Estimated' : 
                           props.nuclear_status === 'suspected' ? 'Suspected' : 'Unknown';
          tooltipContent += `<br>Nuclear: ${props.nuclear_weapons} warheads (${statusText})`;
        }
        
        if (props.description) {
          tooltipContent += `<br><em>${props.description}</em>`;
        }

        tooltip.innerHTML = tooltipContent;
        tooltip.style.left = e.point.x + 10 + 'px';
        tooltip.style.top = e.point.y - 10 + 'px';
      });

      map.on("mouseleave", "borders-fill", () => {
        if (hoverId) {
          map.setFeatureState({ source: "borders", id: hoverId }, { hover: false });
        }
        hoverId = null;
        if (tooltip) {
          document.body.removeChild(tooltip);
          tooltip = null;
        }
      });

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

      checkServicesStatus();
      
      setTimeout(() => {
        if (borderManagerRef.current) {
          borderManagerRef.current.updateNuclearIndicators();
        }
      }, 1000);
    });

    return () => map.remove();
  }, [currentStyle]);

  // Keyboard event handling for Psychohistory
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (selectedGameMode === 'psychohistory' && psychohistoryStatus === 'ready') {
        if (event.key === 'ArrowRight' || event.key === ' ') {
          event.preventDefault();
          advancePsychohistoryWeek();
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [selectedGameMode, psychohistoryStatus, psychohistorySimulation]);

  function pushHeadline(h) {
    setHeadlines((prev) => [h, ...prev].slice(0, 12));
  }

  function openWS(sid) {
    if (wsRef.current) try { wsRef.current.close(); } catch {}
    const ws = new WebSocket(`ws://localhost:8001/ws/sessions/${sid}`);
    wsRef.current = ws;
    ws.onopen = () => setStatus(`Session ${sid} | WS connected`);
    ws.onmessage = (evt) => {
      const msg = JSON.parse(evt.data);
      if (msg.type === "WORLD_DIFF") {
        const ent = msg.entities.find((e) => e.id === "US-CVN-1");
        if (ent && markerRef.current) {
          const [lon, lat] = ent.delta.pos;
          markerRef.current.setLngLat([lon, lat]);
        }
        (msg.headlines || []).forEach(pushHeadline);
        setStatus(`Session ${sid} | Tick ${msg.tick}`);
        setQueued(false);
      } else if (msg.type === "BORDER_UPDATE") {
        borderManagerRef.current.applyUpdate(msg.country_id, msg.updates);
      }
    };
  }

  function switchStyle(name) {
    if (!mapRef.current) return;
    setCurrentStyle(name);
    localStorage.setItem("style", name);
    const state = snapshotGameSources();
    mapRef.current.setStyle(STYLES[name]);
    mapRef.current.once("style.load", () => {
      addGameLayers(mapRef.current, state);
      if (!mapRef.current.getSource("borders")) {
        mapRef.current.addSource("borders", { type: "geojson", data: state.borders || emptyFC() });
        mapRef.current.addLayer({
          id: "borders-fill", type: "fill", source: "borders",
          paint: {
            "fill-color": [
            "case",
            ["==", ["get", "faction"], "NATO"], "#2563eb",
            ["==", ["get", "faction"], "NATO_ALIGNED"], "#06b6d4",
            ["==", ["get", "faction"], "RUSSIA_BLOC"], "#dc2626",
            ["==", ["get", "faction"], "CHINA_BLOC"], "#16a34a",
            ["==", ["get", "faction"], "SWING"], "#eab308",
            "#9ca3af"
          ],
            "fill-opacity": ["interpolate", ["linear"], ["get","morale"], 0,0.20, 1,0.55]
          }
        });
        mapRef.current.addLayer({
          id: "borders-outline", type: "line", source: "borders",
          paint: { "line-color":"#fff", "line-width":[ "case", ["boolean",["feature-state","hover"],false], 3.0, 1.5 ] }
        });
        
        if (!mapRef.current.getSource("nuclear-indicators")) {
          mapRef.current.addSource("nuclear-indicators", { 
            type: "geojson", 
            data: { type: "FeatureCollection", features: [] } 
          });
        }
        if (!mapRef.current.getLayer("nuclear-indicators")) {
          mapRef.current.addLayer({
            id: "nuclear-indicators",
            type: "circle",
            source: "nuclear-indicators",
            layout: {
              "circle-radius": [
                "interpolate", ["linear"], ["get", "nuclear_weapons"],
                0, 4, 100, 6, 1000, 8, 6000, 12
              ],
              "circle-allow-overlap": true,
              "circle-ignore-placement": true
            },
            paint: {
              "circle-color": [
                "match", ["get", "nuclear_status"],
                "confirmed", "#dc2626",
                "estimated", "#16a34a",
                "suspected", "#8b5cf6",
                "#6b7280"
              ],
              "circle-stroke-color": "#ffffff",
              "circle-stroke-width": 1,
              "circle-opacity": 0.9
            }
          });
        }
        if (borderManagerRef.current) {
          setTimeout(() => borderManagerRef.current.updateNuclearIndicators(), 100);
        }
      } else {
        mapRef.current.getSource("borders").setData(state.borders || emptyFC());
        if (borderManagerRef.current) {
          setTimeout(() => borderManagerRef.current.updateNuclearIndicators(), 100);
        }
      }
    });
  }

  function snapshotGameSources() {
    const map = mapRef.current;
    const getData = (id) => (map?.getSource(id) && map.getSource(id)._data) || emptyFC();
    return {
      borders: getData("borders"),
      control: getData("control"),
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
            "case",
            ["==", ["get", "faction"], "NATO"], "#2563eb",
            ["==", ["get", "faction"], "NATO_ALIGNED"], "#06b6d4",
            ["==", ["get", "faction"], "RUSSIA_BLOC"], "#dc2626",
            ["==", ["get", "faction"], "CHINA_BLOC"], "#16a34a",
            ["==", ["get", "faction"], "SWING"], "#eab308",
            "#9ca3af"
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
    borderManagerRef.current.applyUpdate(selectedCountry.id, { faction });
    
    fetch(`${API}/borders/${selectedCountry.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ faction })
    }).catch(console.error);
  }

  const selectGameMode = (mode) => {
    setSelectedGameMode(mode);
    setShowMainMenu(false);
    
    if (mode === 'psychohistory') {
      // Don't auto-create simulation - wait for user to select date and click start
      setPsychohistoryStatus('idle');
      setStatus("🧠 Psychohistory mode selected - Choose a date and click Start Simulation");
    } else if (mode === 'single_player' || mode === 'multiplayer') {
      setShowCountrySelection(true);
      setGameMode(mode); // Set the game mode immediately when selected from main menu
    }
  };

  // Check services status and fetch data
  const checkServicesStatus = async () => {
    try {
      const healthResponse = await fetch(`${API}/health`);
      if (!healthResponse.ok) {
        throw new Error(`Health check failed: ${healthResponse.status}`);
      }
      const healthData = await healthResponse.json();
      
      const costResponse = await fetch(`${API}/costs`);
      const costData = await costResponse.json();
      
      const servicesAvailable = healthData.chatgpt_available && healthData.world_data_available;
      
      setServicesStatus({
        chatgpt: healthData.chatgpt_available || false,
        news: healthData.world_data_available || false,
        loading: false
      });
      
      setCostInfo(costData);
      
      if (servicesAvailable && healthData.mode === "enhanced") {
        await fetchPlayableCountries();
      } else {
        setPlayableCountries(["US", "CN", "RU", "EU", "IN", "IR", "IL", "KP"]);
      }
    } catch (error) {
      console.error("Error checking services:", error);
      setServicesStatus({
        chatgpt: false,
        news: false,
        loading: false
      });
      setPlayableCountries(["US", "CN", "RU", "EU", "IN", "IR", "IL", "KP"]);
    }
  };


  const fetchPlayableCountries = async () => {
    try {
      const response = await fetch(`${API}/playable-countries`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setPlayableCountries(data);
      
      await fetchCountryComparison();
    } catch (error) {
      console.error("Error fetching playable countries:", error);
      setPlayableCountries({
        countries: ["US", "CN", "RU", "EU", "IN", "IR", "IL", "KP"],
        total: 8,
        categories: {
          major_powers: ["US", "CN", "RU", "EU"],
          rising_powers: ["IN"],
          regional_players: ["IR", "IL", "KP"]
        }
      });
      setCountryComparison(null);
    }
  };

  const fetchCountryComparison = async () => {
    try {
      const response = await fetch(`${API}/playable-countries/compare`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setCountryComparison(data);
    } catch (error) {
      console.warn("Comparison fetch failed, using fallback:", error);
      setCountryComparison(null);
    }
  };

  const selectPlayableCountry = async (countryId) => {
    try {
      const response = await fetch(`${API}/playable-countries/${countryId}/setup`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setSelectedPlayableCountry(data);
    } catch (error) {
      console.error("Error fetching country details:", error);
      
      const fallbackData = {
        country_id: countryId,
        name: countryId === "US" ? "United States" : 
              countryId === "CN" ? "China" : 
              countryId === "RU" ? "Russia" : 
              countryId === "EU" ? "European Union" : 
              countryId === "IN" ? "India" : 
              countryId === "IR" ? "Iran" : 
              countryId === "IL" ? "Israel" : 
              countryId === "KP" ? "North Korea" : countryId,
        type: ["US", "CN", "RU", "EU"].includes(countryId) ? "major_power" : 
               countryId === "IN" ? "rising_power" : "regional_player",
        starting_faction: countryId === "US" ? "US" : 
                         countryId === "CN" ? "CN" : 
                         countryId === "RU" ? "RU" : 
                         countryId === "EU" ? "EU" : "NEUTRAL",
        starting_conditions: {
          morale: countryId === "US" ? 0.8 : 
                  countryId === "CN" ? 0.7 : 
                  countryId === "RU" ? 0.6 : 
                  countryId === "EU" ? 0.7 : 
                  countryId === "IN" ? 0.6 : 
                  countryId === "IR" ? 0.5 : 
                  countryId === "IL" ? 0.7 : 0.4,
          economic_strength: countryId === "US" ? 0.9 : 
                           countryId === "CN" ? 0.8 : 
                           countryId === "RU" ? 0.4 : 
                           countryId === "EU" ? 0.8 : 
                           countryId === "IN" ? 0.6 : 
                           countryId === "IR" ? 0.3 : 
                           countryId === "IL" ? 0.6 : 0.2,
          military_strength: countryId === "US" ? 0.9 : 
                           countryId === "CN" ? 0.7 : 
                           countryId === "RU" ? 0.8 : 
                           countryId === "EU" ? 0.6 : 
                           countryId === "IN" ? 0.5 : 
                           countryId === "IR" ? 0.4 : 
                           countryId === "IL" ? 0.7 : 0.6,
          diplomatic_influence: countryId === "US" ? 0.8 : 
                              countryId === "CN" ? 0.6 : 
                              countryId === "RU" ? 0.5 : 
                              countryId === "EU" ? 0.7 : 
                              countryId === "IN" ? 0.4 : 
                              countryId === "IR" ? 0.3 : 
                              countryId === "IL" ? 0.4 : 0.2
        },
        special_abilities: ["Global Power Projection", "Advanced Technology", "Strong Alliances"],
        starting_units: ["UNIT-1", "UNIT-2"],
        starting_bases: ["BASE-1"],
        starting_allies: [],
        starting_enemies: [],
        victory_conditions: ["Achieve global dominance", "Maintain alliances", "Economic leadership"],
        unique_challenges: ["High expectations", "Complex commitments", "Public opinion"],
        description: "A powerful nation with significant global influence and military capabilities.",
        playstyle_tips: ["Use your global reach", "Leverage alliances", "Maintain superiority"]
      };
      setSelectedPlayableCountry(fallbackData);
    }
  };

  const startGameWithCountry = async (countryId) => {
    try {
      const response = await fetch(`${API}/playable-countries/${countryId}/start-game`, {
        method: "POST"
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      setSessionId(data.session_id);
      setStatus(`Playing as ${data.country_name || countryId} | Session ${data.session_id}`);
      setShowCountrySelection(false);
      
      openWS(data.session_id);
      pushHeadline(`Game started! You are now playing as ${data.country_name || countryId}.`);
      
    } catch (error) {
      console.error("Error starting game with country:", error);
      
      const fallbackSessionId = `fallback-${Date.now()}`;
      setSessionId(fallbackSessionId);
      setStatus(`Playing as ${countryId} | Fallback Session`);
      setShowCountrySelection(false);
      
      const basicSession = {
        session_id: fallbackSessionId,
        selected_country: countryId,
        tick: 0,
        units: [{ id: "US-CVN-1", pos: [28.0, 35.0] }]
      };
      
      if (!SESSIONS) window.SESSIONS = {};
      window.SESSIONS[fallbackSessionId] = basicSession;
      
      pushHeadline(`Fallback game started! You are now playing as ${countryId}.`);
    }
  };

  const createGameSession = async (mode, countryId) => {
    try {
      const response = await fetch(`${API}/game/create-session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          game_mode: mode,
          host_country: countryId,
          round_duration_minutes: 5,
          max_players: mode === "single_player" ? 1 : 8
        })
      });
      
      const data = await response.json();
      setCurrentGameSession(data);
      setGameMode(mode);
      setStatus(`Game session created! Mode: ${mode}, Country: ${countryId}`);
      
      return data.session_id;
    } catch (error) {
      console.error("Error creating game session:", error);
      pushHeadline("Error creating game session. Please try again.");
    }
  };

  const startRoundBasedGame = async () => {
    await createGameSession(gameMode, selectedPlayableCountry.country_id);
      setShowCountrySelection(false);
  };

  const startGameStatusPolling = (sessionId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API}/game/${sessionId}/status`);
        const data = await response.json();
        
        setCurrentRound(data.round_number);
        setGamePhase(data.phase);
        setTimeRemaining(data.time_remaining);
        setRoundSummary(data.round_summary);
        
        if (data.phase === "finished") {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error("Error polling game status:", error);
      }
    }, 1000);
    
    window.gameStatusPolling = pollInterval;
  };

  const submitAction = async (actionType, targetCountry = null, parameters = {}, isSecret = false) => {
    if (!currentGameSession || !selectedPlayableCountry) return;
    
    try {
      const response = await fetch(`${API}/game/${currentGameSession.session_id}/actions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player_country: selectedPlayableCountry.country_id,
          action_type: actionType,
          target_country: targetCountry,
          parameters: parameters,
          is_secret: isSecret
        })
      });
      
      const data = await response.json();
      
      if (data.status === "submitted") {
        pushHeadline(`Action submitted: ${actionType}${targetCountry ? ` targeting ${targetCountry}` : ''}`);
        setPlayerActions(prev => [...prev, data]);
      } else {
        pushHeadline(`Action failed: ${data.message}`);
      }
    } catch (error) {
      console.error("Error submitting action:", error);
      pushHeadline("Error submitting action. Please try again.");
    }
  };

  const formatTimeRemaining = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };



  const createPsychohistorySimulation = async () => {
    try {
      setPsychohistoryStatus('creating');
      setNewsLoading(true);
      setStatus("🧠 Creating World Brain simulation...");
      
      const response = await fetch(`${API}/worldbrain/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          seed: Math.floor(Math.random() * 1000000),
          start_month: selectedStartDate.month,
          start_year: selectedStartDate.year,
          use_present: selectedStartDate.usePresent
        })
      });

      if (response.ok) {
        const data = await response.json();
        setPsychohistorySimulation(data);
        setPsychohistoryMapState(data.map_state);
        setPsychohistoryNews(data.news || []);
        setPsychohistoryTick(1);
        setPsychohistoryStatus('running');
        setNewsLoading(false);
        
        const dateStr = selectedStartDate.usePresent ? "Present" : `${selectedStartDate.month}/${selectedStartDate.year}`;
        setStatus(`🧠 World Brain simulation started: ${dateStr}`);
        
        // Start automatic ticking
        startPsychohistoryTicking(data.id);
      } else {
        console.error('Failed to create psychohistory simulation');
        setPsychohistoryStatus('error');
        setNewsLoading(false);
        setStatus("❌ Failed to start World Brain simulation");
      }
    } catch (error) {
      console.error('Error creating psychohistory simulation:', error);
      setPsychohistoryStatus('error');
      setNewsLoading(false);
      setStatus("❌ Failed to start World Brain simulation");
    }
  };

  const startPsychohistoryTicking = async (simulationId) => {
    // Don't auto-tick - let user control the pace
    setPsychohistoryStatus('ready');
    setStatus("🧠 World Brain ready - Use arrow keys to advance weeks");
  };

  const advancePsychohistoryWeek = async () => {
    if (!psychohistorySimulation || psychohistoryStatus !== 'ready') return;
    
    try {
      setPsychohistoryStatus('processing');
      setStatus("🧠 Processing next week...");
      
      const response = await fetch(`${API}/worldbrain/${psychohistorySimulation.id}/tick`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPsychohistoryNews(prev => [...prev, ...data.news]);
        setPsychohistoryMapState(data.map_state);
        setPsychohistoryTick(prev => prev + 1);
        
        // Update the simulation object with new date
        setPsychohistorySimulation(prev => ({
          ...prev,
          current_date: data.current_date
        }));
        
        // Update status with current world state
        const tension = data.map_state.global_tension || 0;
        const activeConflicts = data.map_state.active_conflicts?.length || 0;
        
        const currentDate = data.current_date || "Current Date";
        setStatus(`🧠 ${currentDate} - Global Tension: ${tension}% | Active Conflicts: ${activeConflicts}`);
        
        setPsychohistoryStatus('ready');
      } else {
        console.error('Failed to tick psychohistory simulation');
        setPsychohistoryStatus('error');
        setStatus("❌ World Brain simulation error");
      }
    } catch (error) {
      console.error('Error ticking psychohistory simulation:', error);
      setPsychohistoryStatus('error');
      setStatus("❌ World Brain simulation error");
    }
  };



  const returnToMainMenu = () => {
    setSelectedGameMode(null);
    setShowMainMenu(true);
    setShowCountrySelection(false);
    setCurrentGameSession(null);
    setPsychohistorySimulation(null);
    setPsychohistoryNews([]);
    setPsychohistoryMapState(null);
    setPsychohistoryTick(0);
    setPsychohistoryStatus('idle');
    setStatus("Ready to select your game mode");
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f172a' }}>
      {/* Map Container - Always visible */}
      <div style={{ flex: 1, position: 'relative' }}>
        <div id="map" style={{ position: "absolute", inset: 0 }} />
      
        {/* Main Menu Overlay - Only when showMainMenu is true */}
        {showMainMenu && (
        <div style={{
            position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
            background: 'rgba(15, 23, 42, 0.85)',
            backdropFilter: 'blur(8px)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
            zIndex: 1000,
          padding: '20px'
        }}>
          <div style={{
            textAlign: 'center',
            marginBottom: '60px'
          }}>
            <h1 style={{
              fontSize: '3.5rem',
              fontWeight: 'bold',
              color: '#f8fafc',
              margin: 0,
              textShadow: '0 4px 8px rgba(0,0,0,0.3)',
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              WWIII Simulator
            </h1>
            <p style={{
              fontSize: '1.2rem',
              color: '#94a3b8',
              marginTop: '10px',
              maxWidth: '600px'
            }}>
              Experience the future of global conflict through predictive history, AI analysis, and strategic gameplay
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '30px',
            maxWidth: '1000px',
            width: '100%'
          }}>
            <div 
              onClick={() => selectGameMode('psychohistory')}
              style={{
                background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
                border: '2px solid #f59e0b',
                borderRadius: '16px',
                padding: '30px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 8px 32px rgba(245, 158, 11, 0.2)',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-8px)';
                e.target.style.boxShadow = '0 16px 48px rgba(245, 158, 11, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 8px 32px rgba(245, 158, 11, 0.2)';
              }}
            >
              <div style={{ fontSize: '3rem', marginBottom: '20px' }}>🧠</div>
              <h2 style={{
                fontSize: '1.8rem',
                fontWeight: 'bold',
                color: '#f8fafc',
                margin: '0 0 15px 0'
              }}>
                Psychohistory
              </h2>
              <p style={{
                color: '#cbd5e1',
                lineHeight: '1.6',
                margin: '0 0 20px 0'
              }}>
                The World Brain - Automated predictive simulation using real news, historical patterns, and AI analysis. 
                Watch as the simulation unfolds without player interference.
              </p>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                color: '#fbbf24',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}>
                <span>Witness the World Brain →</span>
              </div>
            </div>

            <div 
              onClick={() => selectGameMode('single_player')}
              style={{
                background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
                border: '2px solid #3b82f6',
                borderRadius: '16px',
                padding: '30px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 8px 32px rgba(59, 130, 246, 0.2)',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-8px)';
                e.target.style.boxShadow = '0 16px 48px rgba(59, 130, 246, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 8px 32px rgba(59, 130, 246, 0.2)';
              }}
            >
              <div style={{ fontSize: '3rem', marginBottom: '20px' }}>🎮</div>
              <h2 style={{
                fontSize: '1.8rem',
                fontWeight: 'bold',
                color: '#f8fafc',
                margin: '0 0 15px 0'
              }}>
                Single Player
              </h2>
              <p style={{
                color: '#cbd5e1',
                lineHeight: '1.6',
                margin: '0 0 20px 0'
              }}>
                Command one of 8 major powers in a world where AI controls all other nations. 
                Make strategic decisions and shape the course of history.
              </p>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                color: '#60a5fa',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}>
                <span>Choose your nation →</span>
              </div>
            </div>

            <div 
              onClick={() => selectGameMode('multiplayer')}
              style={{
                background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
                border: '2px solid #10b981',
                borderRadius: '16px',
                padding: '30px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 8px 32px rgba(16, 185, 129, 0.2)',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-8px)';
                e.target.style.boxShadow = '0 16px 48px rgba(16, 185, 129, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 8px 32px rgba(16, 185, 129, 0.2)';
              }}
            >
              <div style={{ fontSize: '3rem', marginBottom: '20px' }}>👥</div>
              <h2 style={{
                fontSize: '1.8rem',
                fontWeight: 'bold',
                color: '#f8fafc',
                margin: '0 0 15px 0'
              }}>
                Multiplayer
              </h2>
              <p style={{
                color: '#cbd5e1',
                lineHeight: '1.6',
                margin: '0 0 20px 0'
              }}>
                Compete with 2-8 players in simultaneous decision-making rounds. 
                Hidden actions are revealed at round end - like Werewolf or Mafia.
              </p>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                color: '#34d399',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}>
                <span>Join the battle →</span>
              </div>
            </div>


          </div>

          <div style={{
            marginTop: '60px',
            textAlign: 'center',
            color: '#64748b',
            fontSize: '0.9rem'
          }}>
            <p>Powered by Predictive History, ChatGPT AI, and Real-time Geopolitical Analysis</p>
          </div>
        </div>
        )}
        
        {/* Game Interface - Always visible when not in main menu */}
        {!showMainMenu && (
        <>
            <button
              onClick={returnToMainMenu}
              style={{
                position: 'absolute',
                top: '20px',
                left: '20px',
                zIndex: 1000,
                background: 'rgba(15, 23, 42, 0.9)',
                border: '1px solid #475569',
                borderRadius: '8px',
                padding: '10px 16px',
                color: '#f8fafc',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                backdropFilter: 'blur(10px)',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(30, 41, 59, 0.95)';
                e.target.style.borderColor = '#64748b';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(15, 23, 42, 0.9)';
                e.target.style.borderColor = '#475569';
              }}
            >
              ← Back to Menu
            </button>

            <div
              style={{
                position: "absolute",
                left: 12,
                top: 12,
                width: 350,
                background: "#000",
                color: "#fff",
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

              {costInfo && (
                <div style={{ marginBottom: 16, padding: 12, background: "#111", borderRadius: 8 }}>
                  <div style={{ fontWeight: 500, marginBottom: 8 }}>💰 Cost Info:</div>
                  <div style={{ fontSize: 12, color: "#ccc" }}>
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

            {currentGameSession && (
              <div style={{
                position: "absolute",
                left: 12,
                bottom: 80,
                width: 400,
                background: "#000",
                color: "#fff",
                padding: 16,
                borderRadius: 12,
                boxShadow: "0 8px 20px rgba(0,0,0,.15)",
                border: "2px solid #333"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <h3 style={{ margin: 0, fontSize: 18 }}>🎮 Round-Based Game</h3>
                  <div style={{ fontSize: 12, color: "#999" }}>
                    {gameMode === "single_player" ? "Single Player" : "Multiplayer"}
                  </div>
                </div>
                
                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <span style={{ fontSize: 14, color: "#ccc" }}>Round {currentRound}</span>
                    <span style={{ 
                      fontSize: 14, 
                      color: gamePhase === "planning" ? "#10b981" : "#f59e0b",
                      fontWeight: 600 
                    }}>
                      {gamePhase === "planning" ? "⏰ Planning Phase" : "🔄 Resolution"}
                    </span>
                  </div>
                  
                  {gamePhase === "planning" && (
                    <div style={{ 
                      background: "#1f2937", 
                      padding: 8, 
                      borderRadius: 6, 
                      textAlign: "center",
                      marginBottom: 12
                    }}>
                      <div style={{ fontSize: 20, fontWeight: 600, color: "#10b981" }}>
                        {formatTimeRemaining(timeRemaining)}
                      </div>
                      <div style={{ fontSize: 12, color: "#999" }}>Time Remaining</div>
                    </div>
                  )}
                </div>
                
                {gamePhase === "planning" && (
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 14, color: "#ccc", marginBottom: 8 }}>Available Actions:</div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                      <button 
                        onClick={() => submitAction("form_alliance", "CN")}
                        style={{ 
                          padding: "8px 12px", 
                          background: "#3b82f6", 
                          border: "none", 
                          color: "white", 
                          borderRadius: 6, 
                          cursor: "pointer",
                          fontSize: 12
                        }}
                      >
                        🤝 Form Alliance
                      </button>
                      <button 
                        onClick={() => submitAction("declare_war", "RU")}
                        style={{ 
                          padding: "8px 12px", 
                          background: "#dc2626", 
                          border: "none", 
                          color: "white", 
                          borderRadius: 6, 
                          cursor: "pointer",
                          fontSize: 12
                        }}
                      >
                        ⚔️ Declare War
                      </button>
                      <button 
                        onClick={() => submitAction("invest_in_economy")}
                        style={{ 
                          padding: "8px 12px", 
                          background: "#10b981", 
                          border: "none", 
                          color: "white", 
                          borderRadius: 6, 
                          cursor: "pointer",
                          fontSize: 12
                        }}
                      >
                        💰 Invest Economy
                      </button>
                      <button 
                        onClick={() => submitAction("build_military")}
                        style={{ 
                          padding: "8px 12px", 
                          background: "#8b5cf6", 
                          border: "none", 
                          color: "white", 
                          borderRadius: 6, 
                          cursor: "pointer",
                          fontSize: 12
                        }}
                      >
                        🛡️ Build Military
                      </button>
                    </div>
                  </div>
                )}
                
                {roundSummary && (
                  <div style={{ 
                    background: "#1f2937", 
                    padding: 12, 
                    borderRadius: 8, 
                    fontSize: 12,
                    color: "#ccc"
                  }}>
                    <div style={{ fontWeight: 600, marginBottom: 4, color: "#fbbf24" }}>Round Summary:</div>
                    <div>{roundSummary}</div>
                  </div>
                )}
                
                {playerActions.length > 0 && (
                  <div style={{ marginTop: 12 }}>
                    <div style={{ fontSize: 12, color: "#999", marginBottom: 4 }}>Your Actions:</div>
                    {playerActions.map((action, index) => (
                      <div key={index} style={{ 
                        fontSize: 11, 
                        color: "#ccc", 
                        padding: "4px 8px", 
                        background: "#111", 
                        borderRadius: 4,
                        marginBottom: 2
                      }}>
                        ✓ {action.message}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {selectedGameMode === 'psychohistory' && (
              <div style={{
                position: "absolute",
                right: 12,
                top: 12,
                width: 450,
                background: "#000",
                color: "#fff",
                padding: 16,
                borderRadius: 12,
                boxShadow: "0 8px 20px rgba(0,0,0,.15)",
                border: "2px solid #f59e0b",
                maxHeight: "80vh",
                overflowY: "auto"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <h3 style={{ margin: 0, fontSize: 18 }}>🧠 Psychohistory</h3>
                  <div style={{ fontSize: 12, color: "#999" }}>
                    World Brain Simulation
                  </div>
                </div>
                
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 14, color: "#ccc", marginBottom: 8 }}>
                    🗓️ Start Date
                  </div>
                  
                  {/* Use Present Date Checkbox */}
                  <label style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    marginBottom: 12, 
                    cursor: "pointer",
                    fontSize: 12,
                    color: "#ccc",
                    gap: 8
                  }}>
                    <input
                      type="checkbox"
                      checked={selectedStartDate.usePresent}
                      onChange={(e) => {
                        if (e.target.checked) {
                          const today = new Date();
                          setSelectedStartDate({
                            month: today.getMonth() + 1,
                            year: today.getFullYear(),
                            usePresent: true
                          });
                        } else {
                          setSelectedStartDate(prev => ({ ...prev, usePresent: false }));
                        }
                      }}
                      style={{
                        accentColor: "#f59e0b",
                        transform: "scale(1.2)"
                      }}
                    />
                    🔄 Use Present Date (World Brain)
                  </label>
                  
                  {/* Historical Date Selection */}
                  {!selectedStartDate.usePresent && (
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ fontSize: 12, color: "#999", marginBottom: 8 }}>
                        Select historical date for news simulation:
                      </div>
                      <div style={{ display: "flex", gap: 8 }}>
                        <select 
                          value={selectedStartDate.month}
                          onChange={(e) => setSelectedStartDate(prev => ({ ...prev, month: parseInt(e.target.value) }))}
                          style={{
                            background: "#374151",
                            color: "#fff",
                            border: "1px solid #4b5563",
                            borderRadius: 4,
                            padding: "6px 8px",
                            fontSize: 12,
                            flex: 1
                          }}
                        >
                          {Array.from({length: 12}, (_, i) => i + 1).map(month => (
                            <option key={month} value={month}>
                              {new Date(2000, month-1).toLocaleString('default', { month: 'long' })}
                            </option>
                          ))}
                        </select>
                        
                        <select 
                          value={selectedStartDate.year}
                          onChange={(e) => setSelectedStartDate(prev => ({ ...prev, year: parseInt(e.target.value) }))}
                          style={{
                            background: "#374151",
                            color: "#fff",
                            border: "1px solid #4b5563",
                            borderRadius: 4,
                            padding: "6px 8px",
                            fontSize: 12,
                            flex: 1
                          }}
                        >
                          {Array.from({length: new Date().getFullYear() - 1900 + 1}, (_, i) => new Date().getFullYear() - i).map(year => (
                            <option key={year} value={year}>
                              {year}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  )}

                  {!psychohistorySimulation ? (
                    <button
                      onClick={createPsychohistorySimulation}
                      disabled={psychohistoryStatus === 'creating'}
                      style={{
                        background: psychohistoryStatus === 'creating' ? "#6b7280" : "#f59e0b",
                        color: psychohistoryStatus === 'creating' ? "#ccc" : "#000",
                        border: "none",
                        padding: "10px 16px",
                        borderRadius: 6,
                        cursor: psychohistoryStatus === 'creating' ? "not-allowed" : "pointer",
                        fontSize: 12,
                        fontWeight: 600,
                        width: "100%",
                        marginBottom: 12
                      }}
                    >
                      {psychohistoryStatus === 'creating' ? "🔄 Creating..." : "🚀 Start Simulation"}
                    </button>
                  ) : (
                    <>
                      <div style={{ fontSize: 14, color: "#ccc", marginBottom: 8 }}>
                        Simulation ID: {psychohistorySimulation.id?.slice(0, 8)}...
                      </div>
                      <div style={{ fontSize: 12, color: "#999", marginBottom: 4 }}>
                        Status: {psychohistoryStatus}
                      </div>
                      <div style={{ fontSize: 12, color: "#999", marginBottom: 4 }}>
                        Week: {psychohistoryTick}
                      </div>
                      {psychohistorySimulation.current_date && (
                        <div style={{ fontSize: 11, color: "#888" }}>
                          Date: {new Date(psychohistorySimulation.current_date).toLocaleDateString('en-US', { 
                            year: 'numeric', 
                            month: 'short', 
                            day: 'numeric' 
                          })}
                        </div>
                      )}
                    </>
                  )}
                </div>
                
                {/* Controls */}
                {psychohistorySimulation && (
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 14, color: "#ccc", marginBottom: 8 }}>
                      🎮 Controls
                    </div>
                    <div style={{ fontSize: 11, color: "#999", marginBottom: 8 }}>
                      Press → or SPACE to advance one week
                    </div>
                    <button
                      onClick={advancePsychohistoryWeek}
                      disabled={psychohistoryStatus !== 'ready'}
                      style={{
                        background: psychohistoryStatus === 'ready' ? '#f59e0b' : '#666',
                        color: '#000',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        cursor: psychohistoryStatus === 'ready' ? 'pointer' : 'not-allowed',
                        fontSize: '12px',
                        fontWeight: '600',
                        width: '100%'
                      }}
                    >
                      {psychohistoryStatus === 'ready' ? '⏭️ Advance Week' : 
                       psychohistoryStatus === 'processing' ? '⏳ Processing...' : 
                       psychohistoryStatus === 'completed' ? '✅ Completed' : '❌ Error'}
                    </button>
                  </div>
                )}



                {/* Latest News */}
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 14, color: "#ccc", marginBottom: 8 }}>
                    📰 Latest News {psychohistoryNews.length > 0 && `(${psychohistoryNews.length})`}
                  </div>
                  {newsLoading ? (
                    <div style={{ 
                      padding: 10,
                      background: "#1f2937",
                      borderRadius: 8,
                      marginBottom: 8,
                      fontSize: 11,
                      borderLeft: "3px solid #f59e0b",
                      textAlign: "center",
                      color: "#999"
                    }}>
                      ⏳ Loading news articles...
                    </div>
                  ) : psychohistoryNews.length > 0 ? (
                    <div style={{ maxHeight: "300px", overflowY: "auto" }}>
                      {psychohistoryNews.slice(-5).map((article, index) => (
                        <div key={index} style={{
                          padding: 10,
                          background: "#1f2937",
                          borderRadius: 8,
                          marginBottom: 8,
                          fontSize: 11,
                          borderLeft: "3px solid #f59e0b",
                          cursor: "pointer",
                          transition: "all 0.2s ease"
                        }}
                        onMouseEnter={(e) => e.target.style.background = "#374151"}
                        onMouseLeave={(e) => e.target.style.background = "#1f2937"}
                        onClick={() => {
                          // Show full article in a modal or expand
                          const statChanges = article.stat_changes ? `\n\nStat Changes: ${JSON.stringify(article.stat_changes, null, 2)}` : '';
                          alert(`${article.title}\n\n${article.content}\n\nSource: ${article.source}\nReliability: ${article.reliability}${statChanges}`);
                        }}>
                          <div style={{ fontWeight: 600, color: "#fbbf24", marginBottom: 4, fontSize: 12 }}>
                            {article.title}
                          </div>
                          <div style={{ color: "#ccc", marginBottom: 4, fontSize: 10, lineHeight: 1.3 }}>
                            {article.content.length > 120 ? article.content.substring(0, 120) + "..." : article.content}
                          </div>
                          <div style={{ fontSize: 9, color: "#999", display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span>{new Date(article.timestamp).toLocaleDateString()}</span>
                            <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
                              <span style={{ 
                                background: article.category === 'diplomatic' ? '#3b82f6' : 
                                          article.category === 'military' ? '#ef4444' : 
                                          article.category === 'economic' ? '#10b981' : 
                                          article.category === 'cyber' ? '#8b5cf6' : '#6b7280',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                fontSize: 8,
                                fontWeight: '600'
                              }}>
                                {article.category}
                              </span>
                              <span style={{ 
                                background: article.severity === 'high' ? '#ef4444' : article.severity === 'medium' ? '#f59e0b' : '#10b981',
                                padding: '1px 4px',
                                borderRadius: '3px',
                                fontSize: 7
                              }}>
                                {article.severity.toUpperCase()}
                              </span>
                            </div>
                          </div>
                          <div style={{ fontSize: 8, color: "#666", marginTop: 4, fontStyle: 'italic' }}>
                            Click to read full article • Source: {article.source}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : !psychohistorySimulation ? (
                    <div style={{ 
                      padding: 10,
                      background: "#1f2937",
                      borderRadius: 8,
                      marginBottom: 8,
                      fontSize: 11,
                      borderLeft: "3px solid #f59e0b",
                      textAlign: "center",
                      color: "#999"
                    }}>
                      Select a start date and click "Start Simulation" to begin
                    </div>
                  ) : (
                    <div style={{ 
                      padding: 10,
                      background: "#1f2937",
                      borderRadius: 8,
                      marginBottom: 8,
                      fontSize: 11,
                      borderLeft: "3px solid #10b981",
                      textAlign: "center",
                      color: "#999"
                    }}>
                      No news articles generated yet. Use controls to advance the simulation.
                    </div>
                  )}
                </div>

                {/* World State Summary */}
                {psychohistoryMapState && psychohistoryMapState.countries && (
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 14, color: "#ccc", marginBottom: 8 }}>
                      🌍 World Summary
                    </div>
                    <div style={{ fontSize: 11, color: "#ccc" }}>
                      <div style={{ marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
                        <span>Total Countries:</span>
                        <span style={{ color: '#10b981' }}>
                          {Object.keys(psychohistoryMapState.countries).length}
                        </span>
                      </div>
                      <div style={{ marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
                        <span>Western Bloc:</span>
                        <span style={{ color: '#3b82f6' }}>
                          {Object.values(psychohistoryMapState.countries).filter(c => c.bloc === 'Western').length}
                        </span>
                      </div>
                      <div style={{ marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
                        <span>Eastern Bloc:</span>
                        <span style={{ color: '#ef4444' }}>
                          {Object.values(psychohistoryMapState.countries).filter(c => c.bloc === 'Eastern').length}
                        </span>
                      </div>
                      <div style={{ marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
                        <span>Non-Aligned:</span>
                        <span style={{ color: '#f59e0b' }}>
                          {Object.values(psychohistoryMapState.countries).filter(c => c.bloc === 'Non-Aligned').length}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
                
                
                {/* Instructions */}
                <div style={{ fontSize: 11, color: "#666", lineHeight: 1.4 }}>
                    <div style={{ marginBottom: 4 }}>
                    🧠 Watch the World Brain make decisions based on:
                  </div>
                  <div style={{ marginBottom: 2 }}>• Real-time news analysis</div>
                  <div style={{ marginBottom: 2 }}>• Historical patterns</div>
                  <div style={{ marginBottom: 2 }}>• Country doctrines & objectives</div>
                  <div>• Sociological factors</div>
                </div>
              </div>
            )}
                


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

            {showCountrySelection && (
              <div style={{
                position: "fixed",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: "rgba(0,0,0,0.8)",
                zIndex: 1000,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: 20
              }}>
                <div style={{
                  background: "#000",
                  color: "#fff",
                  padding: 24,
                  borderRadius: 12,
                  maxWidth: 1200,
                  maxHeight: "90vh",
                  overflowY: "auto",
                  border: "2px solid #333"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                    <h2 style={{ margin: 0, fontSize: 24 }}>🎮 Select Your Country</h2>
                    <button 
                      onClick={() => setShowCountrySelection(false)}
                      style={{ background: "#dc2626", border: "none", color: "white", padding: "8px 16px", borderRadius: 6, cursor: "pointer" }}
                    >
                      ✕ Close
                    </button>
                  </div>

                  <div style={{ marginBottom: 20, fontSize: 14, color: "#ccc" }}>
                    Choose from 8 unique playable countries, each with distinct strengths, challenges, and victory conditions.
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 20 }}>
                    {["US", "CN", "RU", "EU", "IN", "IR", "IL", "KP"].map(countryId => (
                      <div key={countryId} style={{ 
                        padding: 16, 
                        border: "1px solid #333", 
                        borderRadius: 8,
                        cursor: "pointer",
                        background: selectedPlayableCountry?.country_id === countryId ? "#1f2937" : "#111",
                        transition: "all 0.2s"
                      }} onClick={() => selectPlayableCountry(countryId)}>
                        <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 4 }}>
                          {countryId === "US" ? "🇺🇸 United States" :
                           countryId === "CN" ? "🇨🇳 China" :
                           countryId === "RU" ? "🇷🇺 Russia" :
                           countryId === "EU" ? "🇪🇺 European Union" :
                           countryId === "IN" ? "🇮🇳 India" :
                           countryId === "IR" ? "🇮🇷 Iran" :
                           countryId === "IL" ? "🇮🇱 Israel" :
                           countryId === "KP" ? "🇰🇵 North Korea" : countryId}
                        </div>
                        <div style={{ fontSize: 12, color: "#999", marginBottom: 8 }}>
                          {["US", "CN", "RU", "EU"].includes(countryId) ? "🏛️ Major Power" :
                           countryId === "IN" ? "📈 Rising Power" : "⚔️ Regional Player"}
                        </div>
                        <div style={{ fontSize: 11, color: "#666" }}>
                          {countryId === "US" ? "Global Superpower" :
                           countryId === "CN" ? "Rising Challenger" :
                           countryId === "RU" ? "Resurgent Power" :
                           countryId === "EU" ? "Economic Union" :
                           countryId === "IN" ? "Non-Aligned Rising Power" :
                           countryId === "IR" ? "Proxy Warfare Master" :
                           countryId === "IL" ? "Tech-Savvy Defender" :
                           countryId === "KP" ? "Nuclear Brinkmanship" : ""}
                        </div>
                      </div>
                    ))}
                  </div>

                  {selectedPlayableCountry && (
                    <div style={{ border: "1px solid #333", borderRadius: 8, padding: 16, marginBottom: 20 }}>
                      <h3 style={{ margin: "0 0 12px 0", color: "#fbbf24" }}>
                        {selectedPlayableCountry.name} - {selectedPlayableCountry.type?.replace('_', ' ').toUpperCase() || 'PLAYABLE'}
                      </h3>
                      
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 16 }}>
                        
                        <div>
                          <h4 style={{ margin: "0 0 8px 0", color: "#3b82f6" }}>Overview</h4>
                          <div style={{ fontSize: 12, color: "#ccc", marginBottom: 8 }}>
                            {selectedPlayableCountry.description || "A powerful nation with significant global influence and military capabilities."}
                          </div>
                          <div style={{ fontSize: 11, color: "#999" }}>
                            <strong>Starting Faction:</strong> {selectedPlayableCountry.starting_faction || "NEUTRAL"}
                          </div>
                        </div>

                        <div>
                          <h4 style={{ margin: "0 0 8px 0", color: "#10b981" }}>Starting Conditions</h4>
                          <div style={{ fontSize: 11, color: "#ccc" }}>
                            <div>Morale: {Math.round((selectedPlayableCountry.starting_conditions?.morale || 0.5) * 100)}%</div>
                            <div>Economic: {Math.round((selectedPlayableCountry.starting_conditions?.economic_strength || 0.5) * 100)}%</div>
                            <div>Military: {Math.round((selectedPlayableCountry.starting_conditions?.military_strength || 0.5) * 100)}%</div>
                            <div>Diplomatic: {Math.round((selectedPlayableCountry.starting_conditions?.diplomatic_influence || 0.5) * 100)}%</div>
                          </div>
                        </div>

                        <div>
                          <h4 style={{ margin: "0 0 8px 0", color: "#8b5cf6" }}>Special Abilities</h4>
                          <div style={{ fontSize: 11, color: "#ccc" }}>
                            {(selectedPlayableCountry.special_abilities || ["Global Power Projection", "Advanced Technology", "Strong Alliances"]).map((ability, index) => (
                              <div key={index} style={{ marginBottom: 2 }}>• {ability}</div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h4 style={{ margin: "0 0 8px 0", color: "#f59e0b" }}>Victory Conditions</h4>
                          <div style={{ fontSize: 11, color: "#ccc" }}>
                            {(selectedPlayableCountry.victory_conditions || ["Achieve global dominance", "Maintain alliances", "Economic leadership"]).map((condition, index) => (
                              <div key={index} style={{ marginBottom: 2 }}>• {condition}</div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h4 style={{ margin: "0 0 8px 0", color: "#ef4444" }}>Unique Challenges</h4>
                          <div style={{ fontSize: 11, color: "#ccc" }}>
                            {(selectedPlayableCountry.unique_challenges || ["High expectations", "Complex commitments", "Public opinion"]).map((challenge, index) => (
                              <div key={index} style={{ marginBottom: 2 }}>• {challenge}</div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h4 style={{ margin: "0 0 8px 0", color: "#06b6d4" }}>Playstyle Tips</h4>
                          <div style={{ fontSize: 11, color: "#ccc" }}>
                            {(selectedPlayableCountry.playstyle_tips || ["Use your global reach", "Leverage alliances", "Maintain superiority"]).map((tip, index) => (
                              <div key={index} style={{ marginBottom: 2 }}>• {tip}</div>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div style={{ marginTop: 16, textAlign: "center" }}>
                        <div style={{ 
                          marginBottom: 16, 
                          padding: "12px 16px", 
                          background: gameMode === "single_player" ? "rgba(59, 130, 246, 0.1)" : "rgba(16, 185, 129, 0.1)", 
                          border: `1px solid ${gameMode === "single_player" ? "#3b82f6" : "#10b981"}`, 
                          borderRadius: 8,
                          color: gameMode === "single_player" ? "#60a5fa" : "#34d399"
                        }}>
                          <div style={{ fontWeight: 600, marginBottom: 4 }}>
                            {gameMode === "single_player" ? "🎮 Single Player Mode" : "👥 Multiplayer Mode"}
                          </div>
                          <div style={{ fontSize: 12 }}>
                            {gameMode === "single_player" 
                              ? "Play against AI-controlled countries in a round-based strategy game"
                              : "Host or join a multiplayer session with other players"
                            }
                          </div>
                        </div>
                        
                        <button 
                          onClick={() => startRoundBasedGame()}
                          style={{ 
                            background: gameMode === "single_player" ? "#3b82f6" : "#10b981", 
                            border: "none", 
                            color: "white", 
                            padding: "12px 24px", 
                            borderRadius: 8, 
                            cursor: "pointer",
                            fontSize: 16,
                            fontWeight: 600,
                            transition: "all 0.2s ease"
                          }}
                          onMouseEnter={(e) => {
                            e.target.style.transform = "scale(1.02)";
                            e.target.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
                          }}
                          onMouseLeave={(e) => {
                            e.target.style.transform = "scale(1)";
                            e.target.style.boxShadow = "none";
                          }}
                        >
                          🚀 Start {gameMode === "single_player" ? "Single Player" : "Multiplayer"} Game as {selectedPlayableCountry.name}
                        </button>
                      </div>
                    </div>
                  )}

                  {countryComparison && countryComparison.comparison && (
                    <div style={{ border: "1px solid #333", borderRadius: 8, padding: 16 }}>
                      <h3 style={{ margin: "0 0 12px 0" }}>📊 Country Comparison</h3>
                      <div style={{ overflowX: "auto" }}>
                        <table style={{ width: "100%", fontSize: 11, borderCollapse: "collapse" }}>
                          <thead>
                            <tr style={{ background: "#1f2937" }}>
                              <th style={{ padding: "8px", textAlign: "left", border: "1px solid #333" }}>Country</th>
                              <th style={{ padding: "8px", textAlign: "left", border: "1px solid #333" }}>Type</th>
                              <th style={{ padding: "8px", textAlign: "left", border: "1px solid #333" }}>Difficulty</th>
                              <th style={{ padding: "8px", textAlign: "left", border: "1px solid #333" }}>Morale</th>
                              <th style={{ padding: "8px", textAlign: "left", border: "1px solid #333" }}>Economic</th>
                              <th style={{ padding: "8px", textAlign: "left", border: "1px solid #333" }}>Military</th>
                              <th style={{ padding: "8px", textAlign: "left", border: "1px solid #333" }}>Diplomatic</th>
                              <th style={{ padding: "8px", textAlign: "left", border: "1px solid #333" }}>Abilities</th>
                              <th style={{ padding: "8px", textAlign: "left", border: "1px solid #333" }}>Units</th>
                            </tr>
                          </thead>
                          <tbody>
                            {Object.entries(countryComparison.comparison).map(([countryId, data]) => (
                              <tr key={countryId} style={{ 
                                background: selectedPlayableCountry?.country_id === countryId ? "#1f2937" : "#111",
                                cursor: "pointer"
                              }} onClick={() => selectPlayableCountry(countryId)}>
                                <td style={{ padding: "8px", border: "1px solid #333", fontWeight: 600 }}>{data.name}</td>
                                <td style={{ padding: "8px", border: "1px solid #333" }}>{data.type.replace('_', ' ')}</td>
                                <td style={{ padding: "8px", border: "1px solid #333" }}>{data.difficulty}</td>
                                <td style={{ padding: "8px", border: "1px solid #333" }}>{Math.round(data.starting_stats.morale * 100)}%</td>
                                <td style={{ padding: "8px", border: "1px solid #333" }}>{Math.round(data.starting_stats.economic * 100)}%</td>
                                <td style={{ padding: "8px", border: "1px solid #333" }}>{Math.round(data.starting_stats.military * 100)}%</td>
                                <td style={{ padding: "8px", border: "1px solid #333" }}>{Math.round(data.starting_stats.diplomatic * 100)}%</td>
                                <td style={{ padding: "8px", border: "1px solid #333" }}>{data.special_abilities_count}</td>
                                <td style={{ padding: "8px", border: "1px solid #333" }}>{data.starting_units_count}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
        </>
      )}
       </div>
    </div>
  );
}