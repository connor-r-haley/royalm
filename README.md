# 🌍 WWIII Simulator

A real-time, interactive World War III simulation with accurate country borders, territorial claims, and dynamic faction assignment. Built with React, MapLibre GL JS, and FastAPI.

## 🚀 Features

- **Complete World Map** - 220+ countries with accurate borders
- **Greenland & Antarctica** - Special territories with real territorial claims
- **Real-time Faction Assignment** - Click any country to assign US/RU/NEUTRAL factions
- **WebSocket Updates** - Changes sync across all connected clients
- **Interactive Map** - Hover effects, country selection, and dynamic styling
- **Multiple Map Styles** - Switch between different MapTiler basemaps
- **Real-time Geopolitical Data** - Current events and news integration
- **AI-Powered Analysis** - ChatGPT integration for geopolitical insights
- **Dynamic World Events** - Real-time event detection and impact calculation
- **Comprehensive Country Data** - Economic, military, political, and social statistics
- **Intelligent Caching** - Cost-effective API usage with smart caching
- **Multi-faction Support** - US, Russia, China, EU, India, Japan, and more

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **npm** (comes with Node.js)
- **Git** (for cloning the repository)
- **OpenAI API Key** (for ChatGPT integration - optional)
- **News API Key** (for real-time news - optional)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd royalm
```

### 2. Set Up Python Backend

#### Create Virtual Environment
```bash
python -m venv venv
```

#### Activate Virtual Environment
**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**Note:** If you get any errors, make sure your virtual environment is activated and try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Set Up Environment Variables (Optional)
Create a `.env` file in the backend directory for API keys:

**Option 1: Copy the example file**
```bash
cp env.example .env
# Then edit .env with your actual API keys
```

**Option 2: Create manually**
```bash
# Create .env file in backend directory
OPENAI_API_KEY=your_openai_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

**🔒 Security Note:** 
- The `.env` file is automatically ignored by Git
- Never commit your actual API keys to the repository
- The simulator works without API keys, but with limited real-time features

### 3. Set Up React Frontend

#### Install Node.js Dependencies
```bash
cd ../frontend
npm install
```

## 🎮 Running the Simulator

### 1. Start the Backend Server
```bash
# Make sure you're in the backend directory and virtual environment is activated
cd backend
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

python -m uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The backend will start on `http://localhost:8000`

### 2. Start the Frontend Development Server
```bash
# In a new terminal, navigate to the frontend directory
cd frontend
npm run dev
```

**Expected output:**
```
> frontend@0.0.0 dev
> vite
  VITE v7.1.3  ready in xxxxx ms
  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

The frontend will start on `http://localhost:5173`

### 3. Open the Simulator
Open your browser and navigate to `http://localhost:5173`

**You should see:**
- A world map with country borders
- A style switcher in the top-right corner
- The ability to click on countries and assign factions

## 🎯 How to Use

### Basic Controls
- **Click any country** to select it and assign factions
- **Hover over countries** to see their names
- **Use the style switcher** to change map appearance
- **Assign factions** using the US/RU buttons in the selection panel

### Faction Assignment
1. Click on any country or territory
2. Use the "Assign US" or "Assign RU" buttons
3. Changes are applied in real-time
4. All connected clients see the updates instantly

### Special Territories
- **Greenland** - Territory of Denmark (NATO-aligned)
- **Antarctica** - 7 territorial claims divided into non-overlapping slices:
  - Argentine Antarctica
  - Chilean Antarctic Territory
  - British Antarctic Territory
  - Queen Maud Land (Norway)
  - Australian Antarctic Territory
  - Adélie Land (France)
  - Ross Dependency (New Zealand)

### Real-time Features
- **Current Events Integration** - Real-time news and geopolitical events
- **AI Analysis** - ChatGPT-powered insights and predictions
- **Dynamic Morale System** - Country morale changes based on events
- **Diplomatic Relations** - Real-time diplomatic status tracking
- **Economic Indicators** - GDP, trade, inflation, and more
- **Military Intelligence** - Force levels, technology, and capabilities
- **Political Stability** - Government types, corruption, and unrest indices

## 🏗️ Project Structure

```
royalm/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── models.py            # Data models
│   ├── requirements.txt     # Python dependencies
│   └── *.json              # Country border data
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── borderManager.js # Border data management
│   │   └── index.css       # Styles
│   ├── public/
│   │   └── borders.json    # Static border data
│   └── package.json        # Node.js dependencies
└── README.md
```

## 🔧 Technical Details

### Backend (FastAPI)
- **Real-time WebSocket communication**
- **Country border data management**
- **Faction assignment API**
- **Session management**
- **CORS middleware** for cross-origin requests

### Frontend (React + MapLibre)
- **Interactive map interface**
- **Real-time border updates**
- **Dynamic styling based on factions**
- **Local border data management**
- **Vite** for fast development and building

### Dependencies
**Backend (Python):**
- `fastapi==0.116.1` - Web framework
- `uvicorn[standard]==0.35.0` - ASGI server
- `websockets==15.0.1` - WebSocket support
- `pydantic==2.11.7` - Data validation
- `python-dotenv==1.1.1` - Environment variables
- `aiohttp==3.9.1` - Async HTTP client
- `openai==1.3.7` - OpenAI API integration

**Frontend (Node.js):**
- `react` - UI framework
- `maplibre-gl` - Map rendering
- `vite` - Build tool and dev server

### External APIs (Optional)
- **OpenAI GPT-4** - AI-powered geopolitical analysis
- **NewsAPI** - Real-time news and current events
- **OpenWeather** - Weather data for strategic planning
- **Currency API** - Economic exchange rates

