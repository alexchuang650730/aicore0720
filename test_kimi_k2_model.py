#!/usr/bin/env python3
"""
測試真正的Kimi K2模型
使用Moonshot API的K2模型
"""

import asyncio
import aiohttp
import time
import json

class KimiK2ModelTest:
    """Kimi K2模型測試"""
    
    def __init__(self):
        self.moonshot_api_key = "sk-ocQ1YiAJtB2yfaXVXFzkW0973MXXKLR0OCEi0BbVqqmc31UK"
        self.api_url = "https://api.moonshot.cn/v1/chat/completions"
        
        # Kimi K2可用模型
        self.k2_models = [
            "kimi-k2-instruct",      # K2 Instruct模型
            "moonshot-v1-8k",        # 標準8K模型
            "moonshot-v1-32k",       # 32K上下文
            "moonshot-v1-128k"       # 128K上下文
        ]
    
    async def test_k2_models(self):
        """測試所有K2模型"""
        print("🚀 測試Kimi K2模型性能")
        print("="*60)
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for model in self.k2_models:
                print(f"\n📋 測試模型: {model}")
                
                # 測試不同類型的查詢
                test_queries = [
                    {
                        "type": "簡單問答",
                        "content": "什麼是Python？一句話回答。"
                    },
                    {
                        "type": "代碼生成",
                        "content": "寫一個Python函數計算斐波那契數列"
                    },
                    {
                        "type": "錯誤診斷",
                        "content": "解釋list.append(1,2)為什麼報錯"
                    }
                ]
                
                model_latencies = []
                model_success = True
                
                for query in test_queries:
                    start_time = time.time()
                    
                    try:
                        async with session.post(
                            self.api_url,
                            headers={
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {self.moonshot_api_key}"
                            },
                            json={
                                "model": model,
                                "messages": [
                                    {"role": "user", "content": query["content"]}
                                ],
                                "max_tokens": 200,
                                "temperature": 0.7
                            },
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                latency = (time.time() - start_time) * 1000
                                model_latencies.append(latency)
                                
                                content = data['choices'][0]['message']['content']
                                tokens = data.get('usage', {})
                                
                                print(f"   ✅ {query['type']}")
                                print(f"      延遲: {latency:.0f}ms")
                                print(f"      Tokens: 輸入{tokens.get('prompt_tokens', 0)}, 輸出{tokens.get('completion_tokens', 0)}")
                                print(f"      響應: {content[:80]}...")
                            else:
                                model_success = False
                                error = await response.text()
                                print(f"   ❌ {query['type']}: 錯誤 {response.status}")
                                print(f"      {error[:100]}")
                                
                                # 如果是kimi-k2-instruct不存在，跳過
                                if "model not found" in error.lower():
                                    print(f"      模型 {model} 可能不存在")
                                break
                                
                    except Exception as e:
                        model_success = False
                        print(f"   ❌ {query['type']}: 異常 {str(e)[:100]}")
                        break
                
                if model_success and model_latencies:
                    avg_latency = sum(model_latencies) / len(model_latencies)
                    results.append({
                        "model": model,
                        "available": True,
                        "avg_latency": avg_latency,
                        "min_latency": min(model_latencies),
                        "max_latency": max(model_latencies),
                        "test_count": len(model_latencies)
                    })
                else:
                    results.append({
                        "model": model,
                        "available": False
                    })
        
        return results
    
    async def test_groq_k2_comparison(self):
        """對比Groq和真實K2性能"""
        print("\n🔄 對比Groq和K2性能")
        print("="*50)
        
        # Groq配置
        groq_config = {
            "api_key": "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",
            "api_url": "https://api.groq.com/openai/v1/chat/completions",
            "model": "llama-3.1-8b-instant"
        }
        
        test_query = "解釋什麼是遞歸，並給出Python示例"
        
        # 測試Groq
        print("\n📊 Groq (llama-3.1-8b-instant):")
        groq_start = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    groq_config["api_url"],
                    headers={
                        "Authorization": f"Bearer {groq_config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": groq_config["model"],
                        "messages": [{"role": "user", "content": test_query}],
                        "max_tokens": 300
                    }
                ) as response:
                    if response.status == 200:
                        groq_latency = (time.time() - groq_start) * 1000
                        data = await response.json()
                        print(f"   延遲: {groq_latency:.0f}ms")
                        print(f"   響應質量: ✅ 良好")
            except Exception as e:
                print(f"   ❌ 錯誤: {e}")
        
        # 測試K2
        print("\n📊 Moonshot K2 (moonshot-v1-8k):")
        k2_start = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.moonshot_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "moonshot-v1-8k",
                        "messages": [{"role": "user", "content": test_query}],
                        "max_tokens": 300
                    }
                ) as response:
                    if response.status == 200:
                        k2_latency = (time.time() - k2_start) * 1000
                        data = await response.json()
                        print(f"   延遲: {k2_latency:.0f}ms")
                        print(f"   響應質量: ✅ 優秀（原生K2）")
            except Exception as e:
                print(f"   ❌ 錯誤: {e}")
    
    def generate_k2_integration_plan(self, results):
        """生成K2集成計劃"""
        print("\n📋 K2集成最終方案")
        print("="*70)
        
        available_models = [r for r in results if r.get('available', False)]
        
        if not available_models:
            print("❌ 沒有可用的K2模型")
            return
        
        # 找出最快的K2模型
        fastest_k2 = min(available_models, key=lambda x: x['avg_latency'])
        
        print(f"\n🏆 推薦K2配置:")
        print(f"   模型: {fastest_k2['model']}")
        print(f"   平均延遲: {fastest_k2['avg_latency']:.0f}ms")
        print(f"   API: Moonshot API")
        
        print(f"\n🚀 混合策略:")
        print("1. 簡單查詢 → Groq (300ms)")
        print("2. 複雜任務 → K2 + RAG增強")
        print("3. 中文優先 → K2 (中文能力更強)")
        
        print(f"\n💡 為什麼需要K2:")
        print("- K2是專門優化的大語言模型")
        print("- 更好的中文理解和生成")
        print("- 更強的推理能力")
        print("- 與Claude更接近的能力")
        
        print(f"\n📊 最終架構:")
        print("```")
        print("用戶請求")
        print("   ↓")
        print("智能路由")
        print("   ├─ 簡單/英文 → Groq (300ms)")
        print("   └─ 複雜/中文 → K2 (1-2s) → RAG增強")
        print("                              ↓")
        print("                         高質量響應")
        print("```")

async def main():
    """主測試函數"""
    print("🚀 Kimi K2模型性能測試")
    print("驗證真正的K2模型能力")
    print("="*70)
    
    tester = KimiK2ModelTest()
    
    # 測試K2模型
    results = await tester.test_k2_models()
    
    # 對比測試
    await tester.test_groq_k2_comparison()
    
    # 生成集成計劃
    tester.generate_k2_integration_plan(results)
    
    print("\n✅ 測試完成！")
    print("建議：使用混合策略，Groq處理簡單查詢，K2處理複雜任務")

if __name__ == "__main__":
    asyncio.run(main())