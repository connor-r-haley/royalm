#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
import openai

load_dotenv()

async def test_chatgpt():
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API Key exists: {bool(api_key)}")
    print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")
    
    if not api_key:
        print("No API key found!")
        return
    
    try:
        openai.api_key = api_key
        client = openai.OpenAI()
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello World' in JSON format: {\"message\": \"Hello World\"}"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        content = response.choices[0].message.content
        print(f"Response: {content}")
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_chatgpt())

