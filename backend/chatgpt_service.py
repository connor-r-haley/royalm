#!/usr/bin/env python3
"""
Simple ChatGPT Service for World Brain
"""

import os
import json
import random
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class ChatGPTService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        print(f"ChatGPT Service Init - API Key exists: {bool(self.api_key)}")
        self.base_url = "https://api.openai.com/v1"
        self.client = bool(self.api_key)  # Just use a flag to indicate if we have an API key
        if self.client:
            print("ChatGPT Service Init - Client created successfully")
        else:
            print("ChatGPT Service Init - No API key found")
    
    async def generate_psychohistorical_news(self, 
                                           world_state: Dict[str, Any],
                                           country: str,
                                           event_type: str,
                                           impact_level: int,
                                           system_message: Optional[str] = None,
                                           prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate psychohistorically accurate news using ChatGPT"""
        
        if not self.client:
            return self._generate_fallback_news(country, event_type, impact_level)
        
        try:
            # Create SSL context that doesn't verify certificates (for development)
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [
                            {"role": "system", "content": system_message if system_message else "You are a news archive. Output ONLY the requested articles in the exact format shown."},
                            {"role": "user", "content": prompt if prompt else "Generate a news article"}
                        ],
                        "temperature": 0.1,  # Very low temperature to force consistent formatting
                        "max_tokens": 1000
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {"content": result["choices"][0]["message"]["content"].strip()}
                    else:
                        error_text = await response.text()
                        print(f"❌ API Error: {response.status} - {error_text}")
                        return self._generate_fallback_news(country, event_type, impact_level)
            
        except Exception as e:
            print(f"ChatGPT API error: {e}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {str(e)}")
            return self._generate_fallback_news(country, event_type, impact_level)
    
    def _generate_fallback_news(self, country: str, event_type: str, impact_level: int) -> Dict[str, Any]:
        """Generate fallback news when ChatGPT is unavailable"""
        
        # Create a properly formatted fallback article
        fallback_content = f"""[FALLBACK] Major Development in {country}
A significant {event_type} event has occurred in {country}, affecting regional dynamics and international relations.
SOURCE: FALLBACK News Agency"""
        
        return {"content": fallback_content}

# Global service instance
_chatgpt_service = None

async def get_chatgpt_service() -> ChatGPTService:
    """Get the global ChatGPT service instance"""
    global _chatgpt_service
    if _chatgpt_service is None:
        _chatgpt_service = ChatGPTService()
    return _chatgpt_service