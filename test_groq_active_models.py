#!/usr/bin/env python3
"""
測試Groq當前活躍的模型
使用最新的模型列表
"""

import asyncio
import aiohttp
import time
import json

class GroqActiveModelsTest:
    """Groq活躍模型測試"""
    
    def __init__(self):
        self.api_key = "os.getenv("GROQ_API_KEY", "")"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # 2024年最新可用模型
        self.active_models = [
            "llama3-8b-8192",      # Meta Llama 3 8B
            "llama3-70b-8192",     # Meta Llama 3 70B
            "llama-3.1-70b-versatile",  # Llama 3.1 70B
            "llama-3.1-8b-instant",     # Llama 3.1 8B
            "gemma2-9b-it",        # Google Gemma 2 9B
            "mixtral-8x7b-32768"   # 可能已下線，但仍測試
        ]
    
    async def test_model_availability(self):
        """測試模型可用性和性能"""
        print("🚀 測試Groq當前可用模型")
        print("="*60)
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for model in self.active_models:
                print(f"\n📋 測試模型: {model}")
                
                # 簡單測試查詢
                test_queries = [
                    "Hi, say hello in Chinese",
                    "What is 2+2?",
                    "Write a Python hello world"
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
                                "Authorization": f"Bearer {self.api_key}"
                            },
                            json={
                                "model": model,
                                "messages": [{"role": "user", "content": query}],
                                "max_tokens": 50,
                                "temperature": 0.7
                            },
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                latency = (time.time() - start_time) * 1000
                                model_latencies.append(latency)
                                
                                if len(model_latencies) == 1:  # 只顯示第一個查詢的結果
                                    content = data['choices'][0]['message']['content']
                                    print(f"   ✅ 可用")
                                    print(f"   延遲: {latency:.0f}ms")
                                    print(f"   響應: {content[:50]}...")
                            else:
                                model_success = False
                                error = await response.text()
                                print(f"   ❌ 不可用: {error[:100]}")
                                break
                                
                    except asyncio.TimeoutError:
                        model_success = False
                        print(f"   ❌ 超時")
                        break
                    except Exception as e:
                        model_success = False
                        print(f"   ❌ 錯誤: {str(e)[:100]}")
                        break
                
                if model_success and model_latencies:
                    avg_latency = sum(model_latencies) / len(model_latencies)
                    results.append({
                        "model": model,
                        "available": True,
                        "avg_latency": avg_latency,
                        "min_latency": min(model_latencies),
                        "max_latency": max(model_latencies)
                    })
                else:
                    results.append({
                        "model": model,
                        "available": False
                    })
        
        return results
    
    async def test_best_model_performance(self, best_model: str):
        """深入測試最佳模型的性能"""
        print(f"\n🏆 深入測試最佳模型: {best_model}")
        print("="*60)
        
        test_scenarios = [
            {
                "name": "簡單問答",
                "prompt": "什麼是Python？用一句話回答。",
                "max_tokens": 50
            },
            {
                "name": "代碼生成",
                "prompt": "寫一個計算階乘的Python函數",
                "max_tokens": 150
            },
            {
                "name": "錯誤診斷",
                "prompt": "解釋list.append(1,2)為什麼會報錯",
                "max_tokens": 100
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for scenario in test_scenarios:
                print(f"\n📝 {scenario['name']}")
                
                start_time = time.time()
                
                try:
                    async with session.post(
                        self.api_url,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.api_key}"
                        },
                        json={
                            "model": best_model,
                            "messages": [{"role": "user", "content": scenario['prompt']}],
                            "max_tokens": scenario['max_tokens'],
                            "temperature": 0.7
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            latency = (time.time() - start_time) * 1000
                            
                            content = data['choices'][0]['message']['content']
                            tokens = data.get('usage', {})
                            
                            print(f"   延遲: {latency:.0f}ms")
                            print(f"   Tokens: 輸入{tokens.get('prompt_tokens', 0)}, 輸出{tokens.get('completion_tokens', 0)}")
                            print(f"   響應預覽: {content[:100]}...")
                            
                except Exception as e:
                    print(f"   ❌ 錯誤: {e}")
    
    def generate_recommendations(self, results):
        """生成推薦報告"""
        print("\n📊 Groq模型性能分析報告")
        print("="*70)
        
        available_models = [r for r in results if r.get('available', False)]
        
        if not available_models:
            print("❌ 沒有可用的模型！")
            return None
        
        # 按延遲排序
        available_models.sort(key=lambda x: x['avg_latency'])
        
        print("\n🏆 可用模型排名（按速度）:")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model['model']}")
            print(f"   平均延遲: {model['avg_latency']:.0f}ms")
            print(f"   延遲範圍: {model['min_latency']:.0f}-{model['max_latency']:.0f}ms")
        
        best_model = available_models[0]
        
        print(f"\n💡 推薦使用: {best_model['model']}")
        print(f"   理由: 最低平均延遲 {best_model['avg_latency']:.0f}ms")
        
        if best_model['avg_latency'] < 500:
            print("\n✅ 性能評估: 優秀")
            print("   - 延遲低於500ms，用戶體驗良好")
            print("   - 配合RAG增強，總延遲可控制在1秒內")
            print("   - 完全滿足PowerAutomation需求")
        else:
            print("\n⚠️ 性能評估: 需優化")
            print("   - 延遲略高，需要優化RAG性能")
            print("   - 考慮使用更激進的緩存策略")
        
        return best_model['model']

async def main():
    """主測試函數"""
    print("🚀 Groq活躍模型性能測試")
    print("找出最快的可用模型")
    print("="*70)
    
    tester = GroqActiveModelsTest()
    
    # 測試所有模型
    results = await tester.test_model_availability()
    
    # 生成推薦
    best_model = tester.generate_recommendations(results)
    
    # 深入測試最佳模型
    if best_model:
        await tester.test_best_model_performance(best_model)
    
    print("\n✅ 測試完成！")
    print("下一步：更新k2_provider_integration.py使用最佳模型")

if __name__ == "__main__":
    asyncio.run(main())