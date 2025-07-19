#!/usr/bin/env python3
"""
固定場景基準測試 - 基於你的核心固定需求
專注於最常用的開發場景，避免複雜的瀏覽器自動化
"""

import json
import time
from typing import Dict, List, Any
from real_time_comparison_tracker import quick_claude_log, add_k2_test, show_stats

class FixedScenarioBenchmark:
    """固定場景基準測試"""
    
    def __init__(self):
        self.core_scenarios = self._define_core_scenarios()
        
    def _define_core_scenarios(self) -> List[Dict]:
        """定義你的核心固定需求場景"""
        return [
            {
                "id": "react_hook_form",
                "name": "React Hook表單管理",
                "prompt": "創建React自定義Hook管理表單狀態，包含驗證、提交、錯誤處理",
                "manus_satisfaction": 8,
                "category": "frontend",
                "complexity": "medium",
                "frequency": "每日",
                "importance": "核心",
                "typical_use": "Web應用表單開發"
            },
            {
                "id": "python_api_design", 
                "name": "Python API設計",
                "prompt": "使用FastAPI創建RESTful API，包含認證、CRUD操作、錯誤處理",
                "manus_satisfaction": 9,
                "category": "backend",
                "complexity": "medium",
                "frequency": "每日",
                "importance": "核心",
                "typical_use": "後端API開發"
            },
            {
                "id": "algorithm_optimization",
                "name": "算法性能優化",
                "prompt": "優化Python算法性能，處理大數據集，包含時間複雜度分析",
                "manus_satisfaction": 9,
                "category": "algorithm",
                "complexity": "medium",
                "frequency": "每週", 
                "importance": "重要",
                "typical_use": "性能優化任務"
            },
            {
                "id": "database_query_opt",
                "name": "數據庫查詢優化",
                "prompt": "優化複雜SQL查詢，添加索引建議，處理大量數據的分頁",
                "manus_satisfaction": 8,
                "category": "database", 
                "complexity": "medium",
                "frequency": "每週",
                "importance": "重要",
                "typical_use": "數據庫性能調優"
            },
            {
                "id": "component_architecture",
                "name": "組件架構設計",
                "prompt": "設計可復用的React/Vue組件，包含props接口、事件處理、樣式系統",
                "manus_satisfaction": 8,
                "category": "frontend",
                "complexity": "medium",
                "frequency": "每週",
                "importance": "重要", 
                "typical_use": "組件庫開發"
            },
            {
                "id": "error_debugging",
                "name": "錯誤調試修復",
                "prompt": "分析和修復JavaScript/Python運行時錯誤，包含堆棧追蹤分析",
                "manus_satisfaction": 9,
                "category": "debugging",
                "complexity": "simple",
                "frequency": "每日",
                "importance": "核心",
                "typical_use": "日常調試工作"
            },
            {
                "id": "docker_deployment",
                "name": "Docker部署配置",
                "prompt": "為應用創建Docker配置，包含多階段構建、環境變量、健康檢查",
                "manus_satisfaction": 7,
                "category": "devops",
                "complexity": "medium",
                "frequency": "每月",
                "importance": "重要",
                "typical_use": "應用部署"
            },
            {
                "id": "code_refactoring",
                "name": "代碼重構優化",
                "prompt": "重構遺留代碼，提高可讀性和可維護性，遵循最佳實踐",
                "manus_satisfaction": 8,
                "category": "refactoring",
                "complexity": "medium",
                "frequency": "每週",
                "importance": "重要",
                "typical_use": "代碼質量改進"
            }
        ]
    
    def setup_baseline_tests(self) -> List[str]:
        """設置基準測試 - 記錄Manus 1000小時經驗作為基準"""
        print("🎯 固定場景基準測試設置")
        print("基於你的核心固定開發需求")
        print("=" * 50)
        
        comparison_ids = []
        
        for scenario in self.core_scenarios:
            print(f"\n📋 設置: {scenario['name']}")
            print(f"   使用頻率: {scenario['frequency']}")
            print(f"   重要程度: {scenario['importance']}")
            print(f"   Manus滿意度: {scenario['manus_satisfaction']}/10")
            
            # 估算響應時間
            time_estimate = {
                "simple": 20.0,
                "medium": 35.0,
                "complex": 60.0
            }.get(scenario['complexity'], 35.0)
            
            comparison_id = quick_claude_log(
                prompt=scenario['prompt'],
                response=f"[Manus 1000小時基準] {scenario['typical_use']}",
                satisfaction=scenario['manus_satisfaction'],
                time_seconds=time_estimate,
                category=scenario['category'],
                complexity=scenario['complexity'],
                notes=f"核心場景 | 頻率: {scenario['frequency']} | 重要性: {scenario['importance']}"
            )
            
            scenario['comparison_id'] = comparison_id
            comparison_ids.append(comparison_id)
        
        print(f"\n✅ 已設置 {len(comparison_ids)} 個核心場景基準測試")
        return comparison_ids
    
    def manual_k2_test_session(self) -> None:
        """手動K2測試會話 - 逐一測試核心場景"""
        print("\n🧪 手動K2測試會話")
        print("針對你的核心固定需求進行K2測試")
        print("-" * 40)
        
        # 確保基準測試已設置
        if not any('comparison_id' in s for s in self.core_scenarios):
            print("⚠️ 基準測試未設置，先設置基準...")
            self.setup_baseline_tests()
        
        # 按重要程度排序
        sorted_scenarios = sorted(
            self.core_scenarios,
            key=lambda x: (x['importance'] == '核心', x['frequency'] == '每日'),
            reverse=True
        )
        
        print(f"\n📋 核心場景列表 (按重要性排序):")
        for i, scenario in enumerate(sorted_scenarios):
            status = "🔴" if scenario['importance'] == '核心' else "🟡"
            print(f"{i+1:2d}. {status} {scenario['name']} ({scenario['frequency']})")
        
        try:
            choice = int(input(f"\n選擇要測試的場景 (1-{len(sorted_scenarios)}): ")) - 1
            
            if 0 <= choice < len(sorted_scenarios):
                selected = sorted_scenarios[choice]
                self._conduct_k2_test(selected)
            else:
                print("❌ 無效選擇")
                
        except (ValueError, KeyboardInterrupt):
            print("\n👋 測試會話結束")
    
    def _conduct_k2_test(self, scenario: Dict) -> None:
        """執行單個K2測試"""
        print(f"\n🧪 測試場景: {scenario['name']}")
        print(f"📝 Prompt: {scenario['prompt']}")
        print(f"📊 Manus基準: {scenario['manus_satisfaction']}/10")
        print(f"🎯 典型用途: {scenario['typical_use']}")
        
        print(f"\n請使用此prompt測試K2，然後輸入結果:")
        print("-" * 40)
        
        try:
            k2_satisfaction = int(input("K2滿意度 (1-10): "))
            k2_time = float(input("K2響應時間 (秒): "))
            k2_notes = input("K2測試備註 (簡短): ")
            
            # 記錄K2測試結果
            add_k2_test(
                comparison_id=scenario['comparison_id'],
                k2_response=f"[K2測試] 滿意度: {k2_satisfaction}/10",
                k2_satisfaction=k2_satisfaction,
                k2_time=k2_time,
                notes=k2_notes
            )
            
            # 即時分析
            gap = scenario['manus_satisfaction'] - k2_satisfaction
            gap_percent = (gap / scenario['manus_satisfaction']) * 100
            
            print(f"\n📊 即時分析:")
            print(f"   質量差距: {gap:.1f} 分 ({gap_percent:.1f}%)")
            
            if gap <= 1:
                print("   🟢 K2質量接近Manus，可以使用")
            elif gap <= 2:
                print("   🟡 K2質量可接受，成本優勢明顯")
            else:
                print("   🔴 K2質量不足，建議使用Manus/Claude")
            
        except ValueError:
            print("❌ 輸入格式錯誤")
    
    def batch_k2_simulation(self) -> None:
        """批量K2測試模擬 - 基於預估的K2表現"""
        print("\n🔄 批量K2測試模擬")
        print("基於benchmark分析的預估K2表現")
        
        # 確保基準測試已設置
        if not any('comparison_id' in s for s in self.core_scenarios):
            self.setup_baseline_tests()
        
        # 基於scenario複雜度和類別的K2預估表現
        k2_estimates = {
            "react_hook_form": {"satisfaction": 6, "time": 25.0, "notes": "基本功能正確但缺少高級驗證"},
            "python_api_design": {"satisfaction": 7, "time": 30.0, "notes": "API結構正確但缺少安全考量"},
            "algorithm_optimization": {"satisfaction": 7, "time": 20.0, "notes": "算法正確但優化不足"},
            "database_query_opt": {"satisfaction": 6, "time": 25.0, "notes": "查詢正確但缺少高級優化策略"},
            "component_architecture": {"satisfaction": 6, "time": 28.0, "notes": "基本組件設計但缺少複用性考量"},
            "error_debugging": {"satisfaction": 8, "time": 15.0, "notes": "調試能力強，簡單問題處理好"},
            "docker_deployment": {"satisfaction": 6, "time": 22.0, "notes": "基本Docker配置但缺少生產優化"},
            "code_refactoring": {"satisfaction": 5, "time": 35.0, "notes": "重構建議基礎，缺少深度分析"}
        }
        
        print(f"\n正在模擬 {len(self.core_scenarios)} 個場景的K2測試...")
        
        for scenario in self.core_scenarios:
            estimate = k2_estimates.get(scenario['id'], {
                "satisfaction": 6,
                "time": 30.0, 
                "notes": "K2基本表現"
            })
            
            add_k2_test(
                comparison_id=scenario['comparison_id'],
                k2_response=f"[K2模擬] 滿意度: {estimate['satisfaction']}/10",
                k2_satisfaction=estimate['satisfaction'],
                k2_time=estimate['time'],
                notes=f"模擬測試: {estimate['notes']}"
            )
            
            print(f"✅ {scenario['name']}: K2={estimate['satisfaction']}/10 vs Manus={scenario['manus_satisfaction']}/10")
        
        print(f"\n📊 批量模擬完成!")
    
    def generate_strategy_report(self) -> Dict[str, Any]:
        """生成策略報告"""
        print("\n📋 生成PowerAutomation策略報告")
        
        # 獲取統計數據
        from real_time_comparison_tracker import RealTimeComparisonTracker
        tracker = RealTimeComparisonTracker()
        stats = tracker.get_statistics()
        
        if stats['summary']['comparison_records'] == 0:
            return {"error": "需要先執行K2測試"}
        
        # 分析結果
        claude_avg = stats['summary']['claude_avg_satisfaction']
        k2_avg = stats['summary']['k2_avg_satisfaction']
        quality_gap = stats['summary']['quality_gap']
        
        # 策略建議
        strategy = {
            "overall_assessment": "",
            "routing_strategy": {},
            "cost_optimization": {},
            "product_positioning": {}
        }
        
        # 整體評估
        gap_percentage = (quality_gap / claude_avg) * 100 if claude_avg > 0 else 0
        
        if gap_percentage <= 15:
            strategy["overall_assessment"] = "K2質量優秀，可以大膽推廣K2優先策略"
        elif gap_percentage <= 25:
            strategy["overall_assessment"] = "K2質量良好，適合混合策略"
        elif gap_percentage <= 35:
            strategy["overall_assessment"] = "K2質量可接受，需要智能路由優化"
        else:
            strategy["overall_assessment"] = "K2質量不足，建議保守策略"
        
        # 路由策略
        by_category = stats.get('by_category', {})
        for category, claude_score in by_category.get('claude', {}).items():
            k2_score = by_category.get('k2', {}).get(category, 0)
            if k2_score > 0:
                gap = claude_score - k2_score
                if gap <= 1:
                    strategy["routing_strategy"][category] = "K2優先"
                elif gap <= 2:
                    strategy["routing_strategy"][category] = "K2默認，Claude備用"
                else:
                    strategy["routing_strategy"][category] = "Claude優先"
        
        # 成本優化
        estimated_k2_usage = sum(1 for cat, rec in strategy["routing_strategy"].items() if "K2" in rec)
        total_categories = len(strategy["routing_strategy"])
        k2_percentage = (estimated_k2_usage / total_categories * 100) if total_categories > 0 else 0
        
        strategy["cost_optimization"] = {
            "estimated_k2_usage": f"{k2_percentage:.0f}%",
            "estimated_cost_saving": f"{k2_percentage * 0.9:.0f}%",
            "quality_retention": f"{100 - gap_percentage:.0f}%"
        }
        
        # 產品定位
        if gap_percentage <= 20:
            strategy["product_positioning"] = {
                "primary": "智能成本優化的Claude Code Tool界面",
                "secondary": f"K2提供{100-gap_percentage:.0f}% Claude質量，{k2_percentage*0.9:.0f}%成本節省",
                "target": "成本敏感的開發團隊"
            }
        else:
            strategy["product_positioning"] = {
                "primary": "增強Claude Code Tool體驗的智能界面",
                "secondary": "提供可選的成本優化方案", 
                "target": "注重開發效率的團隊"
            }
        
        print(f"\n📊 策略分析完成:")
        print(f"   質量差距: {gap_percentage:.1f}%")
        print(f"   K2使用比例: {k2_percentage:.0f}%")
        print(f"   預估成本節省: {k2_percentage*0.9:.0f}%")
        print(f"   整體評估: {strategy['overall_assessment']}")
        
        return strategy

def main():
    """主函數"""
    print("🎯 固定場景基準測試")
    print("基於你的核心固定開發需求")
    print("=" * 50)
    
    benchmark = FixedScenarioBenchmark()
    
    print("\n選擇操作:")
    print("1. 設置基準測試 (Manus 1000小時經驗)")
    print("2. 手動K2測試會話")
    print("3. 批量K2測試模擬")
    print("4. 查看統計報告")
    print("5. 生成策略報告")
    
    try:
        choice = input("\n輸入選擇 (1-5): ")
        
        if choice == "1":
            benchmark.setup_baseline_tests()
            
        elif choice == "2":
            benchmark.manual_k2_test_session()
            
        elif choice == "3":
            benchmark.batch_k2_simulation()
            
        elif choice == "4":
            show_stats()
            
        elif choice == "5":
            strategy = benchmark.generate_strategy_report()
            print(f"\n📋 策略報告已生成")
            
        else:
            print("❌ 無效選擇")
            
    except KeyboardInterrupt:
        print("\n👋 程序結束")

if __name__ == "__main__":
    main()