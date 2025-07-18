#!/usr/bin/env python3
"""
深入測試Claude Router透明切換能力
驗證真實的無感切換效果
"""

import asyncio
import time
import os
import json
from typing import Dict, List, Any

class ClaudeRouterDeepTest:
    """Claude Router透明切換深度測試"""
    
    def __init__(self):
        self.test_results = []
        
    async def test_transparent_switching(self):
        """測試透明切換的實際效果"""
        print("🔄 測試透明切換效果")
        print("="*60)
        
        # 測試場景：用戶以為在用Claude，實際使用K2
        test_cases = [
            {
                "scenario": "簡單問答",
                "user_input": "什麼是Python裝飾器？",
                "user_expectation": "Claude級別的詳細解釋",
                "switching_requirement": "K2需要提供同等質量回答"
            },
            {
                "scenario": "代碼生成",
                "user_input": "寫一個Python二分搜索函數",
                "user_expectation": "完整、正確的代碼實現",
                "switching_requirement": "K2生成的代碼質量要接近Claude"
            },
            {
                "scenario": "代碼審查",
                "user_input": "審查這段代碼：def add(a,b): return a+b",
                "user_expectation": "專業的代碼審查建議",
                "switching_requirement": "K2提供有價值的審查意見"
            },
            {
                "scenario": "錯誤診斷",
                "user_input": "為什麼會報錯：list.append(1, 2)",
                "user_expectation": "準確的錯誤解釋和修復建議",
                "switching_requirement": "K2能準確識別並解釋錯誤"
            }
        ]
        
        from huggingface_hub import InferenceClient
        os.environ['HF_TOKEN'] = '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'
        client = InferenceClient(provider='groq', api_key=os.environ['HF_TOKEN'])
        
        results = []
        
        for test in test_cases:
            print(f"\n📋 場景: {test['scenario']}")
            print(f"   用戶期望: {test['user_expectation']}")
            
            try:
                # 測試K2響應
                start_time = time.time()
                
                completion = client.chat.completions.create(
                    model='moonshotai/Kimi-K2-Instruct',
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一個專業的編程助手，請提供詳細、準確的回答。"
                        },
                        {
                            "role": "user",
                            "content": test['user_input']
                        }
                    ],
                    max_tokens=800
                )
                
                k2_response = completion.choices[0].message.content
                response_time = time.time() - start_time
                
                # 評估響應質量
                quality_score = self._evaluate_response_quality(k2_response, test['user_expectation'])
                
                print(f"   K2響應時間: {response_time:.2f}s")
                print(f"   響應質量評分: {quality_score:.2f}/10")
                print(f"   響應預覽: {k2_response[:150]}...")
                
                # 判斷是否能透明切換
                can_switch = quality_score >= 7.0 and response_time < 5.0
                print(f"   可否透明切換: {'✅ 是' if can_switch else '❌ 否'}")
                
                results.append({
                    "scenario": test['scenario'],
                    "quality_score": quality_score,
                    "response_time": response_time,
                    "can_switch": can_switch,
                    "k2_response_length": len(k2_response)
                })
                
            except Exception as e:
                print(f"   ❌ 測試失敗: {e}")
                results.append({
                    "scenario": test['scenario'],
                    "error": str(e)
                })
        
        return results
    
    def _evaluate_response_quality(self, response: str, expectation: str) -> float:
        """評估響應質量（0-10分）"""
        score = 5.0  # 基礎分
        
        # 長度評分
        if len(response) > 200:
            score += 1.0
        if len(response) > 400:
            score += 0.5
            
        # 結構評分
        if any(marker in response for marker in ['1.', '2.', '-', '```']):
            score += 1.0
            
        # 專業性評分
        professional_terms = ['函數', '參數', '返回', '變量', '類型', '方法', 'function', 'parameter', 'return', 'variable']
        term_count = sum(1 for term in professional_terms if term in response.lower())
        score += min(term_count * 0.3, 1.5)
        
        # 完整性評分
        if '例如' in response or 'example' in response.lower() or '```' in response:
            score += 1.0
            
        return min(score, 10.0)
    
    async def test_error_recovery(self):
        """測試錯誤恢復和回退機制"""
        print("\n🔧 測試錯誤恢復機制")
        print("="*50)
        
        error_scenarios = [
            {
                "name": "API超時",
                "simulate": "timeout",
                "expected_behavior": "自動回退到Claude或重試"
            },
            {
                "name": "K2返回空響應",
                "simulate": "empty_response",
                "expected_behavior": "檢測並回退"
            },
            {
                "name": "K2響應質量太低",
                "simulate": "low_quality",
                "expected_behavior": "質量檢查後回退"
            }
        ]
        
        for scenario in error_scenarios:
            print(f"\n❌ 模擬: {scenario['name']}")
            print(f"   期望行為: {scenario['expected_behavior']}")
            
            # 這裡應該測試實際的Router錯誤處理
            # 但由於沒有部署實際的Router，只能模擬
            
            if scenario['simulate'] == 'timeout':
                print("   模擬結果: Router應該在3秒後超時並回退")
            elif scenario['simulate'] == 'empty_response':
                print("   模擬結果: Router應該檢測空響應並重試或回退")
            elif scenario['simulate'] == 'low_quality':
                print("   模擬結果: Router應該有質量閾值檢查")
    
    async def test_user_experience_consistency(self):
        """測試用戶體驗一致性"""
        print("\n👤 測試用戶體驗一致性")
        print("="*50)
        
        # 關鍵體驗指標
        experience_metrics = {
            "響應速度": {
                "claude_baseline": "2-3秒",
                "k2_actual": None,
                "acceptable_range": "1-5秒"
            },
            "響應格式": {
                "claude_baseline": "結構化、專業",
                "k2_actual": None,
                "acceptable_range": "至少有基本結構"
            },
            "錯誤處理": {
                "claude_baseline": "友好、建設性",
                "k2_actual": None,
                "acceptable_range": "能識別並解釋錯誤"
            },
            "代碼質量": {
                "claude_baseline": "可運行、規範",
                "k2_actual": None,
                "acceptable_range": "基本正確"
            }
        }
        
        # 實際測試一個完整交互
        from huggingface_hub import InferenceClient
        client = InferenceClient(provider='groq', api_key=os.environ['HF_TOKEN'])
        
        print("\n🔍 實際體驗測試:")
        
        test_interaction = "幫我優化這段代碼：\nfor i in range(len(arr)):\n    for j in range(len(arr)):\n        if arr[i] > arr[j]:\n            arr[i], arr[j] = arr[j], arr[i]"
        
        try:
            start_time = time.time()
            
            completion = client.chat.completions.create(
                model='moonshotai/Kimi-K2-Instruct',
                messages=[{"role": "user", "content": test_interaction}],
                max_tokens=800
            )
            
            response = completion.choices[0].message.content
            response_time = time.time() - start_time
            
            # 更新實際指標
            experience_metrics["響應速度"]["k2_actual"] = f"{response_time:.2f}秒"
            
            # 檢查響應格式
            has_structure = any(marker in response for marker in ['1.', '2.', '```', '-'])
            experience_metrics["響應格式"]["k2_actual"] = "有結構" if has_structure else "無結構"
            
            # 檢查是否包含優化建議
            has_optimization = any(word in response.lower() for word in ['優化', '改進', '建議', 'better', 'improve'])
            experience_metrics["代碼質量"]["k2_actual"] = "有優化建議" if has_optimization else "無優化建議"
            
            print(f"K2響應時間: {response_time:.2f}秒")
            print(f"響應結構化: {'✅' if has_structure else '❌'}")
            print(f"包含優化建議: {'✅' if has_optimization else '❌'}")
            
        except Exception as e:
            print(f"測試失敗: {e}")
        
        # 顯示對比結果
        print("\n📊 體驗一致性對比:")
        for metric, data in experience_metrics.items():
            print(f"\n{metric}:")
            print(f"  Claude基準: {data['claude_baseline']}")
            print(f"  K2實際: {data['k2_actual'] or '未測試'}")
            print(f"  可接受範圍: {data['acceptable_range']}")
            
            # 判斷是否達標
            if data['k2_actual']:
                if metric == "響應速度":
                    acceptable = response_time < 5.0
                elif metric == "響應格式":
                    acceptable = "有結構" in str(data['k2_actual'])
                else:
                    acceptable = data['k2_actual'] != "無優化建議"
                
                print(f"  達標: {'✅' if acceptable else '❌'}")
    
    async def test_cost_benefit_reality(self):
        """測試實際的成本效益"""
        print("\n💰 測試實際成本效益")
        print("="*50)
        
        # 基於實際定價計算
        pricing = {
            "k2": {
                "input": 2.0,   # 2元/M tokens
                "output": 8.0   # 8元/M tokens
            },
            "claude": {
                "input": 15.0,  # 15元/M tokens
                "output": 75.0  # 75元/M tokens
            }
        }
        
        # 模擬不同規模使用
        usage_scenarios = [
            {"name": "個人開發者", "daily_requests": 50, "avg_tokens": 1000},
            {"name": "小團隊", "daily_requests": 200, "avg_tokens": 1500},
            {"name": "中型公司", "daily_requests": 1000, "avg_tokens": 2000}
        ]
        
        print("📊 30天成本對比（人民幣）:")
        
        for scenario in usage_scenarios:
            total_tokens = scenario['daily_requests'] * scenario['avg_tokens'] * 30
            
            # 假設輸入輸出各占50%
            input_tokens = total_tokens * 0.4
            output_tokens = total_tokens * 0.6
            
            k2_cost = (input_tokens * pricing['k2']['input'] + 
                      output_tokens * pricing['k2']['output']) / 1000000
            
            claude_cost = (input_tokens * pricing['claude']['input'] + 
                          output_tokens * pricing['claude']['output']) / 1000000
            
            savings = claude_cost - k2_cost
            savings_rate = (savings / claude_cost) * 100
            
            print(f"\n{scenario['name']}:")
            print(f"  K2成本: ¥{k2_cost:.2f}")
            print(f"  Claude成本: ¥{claude_cost:.2f}")
            print(f"  節省: ¥{savings:.2f} ({savings_rate:.1f}%)")
            
            # 但要考慮透明切換的實際情況
            if savings_rate > 50:
                print(f"  💡 實際節省需考慮：")
                print(f"     - 部分複雜任務仍需Claude")
                print(f"     - K2可能需要更多tokens達到同等效果")
                print(f"     - 實際節省可能為: {savings_rate * 0.7:.1f}%")
    
    async def generate_deep_router_report(self, switching_results):
        """生成Claude Router深度分析報告"""
        print("\n📋 Claude Router透明切換深度分析報告")
        print("="*70)
        
        # 分析切換成功率
        switchable = [r for r in switching_results if r.get('can_switch', False)]
        switch_rate = len(switchable) / len(switching_results) if switching_results else 0
        
        print(f"\n1️⃣ 透明切換可行性:")
        print(f"   可切換場景: {len(switchable)}/{len(switching_results)} ({switch_rate:.1%})")
        
        # 分析質量分數
        avg_quality = sum(r.get('quality_score', 0) for r in switching_results) / len(switching_results) if switching_results else 0
        print(f"   平均質量分數: {avg_quality:.1f}/10")
        
        # 分析響應時間
        avg_time = sum(r.get('response_time', 0) for r in switching_results if 'response_time' in r) / len([r for r in switching_results if 'response_time' in r]) if switching_results else 0
        print(f"   平均響應時間: {avg_time:.2f}秒")
        
        print(f"\n2️⃣ 場景分析:")
        for result in switching_results:
            if 'error' not in result:
                print(f"   {result['scenario']}: {'✅ 可切換' if result['can_switch'] else '❌ 不可切換'} (質量: {result['quality_score']:.1f}/10)")
        
        print(f"\n3️⃣ 關鍵發現:")
        if switch_rate >= 0.7:
            print("   ✅ 大部分場景可以透明切換")
        elif switch_rate >= 0.5:
            print("   ⚠️ 部分場景可以切換，需要智能路由")
        else:
            print("   ❌ 透明切換效果不理想")
        
        if avg_quality >= 7.0:
            print("   ✅ K2響應質量接近Claude水平")
        elif avg_quality >= 5.0:
            print("   ⚠️ K2響應質量尚可，但有差距")
        else:
            print("   ❌ K2響應質量明顯不足")
        
        return {
            "switch_rate": switch_rate,
            "avg_quality": avg_quality,
            "avg_response_time": avg_time
        }

async def main():
    """主測試函數"""
    print("🚀 Claude Router透明切換深度測試")
    print("驗證真實的無感切換效果")
    print("="*70)
    
    tester = ClaudeRouterDeepTest()
    
    # 1. 測試透明切換
    switching_results = await tester.test_transparent_switching()
    
    # 2. 測試錯誤恢復
    await tester.test_error_recovery()
    
    # 3. 測試用戶體驗一致性
    await tester.test_user_experience_consistency()
    
    # 4. 測試成本效益
    await tester.test_cost_benefit_reality()
    
    # 5. 生成深度報告
    report = await tester.generate_deep_router_report(switching_results)
    
    print("\n🎯 最終結論:")
    if report['switch_rate'] >= 0.6 and report['avg_quality'] >= 6.0:
        print("✅ Claude Router可以實現有效的透明切換")
        print("✅ 簡單到中等複雜度任務可以無感切換到K2")
        print("✅ 用戶可以享受顯著的成本節省")
        print("⚠️ 複雜任務建議保留Claude處理")
    else:
        print("❌ 透明切換效果未達預期")
        print("⚠️ 需要更智能的路由策略")
        print("🔧 建議優化K2響應質量後再部署")

if __name__ == "__main__":
    asyncio.run(main())