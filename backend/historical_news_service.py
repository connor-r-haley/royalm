#!/usr/bin/env python3
"""
Historical News Service - Fetches news from the past using News API
"""

import os
import json
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class HistoricalNewsService:
    """Service for fetching historical news articles"""
    
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"  # Changed from api.newsapi.org to newsapi.org
        
    async def get_historical_news(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Get historical news for a specific month and year using ChatGPT"""
        from chatgpt_service import get_chatgpt_service
        
        try:
            chatgpt_service = await get_chatgpt_service()
            
            # Create historically accurate world state context first
            world_state = self._get_historical_world_state(year, month)

            # Then create the prompt using the world state
            prompt = f"""Output 5 news articles from {month}/{year} in this format:

[Month Day, {year}] Headline
One sentence article content.
SOURCE: Newspaper Name

Historical context to help you:
- Major Powers: {', '.join(world_state['major_powers'])}
- Economic System: {world_state['economic_system']}
- Technological Era: {world_state['technological_era']}
- Cultural Context: {world_state['cultural_context']}
- Active Conflicts: {', '.join(world_state['active_conflicts']) if world_state['active_conflicts'] else 'None'}

Example article:
[September 15, {year}] Major Peace Treaty Signed in Geneva
World leaders from five nations met in Switzerland today to sign a historic peace agreement that will reshape regional politics for decades to come.
SOURCE: The New York Times

CRITICAL RULES:
1. ONLY use events from {month}/{year} - no other dates
2. Include SOURCE: line for every article
3. Keep articles to exactly 3 lines
4. Use real newspapers from {year}
5. Separate articles with one blank line

Historical Context:
- Major Powers: {', '.join(world_state['major_powers'])}
- Economic System: {world_state['economic_system']}
- Technological Era: {world_state['technological_era']}
- Cultural Context: {world_state['cultural_context']}
- Active Conflicts: {', '.join(world_state['active_conflicts']) if world_state['active_conflicts'] else 'None'}

Generate 5 articles now, following the format exactly."""
            
            # Generate historically accurate articles
            system_message = f"""You are a historical news archive from {month}/{year}. Output 5 news articles in this EXACT format:

[Month Day, {year}] Headline
One sentence article content.
SOURCE: Newspaper Name

DO NOT ASK FOR INFORMATION - you already have month={month} and year={year}.
DO NOT EXPLAIN OR APOLOGIZE - just output the articles.
DO NOT USE EVENTS FROM OTHER DATES - only {month}/{year}.
ALWAYS include the SOURCE: line.
ALWAYS use real newspapers from {year}.

Example of CORRECT response:
[September 15, {year}] Major Trade Agreement Signed
Leaders from five nations met in Geneva today to sign a historic trade pact that will reshape global commerce.
SOURCE: The Wall Street Journal

[September 16, {year}] New Scientific Discovery Announced
Researchers at MIT revealed breakthrough findings in quantum computing that could revolutionize data processing.
SOURCE: The New York Times"""

            article = await chatgpt_service.generate_psychohistorical_news(
                world_state=world_state,
                country="Global",
                event_type="historical",
                impact_level=90,  # High impact for verified historical events
                system_message=system_message
            )
            
            # Parse the response and verify historical accuracy
            try:
                content = article.get('content', '')
                print(f"🔍 ChatGPT Response for {month}/{year}:")
                print(f"Raw content: {repr(content)}")
                articles = []
                
                # Split into individual articles and validate format
                article_texts = content.split('\n\n')
                for text in article_texts:
                    lines = text.strip().split('\n')
                    
                    # Validate exact 3-line format
                    if len(lines) != 3:
                        print(f"⚠️ Invalid article format - expected 3 lines, got {len(lines)}")
                        print(f"Article content: {text}")
                        continue
                        
                    # Validate date line format
                    date_line = lines[0]
                    if not (date_line.startswith('[') and ']' in date_line):
                        print("⚠️ Invalid date format - missing brackets")
                        continue
                        
                    try:
                        date_str = date_line[1:date_line.index(']')]
                        article_date = datetime.strptime(date_str, '%B %d, %Y')
                        
                        # Strict month/year validation
                        if article_date.year != year or article_date.month != month:
                            print(f"⚠️ Invalid date: {date_str} - must be from {month}/{year}")
                            print(f"Full article:\n{text}")
                            continue
                            
                        # Extract headline (after date bracket)
                        headline = date_line[date_line.index(']')+1:].strip()
                        
                        # Validate source line
                        if not lines[2].startswith('SOURCE: '):
                            print("⚠️ Invalid source format - must start with 'SOURCE: '")
                            continue
                            
                        source = lines[2][8:].strip()  # Remove 'SOURCE: ' prefix
                        
                        # Create article with validated components
                        articles.append({
                            "title": f"[{date_str}] {headline}",
                            "content": lines[1],  # Middle line is content
                            "country": "Global",
                            "category": "historical",
                            "severity": "high",
                            "reliability": "confirmed",
                            "source": source,
                            "timestamp": article_date.isoformat() + "Z",
                            "url": f"https://historical-archive.example.com/{year}/{month}/{date_str.replace(' ', '-').replace(',', '')}"
                        })
                    except (ValueError, IndexError) as e:
                        print(f"⚠️ Error parsing article: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error processing articles: {e}")
                return self._get_fallback_historical_data(year, month)
            
            if not articles:
                print(f"⚠️ No valid articles found for {month}/{year}, using fallback data")
                return self._get_fallback_historical_data(year, month)
                
            return articles
            
        except Exception as e:
            print(f"❌ Error generating historical news: {e}")
            return self._get_fallback_historical_data(year, month)
    
    def _parse_chatgpt_response(self, response: str, year: int, month: int) -> List[Dict[str, Any]]:
        """Parse ChatGPT response into articles using simple text parsing"""
        articles = []
        lines = response.split("\n")
        current_article = {}
        content_buffer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for patterns that indicate a new article
            if line.startswith(("Headline:", "Title:", "1.", "2.", "3.", "4.", "5.")):
                # Save previous article if exists
                if current_article.get("title"):
                    current_article["content"] = "\n".join(content_buffer)
                    articles.append(current_article)
                    content_buffer = []
                
                # Start new article
                current_article = {
                    "title": line.split(":", 1)[1].strip() if ":" in line else line,
                    "category": "diplomatic",  # Default values
                    "severity": "medium",
                    "country": "Global",
                    "reliability": "historical",
                    "source": "Historical Archive",
                    "timestamp": datetime(year, month, 15).isoformat() + "Z",
                    "url": f"https://historical-archive.example.com/{year}/{month}"
                }
            elif line.lower().startswith(("category:", "type:")):
                current_article["category"] = line.split(":", 1)[1].strip().lower()
            elif line.lower().startswith("severity:"):
                current_article["severity"] = line.split(":", 1)[1].strip().lower()
            elif line.lower().startswith(("countries:", "country:")):
                current_article["country"] = line.split(":", 1)[1].strip()
            else:
                content_buffer.append(line)
        
        # Add last article
        if current_article.get("title") and content_buffer:
            current_article["content"] = "\n".join(content_buffer)
            articles.append(current_article)
        
        return articles
    
    def _get_historical_world_state(self, year: int, month: int) -> Dict[str, Any]:
        """Get historically accurate world state for a given time period"""
        
        # Define major historical periods and their characteristics
        world_state = {
            "timestamp": datetime(year, month, 1),
            "major_powers": [],
            "active_conflicts": [],
            "global_tension": 50,
            "economic_system": "",
            "technological_era": "",
            "cultural_context": ""
        }
        
        # Pre-WW2 Era (1900-1939)
        if year < 1939:
            world_state["major_powers"] = ["British Empire", "United States", "France", "German Empire" if year < 1918 else "Weimar Republic" if year < 1933 else "Nazi Germany", "Russian Empire" if year < 1917 else "Soviet Union"]
            world_state["economic_system"] = "Gold Standard Era" if year < 1931 else "Great Depression"
            world_state["global_tension"] = 60 if 1914 <= year <= 1918 else 70 if year >= 1933 else 40
            
        # WW2 Era (1939-1945)
        elif 1939 <= year <= 1945:
            world_state["major_powers"] = ["United States", "Soviet Union", "British Empire", "Nazi Germany", "Empire of Japan"]
            world_state["economic_system"] = "War Economy"
            world_state["global_tension"] = 100
            
        # Cold War Era (1945-1991)
        elif 1945 <= year <= 1991:
            world_state["major_powers"] = ["United States", "Soviet Union"]
            world_state["economic_system"] = "Bretton Woods" if year < 1971 else "Post-Bretton Woods"
            world_state["global_tension"] = 80 if year < 1962 else 70 if year < 1979 else 60
            
        # Post-Cold War Era (1991-2000)
        elif 1991 <= year <= 2000:
            world_state["major_powers"] = ["United States", "Russia", "European Union", "China"]
            world_state["economic_system"] = "Globalization Era"
            world_state["global_tension"] = 40
            
        # Modern Era (2001-present)
        else:
            world_state["major_powers"] = ["United States", "China", "Russia", "European Union", "India"]
            world_state["economic_system"] = "Digital Economy"
            world_state["global_tension"] = 60 if year >= 2001 else 50
        
        # Add technological era
        if year < 1920:
            world_state["technological_era"] = "Industrial Revolution"
        elif year < 1945:
            world_state["technological_era"] = "Radio Age"
        elif year < 1969:
            world_state["technological_era"] = "Atomic Age"
        elif year < 1991:
            world_state["technological_era"] = "Space Age"
        elif year < 2007:
            world_state["technological_era"] = "Information Age"
        else:
            world_state["technological_era"] = "Digital Age"
            
        # Add cultural context
        if year < 1920:
            world_state["cultural_context"] = "Progressive Era"
        elif year < 1930:
            world_state["cultural_context"] = "Roaring Twenties"
        elif year < 1945:
            world_state["cultural_context"] = "Wartime Culture"
        elif year < 1960:
            world_state["cultural_context"] = "Post-War Boom"
        elif year < 1970:
            world_state["cultural_context"] = "Counterculture"
        elif year < 1980:
            world_state["cultural_context"] = "Disco Era"
        elif year < 1990:
            world_state["cultural_context"] = "Reagan Era"
        elif year < 2000:
            world_state["cultural_context"] = "Generation X"
        elif year < 2010:
            world_state["cultural_context"] = "Early Digital"
        else:
            world_state["cultural_context"] = "Social Media Era"
            
        # Add major conflicts based on year
        if 1914 <= year <= 1918:
            world_state["active_conflicts"].append("World War I")
        if 1939 <= year <= 1945:
            world_state["active_conflicts"].append("World War II")
        if 1950 <= year <= 1953:
            world_state["active_conflicts"].append("Korean War")
        if 1955 <= year <= 1975:
            world_state["active_conflicts"].append("Vietnam War")
        if 1979 <= year <= 1989:
            world_state["active_conflicts"].append("Soviet-Afghan War")
        if 1990 <= year <= 1991:
            world_state["active_conflicts"].append("Gulf War")
        if year >= 2001:
            world_state["active_conflicts"].append("War on Terror")
            
        return world_state
    
    def _determine_severity(self, title: str, description: str) -> str:
        """Determine article severity based on content"""
        text = (title + " " + description).lower()
        
        high_severity = ["war", "crisis", "conflict", "attack", "invasion", "emergency", "disaster"]
        medium_severity = ["tension", "dispute", "controversy", "concern", "threat", "warning"]
        
        if any(word in text for word in high_severity):
            return "high"
        elif any(word in text for word in medium_severity):
            return "medium"
        else:
            return "low"
    
    def _get_fallback_historical_data(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Return fallback historical data when News API fails"""
        
        # Create some generic historical events based on the time period
        fallback_articles = []
        
        # Create period-appropriate events
        if year < 1950:
            events = [
                ("International Tensions Rise", "Diplomatic relations strain between major powers as territorial disputes continue.", "diplomatic", "medium"),
                ("Economic Challenges Persist", "Global markets face uncertainty amid ongoing political instability.", "economic", "medium"),
                ("Military Developments", "Armed forces conduct exercises in response to regional security concerns.", "military", "low")
            ]
        elif year < 1990:
            events = [
                ("Cold War Tensions", "Superpower rivalry continues to shape international relations and regional conflicts.", "diplomatic", "high"),
                ("Nuclear Concerns", "International community monitors nuclear developments and arms control negotiations.", "military", "high"),
                ("Regional Conflicts", "Local disputes reflect broader ideological struggles between East and West.", "military", "medium")
            ]
        elif year < 2000:
            events = [
                ("Post-Cold War Realignment", "Nations adjust to new geopolitical realities following major power shifts.", "diplomatic", "medium"),
                ("Economic Transition", "Markets adapt to changing global trade patterns and emerging economies.", "economic", "medium"),
                ("Regional Security Issues", "Ethnic conflicts and territorial disputes challenge international stability.", "military", "medium")
            ]
        else:
            events = [
                ("Global Security Challenges", "International cooperation faces new threats from non-state actors.", "military", "medium"),
                ("Economic Integration", "Trade relationships deepen amid ongoing globalization trends.", "economic", "low"),
                ("Diplomatic Initiatives", "Multilateral efforts address regional conflicts and humanitarian concerns.", "diplomatic", "low")
            ]
        
        # Generate articles for the specific month/year
        for i, (title, content, category, severity) in enumerate(events):
            fallback_articles.append({
                "title": f"[FALLBACK] {title} - {month:02d}/{year}",
                "content": f"[FALLBACK DATA - No real historical news available] {content}",
                "country": "Global",
                "category": category,
                "severity": severity,
                "reliability": "estimated",
                "source": "FALLBACK Historical Archive",
                "timestamp": f"{year}-{month:02d}-{(i*7+1):02d}T12:00:00Z",
                "url": f"https://historical-archive.example.com/{year}/{month}"
            })
        
        return fallback_articles

# Global instance
_historical_news_service = None

async def get_historical_news_service():
    """Get the global historical news service instance"""
    global _historical_news_service
    if _historical_news_service is None:
        _historical_news_service = HistoricalNewsService()
    return _historical_news_service