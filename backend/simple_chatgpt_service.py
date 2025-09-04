#!/usr/bin/env python3
"""
Simplified ChatGPT service that works around proxy issues
"""

import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleChatGPTService:
    """Simplified ChatGPT service using direct API calls"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        
    async def generate_response(self, messages, model="gpt-4", max_tokens=500):
        """Generate response using direct API call"""
        
        if not self.api_key:
            print("❌ No OpenAI API key configured")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
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
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        print(f"❌ API Error: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None
    
    async def select_and_summarize_news(self, news_articles):
        """Select the best 4 articles and summarize them"""
        
        if not news_articles:
            return []
        
        # Create a list of articles for ChatGPT to analyze
        articles_text = ""
        for i, article in enumerate(news_articles[:20]):  # Limit to first 20 for analysis
            articles_text += f"""
Article {i+1}:
Title: {article.title}
Summary: {article.summary}
Source: {article.source}
URL: {article.url}
Published: {article.published_date}
---
"""
        
        # Prompt for article selection
        selection_prompt = f"""
You are a geopolitical analyst selecting the most important news articles for a WW3 simulation.

From the following articles, select the 4 MOST geopolitically significant ones. Focus on:
- Major conflicts (Ukraine-Russia, China-Taiwan, etc.)
- Nuclear threats or military escalations
- Major diplomatic developments
- Economic sanctions or trade wars
- NATO or alliance developments

Articles to analyze:
{articles_text}

Respond with ONLY a JSON array of the 4 selected article numbers (1-20), like: [3, 7, 12, 15]
"""
        
        messages = [
            {"role": "system", "content": "You are a geopolitical analyst. Respond only with valid JSON."},
            {"role": "user", "content": selection_prompt}
        ]
        
        response = await self.generate_response(messages, max_tokens=100)
        
        if not response:
            print("❌ Failed to get article selection from ChatGPT")
            # Fallback: select first 4 articles
            return news_articles[:4]
        
        try:
            # Clean up the response - remove any markdown formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse the response to get selected article numbers
            selected_indices = json.loads(cleaned_response)
            selected_articles = [news_articles[i-1] for i in selected_indices if 1 <= i <= len(news_articles)]
            
            if len(selected_articles) < 4:
                # Fallback: add more articles if needed
                remaining = [a for a in news_articles if a not in selected_articles]
                selected_articles.extend(remaining[:4-len(selected_articles)])
            
            return selected_articles[:4]
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse ChatGPT response: {e}")
            print(f"Response was: {response}")
            # Try to extract numbers from the response as fallback
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                try:
                    selected_indices = [int(n) for n in numbers[:4]]
                    selected_articles = [news_articles[i-1] for i in selected_indices if 1 <= i <= len(news_articles)]
                    if len(selected_articles) >= 4:
                        return selected_articles[:4]
                except:
                    pass
            return news_articles[:4]
    
    async def summarize_article(self, article):
        """Summarize a single article"""
        
        prompt = f"""
CRITICAL: You are summarizing a REAL news article from {article.published_date}. DO NOT invent ANY fake information.

Original Article:
Title: {article.title}
Summary: {article.summary}
Source: {article.source}
URL: {article.url}
Published: {article.published_date}

STRICT RULES:
- ONLY use information that is EXPLICITLY mentioned in the original article
- DO NOT mention ANY politicians (Biden, Trump, Putin, Xi Jinping, Zelensky, etc.) unless they are actually in the original article
- DO NOT mention ANY events that are not in the original article
- DO NOT mention Ukraine, Russia, China, or any countries unless they are actually in the original article
- DO NOT invent fake meetings, summits, or diplomatic events
- If the original article is about Evergrande, only talk about Evergrande
- If the original article is about France/US relations, only talk about that
- Keep the EXACT same factual information, just shorter

Please provide:
1. A headline that directly reflects the original article title
2. A summary that only contains facts from the original article
3. The original URL

Format as JSON:
{{
    "headline": "Headline based ONLY on original article",
    "summary": "Summary containing ONLY facts from original article",
    "url": "{article.url}"
}}
"""
        
        messages = [
            {"role": "system", "content": "You are a STRICT news summarizer. You ONLY summarize what is EXPLICITLY in the original article. NEVER invent fake politicians, fake events, or fake countries. If the original article doesn't mention Ukraine, don't mention Ukraine. If it doesn't mention Biden, don't mention Biden. ONLY use facts from the original article. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.generate_response(messages, max_tokens=300)
        
        if not response:
            # Fallback to original content
            return {
                "headline": article.title,
                "summary": article.summary,
                "url": article.url
            }
        
        try:
            # Clean up the response - remove any markdown formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse ChatGPT response
            if '{' in cleaned_response and '}' in cleaned_response:
                json_start = cleaned_response.find('{')
                json_end = cleaned_response.rfind('}') + 1
                json_str = cleaned_response[json_start:json_end]
                summary_data = json.loads(json_str)
                
                return {
                    "headline": summary_data.get("headline", article.title),
                    "summary": summary_data.get("summary", article.summary),
                    "url": summary_data.get("url", article.url)
                }
            else:
                # Fallback if JSON parsing fails
                return {
                    "headline": article.title,
                    "summary": article.summary,
                    "url": article.url
                }
        except Exception as e:
            print(f"❌ Failed to parse article summary: {e}")
            print(f"Response was: {response}")
            # Fallback if parsing fails
            return {
                "headline": article.title,
                "summary": article.summary,
                "url": article.url
            }

# Global instance
_simple_chatgpt_service = None

async def get_simple_chatgpt_service():
    """Get the global simple ChatGPT service instance"""
    global _simple_chatgpt_service
    if _simple_chatgpt_service is None:
        _simple_chatgpt_service = SimpleChatGPTService()
    return _simple_chatgpt_service