### Data Sources
- **Country borders**: Extracted from high-quality GeoJSON data
- **Territorial claims**: Based on real international law and treaties
- **Faction assignments**: Dynamic, user-controlled
- **Real-time events**: Live news and geopolitical developments
- **Economic data**: GDP, trade, inflation, and financial indicators
- **Military intelligence**: Force levels, technology, and capabilities
- **Political data**: Government types, stability, and corruption indices
- **Social indicators**: Population, demographics, and unrest metrics

## 🎨 Map Styles

The simulator includes multiple MapTiler styles:
- **Landscape** - Default topographic style
- **Satellite** - Satellite imagery
- **Streets** - Street map style
- **Basic** - Simple, clean style

## 🔄 Real-time Features

- **WebSocket connections** for instant updates
- **Multi-client support** - Multiple users can connect simultaneously
- **Session management** - Persistent game state
- **Border updates** - Real-time faction changes
- **Live news integration** - Current events affect simulation
- **AI-powered analysis** - ChatGPT insights and predictions
- **Dynamic morale system** - Country morale changes based on events
- **Intelligent caching** - Cost-effective API usage
- **Event-driven updates** - Real-time geopolitical developments
- **Predictive modeling** - AI-generated future scenarios

## 🚀 Deployment

### Local Development
Both servers run on localhost with hot-reload enabled for development.

### Production Deployment
For production deployment:
1. Build the frontend: `npm run build`
2. Serve static files from a web server
3. Deploy the FastAPI backend to a production server
4. Configure environment variables for production settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Troubleshooting

### Common Issues

**Backend won't start:**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.9+: `python --version`
- If you get "No module named uvicorn", run: `pip install -r requirements.txt`

**Frontend won't start:**
- Ensure Node.js is installed: `node --version`
- Run `npm install` to install dependencies
- Check for port conflicts (try different ports if needed)

**Map not loading:**
- Verify both backend and frontend are running
- Check browser console for errors (F12 → Console)
- Ensure `borders.json` is in the `frontend/public/` directory
- Try refreshing the page

**WebSocket connection issues:**
- Check that backend is running on port 8000
- Verify firewall settings
- Check browser WebSocket support
- Try opening `http://localhost:8000/` in browser to test backend

**"Address already in use" error:**
- Kill existing processes: `pkill -f uvicorn` (macOS/Linux)
- Or use a different port: `python -m uvicorn main:app --reload --port 8001`

**Virtual environment issues:**
- If you get "No module named" errors, make sure you're in the virtual environment
- Recreate virtual environment if needed:
  ```bash
  rm -rf venv
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

**API key issues:**
- If you get "ChatGPT service not available" errors, check your OpenAI API key
- If you get "NewsAPI" errors, check your News API key
- The simulator works without API keys but with limited features
- Check the `.env` file in the backend directory for proper key configuration

**Real-time data issues:**
- If real-time features aren't working, check your internet connection
- API rate limits may affect real-time updates
- Check the health endpoint: `http://localhost:8000/health`

## 🎮 Game Ideas

Once you have the basic simulator running, consider adding:
- **Military bases and units**
- **Economic resources and trade**
- **Diplomatic relations**
- **Historical scenarios**
- **AI opponents**
- **Save/load functionality**

---

**Happy simulating! 🌍⚔️**

## 🔒 **Security & Privacy**

### **API Key Security**
- **Never commit API keys** to Git repositories
- **Use environment variables** for sensitive data
- **The `.env` file is automatically ignored** by Git
- **Copy `env.example` to `.env`** and add your actual keys

### **Data Privacy**
- **No personal data is collected** or stored
- **API calls are made directly** from your local server
- **No data is sent to external servers** except for API requests
- **All game data is stored locally** in your browser

### **Network Security**
- **Backend runs locally** on `localhost:8000`
- **Frontend runs locally** on `localhost:5173`
- **No external network access** required (except for APIs)
- **WebSocket connections** are local only

### **Before Pushing to GitHub**
1. ✅ **Verify `.env` is in `.gitignore`**
2. ✅ **Check no API keys are in code**
3. ✅ **Test with `env.example`**
4. ✅ **Review all files for sensitive data**

## 💰 **Cost Analysis & Optimization**

### **Recommended AI Model: `gpt-4o-mini`**
- **Input:** $0.15 per 1M tokens
- **Output:** $0.60 per 1M tokens  
- **Cached Input:** $0.075 per 1M tokens (50% discount)

### **Estimated Costs:**
- **1 hour of gameplay:** ~$0.09
- **8 hours/day:** ~$0.72
- **Monthly (heavy usage):** ~$21.60
- **Monthly (moderate usage):** ~$10-15

### **Cost Control Features:**
- **Daily budget limits** (default: $5/day)
- **Monthly budget limits** (default: $100/month)
- **Intelligent caching** (50% cost reduction)
- **Usage tracking** and recommendations
- **Rate limiting** to prevent excessive calls

### **Cost Monitoring:**
```bash
# Check current usage and costs
curl http://localhost:8000/costs

# Monitor usage in real-time
curl http://localhost:8000/health
```

### **Cost Optimization Tips:**
1. **Enable caching** - Reduces costs by 50% for repeated queries
2. **Batch requests** - Combine similar operations
3. **Set budget limits** - Prevent unexpected charges
4. **Use basic mode** - No API costs when advanced features aren't needed
5. **Monitor usage** - Track spending patterns