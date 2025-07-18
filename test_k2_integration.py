#!/usr/bin/env python3
"""K2集成測試"""

import asyncio
import sys
sys.path.append('.')
from k2_provider_final import k2_provider

async def test_k2():
    """測試K2功能"""
    
    test_cases = [
        "什麼是Python？",
        "寫一個快速排序算法",
        "解釋async/await的工作原理"
    ]
    
    print("🧪 測試K2集成")
    print("-"*40)
    
    for query in test_cases:
        print(f"\n查詢: {query}")
        
        result = await k2_provider.chat([
            {"role": "user", "content": query}
        ])
        
        if result['success']:
            print(f"✅ 成功 ({result['latency_ms']:.0f}ms)")
            print(f"響應: {result['content'][:100]}...")
        else:
            print(f"❌ 失敗: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_k2())
