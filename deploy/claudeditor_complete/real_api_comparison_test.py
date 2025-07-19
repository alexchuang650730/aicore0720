#!/usr/bin/env python3
"""
真實API對比測試 - Claude Code Tool vs K2
使用真實API調用，獲得可靠的質量對比數據
"""

import asyncio
import json
import time
import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp
import anthropic

logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """測試案例"""
    name: str
    prompt: str
    category: str
    expected_language: str

@dataclass
class APIResponse:
    """API響應"""
    content: str
    response_time: float
    token_count: int
    cost_estimate: float
    success: bool
    error: Optional[str] = None

class RealAPIComparison:
    """真實API對比測試"""
    
    def __init__(self):
        # API配置 - 需要真實的API密鑰
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.k2_api_key = os.getenv("MOONSHOT_API_KEY")  # 或其他K2提供商
        
        # 初始化客戶端
        if self.claude_api_key:
            self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
        else:
            self.claude_client = None
            
        self.k2_base_url = "https://api.moonshot.cn/v1"  # 月之暗面API
        
        # 測試案例
        self.test_cases = [
            TestCase(
                name="React Hook實現",
                prompt="創建一個React自定義Hook用於API數據獲取，包含loading、error狀態管理和重試機制",
                category="frontend",
                expected_language="typescript"
            ),
            TestCase(
                name="二分搜索算法",
                prompt="實現二分搜索算法，包含完整的錯誤處理、邊界檢查和測試用例",
                category="algorithm",
                expected_language="python"
            ),
            TestCase(
                name="RESTful API設計",
                prompt="使用FastAPI設計用戶管理API，包含CRUD操作、認證授權和OpenAPI文檔",
                category="backend",
                expected_language="python"
            ),
            TestCase(
                name="SQL查詢優化",
                prompt="優化以下SQL查詢性能，添加適當索引和重寫查詢：SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.created_at > '2023-01-01' GROUP BY u.id ORDER BY COUNT(o.id) DESC",
                category="database",
                expected_language="sql"
            ),
            TestCase(
                name="系統架構設計",
                prompt="設計一個高並發的短鏈接服務架構，考慮數據庫分片、緩存策略和負載均衡",
                category="architecture",
                expected_language="python"
            )
        ]
    
    async def run_comparison(self) -> Dict[str, Any]:
        """運行完整對比測試"""
        if not self.claude_client:
            return {"error": "缺少Claude API密鑰"}
        
        if not self.k2_api_key:
            return {"error": "缺少K2 API密鑰"}
        
        print("🚀 開始真實API對比測試")
        print(f"📊 測試案例數量: {len(self.test_cases)}")
        print("=" * 60)
        
        results = []
        
        for i, test_case in enumerate(self.test_cases):
            print(f"\n🧪 測試 {i+1}/{len(self.test_cases)}: {test_case.name}")
            print(f"📝 類別: {test_case.category}")
            
            # 並行調用兩個API
            claude_task = self.call_claude_api(test_case.prompt)
            k2_task = self.call_k2_api(test_case.prompt)
            
            claude_response, k2_response = await asyncio.gather(
                claude_task, k2_task, return_exceptions=True
            )
            
            # 處理異常
            if isinstance(claude_response, Exception):
                claude_response = APIResponse("", 0, 0, 0, False, str(claude_response))
            
            if isinstance(k2_response, Exception):
                k2_response = APIResponse("", 0, 0, 0, False, str(k2_response))
            
            # 質量評估
            comparison = await self.evaluate_responses(
                test_case, claude_response, k2_response
            )
            
            results.append(comparison)
            
            # 打印結果
            self.print_comparison(comparison)
            
            # API限制延遲
            await asyncio.sleep(1)
        
        # 生成總結報告
        summary = self.generate_summary(results)
        self.print_summary(summary)
        
        return {
            "test_results": results,
            "summary": summary,
            "timestamp": time.time()
        }
    
    async def call_claude_api(self, prompt: str) -> APIResponse:
        """調用Claude API"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.claude_client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_time = time.time() - start_time
            content = response.content[0].text
            
            # 估算成本 (Claude 3 Sonnet pricing)
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000  # USD
            
            return APIResponse(
                content=content,
                response_time=response_time,
                token_count=input_tokens + output_tokens,
                cost_estimate=cost,
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Claude API調用失敗: {e}")
            return APIResponse(
                content="",
                response_time=response_time,
                token_count=0,
                cost_estimate=0,
                success=False,
                error=str(e)
            )
    
    async def call_k2_api(self, prompt: str) -> APIResponse:
        """調用K2 API (月之暗面)"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.k2_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "moonshot-v1-8k",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 4096,
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{self.k2_base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        # 估算成本 (月之暗面pricing)
                        input_tokens = result["usage"]["prompt_tokens"]
                        output_tokens = result["usage"]["completion_tokens"]
                        cost = (input_tokens * 0.012 + output_tokens * 0.012) / 1000 * 7  # CNY to USD
                        
                        return APIResponse(
                            content=content,
                            response_time=response_time,
                            token_count=input_tokens + output_tokens,
                            cost_estimate=cost,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"API錯誤 {response.status}: {error_text}")
                        
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"K2 API調用失敗: {e}")
            return APIResponse(
                content="",
                response_time=response_time,
                token_count=0,
                cost_estimate=0,
                success=False,
                error=str(e)
            )
    
    async def evaluate_responses(self, test_case: TestCase, claude_resp: APIResponse, k2_resp: APIResponse) -> Dict[str, Any]:
        """評估響應質量"""
        
        # 基於實際輸出的質量評分
        claude_score = self.score_response(claude_resp.content, test_case) if claude_resp.success else 0
        k2_score = self.score_response(k2_resp.content, test_case) if k2_resp.success else 0
        
        return {
            "test_case": test_case.name,
            "category": test_case.category,
            "claude": {
                "score": claude_score,
                "response_time": claude_resp.response_time,
                "token_count": claude_resp.token_count,
                "cost": claude_resp.cost_estimate,
                "success": claude_resp.success,
                "content_length": len(claude_resp.content),
                "error": claude_resp.error
            },
            "k2": {
                "score": k2_score,
                "response_time": k2_resp.response_time,
                "token_count": k2_resp.token_count,
                "cost": k2_resp.cost_estimate,
                "success": k2_resp.success,
                "content_length": len(k2_resp.content),
                "error": k2_resp.error
            },
            "quality_gap": claude_score - k2_score,
            "cost_ratio": k2_resp.cost_estimate / claude_resp.cost_estimate if claude_resp.cost_estimate > 0 else 0,
            "speed_ratio": claude_resp.response_time / k2_resp.response_time if k2_resp.response_time > 0 else 0
        }
    
    def score_response(self, content: str, test_case: TestCase) -> float:
        """基於內容質量評分 (0-10)"""
        if not content or len(content) < 50:
            return 1.0
        
        score = 5.0  # 基礎分
        
        # 代碼塊檢查
        if "```" in content:
            score += 1.5
        
        # 語言匹配檢查
        if test_case.expected_language in content.lower():
            score += 1.0
        
        # 完整性檢查
        if len(content) > 500:
            score += 1.0
        
        # 錯誤處理檢查
        if any(keyword in content.lower() for keyword in ["try", "catch", "error", "exception", "throw"]):
            score += 1.0
        
        # 註釋和文檔檢查
        if any(keyword in content for keyword in ["//", "#", "/**", '"""', "Args:", "Returns:"]):
            score += 0.5
        
        return min(score, 10.0)
    
    def print_comparison(self, comparison: Dict[str, Any]):
        """打印單個測試對比結果"""
        claude = comparison["claude"]
        k2 = comparison["k2"]
        
        print(f"   📊 Claude: {claude['score']:.1f}/10 | {claude['response_time']:.2f}s | ${claude['cost']:.4f}")
        print(f"   📊 K2:     {k2['score']:.1f}/10 | {k2['response_time']:.2f}s | ${k2['cost']:.4f}")
        print(f"   📈 差距:   {comparison['quality_gap']:.1f} | 成本比: {comparison['cost_ratio']:.2f} | 速度比: {comparison['speed_ratio']:.2f}")
        
        if not claude["success"]:
            print(f"   ❌ Claude錯誤: {claude['error']}")
        if not k2["success"]:
            print(f"   ❌ K2錯誤: {k2['error']}")
    
    def generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """生成總結報告"""
        successful_tests = [r for r in results if r["claude"]["success"] and r["k2"]["success"]]
        
        if not successful_tests:
            return {"error": "沒有成功的測試案例"}
        
        avg_claude_score = sum(r["claude"]["score"] for r in successful_tests) / len(successful_tests)
        avg_k2_score = sum(r["k2"]["score"] for r in successful_tests) / len(successful_tests)
        avg_quality_gap = avg_claude_score - avg_k2_score
        
        avg_claude_cost = sum(r["claude"]["cost"] for r in successful_tests) / len(successful_tests)
        avg_k2_cost = sum(r["k2"]["cost"] for r in successful_tests) / len(successful_tests)
        cost_saving = (1 - avg_k2_cost / avg_claude_cost) * 100 if avg_claude_cost > 0 else 0
        
        avg_claude_time = sum(r["claude"]["response_time"] for r in successful_tests) / len(successful_tests)
        avg_k2_time = sum(r["k2"]["response_time"] for r in successful_tests) / len(successful_tests)
        
        return {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "avg_claude_score": avg_claude_score,
            "avg_k2_score": avg_k2_score,
            "quality_gap": avg_quality_gap,
            "quality_gap_percentage": (avg_quality_gap / avg_claude_score * 100) if avg_claude_score > 0 else 0,
            "avg_claude_cost": avg_claude_cost,
            "avg_k2_cost": avg_k2_cost,
            "cost_saving_percentage": cost_saving,
            "avg_claude_time": avg_claude_time,
            "avg_k2_time": avg_k2_time,
            "speed_improvement": ((avg_claude_time - avg_k2_time) / avg_claude_time * 100) if avg_claude_time > 0 else 0
        }
    
    def print_summary(self, summary: Dict[str, Any]):
        """打印總結報告"""
        if "error" in summary:
            print(f"\n❌ 測試失敗: {summary['error']}")
            return
        
        print("\n" + "=" * 60)
        print("📊 真實API對比測試報告")
        print("=" * 60)
        
        print(f"\n📈 質量對比:")
        print(f"   Claude平均分: {summary['avg_claude_score']:.1f}/10")
        print(f"   K2平均分:     {summary['avg_k2_score']:.1f}/10")
        print(f"   質量差距:     {summary['quality_gap']:.1f} ({summary['quality_gap_percentage']:.1f}%)")
        
        print(f"\n💰 成本對比:")
        print(f"   Claude平均成本: ${summary['avg_claude_cost']:.4f}")
        print(f"   K2平均成本:     ${summary['avg_k2_cost']:.4f}")
        print(f"   成本節省:       {summary['cost_saving_percentage']:.1f}%")
        
        print(f"\n⚡ 速度對比:")
        print(f"   Claude平均時間: {summary['avg_claude_time']:.2f}s")
        print(f"   K2平均時間:     {summary['avg_k2_time']:.2f}s")
        print(f"   速度提升:       {summary['speed_improvement']:.1f}%")
        
        print(f"\n📊 測試概況:")
        print(f"   總測試數:     {summary['total_tests']}")
        print(f"   成功測試數:   {summary['successful_tests']}")

# 執行測試
async def main():
    """主函數"""
    print("🎯 真實API對比測試")
    print("📋 需要環境變量:")
    print("   ANTHROPIC_API_KEY - Claude API密鑰")
    print("   MOONSHOT_API_KEY - 月之暗面API密鑰")
    print()
    
    tester = RealAPIComparison()
    results = await tester.run_comparison()
    
    # 保存結果
    with open("real_api_comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 結果已保存到: real_api_comparison_results.json")

if __name__ == "__main__":
    asyncio.run(main())