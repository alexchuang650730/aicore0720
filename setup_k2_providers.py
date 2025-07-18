#!/usr/bin/env python3
"""
設置K2 Provider環境
配置所有可用的API密鑰
"""

import os
import json
from pathlib import Path

def setup_k2_providers():
    """設置K2 Provider環境變量和配置"""
    
    print("🔧 設置PowerAutomation K2 Providers")
    print("="*60)
    
    # API密鑰配置
    api_keys = {
        "GROQ_API_KEY": "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",
        "MOONSHOT_API_KEY": "sk-ocQ1YiAJtB2yfaXVXFzkW0973MXXKLR0OCEi0BbVqqmc31UK",
        "HF_TOKEN": "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",
        "ANTHROPIC_API_KEY": "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"
    }
    
    # 設置環境變量
    for key, value in api_keys.items():
        os.environ[key] = value
        print(f"✅ 設置 {key}")
    
    # 創建配置文件
    config = {
        "k2_providers": {
            "primary": {
                "name": "groq",
                "model": "llama-3.1-8b-instant",
                "expected_latency_ms": 313,
                "api_key_env": "GROQ_API_KEY"
            },
            "fallback": {
                "name": "moonshot",
                "model": "kimi-k2-instruct",
                "expected_latency_ms": 420,
                "api_key_env": "MOONSHOT_API_KEY"
            }
        },
        "rag_config": {
            "max_latency_ms": 200,
            "cache_enabled": True,
            "parallel_processing": True
        },
        "performance_targets": {
            "total_latency_ms": 600,
            "cost_savings_percent": 90,
            "user_satisfaction_percent": 95
        }
    }
    
    # 保存配置
    config_path = Path("k2_provider_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 配置保存到: {config_path}")
    
    # 創建快速測試腳本
    test_script = '''#!/usr/bin/env python3
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
'''
    
    test_path = Path("quick_test_k2.py")
    with open(test_path, 'w') as f:
        f.write(test_script)
    os.chmod(test_path, 0o755)
    
    print(f"✅ 測試腳本: {test_path}")
    
    # 顯示下一步
    print("\n📋 下一步行動:")
    print("1. 運行快速測試: python3 quick_test_k2.py")
    print("2. 完善RAG系統性能優化")
    print("3. 實現智能路由和故障轉移")
    print("4. 7/30前完成集成測試")
    
    print("\n🎯 預期效果:")
    print("- Groq主力: ~313ms延遲")
    print("- Moonshot備用: ~420ms延遲")
    print("- RAG增強: ~200ms")
    print("- 總延遲: <600ms ✅")
    print("- 成本節省: >90% ✅")

if __name__ == "__main__":
    setup_k2_providers()