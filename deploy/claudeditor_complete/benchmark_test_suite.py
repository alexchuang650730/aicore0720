#!/usr/bin/env python3
"""
PowerAutomation vs Claude 嚴謹UX基準測試套件
立即執行的競爭力驗證工具
"""

import asyncio
import json
import time
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import aiohttp
import statistics
from pathlib import Path

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestTask:
    """測試任務定義"""
    id: str
    category: str
    title: str
    prompt: str
    expected_features: List[str]
    difficulty: str  # easy, medium, hard
    max_time_seconds: int

@dataclass
class TestResult:
    """測試結果"""
    task_id: str
    platform: str  # claude, powerautomation
    start_time: float
    end_time: float
    response: str
    success: bool
    error: str = None
    quality_score: float = 0.0
    feature_coverage: float = 0.0

class BenchmarkTestSuite:
    """基準測試套件"""
    
    def __init__(self):
        self.test_tasks = self._define_test_tasks()
        self.results = []
        
        # API配置
        self.claude_api_key = "your-claude-api-key"
        self.powerauto_endpoint = "http://localhost:8080/api"
        
        logger.info("🧪 基準測試套件初始化完成")
    
    def _define_test_tasks(self) -> List[TestTask]:
        """定義標準測試任務"""
        return [
            # 基礎代碼生成任務
            TestTask(
                id="code_gen_001",
                category="code_generation",
                title="React登錄組件",
                prompt="創建一個React登錄組件，包含用戶名和密碼輸入框、登錄按鈕、表單驗證和錯誤處理",
                expected_features=["react", "form_validation", "error_handling", "responsive"],
                difficulty="easy",
                max_time_seconds=30
            ),
            TestTask(
                id="code_gen_002",
                category="code_generation", 
                title="Python數據分析",
                prompt="編寫Python代碼分析CSV文件中的銷售數據，包括讀取文件、數據清洗、統計分析和可視化",
                expected_features=["pandas", "data_cleaning", "visualization", "statistics"],
                difficulty="medium",
                max_time_seconds=45
            ),
            TestTask(
                id="code_gen_003",
                category="code_generation",
                title="微服務API設計",
                prompt="設計一個用戶管理微服務API，包括註冊、登錄、權限驗證、CRUD操作，使用FastAPI和PostgreSQL",
                expected_features=["fastapi", "authentication", "database", "rest_api"],
                difficulty="hard", 
                max_time_seconds=60
            ),
            
            # 代碼調試任務
            TestTask(
                id="debug_001",
                category="debugging",
                title="JavaScript異步問題",
                prompt="""以下JavaScript代碼有異步處理問題，請修復：
```javascript
function fetchUserData(userId) {
    let userData = null;
    fetch(`/api/users/${userId}`)
        .then(response => response.json())
        .then(data => userData = data);
    return userData;
}
```""",
                expected_features=["async_await", "promise", "error_handling"],
                difficulty="easy",
                max_time_seconds=20
            ),
            TestTask(
                id="debug_002",
                category="debugging",
                title="SQL性能優化",
                prompt="""以下SQL查詢性能很慢，請優化：
```sql
SELECT u.name, p.title, c.name as category 
FROM users u, posts p, categories c
WHERE u.id = p.user_id AND p.category_id = c.id 
AND p.created_at > '2024-01-01'
ORDER BY p.created_at DESC;
```""",
                expected_features=["joins", "indexing", "query_optimization"],
                difficulty="medium", 
                max_time_seconds=30
            ),
            
            # 架構設計任務
            TestTask(
                id="arch_001",
                category="architecture",
                title="電商系統架構",
                prompt="設計一個支持高並發的電商系統架構，需要處理商品管理、訂單處理、支付、庫存管理，預期用戶100萬+",
                expected_features=["microservices", "scalability", "caching", "load_balancing"],
                difficulty="hard",
                max_time_seconds=90
            ),
            
            # 學習解釋任務
            TestTask(
                id="explain_001",
                category="explanation",
                title="解釋機器學習概念",
                prompt="用簡單易懂的方式解釋什麼是梯度下降算法，並提供Python實現例子",
                expected_features=["clear_explanation", "code_example", "visualization"],
                difficulty="medium",
                max_time_seconds=40
            ),
            
            # 複雜問題解決
            TestTask(
                id="complex_001",
                category="problem_solving",
                title="分佈式系統設計",
                prompt="設計一個分佈式文件存儲系統，類似HDFS，需要考慮數據一致性、容錯性、負載均衡和擴展性",
                expected_features=["distributed_systems", "consistency", "fault_tolerance", "replication"],
                difficulty="hard",
                max_time_seconds=120
            )
        ]
    
    async def run_claude_test(self, task: TestTask) -> TestResult:
        """執行Claude測試"""
        start_time = time.time()
        
        try:
            # 模擬Claude API調用
            # 實際使用時需要替換為真實的Claude API
            await asyncio.sleep(2)  # 模擬網絡延遲
            
            # 這裡應該是真實的Claude API調用
            response = f"Claude回應針對任務: {task.title}\n[模擬回應 - 需要集成真實Claude API]"
            
            end_time = time.time()
            
            return TestResult(
                task_id=task.id,
                platform="claude",
                start_time=start_time,
                end_time=end_time,
                response=response,
                success=True,
                quality_score=8.5,  # 模擬分數
                feature_coverage=0.85
            )
            
        except Exception as e:
            end_time = time.time()
            return TestResult(
                task_id=task.id,
                platform="claude",
                start_time=start_time,
                end_time=end_time,
                response="",
                success=False,
                error=str(e)
            )
    
    async def run_powerautomation_test(self, task: TestTask) -> TestResult:
        """執行PowerAutomation測試"""
        start_time = time.time()
        
        try:
            # 調用PowerAutomation API
            async with aiohttp.ClientSession() as session:
                payload = {
                    "prompt": task.prompt,
                    "task_type": task.category,
                    "use_workflows": True,
                    "use_memory_rag": True,
                    "k2_mode": "groq"  # 海外用Groq
                }
                
                async with session.post(
                    f"{self.powerauto_endpoint}/chat/complete",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=task.max_time_seconds + 10)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        end_time = time.time()
                        
                        return TestResult(
                            task_id=task.id,
                            platform="powerautomation",
                            start_time=start_time,
                            end_time=end_time,
                            response=result.get("response", ""),
                            success=result.get("success", False),
                            quality_score=self._evaluate_response_quality(result.get("response", ""), task),
                            feature_coverage=self._evaluate_feature_coverage(result.get("response", ""), task)
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"API Error: {response.status} - {error_text}")
                        
        except Exception as e:
            end_time = time.time()
            return TestResult(
                task_id=task.id,
                platform="powerautomation",
                start_time=start_time,
                end_time=end_time,
                response="",
                success=False,
                error=str(e)
            )
    
    def _evaluate_response_quality(self, response: str, task: TestTask) -> float:
        """評估回應質量 (簡化版)"""
        if not response:
            return 0.0
        
        quality_indicators = {
            "length": len(response) > 100,  # 回應長度足夠
            "code_blocks": "```" in response,  # 包含代碼塊
            "explanations": any(word in response.lower() for word in ["因為", "所以", "這樣", "解釋"]),
            "structure": response.count("\n") > 3,  # 結構化回應
            "keywords": any(feature in response.lower() for feature in task.expected_features)
        }
        
        score = sum(quality_indicators.values()) / len(quality_indicators)
        return min(score * 10, 10.0)  # 轉換為10分制
    
    def _evaluate_feature_coverage(self, response: str, task: TestTask) -> float:
        """評估功能覆蓋度"""
        if not response or not task.expected_features:
            return 0.0
        
        covered_features = 0
        for feature in task.expected_features:
            if feature.lower() in response.lower():
                covered_features += 1
        
        return covered_features / len(task.expected_features)
    
    async def run_comparison_test(self, task: TestTask) -> Tuple[TestResult, TestResult]:
        """運行對比測試"""
        logger.info(f"🔬 開始測試任務: {task.title} ({task.difficulty})")
        
        # 並行執行兩個平台的測試
        claude_task = asyncio.create_task(self.run_claude_test(task))
        powerauto_task = asyncio.create_task(self.run_powerautomation_test(task))
        
        claude_result, powerauto_result = await asyncio.gather(claude_task, powerauto_task)
        
        # 記錄結果
        self.results.extend([claude_result, powerauto_result])
        
        # 即時報告
        self._report_task_results(task, claude_result, powerauto_result)
        
        return claude_result, powerauto_result
    
    def _report_task_results(self, task: TestTask, claude_result: TestResult, powerauto_result: TestResult):
        """報告單個任務結果"""
        print(f"\n📊 任務結果: {task.title}")
        print("=" * 50)
        
        # 響應時間對比
        claude_time = claude_result.end_time - claude_result.start_time
        powerauto_time = powerauto_result.end_time - powerauto_result.start_time
        
        print(f"⏱️  響應時間:")
        print(f"   Claude: {claude_time:.2f}s")
        print(f"   PowerAutomation: {powerauto_time:.2f}s")
        print(f"   勝者: {'PowerAutomation' if powerauto_time < claude_time else 'Claude'}")
        
        # 質量對比
        print(f"\n⭐ 質量分數:")
        print(f"   Claude: {claude_result.quality_score:.1f}/10")
        print(f"   PowerAutomation: {powerauto_result.quality_score:.1f}/10")
        print(f"   勝者: {'PowerAutomation' if powerauto_result.quality_score > claude_result.quality_score else 'Claude'}")
        
        # 功能覆蓋度
        print(f"\n🎯 功能覆蓋:")
        print(f"   Claude: {claude_result.feature_coverage:.1%}")
        print(f"   PowerAutomation: {powerauto_result.feature_coverage:.1%}")
        
        # 成功率
        print(f"\n✅ 成功執行:")
        print(f"   Claude: {'成功' if claude_result.success else '失敗'}")
        print(f"   PowerAutomation: {'成功' if powerauto_result.success else '失敗'}")
        
        if claude_result.error:
            print(f"   Claude錯誤: {claude_result.error}")
        if powerauto_result.error:
            print(f"   PowerAutomation錯誤: {powerauto_result.error}")
    
    async def run_full_benchmark(self) -> Dict[str, Any]:
        """運行完整基準測試"""
        logger.info("🚀 開始完整基準測試")
        start_time = time.time()
        
        # 按類別分組測試
        categories = {}
        for task in self.test_tasks:
            if task.category not in categories:
                categories[task.category] = []
            categories[task.category].append(task)
        
        # 逐個執行測試
        all_results = []
        for category, tasks in categories.items():
            logger.info(f"📂 測試類別: {category}")
            
            for task in tasks:
                claude_result, powerauto_result = await self.run_comparison_test(task)
                all_results.append((task, claude_result, powerauto_result))
                
                # 稍作休息避免API限制
                await asyncio.sleep(1)
        
        # 生成綜合報告
        report = self._generate_final_report(all_results)
        
        # 保存結果
        await self._save_results(report)
        
        end_time = time.time()
        logger.info(f"✅ 基準測試完成，總耗時: {end_time - start_time:.2f}秒")
        
        return report
    
    def _generate_final_report(self, all_results: List[Tuple[TestTask, TestResult, TestResult]]) -> Dict[str, Any]:
        """生成最終報告"""
        claude_scores = []
        powerauto_scores = []
        claude_times = []
        powerauto_times = []
        
        category_results = {}
        
        for task, claude_result, powerauto_result in all_results:
            # 收集分數
            if claude_result.success:
                claude_scores.append(claude_result.quality_score)
                claude_times.append(claude_result.end_time - claude_result.start_time)
                
            if powerauto_result.success:
                powerauto_scores.append(powerauto_result.quality_score)
                powerauto_times.append(powerauto_result.end_time - powerauto_result.start_time)
            
            # 按類別統計
            if task.category not in category_results:
                category_results[task.category] = {
                    "claude_wins": 0,
                    "powerauto_wins": 0,
                    "draws": 0,
                    "tasks": []
                }
            
            # 判斷勝負
            claude_total = claude_result.quality_score + (10 if claude_result.success else 0)
            powerauto_total = powerauto_result.quality_score + (10 if powerauto_result.success else 0)
            
            if powerauto_total > claude_total:
                category_results[task.category]["powerauto_wins"] += 1
                winner = "PowerAutomation"
            elif claude_total > powerauto_total:
                category_results[task.category]["claude_wins"] += 1
                winner = "Claude"
            else:
                category_results[task.category]["draws"] += 1
                winner = "Draw"
            
            category_results[task.category]["tasks"].append({
                "task": task.title,
                "winner": winner,
                "claude_score": claude_result.quality_score,
                "powerauto_score": powerauto_result.quality_score
            })
        
        # 計算總體統計
        overall_stats = {
            "claude": {
                "avg_quality": statistics.mean(claude_scores) if claude_scores else 0,
                "avg_response_time": statistics.mean(claude_times) if claude_times else 0,
                "success_rate": len(claude_scores) / len(all_results),
                "total_wins": sum(cat["claude_wins"] for cat in category_results.values())
            },
            "powerautomation": {
                "avg_quality": statistics.mean(powerauto_scores) if powerauto_scores else 0,
                "avg_response_time": statistics.mean(powerauto_times) if powerauto_times else 0,
                "success_rate": len(powerauto_scores) / len(all_results),
                "total_wins": sum(cat["powerauto_wins"] for cat in category_results.values())
            }
        }
        
        return {
            "test_date": datetime.now().isoformat(),
            "total_tasks": len(all_results),
            "overall_stats": overall_stats,
            "category_results": category_results,
            "raw_results": [
                {
                    "task": asdict(task),
                    "claude": asdict(claude_result),
                    "powerauto": asdict(powerauto_result)
                }
                for task, claude_result, powerauto_result in all_results
            ]
        }
    
    async def _save_results(self, report: Dict[str, Any]):
        """保存測試結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_results_{timestamp}.json"
        
        # 保存完整結果
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 生成摘要報告
        summary_filename = f"benchmark_summary_{timestamp}.md"
        await self._generate_summary_report(report, summary_filename)
        
        logger.info(f"📄 結果已保存: {filename}")
        logger.info(f"📋 摘要已保存: {summary_filename}")
    
    async def _generate_summary_report(self, report: Dict[str, Any], filename: str):
        """生成摘要報告"""
        claude_stats = report["overall_stats"]["claude"]
        powerauto_stats = report["overall_stats"]["powerautomation"]
        
        summary = f"""# PowerAutomation vs Claude 基準測試報告
