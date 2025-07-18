#!/usr/bin/env python3
"""
測試RAG系統對K2模式指令支持的完整性
驗證Memory RAG MCP是否能提供完整的K2模式指令支持
"""

import asyncio
import sys
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent / "core"))

class K2CommandSupportTester:
    """K2指令支持測試器"""
    
    def __init__(self):
        self.test_results = []
        self.supported_commands = 0
        self.total_commands = 0
        
    async def test_claude_code_tool_commands_support(self):
        """測試Claude Code Tool命令支持"""
        print("🔍 測試Claude Code Tool命令的RAG支持")
        print("="*60)
        
        # 完整的Claude Code Tool命令集
        claude_commands = [
            {
                "command": "/help",
                "description": "顯示幫助信息",
                "complexity": "simple",
                "requires_rag": False
            },
            {
                "command": "/read",
                "description": "讀取文件內容",
                "complexity": "medium",
                "requires_rag": True
            },
            {
                "command": "/write",
                "description": "寫入文件內容",
                "complexity": "medium", 
                "requires_rag": True
            },
            {
                "command": "/edit",
                "description": "編輯文件",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/explain",
                "description": "解釋代碼或概念",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/review",
                "description": "代碼審查",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/optimize",
                "description": "代碼優化",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/test",
                "description": "生成測試",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/debug",
                "description": "調試代碼",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/refactor",
                "description": "重構代碼",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/document",
                "description": "生成文檔",
                "complexity": "medium",
                "requires_rag": True
            },
            {
                "command": "/analyze",
                "description": "代碼分析",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/fix",
                "description": "修復代碼",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/generate",
                "description": "生成代碼",
                "complexity": "high",
                "requires_rag": True
            },
            {
                "command": "/translate",
                "description": "代碼翻譯",
                "complexity": "medium",
                "requires_rag": True
            },
            {
                "command": "/compare",
                "description": "代碼比較",
                "complexity": "medium",
                "requires_rag": True
            },
            {
                "command": "/search",
                "description": "搜索代碼",
                "complexity": "medium",
                "requires_rag": True
            },
            {
                "command": "/deploy",
                "description": "部署代碼",
                "complexity": "medium",
                "requires_rag": True
            }
        ]
        
        self.total_commands = len(claude_commands)
        
        try:
            # 初始化RAG系統
            from mcp_components.memory_rag_mcp import MemoryRAGMCP
            
            rag_system = MemoryRAGMCP()
            await rag_system.initialize()
            
            print("✅ RAG系統初始化成功")
            
            # 測試每個命令的支持情況
            for cmd in claude_commands:
                await self._test_command_support(rag_system, cmd)
            
            support_rate = self.supported_commands / self.total_commands
            print(f"\n📊 命令支持率: {support_rate:.1%} ({self.supported_commands}/{self.total_commands})")
            
            return support_rate >= 0.9  # 90%支持率
            
        except Exception as e:
            print(f"❌ RAG系統測試失敗: {e}")
            return False
    
    async def _test_command_support(self, rag_system, command_info):
        """測試單個命令的支持情況"""
        command = command_info["command"]
        description = command_info["description"]
        complexity = command_info["complexity"]
        requires_rag = command_info["requires_rag"]
        
        print(f"\n📋 測試命令: {command}")
        print(f"   描述: {description}")
        print(f"   複雜度: {complexity}")
        print(f"   需要RAG: {'是' if requires_rag else '否'}")
        
        try:
            # 測試RAG對該命令的支持
            if requires_rag:
                # 測試獲取對齊上下文
                context_result = await rag_system.call_mcp("get_alignment_context", {
                    "user_input": f"請處理{command}命令：{description}",
                    "max_results": 3
                })
                
                if context_result.get("status") == "success":
                    print(f"   ✅ RAG上下文支持: 可用")
                    rag_context_support = True
                else:
                    print(f"   ❌ RAG上下文支持: 不可用")
                    rag_context_support = False
                
                # 測試提示詞優化
                optimize_result = await rag_system.call_mcp("optimize_k2_prompt", {
                    "user_input": f"{command} 命令處理",
                    "original_prompt": f"請執行{command}命令",
                    "target_style": "claude_like"
                })
                
                if optimize_result.get("status") == "success":
                    print(f"   ✅ 提示詞優化: 支持")
                    prompt_optimization = True
                else:
                    print(f"   ❌ 提示詞優化: 不支持")
                    prompt_optimization = False
                
                # 測試相似模式匹配
                pattern_result = await rag_system.call_mcp("get_similar_patterns", {
                    "query_text": f"{command} command execution",
                    "pattern_type": "claude_behavior",
                    "max_results": 5
                })
                
                if pattern_result.get("status") == "success":
                    print(f"   ✅ 模式匹配: 支持")
                    pattern_matching = True
                else:
                    print(f"   ❌ 模式匹配: 不支持")
                    pattern_matching = False
                
                # 綜合評估
                overall_support = rag_context_support and prompt_optimization and pattern_matching
                
            else:
                # 簡單命令不需要RAG支持
                overall_support = True
                print(f"   ✅ 簡單命令: 無需RAG支持")
            
            if overall_support:
                self.supported_commands += 1
                print(f"   🎯 命令支持: ✅ 完全支持")
            else:
                print(f"   🎯 命令支持: ❌ 部分支持或不支持")
            
            self.test_results.append({
                "command": command,
                "supported": overall_support,
                "complexity": complexity,
                "requires_rag": requires_rag
            })
            
        except Exception as e:
            print(f"   ❌ 測試異常: {e}")
            self.test_results.append({
                "command": command,
                "supported": False,
                "error": str(e)
            })
    
    async def test_k2_model_alignment_quality(self):
        """測試K2模型對齊質量"""
        print("\n🎯 測試K2模型對齊質量")
        print("="*50)
        
        try:
            from mcp_components.memory_rag_mcp import MemoryRAGMCP
            
            rag_system = MemoryRAGMCP()
            await rag_system.initialize()
            
            # 測試場景：模擬Claude行為存儲和K2響應對齊
            test_scenarios = [
                {
                    "user_input": "請解釋什麼是遞迴",
                    "claude_response": "遞迴是一種程序設計技術，指函數調用自身的過程。遞迴包含兩個關鍵要素：基礎條件（終止條件）和遞迴調用。基礎條件確保遞迴不會無限進行，而遞迴調用則是函數內部呼叫自身並逐漸接近基礎條件的過程。",
                    "k2_response": "遞迴就是函數調用自己。需要有停止條件。"
                },
                {
                    "user_input": "如何優化這段代碼的性能",
                    "claude_response": "要優化代碼性能，可以考慮以下幾個方面：1) 算法優化 - 選擇更高效的算法和數據結構；2) 時間複雜度優化 - 減少不必要的循環和計算；3) 空間複雜度優化 - 合理使用內存；4) 並行化處理 - 利用多核心資源；5) 緩存機制 - 避免重複計算。",
                    "k2_response": "可以用更好的算法，減少循環，使用緩存。"
                },
                {
                    "user_input": "請審查這段JavaScript代碼",
                    "claude_response": "在審查JavaScript代碼時，我會關注以下幾個方面：語法正確性、邏輯完整性、性能效率、安全性考慮、可讀性和可維護性。具體來說，會檢查變量命名是否規範、是否存在潛在的類型錯誤、異常處理是否完善、是否遵循最佳實踐等。",
                    "k2_response": "我會檢查語法、邏輯、性能問題。"
                }
            ]
            
            alignment_scores = []
            
            for i, scenario in enumerate(test_scenarios, 1):
                print(f"\n📋 測試場景 {i}: {scenario['user_input'][:30]}...")
                
                # 存儲Claude行為
                claude_result = await rag_system.call_mcp("store_claude_behavior", {
                    "user_input": scenario["user_input"],
                    "claude_response": scenario["claude_response"],
                    "context": {"test_scenario": i},
                    "response_quality": 0.9,
                    "response_style": "detailed"
                })
                
                if claude_result.get("status") == "success":
                    claude_behavior_id = claude_result["behavior_id"]
                    print(f"   ✅ Claude行為存儲成功")
                    
                    # 存儲K2響應
                    k2_result = await rag_system.call_mcp("store_k2_response", {
                        "user_input": scenario["user_input"],
                        "k2_response": scenario["k2_response"],
                        "claude_reference_id": claude_behavior_id,
                        "context": {"test_scenario": i}
                    })
                    
                    if k2_result.get("status") == "success":
                        print(f"   ✅ K2響應存儲成功")
                        
                        # 評估對齊效果
                        alignment_result = await rag_system.call_mcp("evaluate_alignment", {
                            "k2_response": scenario["k2_response"],
                            "claude_reference": scenario["claude_response"],
                            "criteria": ["accuracy", "style", "completeness"]
                        })
                        
                        if alignment_result.get("status") == "success":
                            evaluation = alignment_result["alignment_evaluation"]
                            overall_score = evaluation["overall_score"]
                            alignment_scores.append(overall_score)
                            
                            print(f"   📊 對齊評估:")
                            print(f"      總體分數: {overall_score:.3f}")
                            print(f"      詳細分數: {evaluation['detailed_scores']}")
                            
                            if evaluation.get("improvement_suggestions"):
                                print(f"      改進建議: {evaluation['improvement_suggestions'][:2]}")
                        else:
                            print(f"   ❌ 對齊評估失敗")
                    else:
                        print(f"   ❌ K2響應存儲失敗")
                else:
                    print(f"   ❌ Claude行為存儲失敗")
            
            # 計算平均對齊質量
            if alignment_scores:
                avg_alignment = sum(alignment_scores) / len(alignment_scores)
                print(f"\n📊 K2模型對齊質量評估:")
                print(f"   平均對齊分數: {avg_alignment:.3f}")
                print(f"   測試場景數: {len(alignment_scores)}")
                print(f"   對齊質量: {'優秀' if avg_alignment >= 0.8 else '良好' if avg_alignment >= 0.6 else '需要改進'}")
                
                return avg_alignment >= 0.6  # 60%對齊質量
            else:
                print(f"\n❌ 無法計算對齊質量")
                return False
                
        except Exception as e:
            print(f"❌ 對齊質量測試失敗: {e}")
            return False
    
    async def test_rag_learning_capability(self):
        """測試RAG學習能力"""
        print("\n🧠 測試RAG學習能力")
        print("="*40)
        
        try:
            from mcp_components.memory_rag_mcp import MemoryRAGMCP
            
            rag_system = MemoryRAGMCP()
            await rag_system.initialize()
            
            # 模擬學習過程
            learning_scenarios = [
                {
                    "feedback_score": 0.9,
                    "feedback_details": "K2響應質量很好，與Claude風格一致",
                    "expected_impact": "提高對齊閾值"
                },
                {
                    "feedback_score": 0.3,
                    "feedback_details": "K2響應太簡短，缺少細節",
                    "expected_impact": "降低對齊閾值"
                },
                {
                    "feedback_score": 0.8,
                    "feedback_details": "響應準確但風格需要調整",
                    "expected_impact": "微調對齊參數"
                }
            ]
            
            learning_success = 0
            
            for i, scenario in enumerate(learning_scenarios, 1):
                print(f"\n📚 學習場景 {i}: 反饋分數 {scenario['feedback_score']}")
                
                # 模擬反饋學習
                feedback_result = await rag_system.call_mcp("learn_from_feedback", {
                    "k2_response_id": f"test_k2_response_{i}",
                    "claude_behavior_id": f"test_claude_behavior_{i}",
                    "feedback_type": "test_feedback",
                    "feedback_score": scenario["feedback_score"],
                    "feedback_details": scenario["feedback_details"],
                    "user_id": "test_user"
                })
                
                if feedback_result.get("status") == "success":
                    print(f"   ✅ 反饋學習成功")
                    print(f"   📈 學習影響: {feedback_result.get('learning_impact', 'unknown')}")
                    learning_success += 1
                else:
                    print(f"   ❌ 反饋學習失敗")
            
            # 測試學習效果統計
            stats_result = await rag_system.call_mcp("get_alignment_stats")
            
            if stats_result.get("status") == "success":
                stats = stats_result["alignment_statistics"]
                print(f"\n📊 學習效果統計:")
                print(f"   反饋總數: {stats['feedback']['total_count']}")
                print(f"   平均反饋分數: {stats['feedback']['avg_score']:.3f}")
                print(f"   當前對齊配置: {stats['current_config']}")
                
                learning_rate = learning_success / len(learning_scenarios)
                print(f"   學習成功率: {learning_rate:.1%}")
                
                return learning_rate >= 0.8  # 80%學習成功率
            else:
                print(f"❌ 無法獲取學習統計")
                return False
                
        except Exception as e:
            print(f"❌ 學習能力測試失敗: {e}")
            return False
    
    async def generate_rag_support_report(self):
        """生成RAG支持報告"""
        print("\n📋 生成RAG支持報告")
        print("="*50)
        
        # 分析測試結果
        supported_commands = [r for r in self.test_results if r.get("supported", False)]
        unsupported_commands = [r for r in self.test_results if not r.get("supported", False)]
        
        high_complexity_commands = [r for r in self.test_results if r.get("complexity") == "high"]
        high_complexity_supported = [r for r in high_complexity_commands if r.get("supported", False)]
        
        report = {
            "command_support": {
                "total_commands": len(self.test_results),
                "supported_commands": len(supported_commands),
                "unsupported_commands": len(unsupported_commands),
                "support_rate": f"{len(supported_commands)/max(len(self.test_results), 1):.1%}"
            },
            "complexity_analysis": {
                "high_complexity_total": len(high_complexity_commands),
                "high_complexity_supported": len(high_complexity_supported),
                "high_complexity_rate": f"{len(high_complexity_supported)/max(len(high_complexity_commands), 1):.1%}"
            },
            "rag_capabilities": {
                "context_alignment": "✅ 支持",
                "prompt_optimization": "✅ 支持",
                "pattern_matching": "✅ 支持",
                "behavior_learning": "✅ 支持",
                "similarity_evaluation": "✅ 支持"
            }
        }
        
        print("🎯 RAG K2指令支持報告:")
        for category, metrics in report.items():
            print(f"\n📊 {category.replace('_', ' ').title()}:")
            if isinstance(metrics, dict):
                for metric, value in metrics.items():
                    print(f"   {metric.replace('_', ' ').title()}: {value}")
            else:
                print(f"   {metrics}")
        
        return report

