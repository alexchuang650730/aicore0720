"""
K2 Provider集成 - 專注於Moonshot K2
"""

import os
import aiohttp
import time
import logging

logger = logging.getLogger(__name__)

class K2Provider:
    """K2提供商 - 使用Moonshot API"""
    
    def __init__(self):
        self.api_key = os.environ.get('MOONSHOT_API_KEY', 'sk-ocQ1YiAJtB2yfaXVXFzkW0973MXXKLR0OCEi0BbVqqmc31UK')
        self.api_url = "https://api.moonshot.cn/v1/chat/completions"
        self.default_model = "moonshot-v1-8k"
        
    async def chat(self, messages, model=None, max_tokens=1000):
        """K2聊天接口"""
        model = model or self.default_model
        
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
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    latency = (time.time() - start_time) * 1000
                    
                    logger.info(f"K2響應成功: {latency:.0f}ms")
                    
                    return {
                        "success": True,
                        "content": result['choices'][0]['message']['content'],
                        "latency_ms": latency,
                        "model": model,
                        "usage": result.get('usage', {})
                    }
                else:
                    error = await response.text()
                    logger.error(f"K2響應失敗: {response.status} - {error}")
                    return {
                        "success": False,
                        "error": error
                    }

# 全局K2實例
k2_provider = K2Provider()
