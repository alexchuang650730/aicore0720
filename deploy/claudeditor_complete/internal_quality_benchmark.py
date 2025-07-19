#!/usr/bin/env python3
"""
PowerAutomation 內部質量基準測試
Claude Code Tool vs K2輸出質量對比
我們自己就是最嚴格的用戶
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import aiohttp
import re

logger = logging.getLogger(__name__)

@dataclass
class CodeTest:
    """代碼測試案例"""
    name: str
    prompt: str
    expected_language: str
    complexity_level: str  # simple, medium, complex
    test_category: str  # algorithm, web_dev, data_processing, system_design

@dataclass
class QualityScore:
    """質量評分"""
    correctness: float  # 0-10 正確性
    completeness: float  # 0-10 完整性
    style: float  # 0-10 代碼風格
    performance: float  # 0-10 性能考量
    documentation: float  # 0-10 文檔和註釋
    total: float  # 總分

class InternalBenchmarkTester:
    """內部基準測試器"""
    
    def __init__(self):
        self.claude_api_key = None  # 需要設置
        self.k2_api_key = None      # 需要設置
        self.test_results = []
        
        # 定義測試案例
        self.test_cases = self._create_test_cases()
        
    def _create_test_cases(self) -> List[CodeTest]:
        """創建測試案例庫"""
        return [
            # 簡單算法題
            CodeTest(
                name="二分搜索實現",
                prompt="實現一個二分搜索算法，要求包含完整的錯誤處理和邊界檢查",
                expected_language="python",
                complexity_level="simple",
                test_category="algorithm"
            ),
            
            # Web開發
            CodeTest(
                name="React Todo應用",
                prompt="創建一個React Todo應用，包含添加、刪除、標記完成功能，使用TypeScript和現代React hooks",
                expected_language="typescript",
                complexity_level="medium",
                test_category="web_dev"
            ),
            
            # 系統設計
            CodeTest(
                name="分佈式緩存設計",
                prompt="設計一個分佈式緩存系統，考慮一致性、分區容錯和可用性，提供Python實現",
                expected_language="python", 
                complexity_level="complex",
                test_category="system_design"
            ),
            
            # 數據處理
            CodeTest(
                name="時間序列分析",
                prompt="編寫Python代碼分析股票價格時間序列，包括移動平均、趨勢分析和可視化",
                expected_language="python",
                complexity_level="medium", 
                test_category="data_processing"
            ),
            
            # API設計
            CodeTest(
                name="RESTful API設計",
                prompt="使用FastAPI創建一個用戶管理API，包含認證、授權、CRUD操作和API文檔",
                expected_language="python",
                complexity_level="medium",
                test_category="web_dev"
            ),
            
            # 前端組件
            CodeTest(
                name="可復用表格組件",
                prompt="創建一個可復用的React表格組件，支持排序、分頁、搜索和自定義列，使用TypeScript",
                expected_language="typescript",
                complexity_level="complex",
                test_category="web_dev"
            ),
            
            # 算法優化
            CodeTest(
                name="最短路徑算法",
                prompt="實現Dijkstra算法解決最短路徑問題，要求O(V log V)時間複雜度，包含完整測試",
                expected_language="python",
                complexity_level="complex",
                test_category="algorithm"
            ),
            
            # 數據庫設計
            CodeTest(
                name="電商數據庫設計",
                prompt="設計電商平台數據庫架構，包含用戶、商品、訂單表結構和優化的SQL查詢",
                expected_language="sql",
                complexity_level="medium",
                test_category="system_design"
            ),
            
            # DevOps自動化
            CodeTest(
                name="CI/CD流水線",
                prompt="創建GitHub Actions工作流，實現自動測試、構建和部署到AWS，包含環境變量管理",
                expected_language="yaml",
                complexity_level="medium",
                test_category="web_dev"
            ),
            
            # 性能優化
            CodeTest(
                name="大數據處理優化",
                prompt="優化處理10億條記錄的Python程序，使用多進程、內存映射和批處理技術",
                expected_language="python",
                complexity_level="complex",
                test_category="data_processing"
            )
        ]
    
    async def run_full_benchmark(self) -> Dict[str, Any]:
        """運行完整基準測試"""
        print("🚀 開始PowerAutomation內部質量基準測試")
        print(f"📊 測試案例數量: {len(self.test_cases)}")
        print("=" * 60)
        
        results = []
        
        for i, test_case in enumerate(self.test_cases):
            print(f"\n🧪 測試 {i+1}/{len(self.test_cases)}: {test_case.name}")
            print(f"📝 類別: {test_case.test_category} | 複雜度: {test_case.complexity_level}")
            
            # 同時測試Claude和K2
            claude_result = await self._test_claude_output(test_case)
            k2_result = await self._test_k2_output(test_case)
            
            # 評分對比
            comparison = self._compare_outputs(test_case, claude_result, k2_result)
            results.append(comparison)
            
            # 實時輸出結果
            self._print_comparison_result(comparison)
            
            # 短暫延遲避免API限制
            await asyncio.sleep(2)
        
        # 生成總結報告
        summary = self._generate_summary_report(results)
        self._print_final_report(summary)
        
        return {
            "test_results": results,
            "summary": summary,
            "timestamp": time.time()
        }
    
    async def _test_claude_output(self, test_case: CodeTest) -> Dict[str, Any]:
        """測試Claude Code Tool輸出"""
        try:
            # 模擬Claude API調用
            # 實際實現需要真實的Claude API
            print("   🤖 正在測試Claude Code Tool...")
            
            # 這裡應該是真實的Claude API調用
            claude_response = await self._mock_claude_api(test_case.prompt)
            
            return {
                "success": True,
                "response": claude_response,
                "response_time": 2.5,
                "model": "claude-3-sonnet"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }
    
    async def _test_k2_output(self, test_case: CodeTest) -> Dict[str, Any]:
        """測試K2輸出"""
        try:
            print("   🎯 正在測試K2模型...")
            
            # 這裡應該是真實的K2 API調用
            k2_response = await self._mock_k2_api(test_case.prompt)
            
            return {
                "success": True,
                "response": k2_response,
                "response_time": 1.8,
                "model": "moonshot-v1"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }
    
    async def _mock_claude_api(self, prompt: str) -> str:
        """模擬Claude API（實際使用時替換為真實API）"""
        # 這是模擬輸出，實際測試時需要真實API
        if "二分搜索" in prompt:
            return '''```python
def binary_search(arr, target):
    """
    二分搜索算法實現
    
    Args:
        arr: 已排序的數組
        target: 目標值
        
    Returns:
        int: 目標值的索引，如果不存在返回-1
    """
    if not arr:
        return -1
    
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# 測試案例
def test_binary_search():
    assert binary_search([1, 2, 3, 4, 5], 3) == 2
    assert binary_search([1, 2, 3, 4, 5], 6) == -1
    assert binary_search([], 1) == -1
    assert binary_search([1], 1) == 0
    print("所有測試通過!")

if __name__ == "__main__":
    test_binary_search()
```'''
        else:
            return "# Claude 模擬輸出\n# 完整、專業的代碼實現..."
    
    async def _mock_k2_api(self, prompt: str) -> str:
        """模擬K2 API（實際使用時替換為真實API）"""
        if "二分搜索" in prompt:
            return '''```python
def binary_search(nums, target):
    """二分搜索實現"""
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# 測試
arr = [1,2,3,4,5]
print(binary_search(arr, 3))  # 輸出: 2
```'''
        else:
            return "# K2 模擬輸出\n# 功能正確但可能不夠完整的代碼..."
    
    def _compare_outputs(self, test_case: CodeTest, claude_result: Dict, k2_result: Dict) -> Dict[str, Any]:
        """對比兩個輸出的質量"""
        
        # 評分Claude輸出
        claude_score = self._score_output(claude_result.get("response", ""), test_case)
        
        # 評分K2輸出  
        k2_score = self._score_output(k2_result.get("response", ""), test_case)
        
        # 計算質量差距
        quality_gap = claude_score.total - k2_score.total
        gap_percentage = (quality_gap / claude_score.total) * 100 if claude_score.total > 0 else 0
        
        return {
            "test_case": test_case.name,
            "category": test_case.test_category,
            "complexity": test_case.complexity_level,
            "claude_score": claude_score,
            "k2_score": k2_score,
            "quality_gap": quality_gap,
            "gap_percentage": gap_percentage,
            "k2_acceptable": k2_score.total >= 7.0,  # 我們的接受標準
            "response_time_comparison": {
                "claude": claude_result.get("response_time", 0),
                "k2": k2_result.get("response_time", 0)
            }
        }
    
    def _score_output(self, output: str, test_case: CodeTest) -> QualityScore:
        """評分代碼輸出質量（我們作為專家的評分）"""
        
        # 基於我們的經驗評分
        correctness = self._score_correctness(output, test_case)
        completeness = self._score_completeness(output, test_case)
        style = self._score_style(output)
        performance = self._score_performance(output, test_case)
        documentation = self._score_documentation(output)
        
        total = (correctness + completeness + style + performance + documentation) / 5
        
        return QualityScore(
            correctness=correctness,
            completeness=completeness,
            style=style,
            performance=performance,
            documentation=documentation,
            total=total
        )
    
    def _score_correctness(self, output: str, test_case: CodeTest) -> float:
        """評分正確性"""
        if not output or len(output) < 50:
            return 1.0
        
        # 檢查是否包含代碼塊
        has_code = "```" in output or "def " in output or "function " in output
        if not has_code:
            return 3.0
        
        # 檢查語法正確性（簡化版）
        if test_case.expected_language == "python":
            if "def " in output and ":" in output:
                return 8.5  # Claude通常語法正確
            return 6.0
        
        return 7.5  # 默認分數
    
    def _score_completeness(self, output: str, test_case: CodeTest) -> float:
        """評分完整性"""
        completeness_indicators = [
            "import" in output or "from " in output,  # 導入語句
            "def " in output or "function " in output,  # 函數定義
            "test" in output.lower() or "assert" in output,  # 測試代碼
            "if __name__" in output,  # 主程序入口
            len(output) > 200  # 足夠的代碼量
        ]
        
        score = sum(completeness_indicators) * 2
        return min(score, 10.0)
    
    def _score_style(self, output: str) -> float:
        """評分代碼風格"""
        style_indicators = [
            '"""' in output or "'''" in output,  # 文檔字符串
            "# " in output,  # 註釋
            "\n\n" in output,  # 適當的空行
            not re.search(r'\w{50,}', output),  # 沒有過長的變量名
        ]
        
        score = sum(style_indicators) * 2.5
        return min(score, 10.0)
    
    def _score_performance(self, output: str, test_case: CodeTest) -> float:
        """評分性能考量"""
        if test_case.complexity_level == "simple":
            return 8.0  # 簡單任務性能要求不高
        
        performance_indicators = [
            "O(" in output,  # 時間複雜度分析
            "optimize" in output.lower() or "efficient" in output.lower(),
            "cache" in output.lower() or "memo" in output.lower(),
        ]
        
        base_score = 6.0
        bonus = sum(performance_indicators) * 1.3
        return min(base_score + bonus, 10.0)
    
    def _score_documentation(self, output: str) -> float:
        """評分文檔和註釋"""
        doc_indicators = [
            '"""' in output or "'''" in output,  # 文檔字符串
            "Args:" in output or "Parameters:" in output,  # 參數說明
            "Returns:" in output or "Return:" in output,  # 返回值說明
            "# " in output,  # 行內註釋
            "Example:" in output or "例子" in output,  # 使用示例
        ]
        
        score = sum(doc_indicators) * 2
        return min(score, 10.0)
    
    def _print_comparison_result(self, comparison: Dict[str, Any]):
        """打印對比結果"""
        print(f"   📊 Claude: {comparison['claude_score'].total:.1f}/10")
        print(f"   📊 K2:     {comparison['k2_score'].total:.1f}/10")
        print(f"   📈 差距:   {comparison['quality_gap']:.1f} ({comparison['gap_percentage']:.1f}%)")
        
        if comparison['k2_acceptable']:
            print("   ✅ K2質量可接受")
        else:
            print("   ❌ K2質量需要改進")
    
    def _generate_summary_report(self, results: List[Dict]) -> Dict[str, Any]:
        """生成總結報告"""
        total_tests = len(results)
        acceptable_tests = sum(1 for r in results if r['k2_acceptable'])
        
        avg_claude_score = sum(r['claude_score'].total for r in results) / total_tests
        avg_k2_score = sum(r['k2_score'].total for r in results) / total_tests
        avg_gap = avg_claude_score - avg_k2_score
        
        # 按類別分組統計
        by_category = {}
        for result in results:
            category = result['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)
        
        category_stats = {}
        for category, category_results in by_category.items():
            category_stats[category] = {
                "count": len(category_results),
                "k2_acceptable_rate": sum(1 for r in category_results if r['k2_acceptable']) / len(category_results),
                "avg_gap": sum(r['quality_gap'] for r in category_results) / len(category_results)
            }
        
        return {
            "total_tests": total_tests,
            "k2_acceptable_count": acceptable_tests,
            "k2_acceptable_rate": acceptable_tests / total_tests,
            "avg_claude_score": avg_claude_score,
            "avg_k2_score": avg_k2_score,
            "avg_quality_gap": avg_gap,
            "gap_percentage": (avg_gap / avg_claude_score) * 100,
            "category_breakdown": category_stats,
            "recommendation": self._generate_recommendation(avg_k2_score, acceptable_tests / total_tests)
        }
    
    def _generate_recommendation(self, avg_k2_score: float, acceptable_rate: float) -> str:
        """生成建議"""
        if avg_k2_score >= 8.0 and acceptable_rate >= 0.8:
            return "🚀 K2質量優秀，可以立即推向市場"
        elif avg_k2_score >= 7.0 and acceptable_rate >= 0.7:
            return "✅ K2質量良好，可以作為Claude的替代方案"
        elif avg_k2_score >= 6.0 and acceptable_rate >= 0.6:
            return "⚠️ K2質量可接受，需要在特定場景下優化"
        else:
            return "❌ K2質量不足，需要大幅改進或重新評估策略"
    
    def _print_final_report(self, summary: Dict[str, Any]):
        """打印最終報告"""
        print("\n" + "=" * 60)
        print("🎯 PowerAutomation 內部質量基準測試報告")
        print("=" * 60)
        
        print(f"\n📊 總體結果:")
        print(f"   測試案例總數: {summary['total_tests']}")
        print(f"   K2可接受案例: {summary['k2_acceptable_count']}/{summary['total_tests']}")
        print(f"   K2可接受率: {summary['k2_acceptable_rate']:.1%}")
        
        print(f"\n🎯 平均分數:")
        print(f"   Claude平均分: {summary['avg_claude_score']:.1f}/10")
        print(f"   K2平均分:     {summary['avg_k2_score']:.1f}/10")
        print(f"   質量差距:     {summary['avg_quality_gap']:.1f} ({summary['gap_percentage']:.1f}%)")
        
        print(f"\n📈 分類別統計:")
        for category, stats in summary['category_breakdown'].items():
            print(f"   {category}: {stats['k2_acceptable_rate']:.1%} 可接受率")
        
        print(f"\n🎯 我們的結論:")
        print(f"   {summary['recommendation']}")
        
        print("\n" + "=" * 60)

# 立即執行測試
async def run_internal_test():
    """運行內部測試"""
    tester = InternalBenchmarkTester()
    results = await tester.run_full_benchmark()
    
    # 保存結果
    with open('internal_benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

if __name__ == "__main__":
    print("🚀 開始PowerAutomation內部質量基準測試")
    print("👥 測試者：我們這些每天寫代碼16小時+的專家")
    print("🎯 目標：驗證K2是否能達到我們的質量標準")
    print()
    
    asyncio.run(run_internal_test())