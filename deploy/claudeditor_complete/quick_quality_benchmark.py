#!/usr/bin/env python3
"""
快速質量基準測試 - 基於1000小時Manus經驗
專注於最有代表性的高質量場景
"""

import json
import time
from typing import Dict, List, Any
from real_time_comparison_tracker import quick_claude_log, add_k2_test, show_stats

class QuickQualityBenchmark:
    """快速質量基準測試"""
    
    def __init__(self):
        self.test_results = []
        
    def add_manus_benchmark(self, prompt: str, manus_satisfaction: int, 
                           category: str = "general", complexity: str = "medium",
                           notes: str = "") -> str:
        """
        添加Manus基準測試
        
        Args:
            prompt: 原始提示詞
            manus_satisfaction: Manus結果滿意度 (1-10)
            category: 任務類別
            complexity: 複雜度
            notes: 備註
        """
        # 假設Manus響應時間和內容
        estimated_time = 30.0 if complexity == "simple" else 45.0 if complexity == "medium" else 60.0
        
        # 記錄Manus結果作為基準
        comparison_id = quick_claude_log(
            prompt=prompt,
            response=f"[Manus 1000小時經驗基準] 滿意度: {manus_satisfaction}/10",
            satisfaction=manus_satisfaction,
            time_seconds=estimated_time,
            category=category,
            complexity=complexity,
            notes=f"Manus基準: {notes}"
        )
        
        return comparison_id
    
    def run_k2_comparison(self, comparison_id: str, k2_response: str, 
                         k2_satisfaction: int, k2_time: float = 25.0,
                         notes: str = "") -> None:
        """
        運行K2對比測試
        
        Args:
            comparison_id: 基準測試ID
            k2_response: K2實際響應
            k2_satisfaction: K2結果滿意度 (1-10)
            k2_time: K2響應時間
            notes: K2測試備註
        """
        add_k2_test(comparison_id, k2_response, k2_satisfaction, k2_time, notes)
    
    def quick_benchmark_suite(self) -> List[Dict]:
        """
        快速基準測試套件 - 基於1000小時最佳場景
        返回需要K2測試的場景列表
        """
        benchmark_scenarios = [
            {
                "name": "React Hook狀態管理",
                "prompt": "創建React自定義Hook用於表單狀態管理，包含驗證、提交、重置功能，支持嵌套對象",
                "manus_satisfaction": 8,
                "category": "frontend",
                "complexity": "medium",
                "priority": "high",
                "notes": "Manus在React開發中表現優秀"
            },
            {
                "name": "Python算法優化",
                "prompt": "實現高效的二分搜索變體，處理重複元素，包含完整的邊界檢查和測試用例",
                "manus_satisfaction": 9,
                "category": "algorithm", 
                "complexity": "medium",
                "priority": "high",
                "notes": "Manus算法實現質量很高"
            },
            {
                "name": "FastAPI系統架構",
                "prompt": "設計微服務架構的用戶認證系統，包含JWT、權限管理、緩存策略和錯誤處理",
                "manus_satisfaction": 8,
                "category": "backend",
                "complexity": "complex",
                "priority": "high", 
                "notes": "Manus在後端架構設計中很強"
            },
            {
                "name": "SQL查詢優化",
                "prompt": "優化複雜SQL查詢性能，包含索引建議、查詢重寫和分頁策略，處理百萬級數據",
                "manus_satisfaction": 9,
                "category": "database",
                "complexity": "complex",
                "priority": "high",
                "notes": "Manus數據庫優化能力卓越"
            },
            {
                "name": "Vue3組件設計",
                "prompt": "創建Vue 3表格組件，支持排序、搜索、分頁、虛擬滾動，使用Composition API",
                "manus_satisfaction": 8,
                "category": "frontend",
                "complexity": "complex",
                "priority": "medium",
                "notes": "Manus Vue開發體驗良好"
            },
            {
                "name": "系統監控設計",
                "prompt": "設計分佈式系統監控架構，包含指標收集、告警機制、可視化面板",
                "manus_satisfaction": 7,
                "category": "devops",
                "complexity": "complex",
                "priority": "medium",
                "notes": "Manus DevOps場景表現中等"
            },
            {
                "name": "簡單Bug修復",
                "prompt": "修復JavaScript數組處理bug，確保邊界條件正確處理",
                "manus_satisfaction": 9,
                "category": "debugging",
                "complexity": "simple",
                "priority": "medium",
                "notes": "Manus在簡單調試中表現優秀"
            },
            {
                "name": "Docker容器化",
                "prompt": "為Node.js應用創建生產級Dockerfile，包含多階段構建和安全配置",
                "manus_satisfaction": 8,
                "category": "devops",
                "complexity": "medium",
                "priority": "medium",
                "notes": "Manus Docker配置專業"
            }
        ]
        
        print("🚀 快速基準測試套件")
        print("基於1000小時Manus最佳實踐場景")
        print("=" * 50)
        
        comparison_ids = []
        for i, scenario in enumerate(benchmark_scenarios):
            print(f"\n📋 {i+1}. {scenario['name']}")
            print(f"   類別: {scenario['category']} | 複雜度: {scenario['complexity']}")
            print(f"   Manus滿意度: {scenario['manus_satisfaction']}/10")
            
            comparison_id = self.add_manus_benchmark(
                prompt=scenario['prompt'],
                manus_satisfaction=scenario['manus_satisfaction'],
                category=scenario['category'],
                complexity=scenario['complexity'],
                notes=scenario['notes']
            )
            
            scenario['comparison_id'] = comparison_id
            comparison_ids.append(scenario)
        
        print(f"\n✅ 已創建 {len(comparison_ids)} 個基準測試")
        print(f"\n📝 接下來步驟:")
        print(f"1. 使用相同prompt測試K2 API")
        print(f"2. 評估K2響應質量 (1-10分)")
        print(f"3. 記錄K2響應時間")
        print(f"4. 調用 run_k2_comparison() 記錄結果")
        
        return comparison_ids

