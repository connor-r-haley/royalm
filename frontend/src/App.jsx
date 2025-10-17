import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import BorderManager from "./borderManager";

const API = "http://localhost:8000";
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
  const [showServiceStatus, setShowServiceStatus] = useState(false);
  const [activeSettingsTab, setActiveSettingsTab] = useState('api'); // 'api', 'map', 'about'
  const [newsLoading, setNewsLoading] = useState(false);
  const [selectedStartDate, setSelectedStartDate] = useState(() => {
    const today = new Date();
    return {
      month: today.getMonth() + 1,
      year: today.getFullYear(),
      usePresent: true
    };
  });

  // Settings dropdown + floating panels (API, Map, About, Databases)
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);
  const settingsMenuRef = useRef(null);
  const settingsButtonRef = useRef(null);
  const [settingsMenuPos, setSettingsMenuPos] = useState({ top: 56, right: 20 });

  const [panelVisible, setPanelVisible] = useState({ api: false, map: false, about: false, country: false });
  const [panelPos, setPanelPos] = useState({
    api: { x: typeof window !== 'undefined' ? window.innerWidth - 460 : 800, y: 90 },
    map: { x: typeof window !== 'undefined' ? window.innerWidth - 500 : 760, y: 140 },
    about: { x: typeof window !== 'undefined' ? window.innerWidth - 420 : 820, y: 190 },
    country: { x: typeof window !== 'undefined' ? window.innerWidth - 540 : 700, y: 90 }
  });
  const draggingRef = useRef(null);

  // Country data table helpers
  const [forgeQuery, setForgeQuery] = useState('');
  const [forgeSortBy, setForgeSortBy] = useState({ key: 'name', dir: 'asc' });
  // Databases panel tabs: countries | leaders
  const [databasesTab, setDatabasesTab] = useState('countries');
  const [leadersRows, setLeadersRows] = useState([]);

  function getCountryRows() {
    if (!psychohistoryMapState || !psychohistoryMapState.country_states) return [];
    const entries = Object.entries(psychohistoryMapState.country_states).map(([id, state]) => ({ id, ...state }));
    const rows = entries.map(c => ({
      id: c.id,
      name: c.name || c.id,
      allegiance: c.allegiance || c.faction || c.bloc || 'Unknown',
      gdp: c.gdp || c.economic || c.gdp_billion || 0,
      nukes: c.nuclear_warheads || c.nukes || 0,
      population: c.population || 0,
      military_budget: c.military_budget || 0,
      regime_type: c.regime_type || 'Unknown',
      morale: typeof c.morale === 'number' ? c.morale : 0
    }));
    let filtered = rows;
    if (forgeQuery) {
      const q = forgeQuery.toLowerCase();
      filtered = rows.filter(r => Object.values(r).some(v => String(v).toLowerCase().includes(q)));
    }
    const { key, dir } = forgeSortBy;
    filtered.sort((a, b) => {
      const av = a[key];
      const bv = b[key];
      if (typeof av === 'number' && typeof bv === 'number') return dir === 'asc' ? av - bv : bv - av;
      return dir === 'asc' ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
    });
    return filtered;
  }

  const toggleForgeSort = (key) => setForgeSortBy(prev => ({ key, dir: prev.key === key && prev.dir === 'asc' ? 'desc' : 'asc' }));

  const updateAllegiance = (countryId, newAllegiance) => {
    if (!borderManagerRef.current) return;
    const factionMap = { Western: 'NATO', Eastern: 'RUSSIA_BLOC', 'Non-Aligned': 'SWING', NATO:'NATO', RUSSIA_BLOC:'RUSSIA_BLOC', CHINA_BLOC:'CHINA_BLOC', SWING:'SWING' };
    const faction = factionMap[newAllegiance] || 'SWING';
    borderManagerRef.current.applyUpdate(countryId, { faction });
    // Update local map state so table reflects change immediately
    setPsychohistoryMapState(prev => {
      if (!prev || !prev.country_states) return prev;
      const next = { ...prev, country_states: { ...prev.country_states } };
      const cs = { ...(next.country_states[countryId] || {}) };
      cs.faction = faction;
      // Derive human-readable allegiance label
      const label = (faction === 'NATO') ? 'Western' : (faction === 'RUSSIA_BLOC' || faction === 'CHINA_BLOC') ? 'Eastern' : 'Non-Aligned';
      cs.allegiance = label;
      cs.bloc = label;
      next.country_states[countryId] = cs;
      return next;
    });
  };

  // Ensure we have complete country data (~200+) for Country Data panel
  async function ensureCountryData() {
    // If we already have a comprehensive set, skip
    if (psychohistoryMapState && psychohistoryMapState.country_states && Object.keys(psychohistoryMapState.country_states).length > 100) return;

    // Build baseStates from borders first (ensures ~200 entries), then overlay with /worlddata and /ref
    let baseStates = {};

    // Step 1: borders baseline
    try {
      const rBorders = await fetch('/borders-enhanced-detailed.json');
      const gj = await rBorders.json();
      if (gj && Array.isArray(gj.features)) {
        gj.features.forEach((f) => {
          const id = f?.properties?.id || f?.properties?.iso_a3 || f?.properties?.iso_a2 || f?.properties?.name || Math.random().toString(36).slice(2);
          const name = f?.properties?.name || id;
          const key = String(id).toUpperCase();
          baseStates[key] = {
            id: key,
            name,
            gdp: 0,
            nuclear_warheads: 0,
            population: 0,
            military_budget: 0,
            regime_type: 'Unknown',
            bloc: 'Unknown',
            allegiance: 'Unknown',
            morale: 0.5
          };
        });
      }
    } catch {}

    // Step 2: overlay legacy /worlddata/countries if available
    try {
      const rLegacy = await fetch(`${API}/worlddata/countries`);
      if (rLegacy.ok) {
        const obj = await rLegacy.json();
        if (obj && typeof obj === 'object') {
          Object.entries(obj).forEach(([key, v]) => {
            const id = String(key).toUpperCase();
            const prev = baseStates[id] || { id, name: id };
            baseStates[id] = {
              ...prev,
              name: (v && v.name) || prev.name,
              gdp: (v && (v.gdp_usd_billion ?? v.gdp_2024 ?? v.gdp)) ?? prev.gdp ?? 0,
              nuclear_warheads: (v && (v.nuclear_warheads ?? v.nukes)) ?? prev.nuclear_warheads ?? 0,
              population: (v && v.population) ?? prev.population ?? 0,
              military_budget: (v && v.military_budget) ?? prev.military_budget ?? 0,
              regime_type: (v && (v.gov_type || v.regime_type)) || prev.regime_type || 'Unknown',
              bloc: (v && (v.bloc || v.allegiance)) || prev.bloc || 'Unknown',
              allegiance: (v && (v.allegiance || v.bloc)) || prev.allegiance || 'Unknown',
              morale: typeof v?.morale === 'number' ? v.morale : prev.morale ?? 0.5,
            };
          });
        }
      }
    } catch {}

    // Step 3: overlay /ref countries for richer fields
    try {
      const rApi = await fetch(`${API}/ref/countries?limit=10000`);
      if (rApi.ok) {
        const apiData = await rApi.json();
        for (const v of apiData || []) {
          const id = v.code || v.code3 || v.code2 || v.name;
          if (!id) continue;
          const key = String(id).toUpperCase();
          const prev = baseStates[key] || { id: key, name: v.name || key };
          baseStates[key] = {
            ...prev,
            name: v.name || prev.name,
            gdp: v.gdp_usd_billion ?? prev.gdp ?? 0,
            population: v.population ?? prev.population ?? 0,
            regime_type: v.gov_type || prev.regime_type || 'Unknown'
          };
        }
      }
    } catch {}

    // Step 4: overlay live World Bank GDP and Population
    try {
      const [gdpRes, popRes] = await Promise.all([
        fetch(`${API}/ref/worldbank/gdp`),
        fetch(`${API}/ref/worldbank/population`)
      ]);
      const gdp = gdpRes.ok ? await gdpRes.json() : {};
      const pop = popRes.ok ? await popRes.json() : {};
      Object.keys(baseStates).forEach((id) => {
        const key = String(id).toUpperCase();
        const prev = baseStates[key];
        const gdpVal = gdp && gdp[key] ? gdp[key].value : undefined;
        const popVal = pop && pop[key] ? pop[key].value : undefined;
        baseStates[key] = {
          ...prev,
          gdp: typeof gdpVal === 'number' ? gdpVal : prev.gdp,
          population: typeof popVal === 'number' ? popVal : prev.population
        };
      });
    } catch {}

    if (Object.keys(baseStates).length > 0) {
      setPsychohistoryMapState({ country_states: baseStates });
    }
  }

  // Load leaders dataset for Databases tab
  async function ensureLeadersData() {
    if (leadersRows && leadersRows.length > 0) return;
    try {
      const r = await fetch(`${API}/ref/leaders?limit=10000`);
      if (r.ok) {
        const data = await r.json();
        setLeadersRows(Array.isArray(data) ? data : []);
      }
    } catch {}
  }

  useEffect(() => {
    if (panelVisible.country && databasesTab === 'leaders') {
      ensureLeadersData();
    }
  }, [panelVisible.country, databasesTab]);

  // Ensure countries are loaded whenever the Databases panel opens
  useEffect(() => {
    if (panelVisible.country) {
      const count = psychohistoryMapState && psychohistoryMapState.country_states ? Object.keys(psychohistoryMapState.country_states).length : 0;
      if (!count || count < 5) {
        ensureCountryData();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [panelVisible.country]);

  // Dragging + keep dropdown anchored on scroll
  useEffect(() => {
    const onMove = (e) => {
      if (!draggingRef.current) return;
      const { key, offsetX, offsetY } = draggingRef.current;
      setPanelPos(prev => ({ ...prev, [key]: { x: Math.max(0, e.clientX - offsetX), y: Math.max(0, e.clientY - offsetY) } }));
    };
    const onUp = () => { draggingRef.current = null; };
    const onScroll = () => {
      if (showSettingsMenu && settingsButtonRef.current) {
        const rect = settingsButtonRef.current.getBoundingClientRect();
        setSettingsMenuPos({ top: rect.bottom + 8, right: window.innerWidth - rect.right });
      }
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    window.addEventListener('scroll', onScroll, true);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
      window.removeEventListener('scroll', onScroll, true);
    };
  }, [showSettingsMenu]);

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

      setTimeout(() => {
        if (borderManagerRef.current) {
          borderManagerRef.current.updateNuclearIndicators();
        }
      }, 1000);
    });

    return () => map.remove();
  }, [currentStyle]);

  // Check service status on mount and periodically
  useEffect(() => {
    // Initial check
    checkServicesStatus();
    
    // Set up periodic check every 30 seconds
    const intervalId = setInterval(() => {
      checkServicesStatus();
    }, 30000);
    
    return () => clearInterval(intervalId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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

  // Define helper functions in the correct order (bottom-up dependency)
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
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', background: '#0f172a', overflow: 'hidden' }}>
      {/* Top Navigation Bar */}
      <div style={{ 
        background: '#000', 
        height: '60px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        position: 'relative',
        borderBottom: '1px solid #333',
        zIndex: 2000
      }}>
        {/* Back to Menu Button */}
        {!showMainMenu && (
          <div style={{ position: 'absolute', left: '20px' }}>
            <button 
              onClick={returnToMainMenu}
              style={{ 
                background: '#1a1a1a', 
                border: '1px solid #333',
                color: '#fff',
                width: '40px',
                height: '40px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.target.style.background = '#2a2a2a'}
              onMouseLeave={(e) => e.target.style.background = '#1a1a1a'}
            >
              ←
            </button>
          </div>
        )}
        
        <h1 style={{ 
          margin: 0, 
          fontSize: '1.5rem', 
          fontWeight: 'bold', 
          color: '#fff',
          letterSpacing: '2px'
        }}>
          MORALOCRACY
        </h1>
        
         {/* Settings Dropdown with hoverable menu and floating panels */}
        <div style={{ position: 'absolute', right: '20px' }}>
          <button 
             ref={settingsButtonRef}
             onClick={(e) => {
               setShowSettingsMenu(prev => !prev);
               const rect = e.currentTarget.getBoundingClientRect();
               setSettingsMenuPos({ top: rect.bottom + 8, right: window.innerWidth - rect.right });
             }}
            style={{ 
              background: '#1a1a1a', 
              border: '1px solid #333',
              color: '#fff',
              width: '40px',
              height: '40px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1.2rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.background = '#2a2a2a'}
            onMouseLeave={(e) => e.target.style.background = '#1a1a1a'}
          >
            ⚙️
          </button>
           {showSettingsMenu && (
             <div ref={settingsMenuRef}
               style={{ position: 'fixed', right: settingsMenuPos.right, top: settingsMenuPos.top, background: '#000', border: '1px solid #333', borderRadius: 8, padding: 6, minWidth: 200, zIndex: 2200, maxHeight: '60vh', overflowY: 'auto' }}
               onWheel={(e)=>{ e.stopPropagation(); }}
             >
                {[
                  { key: 'country', label: 'Databases' },
                 { key: 'api', label: 'API Status' },
                 { key: 'map', label: 'Map' },
                 { key: 'about', label: 'About' },
               ].map(item => (
                 <div key={item.key}
                   onClick={() => {
                     setPanelVisible(prev => ({ ...prev, [item.key]: true }));
                     if (item.key === 'country') { ensureCountryData(); }
                     setShowSettingsMenu(false);
                   }}
                   style={{ padding: '8px 10px', borderRadius: 6, cursor: 'pointer' }}
                   onMouseEnter={(e)=> e.currentTarget.style.background = '#111'}
                   onMouseLeave={(e)=> e.currentTarget.style.background = 'transparent'}
                 >
                   {item.label}
                 </div>
               ))}
             </div>
           )}
        </div>
      </div>

      {/* Map Container - Always visible */}
      <div style={{ flex: 1, position: 'relative', width: '100%', height: '100%' }}>
        <div id="map" style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, width: '100%', height: '100%' }} />
      
        {/* Main Menu Overlay - Only when showMainMenu is true */}
        {showMainMenu && (
        <div style={{
            position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
            background: '#000',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
            zIndex: 1500,
          padding: '20px',
          pointerEvents: 'auto'
        }}>
          <div style={{
            textAlign: 'center',
            marginBottom: '80px'
          }}>
            <h1 style={{
              fontSize: '4.5rem',
              fontWeight: 'bold',
              color: '#fff',
              margin: 0,
              letterSpacing: '8px',
              fontFamily: 'monospace'
            }}>
              WWIII SIMULATOR
            </h1>
            <div style={{
              width: '120px',
              height: '2px',
              background: '#fff',
              margin: '20px auto',
              opacity: 0.3
            }}></div>
            <p style={{
              fontSize: '1rem',
              color: '#888',
              marginTop: '10px',
              maxWidth: '600px',
              letterSpacing: '2px',
              fontFamily: 'monospace'
            }}>
              PREDICTIVE HISTORY • AI ANALYSIS • STRATEGIC GAMEPLAY
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '2px',
            maxWidth: '900px',
            width: '100%',
            position: 'relative',
            zIndex: 1501,
            background: '#333',
            border: '1px solid #333'
          }}>
            <div 
              onClick={() => selectGameMode('psychohistory')}
              style={{
                background: '#000',
                border: 'none',
                padding: '40px 30px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#1a1a1a';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#000';
              }}
            >
              <div style={{ 
                fontSize: '2.5rem', 
                marginBottom: '20px',
                filter: 'grayscale(100%)'
              }}>🧠</div>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: '#fff',
                margin: '0 0 15px 0',
                letterSpacing: '3px',
                fontFamily: 'monospace'
              }}>
                PSYCHOHISTORY
              </h2>
              <p style={{
                color: '#888',
                lineHeight: '1.8',
                margin: '0 0 20px 0',
                fontSize: '0.85rem'
              }}>
                The World Brain - Automated predictive simulation using real news, historical patterns, and AI analysis.
              </p>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                color: '#fff',
                fontSize: '0.75rem',
                fontWeight: '600',
                letterSpacing: '2px',
                fontFamily: 'monospace'
              }}>
                <span>WITNESS →</span>
              </div>
            </div>

            <div 
              onClick={() => selectGameMode('single_player')}
              style={{
                background: '#000',
                border: 'none',
                padding: '40px 30px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#1a1a1a';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#000';
              }}
            >
              <div style={{ 
                fontSize: '2.5rem', 
                marginBottom: '20px',
                filter: 'grayscale(100%)'
              }}>🎮</div>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: '#fff',
                margin: '0 0 15px 0',
                letterSpacing: '3px',
                fontFamily: 'monospace'
              }}>
                SINGLE PLAYER
              </h2>
              <p style={{
                color: '#888',
                lineHeight: '1.8',
                margin: '0 0 20px 0',
                fontSize: '0.85rem'
              }}>
                Command one of 8 major powers in a world where AI controls all other nations.
              </p>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                color: '#fff',
                fontSize: '0.75rem',
                fontWeight: '600',
                letterSpacing: '2px',
                fontFamily: 'monospace'
              }}>
                <span>CHOOSE →</span>
              </div>
            </div>

            <div 
              onClick={() => selectGameMode('multiplayer')}
              style={{
                background: '#000',
                border: 'none',
                padding: '40px 30px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#1a1a1a';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#000';
              }}
            >
              <div style={{ 
                fontSize: '2.5rem', 
                marginBottom: '20px',
                filter: 'grayscale(100%)'
              }}>👥</div>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: '#fff',
                margin: '0 0 15px 0',
                letterSpacing: '3px',
                fontFamily: 'monospace'
              }}>
                MULTIPLAYER
              </h2>
              <p style={{
                color: '#888',
                lineHeight: '1.8',
                margin: '0 0 20px 0',
                fontSize: '0.85rem'
              }}>
                Compete with 2-8 players in simultaneous decision-making rounds.
              </p>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                color: '#fff',
                fontSize: '0.75rem',
                fontWeight: '600',
                letterSpacing: '2px',
                fontFamily: 'monospace'
              }}>
                <span>JOIN →</span>
              </div>
            </div>
          </div>

          <div style={{
            marginTop: '80px',
            textAlign: 'center',
            color: '#444',
            fontSize: '0.7rem',
            letterSpacing: '2px',
            fontFamily: 'monospace'
          }}>
            <p>POWERED BY PREDICTIVE HISTORY • CHATGPT AI • REAL-TIME GEOPOLITICAL ANALYSIS</p>
          </div>
        </div>
        )}
        
        {/* Game Interface - Always visible when not in main menu */}
        {!showMainMenu && (
        <>
            {false && showServiceStatus && (
              <div
                style={{
                  position: "fixed",
                  right: 20,
                  top: 70,
                  width: 400,
                  background: "#000",
                  color: "#fff",
                  borderRadius: 12,
                  boxShadow: "0 8px 20px rgba(0,0,0,.15)",
                  maxHeight: "80vh",
                  overflowY: "auto",
                  border: "1px solid #333",
                  zIndex: 2001
                }}
              >
                {/* Tab Headers */}
                <div style={{ 
                  display: 'flex', 
                  borderBottom: '1px solid #333',
                  background: '#0a0a0a'
                }}>
                  <button
                    onClick={() => setActiveSettingsTab('api')}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: activeSettingsTab === 'api' ? '#1a1a1a' : 'transparent',
                      border: 'none',
                      borderBottom: activeSettingsTab === 'api' ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeSettingsTab === 'api' ? '#3b82f6' : '#999',
                      cursor: 'pointer',
                      fontSize: '13px',
                      fontWeight: 600,
                      transition: 'all 0.2s'
                    }}
                  >
                    🚀 API Status
                  </button>
                  <button
                    onClick={() => setActiveSettingsTab('map')}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: activeSettingsTab === 'map' ? '#1a1a1a' : 'transparent',
                      border: 'none',
                      borderBottom: activeSettingsTab === 'map' ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeSettingsTab === 'map' ? '#3b82f6' : '#999',
                      cursor: 'pointer',
                      fontSize: '13px',
                      fontWeight: 600,
                      transition: 'all 0.2s'
                    }}
                  >
                    🗺️ Map
                  </button>
                  <button
                    onClick={() => setActiveSettingsTab('about')}
                    style={{
                      flex: 1,
                      padding: '12px',
                      background: activeSettingsTab === 'about' ? '#1a1a1a' : 'transparent',
                      border: 'none',
                      borderBottom: activeSettingsTab === 'about' ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeSettingsTab === 'about' ? '#3b82f6' : '#999',
                      cursor: 'pointer',
                      fontSize: '13px',
                      fontWeight: 600,
                      transition: 'all 0.2s'
                    }}
                  >
                    ℹ️ About
                  </button>
                </div>

                {/* Tab Content */}
                <div style={{ padding: 16 }}>
                  {/* API Status Tab */}
                  {activeSettingsTab === 'api' && (
                    <>
                      <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 16 }}>
                        API & Services Status
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
                          fontSize: 12,
                          width: '100%'
                        }}
                      >
                        🔄 Refresh Status
                      </button>
                    </>
                  )}

                  {/* Map Settings Tab */}
                  {activeSettingsTab === 'map' && (
                    <>
                      <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 16 }}>
                        Map Settings
                      </div>

                      <div style={{ marginBottom: 16 }}>
                        <div style={{ fontWeight: 500, marginBottom: 8, fontSize: 14 }}>Map Style:</div>
                        <select
                          value={currentStyle}
                          onChange={(e) => switchStyle(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '8px 12px',
                            background: '#1a1a1a',
                            border: '1px solid #333',
                            color: '#fff',
                            borderRadius: 6,
                            fontSize: 13,
                            cursor: 'pointer'
                          }}
                        >
                          <option value="Landscape">🌄 Landscape</option>
                          <option value="SatelliteMain">🛰️ Satellite</option>
                          <option value="ModernPolitical">🗺️ Modern Political</option>
                          <option value="SatellitePolitical">🌍 Satellite Political</option>
                          <option value="GreyscalePolitical">⚫ Greyscale</option>
                          <option value="TonerBW">⬛ Black & White</option>
                        </select>
                      </div>

                      <div style={{ marginBottom: 16 }}>
                        <div style={{ fontWeight: 500, marginBottom: 8, fontSize: 14 }}>Display Options:</div>
                        <div style={{ 
                          padding: 12, 
                          background: '#111', 
                          borderRadius: 8,
                          fontSize: 13,
                          color: '#999'
                        }}>
                          <div style={{ marginBottom: 8 }}>
                            ℹ️ Hover over countries to see details
                          </div>
                          <div style={{ marginBottom: 8 }}>
                            🖱️ Click countries to select them
                          </div>
                          <div>
                            🎨 Nuclear indicators show warhead counts
                          </div>
                        </div>
                      </div>
                    </>
                  )}

                  {/* About Tab */}
                  {activeSettingsTab === 'about' && (
                    <>
                      <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 16 }}>
                        About WWIII Simulator
                      </div>

                      <div style={{ marginBottom: 16, padding: 12, background: '#111', borderRadius: 8 }}>
                        <div style={{ fontWeight: 500, marginBottom: 8 }}>Version:</div>
                        <div style={{ fontSize: 13, color: '#999' }}>v1.0.0 - Beta</div>
                      </div>

                      <div style={{ marginBottom: 16 }}>
                        <div style={{ fontWeight: 500, marginBottom: 8 }}>Keyboard Shortcuts:</div>
                        <div style={{ 
                          padding: 12, 
                          background: '#111', 
                          borderRadius: 8,
                          fontSize: 12,
                          color: '#ccc'
                        }}>
                          <div style={{ marginBottom: 6 }}>
                            <span style={{ color: '#3b82f6', fontWeight: 600 }}>→ / SPACE</span> - Advance week (Psychohistory)
                          </div>
                          <div style={{ marginBottom: 6 }}>
                            <span style={{ color: '#3b82f6', fontWeight: 600 }}>←</span> - Return to main menu
                          </div>
                          <div>
                            <span style={{ color: '#3b82f6', fontWeight: 600 }}>⚙️</span> - Toggle settings
                          </div>
                        </div>
                      </div>

                      <div style={{ marginBottom: 16 }}>
                        <div style={{ fontWeight: 500, marginBottom: 8 }}>Credits:</div>
                        <div style={{ 
                          padding: 12, 
                          background: '#111', 
                          borderRadius: 8,
                          fontSize: 12,
                          color: '#ccc'
                        }}>
                          <div style={{ marginBottom: 4 }}>🤖 Powered by OpenAI GPT-4o-mini</div>
                          <div style={{ marginBottom: 4 }}>📰 News API for real-time data</div>
                          <div style={{ marginBottom: 4 }}>🗺️ MapTiler for map rendering</div>
                          <div>⚛️ Built with React + Vite</div>
                        </div>
                      </div>

                      <div style={{ 
                        padding: 12, 
                        background: '#1a1a2e', 
                        borderRadius: 8,
                        fontSize: 11,
                        color: '#64748b',
                        borderLeft: '3px solid #3b82f6'
                      }}>
                        Experience the future of global conflict through predictive history, AI analysis, and strategic gameplay.
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
            {panelVisible.country && (
              <div style={{ position:'fixed', left: panelPos.country.x, top: panelPos.country.y, width: 520, background:'#000', color:'#fff', border:'1px solid #333', borderRadius:12, boxShadow:'0 8px 20px rgba(0,0,0,.15)', zIndex:2100 }}>
                <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:12, borderBottom:'1px solid #333', cursor:'move' }}
                  onMouseDown={(e)=>{ draggingRef.current = { key:'country', offsetX: e.clientX - panelPos.country.x, offsetY: e.clientY - panelPos.country.y }; }}
                  onMouseUp={()=>{ draggingRef.current = null; }}
                >
                  <div style={{ fontWeight:600 }}>Databases</div>
                  <button onClick={()=>setPanelVisible(p=>({ ...p, country:false }))} style={{ background:'#dc2626', border:'none', color:'#fff', padding:'6px 10px', borderRadius:6, cursor:'pointer' }}>Close</button>
                </div>
                <div style={{ padding:12 }}>
                  <div style={{ marginBottom:8 }}>
                    <input value={forgeQuery} onChange={(e)=>setForgeQuery(e.target.value)} placeholder="Search…" style={{ width:'100%', padding:'8px 10px', background:'#111', border:'1px solid #333', borderRadius:6, color:'#fff' }} />
                  </div>
                  <div style={{ overflow:'auto', maxHeight:'60vh' }}>
                    {/* Databases tabs */}
                    <div style={{ display:'flex', gap:6, marginBottom:8, flexWrap:'wrap' }}>
                      {[
                        { key:'countries', label:'Countries' },
                        { key:'leaders', label:'Leaders' },
                        { key:'allegiances', label:'Allegiances' },
                        { key:'gdp', label:'GDP' },
                        { key:'nukes', label:'Nukes' },
                        { key:'population', label:'Population' },
                        { key:'military', label:'Military' },
                        { key:'regime', label:'Regime' },
                      ].map(tab => (
                        <button key={tab.key} onClick={()=>setDatabasesTab(tab.key)}
                          style={{ padding:'6px 10px', border:'1px solid #333', borderRadius:6, background: databasesTab===tab.key?'#1f2937':'#0a0a0a', color:'#ddd', cursor:'pointer' }}>
                          {tab.label}
                        </button>
                      ))}
                    </div>
                    {databasesTab==='countries' && (
                    <table style={{ width:'100%', fontSize:12, borderCollapse:'collapse' }}>
                      <thead>
                        <tr>
                          <th onClick={()=>toggleForgeSort('name')} style={{ textAlign:'left', padding:'6px', cursor:'pointer', borderBottom:'1px solid #333' }}>
                            Country{forgeSortBy.key==='name' ? (forgeSortBy.dir==='asc'?' ▲':' ▼') : ''}
                          </th>
                          <th onClick={()=>toggleForgeSort('allegiance')} style={{ textAlign:'left', padding:'6px', cursor:'pointer', borderBottom:'1px solid #333' }}>
                            Allegiance{forgeSortBy.key==='allegiance' ? (forgeSortBy.dir==='asc'?' ▲':' ▼') : ''}
                          </th>
                          <th onClick={()=>toggleForgeSort('gdp')} style={{ textAlign:'left', padding:'6px', cursor:'pointer', borderBottom:'1px solid #333' }}>
                            GDP{forgeSortBy.key==='gdp' ? (forgeSortBy.dir==='asc'?' ▲':' ▼') : ''}
                          </th>
                          <th onClick={()=>toggleForgeSort('nukes')} style={{ textAlign:'left', padding:'6px', cursor:'pointer', borderBottom:'1px solid #333' }}>
                            Nukes{forgeSortBy.key==='nukes' ? (forgeSortBy.dir==='asc'?' ▲':' ▼') : ''}
                          </th>
                          <th onClick={()=>toggleForgeSort('population')} style={{ textAlign:'left', padding:'6px', cursor:'pointer', borderBottom:'1px solid #333' }}>
                            Population{forgeSortBy.key==='population' ? (forgeSortBy.dir==='asc'?' ▲':' ▼') : ''}
                          </th>
                          <th onClick={()=>toggleForgeSort('military_budget')} style={{ textAlign:'left', padding:'6px', cursor:'pointer', borderBottom:'1px solid #333' }}>
                            Military Budget{forgeSortBy.key==='military_budget' ? (forgeSortBy.dir==='asc'?' ▲':' ▼') : ''}
                          </th>
                          <th onClick={()=>toggleForgeSort('regime_type')} style={{ textAlign:'left', padding:'6px', cursor:'pointer', borderBottom:'1px solid #333' }}>
                            Regime{forgeSortBy.key==='regime_type' ? (forgeSortBy.dir==='asc'?' ▲':' ▼') : ''}
                          </th>
                          <th style={{ width: 120, borderBottom:'1px solid #333' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {getCountryRows().map(row => (
                          <tr key={row.id} style={{ background:'#0b1220' }}>
                            <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.name}</td>
                            <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.allegiance}</td>
                            <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{Number(row.gdp).toLocaleString()}</td>
                            <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.nukes}</td>
                            <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{Number(row.population||0).toLocaleString()}</td>
                            <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>
                              <select defaultValue={row.allegiance} onChange={(e)=>updateAllegiance(row.id, e.target.value)} style={{ padding:'4px 6px', background:'#111', color:'#fff', border:'1px solid #333', borderRadius:6 }}>
                                {['Western','Eastern','Non-Aligned','NATO','RUSSIA_BLOC','CHINA_BLOC','SWING'].map(a => (
                                  <option key={a} value={a}>{a}</option>
                                ))}
                              </select>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    )}
                    {databasesTab==='leaders' && (
                      <table style={{ width:'100%', fontSize:12, borderCollapse:'collapse' }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Name</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Title</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Country</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Start Date</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Ideology</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Approval</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(leadersRows||[])
                            .filter(row => {
                              if (!forgeQuery) return true;
                              const q = forgeQuery.toLowerCase();
                              return Object.values(row).some(v => String(v).toLowerCase().includes(q));
                            })
                            .map(row => (
                            <tr key={row.id} style={{ background:'#0b1220' }}>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.name}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.title}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.country_code}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.start_date || ''}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.ideology || ''}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.approval ?? ''}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                    {databasesTab==='allegiances' && (
                      <table style={{ width:'100%', fontSize:12, borderCollapse:'collapse' }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Country</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Allegiance</th>
                            <th style={{ width:120, borderBottom:'1px solid #333' }}>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {getCountryRows().map(row => (
                            <tr key={row.id} style={{ background:'#0b1220' }}>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.name}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.allegiance}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>
                                <select defaultValue={row.allegiance} onChange={(e)=>updateAllegiance(row.id, e.target.value)} style={{ padding:'4px 6px', background:'#111', color:'#fff', border:'1px solid #333', borderRadius:6 }}>
                                  {['Western','Eastern','Non-Aligned','NATO','RUSSIA_BLOC','CHINA_BLOC','SWING'].map(a => (
                                    <option key={a} value={a}>{a}</option>
                                  ))}
                                </select>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                    {databasesTab==='gdp' && (
                      <table style={{ width:'100%', fontSize:12, borderCollapse:'collapse' }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Country</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>GDP (USD B)</th>
                          </tr>
                        </thead>
                        <tbody>
                          {getCountryRows().map(row => (
                            <tr key={row.id} style={{ background:'#0b1220' }}>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.name}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{Number(row.gdp||0).toLocaleString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                    {databasesTab==='nukes' && (
                      <table style={{ width:'100%', fontSize:12, borderCollapse:'collapse' }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Country</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Warheads</th>
                          </tr>
                        </thead>
                        <tbody>
                          {getCountryRows().map(row => (
                            <tr key={row.id} style={{ background:'#0b1220' }}>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.name}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.nukes}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                    {databasesTab==='population' && (
                      <table style={{ width:'100%', fontSize:12, borderCollapse:'collapse' }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Country</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Population</th>
                          </tr>
                        </thead>
                        <tbody>
                          {getCountryRows().map(row => (
                            <tr key={row.id} style={{ background:'#0b1220' }}>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.name}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{Number(row.population||0).toLocaleString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                    {databasesTab==='military' && (
                      <table style={{ width:'100%', fontSize:12, borderCollapse:'collapse' }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Country</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Military Budget</th>
                          </tr>
                        </thead>
                        <tbody>
                          {getCountryRows().map(row => (
                            <tr key={row.id} style={{ background:'#0b1220' }}>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.name}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{Number(row.military_budget||0).toLocaleString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                    {databasesTab==='regime' && (
                      <table style={{ width:'100%', fontSize:12, borderCollapse:'collapse' }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Country</th>
                            <th style={{ textAlign:'left', padding:'6px', borderBottom:'1px solid #333' }}>Regime</th>
                          </tr>
                        </thead>
                        <tbody>
                          {getCountryRows().map(row => (
                            <tr key={row.id} style={{ background:'#0b1220' }}>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.name}</td>
                              <td style={{ padding:'6px', borderBottom:'1px solid #222' }}>{row.regime_type}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Floating API panel */}
            {panelVisible.api && (
              <div
                style={{ position:'fixed', left: panelPos.api.x, top: panelPos.api.y, width: 400, background:'#000', color:'#fff', border:'1px solid #333', borderRadius:12, boxShadow:'0 8px 20px rgba(0,0,0,.15)', zIndex:2100 }}>
                <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:8, borderBottom:'1px solid #333', cursor:'move' }}
                  onMouseDown={(e)=>{ draggingRef.current = { key:'api', offsetX: e.clientX - panelPos.api.x, offsetY: e.clientY - panelPos.api.y }; }}
                  onMouseUp={()=>{ draggingRef.current = null; }}
                >
                  <div style={{ fontWeight:600 }}>API Status</div>
                  <button onClick={()=>setPanelVisible(p=>({ ...p, api:false }))} style={{ background:'#dc2626', border:'none', color:'#fff', padding:'4px 8px', borderRadius:6, cursor:'pointer' }}>Close</button>
                </div>
                <div style={{ padding:16 }}>
                  <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 16 }}>API & Services Status</div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontWeight: 500, marginBottom: 8 }}>Service Status:</div>
                    {servicesStatus.loading ? (
                      <div style={{ color: '#666', fontSize: 14 }}>Loading services...</div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: servicesStatus.chatgpt ? '#10b981' : '#ef4444' }}></span>
                          <span style={{ fontSize: 14 }}>🤖 OpenAI GPT-4o-mini: {servicesStatus.chatgpt ? '✅ Active' : '❌ Inactive'}</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: servicesStatus.news ? '#10b981' : '#ef4444' }}></span>
                          <span style={{ fontSize: 14 }}>📰 News API: {servicesStatus.news ? '✅ Active' : '❌ Inactive'}</span>
                        </div>
                      </div>
                    )}
                  </div>
                  {costInfo && (
                    <div style={{ marginBottom: 16, padding: 12, background: '#111', borderRadius: 8 }}>
                      <div style={{ fontWeight: 500, marginBottom: 8 }}>💰 Cost Info:</div>
                      <div style={{ fontSize: 12, color: '#ccc' }}>
                        <div>Model: {costInfo.pricing?.model || 'N/A'}</div>
                        <div>Input: {costInfo.pricing?.input_per_1m_tokens || 'N/A'}</div>
                        <div>Output: {costInfo.pricing?.output_per_1m_tokens || 'N/A'}</div>
                        {costInfo.cost_estimates && (
                          <div style={{ marginTop: 4 }}>
                            <div>Hourly: {costInfo.cost_estimates.hourly_gameplay}</div>
                            <div>Monthly: {costInfo.cost_estimates.monthly}</div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  <button onClick={checkServicesStatus} style={{ padding: '8px 16px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 12, width: '100%' }}>🔄 Refresh Status</button>
                </div>
              </div>
            )}

            {/* Floating Map panel */}
            {panelVisible.map && (
              <div style={{ position:'fixed', left: panelPos.map.x, top: panelPos.map.y, width: 380, background:'#000', color:'#fff', border:'1px solid #333', borderRadius:12, boxShadow:'0 8px 20px rgba(0,0,0,.15)', zIndex:2100 }}>
                <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:8, borderBottom:'1px solid #333', cursor:'move' }}
                  onMouseDown={(e)=>{ draggingRef.current = { key:'map', offsetX: e.clientX - panelPos.map.x, offsetY: e.clientY - panelPos.map.y }; }}
                  onMouseUp={()=>{ draggingRef.current = null; }}
                >
                  <div style={{ fontWeight:600 }}>Map Settings</div>
                  <button onClick={()=>setPanelVisible(p=>({ ...p, map:false }))} style={{ background:'#dc2626', border:'none', color:'#fff', padding:'4px 8px', borderRadius:6, cursor:'pointer' }}>Close</button>
                </div>
                <div style={{ padding:16 }}>
                  <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 16 }}>Map Settings</div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontWeight: 500, marginBottom: 8, fontSize: 14 }}>Map Style:</div>
                    <select value={currentStyle} onChange={(e)=>switchStyle(e.target.value)} style={{ width:'100%', padding:'8px 12px', background:'#1a1a1a', border:'1px solid #333', color:'#fff', borderRadius:6, fontSize:13, cursor:'pointer' }}>
                      <option value="Landscape">🌄 Landscape</option>
                      <option value="SatelliteMain">🛰️ Satellite</option>
                      <option value="ModernPolitical">🗺️ Modern Political</option>
                      <option value="SatellitePolitical">🌍 Satellite Political</option>
                      <option value="GreyscalePolitical">⚫ Greyscale</option>
                      <option value="TonerBW">⬛ Black & White</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Floating About panel */}
            {panelVisible.about && (
              <div style={{ position:'fixed', left: panelPos.about.x, top: panelPos.about.y, width: 380, background:'#000', color:'#fff', border:'1px solid #333', borderRadius:12, boxShadow:'0 8px 20px rgba(0,0,0,.15)', zIndex:2100 }}>
                <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:8, borderBottom:'1px solid #333', cursor:'move' }}
                  onMouseDown={(e)=>{ draggingRef.current = { key:'about', offsetX: e.clientX - panelPos.about.x, offsetY: e.clientY - panelPos.about.y }; }}
                  onMouseUp={()=>{ draggingRef.current = null; }}
                >
                  <div style={{ fontWeight:600 }}>About</div>
                  <button onClick={()=>setPanelVisible(p=>({ ...p, about:false }))} style={{ background:'#dc2626', border:'none', color:'#fff', padding:'4px 8px', borderRadius:6, cursor:'pointer' }}>Close</button>
                </div>
                <div style={{ padding:16 }}>
                  <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 16 }}>About WWIII Simulator</div>
                  <div style={{ marginBottom: 16, padding: 12, background: '#111', borderRadius: 8 }}>
                    <div style={{ fontWeight: 500, marginBottom: 8 }}>Version:</div>
                    <div style={{ fontSize: 13, color: '#999' }}>v1.0.0 - Beta</div>
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontWeight: 500, marginBottom: 8 }}>Keyboard Shortcuts:</div>
                    <div style={{ padding: 12, background: '#111', borderRadius: 8, fontSize: 12, color: '#ccc' }}>
                      <div style={{ marginBottom: 6 }}><span style={{ color: '#3b82f6', fontWeight: 600 }}>→ / SPACE</span> - Advance week (Psychohistory)</div>
                      <div style={{ marginBottom: 6 }}><span style={{ color: '#3b82f6', fontWeight: 600 }}>←</span> - Return to main menu</div>
                      <div><span style={{ color: '#3b82f6', fontWeight: 600 }}>⚙️</span> - Toggle settings</div>
                    </div>
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontWeight: 500, marginBottom: 8 }}>Credits:</div>
                    <div style={{ padding: 12, background: '#111', borderRadius: 8, fontSize: 12, color: '#ccc' }}>
                      <div style={{ marginBottom: 4 }}>🤖 Powered by OpenAI GPT-4o-mini</div>
                      <div style={{ marginBottom: 4 }}>📰 News API for real-time data</div>
                      <div style={{ marginBottom: 4 }}>🗺️ MapTiler for map rendering</div>
                      <div>⚛️ Built with React + Vite</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
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
                overflowY: "auto",
                zIndex: 1000
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