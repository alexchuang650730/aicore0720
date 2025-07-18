#!/usr/bin/env python3
"""快速測試K2 Providers"""

import os
import asyncio
import aiohttp
import time

async def test_groq():
    """測試Groq API"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    start = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                latency = (time.time() - start) * 1000
                print(f"✅ Groq: {latency:.0f}ms")
            else:
                print(f"❌ Groq: {response.status}")

async def test_moonshot():
    """測試Moonshot API"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['MOONSHOT_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "moonshot-v1-8k",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 10
    }
    
    start = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                latency = (time.time() - start) * 1000
                print(f"✅ Moonshot: {latency:.0f}ms")
            else:
                print(f"❌ Moonshot: {response.status}")

async def main():
    print("🚀 快速測試K2 Providers")
    print("="*40)
    await asyncio.gather(test_groq(), test_moonshot())

if __name__ == "__main__":
    asyncio.run(main())