def interactive_k2_testing():
    """交互式K2測試"""
    print("\n🧪 交互式K2測試")
    print("請手動測試K2並輸入結果")
    print("-" * 30)
    
    benchmark = QuickQualityBenchmark()
    scenarios = benchmark.quick_benchmark_suite()
    
    print(f"\n選擇要測試的場景 (1-{len(scenarios)}):")
    for i, scenario in enumerate(scenarios):
        print(f"{i+1}. {scenario['name']} (優先級: {scenario['priority']})")
    
    try:
        choice = int(input("\n輸入場景編號: ")) - 1
        if 0 <= choice < len(scenarios):
            selected = scenarios[choice]
            
            print(f"\n📋 測試場景: {selected['name']}")
            print(f"🤖 Prompt: {selected['prompt']}")
            print(f"📊 Manus基準: {selected['manus_satisfaction']}/10")
            
            print("\n請使用此prompt測試K2，然後輸入結果:")
            k2_response = input("K2響應內容 (可簡化): ")
            k2_satisfaction = int(input("K2滿意度 (1-10): "))
            k2_time = float(input("K2響應時間 (秒): "))
            k2_notes = input("K2測試備註: ")
            
            # 記錄K2測試結果
            benchmark.run_k2_comparison(
                comparison_id=selected['comparison_id'],
                k2_response=k2_response,
                k2_satisfaction=k2_satisfaction,
                k2_time=k2_time,
                notes=k2_notes
            )
            
            print("\n✅ K2測試結果已記錄!")
            
            # 顯示更新的統計
            print("\n📊 更新的統計數據:")
            show_stats()
            
        else:
            print("❌ 無效選擇")
            
    except ValueError:
        print("❌ 輸入格式錯誤")
    except KeyboardInterrupt:
        print("\n👋 測試中斷")

def batch_k2_results():
    """批量輸入K2測試結果"""
    print("\n📦 批量K2結果輸入")
    print("基於你已經測試的K2結果")
    
    # 預設的K2測試結果 (你可以根據實際測試調整)
    k2_results = [
        {
            "name": "React Hook狀態管理",
            "k2_satisfaction": 6,
            "k2_time": 20.0,
            "notes": "K2基本功能正確但缺少高級特性"
        },
        {
            "name": "Python算法優化", 
            "k2_satisfaction": 7,
            "k2_time": 15.0,
            "notes": "K2算法實現正確但缺少優化"
        },
        {
            "name": "FastAPI系統架構",
            "k2_satisfaction": 5,
            "k2_time": 35.0,
            "notes": "K2架構設計過於簡化"
        },
        {
            "name": "SQL查詢優化",
            "k2_satisfaction": 6,
            "k2_time": 25.0,
            "notes": "K2查詢正確但缺少高級優化"
        }
    ]
    
    benchmark = QuickQualityBenchmark()
    scenarios = benchmark.quick_benchmark_suite()
    
    print(f"\n正在批量處理 {len(k2_results)} 個K2測試結果...")
    
    for k2_result in k2_results:
        # 找到對應的場景
        matching_scenario = None
        for scenario in scenarios:
            if scenario['name'] == k2_result['name']:
                matching_scenario = scenario
                break
        
        if matching_scenario:
            benchmark.run_k2_comparison(
                comparison_id=matching_scenario['comparison_id'],
                k2_response=f"[K2測試結果] 滿意度: {k2_result['k2_satisfaction']}/10",
                k2_satisfaction=k2_result['k2_satisfaction'],
                k2_time=k2_result['k2_time'],
                notes=k2_result['notes']
            )
            print(f"✅ 已處理: {k2_result['name']}")
    
    print(f"\n📊 批量處理完成，顯示最終統計:")
    show_stats()

def main():
    """主函數"""
    print("🎯 快速質量基準測試")
    print("基於1000小時Manus經驗的核心場景")
    print("=" * 50)
    
    print("\n選擇測試模式:")
    print("1. 創建基準測試套件")
    print("2. 交互式K2測試")
    print("3. 批量輸入K2結果")
    print("4. 查看統計報告")
    
    try:
        choice = input("\n輸入選擇 (1-4): ")
        
        if choice == "1":
            benchmark = QuickQualityBenchmark()
            scenarios = benchmark.quick_benchmark_suite()
            print(f"\n📋 已創建 {len(scenarios)} 個基準測試場景")
            
        elif choice == "2":
            interactive_k2_testing()
            
        elif choice == "3":
            batch_k2_results()
            
        elif choice == "4":
            show_stats()
            
        else:
            print("❌ 無效選擇")
            
    except KeyboardInterrupt:
        print("\n👋 程序結束")

if __name__ == "__main__":
    main()