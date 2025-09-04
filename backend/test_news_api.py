#!/usr/bin/env python3
"""
News API Test Script
Tests connection and functionality of the News API integration.
"""

import os
import json
import ssl
import aiohttp
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('NEWS_API_KEY')
BASE_URL = "https://newsapi.org/v2"  # Changed from api.newsapi.org to newsapi.org

async def test_api_key():
    """Test if API key is configured and valid"""
    print("\n🔑 Testing API Key Configuration:")
    if not API_KEY:
        print("❌ No API key found in environment variables")
        print("   Please set NEWS_API_KEY in your .env file")
        return False
    print("✅ API key found")
    return True

async def test_api_connection():
    """Test basic connection to News API"""
    print("\n🌐 Testing API Connection:")
    try:
        # Create SSL context that doesn't verify certificates (for development)
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Test with a simple top headlines request
            url = f"{BASE_URL}/top-headlines"
            params = {
                "country": "us",
                "pageSize": 1
            }
            headers = {
                "X-Api-Key": API_KEY
            }
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    print("✅ Successfully connected to News API")
                    data = await response.json()
                    print(f"   Response status: {data.get('status')}")
                    return True
                else:
                    print(f"❌ API request failed with status {response.status}")
                    print(f"   Error: {await response.text()}")
                    return False
                
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

async def test_historical_search(year: int, month: int):
    """Test historical news search functionality"""
    print(f"\n📅 Testing Historical Search for {month}/{year}:")
    
    try:
        # Create date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Format dates for API
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        # Test with a single category
        test_category = "military"
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            url = f"{BASE_URL}/everything"
            params = {
                "q": test_category,
                "from": from_date,
                "to": to_date,
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": 10
            }
            headers = {
                "X-Api-Key": API_KEY
            }
            
            print(f"🔍 Searching for '{test_category}' articles between {from_date} and {to_date}")
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "ok":
                        articles = data.get("articles", [])
                        print(f"✅ Found {len(articles)} articles")
                        if articles:
                            print("\n📰 Sample Article:")
                            article = articles[0]
                            print(f"   Title: {article.get('title')}")
                            print(f"   Source: {article.get('source', {}).get('name')}")
                            print(f"   Date: {article.get('publishedAt')}")
                        return True
                    else:
                        print(f"❌ API returned error: {data.get('message')}")
                        return False
                else:
                    print(f"❌ Request failed with status {response.status}")
                    print(f"   Error: {await response.text()}")
                    return False
                
    except Exception as e:
        print(f"❌ Error during historical search: {str(e)}")
        return False

async def test_request_limits():
    """Test API request limits and quotas"""
    print("\n📊 Testing API Limits:")
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            url = f"{BASE_URL}/everything"
            headers = {
                "X-Api-Key": API_KEY
            }
            
            # Make a request that will show our quota info
            params = {
                "q": "test",
                "pageSize": 1
            }
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    # Check response headers for rate limit info
                    rate_limit = response.headers.get('X-RateLimit-Limit')
                    rate_remaining = response.headers.get('X-RateLimit-Remaining')
                    
                    if rate_limit and rate_remaining:
                        print(f"✅ Rate Limit: {rate_limit}")
                        print(f"✅ Remaining Requests: {rate_remaining}")
                    else:
                        print("⚠️ Rate limit information not found in headers")
                    
                    return True
                else:
                    print(f"❌ Request failed with status {response.status}")
                    return False
                
    except Exception as e:
        print(f"❌ Error checking rate limits: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Starting News API Tests...")
    
    # Test API key
    if not await test_api_key():
        return
    
    # Test basic connection
    if not await test_api_connection():
        return
    
    # Test historical search with recent date (within last 30 days)
    current_date = datetime.now()
    test_date = current_date - timedelta(days=7)  # Test 1 week ago
    await test_historical_search(test_date.year, test_date.month)
    
    # Test API limits
    await test_request_limits()
    
    print("\n✨ Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