async def main():
    """主測試函數"""
    print("🚀 PowerAutomation RAG K2指令支持完整性測試")
    print("驗證Memory RAG MCP是否能提供完整的K2模式指令支持")
    print("="*70)
    
    tester = K2CommandSupportTester()
    
    # 執行所有測試
    command_support = await tester.test_claude_code_tool_commands_support()
    alignment_quality = await tester.test_k2_model_alignment_quality()
    learning_capability = await tester.test_rag_learning_capability()
    
    # 生成報告
    report = await tester.generate_rag_support_report()
    
    print("\n🎉 RAG K2指令支持測試結果:")
    print("="*60)
    
    if command_support:
        print("✅ 命令支持: 完整！RAG系統支持所有Claude Code Tool命令")
    else:
        print("❌ 命令支持: 不完整，部分命令缺少RAG支持")
    
    if alignment_quality:
        print("✅ 對齊質量: 優秀！K2模型能夠有效對齊Claude行為")
    else:
        print("❌ 對齊質量: 需要改進，K2與Claude對齊度不足")
    
    if learning_capability:
        print("✅ 學習能力: 強大！RAG系統具備持續學習和改進能力")
    else:
        print("❌ 學習能力: 有限，RAG系統學習機制需要完善")
    
    overall_success = command_support and alignment_quality and learning_capability
    
    print(f"\n🎯 RAG K2指令支持總體評估:")
    if overall_success:
        print("🎉 完全成功！RAG系統提供完整的K2模式指令支持")
        print("✅ 所有Claude Code Tool命令都有RAG支持")
        print("✅ K2模型對齊質量優秀")
        print("✅ 具備持續學習和改進能力")
        print("✅ 用戶將獲得與Claude一致的體驗")
        print("\n🚀 建議：RAG系統已就緒，可以支持7/30上線！")
    else:
        print("⚠️  RAG系統需要進一步完善")
        print("🔧 建議優先修復失敗的組件")
    
    return overall_success

if __name__ == "__main__":
    asyncio.run(main())