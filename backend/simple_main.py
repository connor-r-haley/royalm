#!/usr/bin/env python3
"""
Simple FastAPI Backend - Minimal version to get the app running
"""

import json
import os
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    has_dotenv = True
except ImportError:
    has_dotenv = False

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(title="World Brain API - Simple", version="1.0.0")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        """Simple health check"""
        # Check if OpenAI API key is available
        openai_key = os.getenv('OPENAI_API_KEY')
        chatgpt_available = openai_key is not None and openai_key != 'your_openai_api_key_here'
        
        return {
            "status": "healthy",
            "world_brain_available": chatgpt_available,
            "world_data_available": True,
            "world_leaders_available": True,
            "chatgpt_available": chatgpt_available,
            "message": "ChatGPT available" if chatgpt_available else "Add OpenAI API key to .env file to enable ChatGPT"
        }
    
    @app.get("/costs")
    async def get_costs():
        """Get cost information"""
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
    
    @app.post("/worldbrain/create")
    async def create_simulation():
        """Placeholder simulation creation"""
        return {
            "id": "demo-simulation-123",
            "status": "simulation_active",
            "current_date": datetime.now().strftime("%m/%d/%Y"),
            "countries": {},
            "news": [
                {
                    "title": "System Starting Up",
                    "content": "The World Brain simulation system is initializing. Please wait while all services come online.",
                    "country": "Global",
                    "category": "system",
                    "severity": "medium",
                    "reliability": "confirmed",
                    "source": "System",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "map_state": {
                "global_tension": 50,
                "bloc_distribution": {"Western": 1, "Eastern": 1, "Non-Aligned": 1},
                "active_conflicts": [],
                "country_states": {}
            },
            "global_indicators": {}
        }

    @app.post("/worldbrain/{simulation_id}/advance-month")
    async def advance_month(simulation_id: str):
        """Advance simulation by one month"""
        return {
            "simulation_id": simulation_id,
            "current_date": datetime.now().strftime("%m/%d/%Y"),
            "news": [
                {
                    "title": "Month Advanced",
                    "content": "The simulation has progressed by one month. Global tensions remain stable.",
                    "country": "Global",
                    "category": "system",
                    "severity": "low",
                    "reliability": "confirmed",
                    "source": "System",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "map_state": {
                "global_tension": 45,
                "bloc_distribution": {"Western": 1, "Eastern": 1, "Non-Aligned": 1},
                "active_conflicts": [],
                "country_states": {}
            },
            "global_indicators": {},
            "use_historical_news": False
        }

    @app.post("/worldbrain/{simulation_id}/tick")
    async def advance_tick(simulation_id: str):
        """Advance simulation by one tick/week"""
        import random
        
        # Generate some realistic-looking news
        news_templates = [
            {
                "title": "Global Markets React to Policy Changes",
                "content": "International financial markets showed mixed reactions today as major economies adjust their fiscal policies. Analysts note increased volatility in currency exchanges and commodity prices.",
                "country": "Global",
                "category": "economic",
                "severity": "medium"
            },
            {
                "title": "Diplomatic Tensions Rise in Eastern Europe",
                "content": "Recent diplomatic exchanges between neighboring countries have escalated, with both sides calling for international mediation. Regional stability remains a concern for global observers.",
                "country": "Europe",
                "category": "diplomatic",
                "severity": "high"
            },
            {
                "title": "Cybersecurity Concerns Mount Globally",
                "content": "Government agencies worldwide report increased cyber threats targeting critical infrastructure. Security experts recommend enhanced defensive measures and international cooperation.",
                "country": "Global",
                "category": "cyber",
                "severity": "high"
            },
            {
                "title": "Military Exercises Conducted in Pacific Region",
                "content": "Large-scale military exercises involving multiple nations concluded in the Pacific region. The drills focused on joint operations and regional security cooperation.",
                "country": "Pacific",
                "category": "military",
                "severity": "medium"
            }
        ]
        
        # Select random news
        selected_news = random.choice(news_templates)
        selected_news["source"] = random.choice(["Reuters", "Associated Press", "BBC News", "CNN International"])
        selected_news["reliability"] = random.choice(["confirmed", "likely", "uncertain"])
        selected_news["timestamp"] = datetime.now().isoformat()
        
        # Simulate changing global tension
        tension = random.randint(35, 75)
        
        return {
            "simulation_id": simulation_id,
            "current_date": datetime.now().strftime("%m/%d/%Y"),
            "news": [selected_news],
            "map_state": {
                "global_tension": tension,
                "bloc_distribution": {"Western": random.randint(1, 3), "Eastern": random.randint(1, 3), "Non-Aligned": random.randint(1, 2)},
                "active_conflicts": [] if tension < 60 else ["Regional Dispute"],
                "country_states": {
                    "US": {"status": "stable", "tension": random.randint(20, 50)},
                    "CN": {"status": "stable", "tension": random.randint(30, 60)},
                    "RU": {"status": "stable", "tension": random.randint(40, 70)}
                }
            },
            "global_indicators": {
                "economic_stability": random.randint(60, 90),
                "diplomatic_relations": random.randint(40, 80)
            },
            "use_historical_news": False
        }

    @app.get("/worlddata/countries")
    async def get_countries():
        """Get basic country data"""
        return {
            "US": {"name": "United States", "gdp": 21000000, "population": 330000000},
            "CN": {"name": "China", "gdp": 14000000, "population": 1400000000},
            "RU": {"name": "Russia", "gdp": 1700000, "population": 146000000}
        }

    @app.get("/worldleaders/leaders")
    async def get_leaders():
        """Get basic leader data"""
        return {
            "us_leader": {"name": "US Leader", "country": "US"},
            "cn_leader": {"name": "CN Leader", "country": "CN"},
            "ru_leader": {"name": "RU Leader", "country": "RU"}
        }

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001)
        
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install: pip install fastapi uvicorn")
    exit(1)
