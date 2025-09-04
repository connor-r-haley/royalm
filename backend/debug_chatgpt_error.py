#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
import openai
import json

load_dotenv()

async def debug_chatgpt():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("No API key found!")
        return
    
    try:
        openai.api_key = api_key
        client = openai.OpenAI()
        
        prompt = """
Generate a realistic news article about United States in the context of diplomatic events.

Country: United States
Event Type: diplomatic
Impact Level: 75/100

Requirements:
- Make it specific to United States and current world events
- Reference real leaders and places when possible
- Make it unpredictable but realistic
- Keep it public-facing (not classified intelligence)
- Use a realistic news source

Return ONLY valid JSON in this exact format:
{
    "headline": "Specific headline about United States",
    "content": "2-3 sentences with specific details about United States and diplomatic",
    "source": "Realistic news source name",
    "severity": "high/medium/low",
    "reliability": "confirmed/likely/unconfirmed",
    "stat_changes": {
        "economy": "+2/-2",
        "military": "+2/-2",
        "diplomacy": "+2/-2",
        "morale": "+2/-2"
    }
}
"""
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a psychohistorian and geopolitical analyst. Generate realistic, unpredictable news articles based on deep patterns of human behavior and civilization dynamics."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        print("Full API Response:")
        print(json.dumps(response.model_dump(), indent=2))
        
        print("\n" + "="*50)
        print("Content field:")
        content = response.choices[0].message.content
        print(content)
        
        # Try to access description field
        print("\n" + "="*50)
        print("Trying to access 'description' field...")
        try:
            description = response.description
            print(f"Description: {description}")
        except AttributeError as e:
            print(f"AttributeError: {e}")
        except KeyError as e:
            print(f"KeyError: {e}")
        except Exception as e:
            print(f"Other error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_chatgpt())

