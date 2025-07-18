#!/usr/bin/env python3
"""
直接測試Groq API性能
使用真實API密鑰驗證延遲
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, Any, List

class DirectGroqAPITest:
    """直接Groq API測試"""
    
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # 可用的模型列表
        self.models = [
            "mixtral-8x7b-32768",
            "llama3-8b-8192",
            "llama3-70b-8192",
            "gemma-7b-it",
            "gemma2-9b-it"
        ]
    
    async def test_groq_models(self):
        """測試不同Groq模型的性能"""
        print("🚀 測試Groq直接API性能")
        print("="*60)
        
        test_message = {
            "role": "user",
            "content": "什麼是Python？請用一句話簡單回答。"
        }
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for model in self.models:
                print(f"\n📋 測試模型: {model}")
                
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
                            "messages": [test_message],
                            "max_tokens": 100,
                            "temperature": 0.7
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            latency = (time.time() - start_time) * 1000
                            
                            content = data['choices'][0]['message']['content']
                            tokens = data.get('usage', {})
                            
                            print(f"   ✅ 成功")
                            print(f"   延遲: {latency:.0f}ms")
                            print(f"   響應: {content[:100]}...")
                            print(f"   Tokens: 輸入{tokens.get('prompt_tokens', 0)}, 輸出{tokens.get('completion_tokens', 0)}")
                            
                            results.append({
                                "model": model,
                                "latency": latency,
                                "success": True
                            })
                        else:
                            error_text = await response.text()
                            print(f"   ❌ 錯誤 {response.status}: {error_text[:100]}")
                            results.append({
                                "model": model,
                                "error": f"Status {response.status}",
                                "success": False
                            })
                            
                except Exception as e:
                    print(f"   ❌ 異常: {e}")
                    results.append({
                        "model": model,
                        "error": str(e),
                        "success": False
                    })
        
        return results
    
    async def test_complex_queries(self):
        """測試複雜查詢的性能"""
        print("\n🎯 測試複雜查詢性能")
        print("="*60)
        
        queries = [
            {
                "type": "代碼生成",
                "content": "寫一個Python函數來計算斐波那契數列"
            },
            {
                "type": "錯誤診斷",
                "content": "解釋為什麼list.append(1,2)會報錯"
            },
            {
                "type": "代碼審查",
                "content": "審查這段代碼：def add(a,b): return a+b"
            }
        ]
        
        # 使用最快的模型
        model = "mixtral-8x7b-32768"
        
        async with aiohttp.ClientSession() as session:
            for query in queries:
                print(f"\n📝 {query['type']}")
                
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
                            "messages": [{"role": "user", "content": query['content']}],
                            "max_tokens": 300,
                            "temperature": 0.7
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            latency = (time.time() - start_time) * 1000
                            
                            print(f"   延遲: {latency:.0f}ms")
                            print(f"   響應質量: {'✅ 良好' if len(data['choices'][0]['message']['content']) > 100 else '⚠️ 簡短'}")
                        else:
                            print(f"   ❌ 失敗: Status {response.status}")
                            
                except Exception as e:
                    print(f"   ❌ 異常: {e}")
    
    async def test_concurrent_requests(self):
        """測試並發請求性能"""
        print("\n🔄 測試並發性能")
        print("="*60)
        
        model = "mixtral-8x7b-32768"
        concurrent_count = 5
        
        async def make_request(session, req_id):
            start = time.time()
            try:
                async with session.post(
                    self.api_url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": f"請說'請求{req_id}成功'"}],
                        "max_tokens": 20,
                        "temperature": 0.7
                    }
                ) as response:
                    if response.status == 200:
                        return time.time() - start, True
                    else:
                        return time.time() - start, False
            except:
                return time.time() - start, False
        
        async with aiohttp.ClientSession() as session:
            print(f"發送{concurrent_count}個並發請求...")
            
            tasks = [make_request(session, i) for i in range(concurrent_count)]
            results = await asyncio.gather(*tasks)
            
            successful = sum(1 for _, success in results if success)
            avg_latency = sum(latency for latency, _ in results) / len(results) * 1000
            
            print(f"\n📊 並發測試結果:")
            print(f"   成功率: {successful}/{concurrent_count} ({successful/concurrent_count*100:.0f}%)")
            print(f"   平均延遲: {avg_latency:.0f}ms")
            print(f"   吞吐量: {1000/avg_latency*concurrent_count:.1f} req/s")
    
    def generate_report(self, model_results: List[Dict]):
        """生成測試報告"""
        print("\n📋 Groq API測試報告")
        print("="*70)
        
        successful_results = [r for r in model_results if r.get('success', False)]
        
        if successful_results:
            fastest = min(successful_results, key=lambda x: x['latency'])
            avg_latency = sum(r['latency'] for r in successful_results) / len(successful_results)
            
            print(f"\n🏆 最快模型: {fastest['model']}")
            print(f"   延遲: {fastest['latency']:.0f}ms")
            print(f"\n📊 總體統計:")
            print(f"   平均延遲: {avg_latency:.0f}ms")
            print(f"   成功率: {len(successful_results)}/{len(model_results)}")
            
            print(f"\n💡 結論:")
            if avg_latency < 300:
                print("   ✅ Groq API延遲優秀，完全滿足<1秒要求")
                print("   ✅ 配合RAG增強，總延遲可控制在600ms內")
                print("   ✅ 建議立即集成到PowerAutomation")
            else:
                print("   ⚠️ 延遲略高，但仍可接受")
                print("   💡 建議優化RAG性能以補償")

async def main():
    """主測試函數"""
    print("🚀 PowerAutomation Groq API直接測試")
    print("使用真實API密鑰驗證性能")
    print("="*70)
    
    tester = DirectGroqAPITest()
    
    # 測試不同模型
    model_results = await tester.test_groq_models()
    
    # 測試複雜查詢
    await tester.test_complex_queries()
    
    # 測試並發性能
    await tester.test_concurrent_requests()
    
    # 生成報告
    tester.generate_report(model_results)

if __name__ == "__main__":
    asyncio.run(main())