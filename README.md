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

## ⚠️ IMPORTANT: Setup Requirements

**🚨 CRITICAL:** This project requires specific versions to work properly. Follow these instructions exactly to avoid common setup issues.

## 📋 Prerequisites

- **Python 3.9+** (3.11+ recommended)
- **Node.js 18.x** (⚠️ NOT Node.js 20+ or 16-)
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

#### ⚠️ CRITICAL: Use Correct Node.js Version
**This project requires Node.js 18.x for compatibility.**

**Check your Node.js version:**
```bash
node --version
```

**If you have the wrong version:**
- **Install Node.js 18.x** from [nodejs.org](https://nodejs.org/)
- **Or use nvm to switch versions:**
```bash
nvm install 18
nvm use 18
```

#### Install Node.js Dependencies
```bash
cd ../frontend
npm install
```

**⚠️ IMPORTANT:** If you see any errors about React versions or Babel, run:
```bash
rm -rf node_modules package-lock.json
npm install
```

## 🎮 Running the Simulator

### 1. Start the Backend Server
```bash
# Make sure you're in the backend directory and virtual environment is activated
cd backend
source venv/bin/activate  # On macOS/Linux
# OR
# venv\Scripts\activate  # On Windows

python main.py
```

**✅ Success:** You should see:
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start the Frontend Server
```bash
# Open a NEW terminal window/tab
cd frontend
npm run dev
```

**✅ Success:** You should see:
```
VITE v7.1.x ready in XXX ms
➜  Local:   http://localhost:5173/
```

### 3. Access the Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000

## 🔧 Troubleshooting

### White Page / App Won't Load
**Problem:** You see a white page in the browser
**Solution:** 
1. Check Node.js version: `node --version` (should be 18.x)
2. Clear dependencies: `rm -rf node_modules package-lock.json`
3. Reinstall: `npm install`
4. Restart: `npm run dev`

### Backend Won't Start
**Problem:** `python main.py` fails
**Solution:**
1. Ensure virtual environment is activated
2. Check Python version: `python --version` (should be 3.9+)
3. Reinstall requirements: `pip install -r requirements.txt`

### Import Errors
**Problem:** Module not found errors
**Solution:**
1. Make sure you're in the correct directory
2. Ensure virtual environment is activated for backend
3. Ensure Node.js dependencies are installed for frontend

### Port Already in Use
**Problem:** "Address already in use" error
**Solution:**
1. Kill existing processes: `pkill -f "python main.py"` or `pkill -f "vite"`
2. Or use different ports by modifying the code

## 🎯 Quick Start Commands

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend  
cd frontend
npm run dev
```

## 📱 Using the Simulator

1. **Open http://localhost:5173** in your browser
2. **Select a game mode** from the main menu
3. **Create a new simulation** to start
4. **Click countries** to assign factions
5. **View real-time news** and geopolitical events
6. **Interact with the map** using different styles

## 🆘 Still Having Issues?

If you're still experiencing problems:

1. **Check the terminal output** for specific error messages
2. **Verify your versions:**
   - Python: `python --version`
   - Node.js: `node --version`
   - npm: `npm --version`
3. **Ensure all dependencies are installed** in both backend and frontend
4. **Try the troubleshooting steps above**

## 🔄 Updates and Maintenance

When pulling updates from Git:
1. **Backend:** `pip install -r requirements.txt` (with venv activated)
2. **Frontend:** `npm install` (to get new dependencies)

---

**🎉 You're all set!** The simulator should now work without the common setup issues.