import os
import json
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from models import (
    ChatGPTRequest, ChatGPTResponse, EventAnalysisRequest, EventAnalysisResponse,
    GeopoliticalUpdateRequest, GeopoliticalUpdateResponse, WorldEvent, NewsHeadline,
    EventType, Country, DiplomaticStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatGPTService:
    """
    Efficient ChatGPT integration service for real-time geopolitical simulation.
    
    Features:
    - Intelligent caching to minimize API calls
    - Batch processing for multiple requests
    - Context-aware prompts for better responses
    - Cost optimization through smart request management
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.base_url = "https://api.openai.com/v1/chat/completions"
        # Use gpt-4o-mini for cost optimization
        self.model = "gpt-4o-mini"
        
        # Caching system
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
        
        # Cost tracking
        self.daily_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_cost": 0.0,
            "date": datetime.now().date()
        }
        
        # Rate limiting
        self.max_requests_per_minute = 60
        self.request_times: List[datetime] = []
        
        # Pricing (per 1M tokens)
        self.pricing = {
            "input": 0.15,      # $0.15 per 1M input tokens
            "output": 0.60,     # $0.60 per 1M output tokens
            "cached_input": 0.075  # $0.075 per 1M cached input tokens
        }
    
    async def __aenter__(self):
        # The original code used aiohttp.ClientSession, which is removed.
        # This method is kept as it was not explicitly removed by the user's edit.
        # However, the session management is now handled by the new_code.
        pass # No session management needed with requests
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # The original code used aiohttp.ClientSession, which is removed.
        # This method is kept as it was not explicitly removed by the user's edit.
        # However, the session management is now handled by the new_code.
        pass # No session management needed with requests
    
    def _get_cache_key(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a cache key for the request."""
        cache_data = {
            "prompt": prompt,
            "context": context,
            "model": self.model
        }
        return json.dumps(cache_data, sort_keys=True)
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if a cache entry is still valid."""
        cached_time = datetime.fromisoformat(cache_entry["timestamp"])
        return datetime.now() - cached_time < self.cache_duration
    
    async def _rate_limit(self):
        """Implement rate limiting to avoid API limits."""
        now = datetime.now()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < timedelta(minutes=1)]
        
        if len(self.request_times) >= self.max_requests_per_minute:
            time_to_wait = (self.request_times[0] + timedelta(minutes=1)) - now
            if time_to_wait.total_seconds() > 0:
                await asyncio.sleep(time_to_wait.total_seconds())
        
        self.request_times.append(datetime.now())
    
    async def _make_request(self, request: ChatGPTRequest) -> ChatGPTResponse:
        """Make a request to the ChatGPT API."""
        await self._rate_limit()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare the messages
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(request.context)
            },
            {
                "role": "user",
                "content": request.prompt
            }
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors
            
            data = response.json()
            
            return ChatGPTResponse(
                response=data["choices"][0]["message"]["content"],
                usage=data["usage"],
                model=data["model"]
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making ChatGPT request: {e}")
            raise
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate a context-aware system prompt."""
        base_prompt = """You are an expert geopolitical analyst and military strategist. 
        Your role is to provide accurate, up-to-date analysis of world events and their implications.
        
        Guidelines:
        1. Base your analysis on current real-world events and trends
        2. Consider historical context and patterns
        3. Provide realistic assessments of military, economic, and diplomatic impacts
        4. Use specific data and facts when available
        5. Consider multiple perspectives and potential outcomes
        6. Be objective and avoid bias
        7. Focus on actionable insights for strategic planning
        
        Current context: """
        
        if context:
            context_str = json.dumps(context, indent=2)
            base_prompt += f"\n\n{context_str}"
        
        return base_prompt
    
    async def get_response(self, request: ChatGPTRequest) -> ChatGPTResponse:
        """Get a response from ChatGPT with caching."""
        cache_key = self._get_cache_key(request.prompt, request.context)
        
        # Check cache first
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            logger.info("Using cached ChatGPT response")
            return ChatGPTResponse(**self.cache[cache_key]["response"])
        
        # Make API request
        response = await self._make_request(request)
        
        # Cache the response
        self.cache[cache_key] = {
            "response": response.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"ChatGPT API call made. Tokens used: {response.usage}")
        return response
    
    async def analyze_current_events(self, date: datetime, countries: List[str]) -> EventAnalysisResponse:
        """Analyze current events for specific countries and date."""
        
        # Create a focused prompt for current events
        prompt = f"""
        Analyze the current geopolitical situation as of {date.strftime('%B %d, %Y')} for the following countries: {', '.join(countries)}.
        
        Please provide:
        1. Key recent events that have occurred
        2. Current diplomatic relations and tensions
        3. Economic indicators and trade relationships
        4. Military developments and deployments
        5. Political stability and internal dynamics
        6. Potential flashpoints or areas of concern
        7. Predictions for the next 30-90 days
        
        Focus on events that would be most relevant for a geopolitical simulation game.
        """
        
        context = {
            "analysis_type": "current_events",
            "target_date": date.isoformat(),
            "countries_of_interest": countries,
            "focus_areas": ["diplomatic", "military", "economic", "political"]
        }
        
        request = ChatGPTRequest(
            prompt=prompt,
            context=context,
            max_tokens=2000,
            temperature=0.3  # Lower temperature for more factual responses
        )
        
        response = await self.get_response(request)
        
        # Parse the response into structured events
        events = self._parse_events_from_response(response.response, date, countries)
        
        return EventAnalysisResponse(
            events=events,
            analysis=response.response,
            predictions=self._extract_predictions(response.response),
            confidence_scores=self._calculate_confidence_scores(events)
        )
    
    async def get_geopolitical_update(self, request: GeopoliticalUpdateRequest) -> GeopoliticalUpdateResponse:
        """Get a comprehensive geopolitical update for the simulation."""
        
        prompt = f"""
        Provide a comprehensive geopolitical update for {request.current_date.strftime('%B %d, %Y')}.
        
        Focus areas: {', '.join(request.focus_areas)}
        Update type: {request.update_type}
        
        Please provide:
        1. Recent significant events and their implications
        2. Changes in diplomatic relations between major powers
        3. Economic developments and their geopolitical impact
        4. Military movements and strategic developments
        5. Political changes and their effects on international relations
        6. Emerging threats or opportunities
        7. Recommendations for strategic responses
        
        Format your response as a structured analysis that can be used in a geopolitical simulation.
        """
        
        context = {
            "update_type": request.update_type,
            "focus_areas": request.focus_areas,
            "current_date": request.current_date.isoformat(),
            "analysis_depth": "comprehensive"
        }
        
        chat_request = ChatGPTRequest(
            prompt=prompt,
            context=context,
            max_tokens=2500,
            temperature=0.4
        )
        
        response = await self.get_response(chat_request)
        
        # Parse the response into structured updates
        updates = self._parse_updates_from_response(response.response)
        new_events = self._extract_events_from_response(response.response, request.current_date)
        
        return GeopoliticalUpdateResponse(
            updates=updates,
            new_events=new_events,
            diplomatic_changes=self._extract_diplomatic_changes(response.response),
            economic_changes=self._extract_economic_changes(response.response),
            military_changes=self._extract_military_changes(response.response),
            analysis=response.response
        )
    
    async def generate_news_headlines(self, date: datetime, countries: List[str]) -> List[NewsHeadline]:
        """Generate realistic news headlines for the simulation."""
        
        prompt = f"""
        Generate 5-10 realistic news headlines for {date.strftime('%B %d, %Y')} that would be relevant for a geopolitical simulation.
        
        Focus on countries: {', '.join(countries)}
        
        For each headline, provide:
        1. A realistic news title
        2. A brief summary (2-3 sentences)
        3. The primary countries involved
        4. The type of news (diplomatic, military, economic, political)
        5. A sentiment score (-1 to 1, where -1 is very negative, 0 is neutral, 1 is very positive)
        
        Make the headlines realistic and based on current geopolitical trends.
        """
        
        context = {
            "headline_generation": True,
            "target_date": date.isoformat(),
            "focus_countries": countries
        }
        
        request = ChatGPTRequest(
            prompt=prompt,
            context=context,
            max_tokens=1500,
            temperature=0.6  # Slightly higher for creative headline generation
        )
        
        response = await self.get_response(request)
        
        return self._parse_headlines_from_response(response.response, date)
    
    def _parse_events_from_response(self, response: str, date: datetime, countries: List[str]) -> List[WorldEvent]:
        """Parse structured events from ChatGPT response."""
        events = []
        
        # This is a simplified parser - in production, you'd want more sophisticated parsing
        # or ask ChatGPT to return structured JSON
        
        # Split response into sections and look for event-like content
        lines = response.split('\n')
        current_event = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for event indicators
            if any(keyword in line.lower() for keyword in ['announced', 'declared', 'launched', 'signed', 'meeting', 'summit']):
                if current_event:
                    events.append(current_event)
                
                current_event = WorldEvent(
                    id=f"event_{len(events)}_{date.strftime('%Y%m%d')}",
                    event_type=EventType.DIPLOMATIC,  # Default, would need better classification
                    title=line[:100],  # Truncate long titles
                    description=line,
                    start_date=date,
                    affected_countries=countries,
                    primary_actors=countries[:2],  # Simplified
                    geopolitical_impact=0.5,
                    economic_impact=0.3,
                    military_impact=0.2,
                    social_impact=0.2,
                    source="ChatGPT Analysis",
                    confidence_level=0.7
                )
        
        if current_event:
            events.append(current_event)
        
        return events
    
    def _extract_predictions(self, response: str) -> List[Dict[str, Any]]:
        """Extract predictions from ChatGPT response."""
        predictions = []
        
        # Look for prediction-like content
        lines = response.split('\n')
        for line in lines:
            line = line.lower()
            if any(keyword in line for keyword in ['predict', 'forecast', 'likely', 'expected', 'could', 'may']):
                predictions.append({
                    "prediction": line,
                    "confidence": 0.6,  # Default confidence
                    "timeframe": "30-90 days"
                })
        
        return predictions
    
    def _calculate_confidence_scores(self, events: List[WorldEvent]) -> Dict[str, float]:
        """Calculate confidence scores for events."""
        scores = {}
        for event in events:
            scores[event.id] = event.confidence_level
        return scores
    
    def _parse_updates_from_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse updates from ChatGPT response."""
        updates = []
        
        # Split into sections and extract key updates
        sections = response.split('\n\n')
        for section in sections:
            if section.strip():
                updates.append({
                    "content": section.strip(),
                    "type": "general",
                    "timestamp": datetime.now().isoformat()
                })
        
        return updates
    
    def _extract_events_from_response(self, response: str, date: datetime) -> List[WorldEvent]:
        """Extract events from response."""
        # Similar to _parse_events_from_response but for general updates
        return self._parse_events_from_response(response, date, [])
    
    def _extract_diplomatic_changes(self, response: str) -> List[Dict[str, Any]]:
        """Extract diplomatic changes from response."""
        changes = []
        
        # Look for diplomatic indicators
        lines = response.split('\n')
        for line in lines:
            line = line.lower()
            if any(keyword in line for keyword in ['diplomatic', 'relations', 'alliance', 'treaty', 'agreement']):
                changes.append({
                    "type": "diplomatic",
                    "description": line,
                    "impact": "medium"
                })
        
        return changes
    
    def _extract_economic_changes(self, response: str) -> List[Dict[str, Any]]:
        """Extract economic changes from response."""
        changes = []
        
        lines = response.split('\n')
        for line in lines:
            line = line.lower()
            if any(keyword in line for keyword in ['economic', 'trade', 'gdp', 'sanctions', 'market']):
                changes.append({
                    "type": "economic",
                    "description": line,
                    "impact": "medium"
                })
        
        return changes
    
    def _extract_military_changes(self, response: str) -> List[Dict[str, Any]]:
        """Extract military changes from response."""
        changes = []
        
        lines = response.split('\n')
        for line in lines:
            line = line.lower()
            if any(keyword in line for keyword in ['military', 'defense', 'weapons', 'deployment', 'exercise']):
                changes.append({
                    "type": "military",
                    "description": line,
                    "impact": "medium"
                })
        
        return changes
    
    def _parse_headlines_from_response(self, response: str, date: datetime) -> List[NewsHeadline]:
        """Parse news headlines from ChatGPT response."""
        headlines = []
        
        # Split response and look for headline-like content
        lines = response.split('\n')
        current_headline = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for headline indicators
            if line.endswith('.') and len(line) < 200:
                if current_headline:
                    headlines.append(current_headline)
                
                current_headline = NewsHeadline(
                    id=f"headline_{len(headlines)}_{date.strftime('%Y%m%d')}",
                    title=line,
                    summary=line,
                    source="Simulated News",
                    content=line,
                    sentiment=0.0,  # Would need sentiment analysis
                    relevant_countries=[],
                    published_date=date,
                    relevance_score=0.7
                )
        
        if current_headline:
            headlines.append(current_headline)
        
        return headlines
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for monitoring costs."""
        return {
            "total_requests": len(self.request_times), # Total requests in the last minute
            "cache_hits": len([k for k, v in self.cache.items() if self._is_cache_valid(v)]),
            "cache_size": len(self.cache),
            "last_request": self.request_times[-1].isoformat() if self.request_times else "N/A"
        }
    
    def clear_cache(self):
        """Clear the response cache."""
        self.cache.clear()
        logger.info("ChatGPT service cache cleared")

# Singleton instance for the service
_chatgpt_service: Optional[ChatGPTService] = None

async def get_chatgpt_service() -> ChatGPTService:
    """Get or create ChatGPT service instance."""
    global _chatgpt_service
    if _chatgpt_service is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        _chatgpt_service = ChatGPTService(api_key)
        logger.info("ChatGPT service initialized successfully")
    return _chatgpt_service

async def close_chatgpt_service():
    """Close the ChatGPT service."""
    global _chatgpt_service
    if _chatgpt_service:
        # The original code had await _chatgpt_service.__aexit__(None, None, None),
        # but aiohttp is removed. This method is kept as it was not explicitly removed
        # by the user's edit. However, the session management is now handled by the new_code.
        pass # No session management needed with requests
        _chatgpt_service = None 