測試時間: {report["test_date"]}
測試任務數: {report["total_tasks"]}

## 🏆 總體勝負
- Claude勝利: {claude_stats["total_wins"]}場
- PowerAutomation勝利: {powerauto_stats["total_wins"]}場
- 平局: {report["total_tasks"] - claude_stats["total_wins"] - powerauto_stats["total_wins"]}場

## 📊 性能對比

| 指標 | Claude | PowerAutomation | 勝者 |
|------|--------|-----------------|------|
| 平均質量分數 | {claude_stats["avg_quality"]:.1f}/10 | {powerauto_stats["avg_quality"]:.1f}/10 | {"PowerAutomation" if powerauto_stats["avg_quality"] > claude_stats["avg_quality"] else "Claude"} |
| 平均響應時間 | {claude_stats["avg_response_time"]:.2f}s | {powerauto_stats["avg_response_time"]:.2f}s | {"PowerAutomation" if powerauto_stats["avg_response_time"] < claude_stats["avg_response_time"] else "Claude"} |
| 成功率 | {claude_stats["success_rate"]:.1%} | {powerauto_stats["success_rate"]:.1%} | {"PowerAutomation" if powerauto_stats["success_rate"] > claude_stats["success_rate"] else "Claude"} |

## 📂 分類別結果
"""
        
        for category, results in report["category_results"].items():
            summary += f"\n### {category.title()}\n"
            summary += f"- Claude勝利: {results['claude_wins']}場\n"
            summary += f"- PowerAutomation勝利: {results['powerauto_wins']}場\n"
            summary += f"- 平局: {results['draws']}場\n"
        
        # 結論
        overall_winner = "PowerAutomation" if powerauto_stats["total_wins"] > claude_stats["total_wins"] else "Claude"
        summary += f"\n## 🎯 結論\n"
        summary += f"總體勝者: **{overall_winner}**\n\n"
        
        if overall_winner == "PowerAutomation":
            summary += "✅ PowerAutomation在此次測試中表現優於Claude，特別是在成本效益和功能完整性方面。\n"
        else:
            summary += "⚠️ PowerAutomation仍需改進，特別是在對話質量和響應穩定性方面。\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary)

# 主執行函數
async def main():
    """主執行函數"""
    print("🧪 PowerAutomation vs Claude 基準測試開始")
    print("=" * 60)
    
    # 創建測試套件
    test_suite = BenchmarkTestSuite()
    
    # 運行測試
    try:
        report = await test_suite.run_full_benchmark()
        
        # 打印最終結果
        print("\n🎉 測試完成！")
        print("=" * 60)
        
        claude_stats = report["overall_stats"]["claude"]
        powerauto_stats = report["overall_stats"]["powerautomation"]
        
        print(f"📊 最終得分:")
        print(f"   Claude: {claude_stats['total_wins']}勝 (平均{claude_stats['avg_quality']:.1f}分)")
        print(f"   PowerAutomation: {powerauto_stats['total_wins']}勝 (平均{powerauto_stats['avg_quality']:.1f}分)")
        
        if powerauto_stats["total_wins"] > claude_stats["total_wins"]:
            print("🏆 PowerAutomation 勝出！")
        elif claude_stats["total_wins"] > powerauto_stats["total_wins"]:
            print("🏆 Claude 勝出！")
        else:
            print("🤝 平局！")
            
    except Exception as e:
        logger.error(f"❌ 測試執行失敗: {e}")
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())