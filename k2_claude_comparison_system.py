#!/usr/bin/env python3
"""
K2 與 Claude Code 語義相似度比較系統
使用真實的 K2 API 進行對比測試
"""

import json
import os
import logging
import time
from typing import Dict, List, Tuple
from groq import Groq
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class K2ClaudeComparisonEngine:
    """K2 與 Claude Code 比較引擎"""
    
    def __init__(self, groq_api_key: str):
        self.groq_client = Groq(api_key=groq_api_key)
        self.k2_model = "moonshotai/kimi-k2-instruct"
        
        # 測試案例
        self.test_cases = [
            {
                "id": "basic_coding",
                "prompt": "寫一個函數來計算斐波那契數列的第n項",
                "expected_tools": [],
                "category": "代碼生成"
            },
            {
                "id": "file_operation",
                "prompt": "請幫我讀取 main.py 文件並找出所有的函數定義",
                "expected_tools": ["Read", "Grep"],
                "category": "文件操作"
            },
            {
                "id": "code_refactor",
                "prompt": "重構這段代碼，提高性能並添加類型註解",
                "expected_tools": ["Read", "Edit"],
                "category": "代碼重構"
            },
            {
                "id": "project_setup",
                "prompt": "創建一個新的 Python 專案結構，包含 src/, tests/, 和配置文件",
                "expected_tools": ["Write", "Bash"],
                "category": "專案設置"
            },
            {
                "id": "debug_analysis",
                "prompt": "分析這個錯誤: TypeError: 'NoneType' object is not iterable",
                "expected_tools": [],
                "category": "錯誤分析"
            }
        ]
        
        # Claude Code 模擬回應（實際應用中應調用真實 API）
        self.claude_responses = {
            "basic_coding": {
                "response": "我將為您創建一個計算斐波那契數列的函數。\n\n```python\ndef fibonacci(n: int) -> int:\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n```",
                "tools": []
            },
            "file_operation": {
                "response": "我將讀取 main.py 文件並找出所有函數定義。\n\n<function_calls>\n<invoke name=\"Read\">\n<parameter name=\"file_path\">main.py</parameter>\n</invoke>\n</function_calls>",
                "tools": ["Read"]
            }
        }
        
    def generate_k2_response(self, prompt: str, include_tools: bool = True) -> Dict:
        """生成 K2 回應"""
        
        messages = [{
            "role": "user",
            "content": prompt if not include_tools else f"""
你是一個強大的編程助手，可以使用以下工具:
- Read(讀取文件)、Write(寫入文件)、Edit(編輯文件)
- Grep(搜索內容)、Glob(查找文件)、Bash(執行命令)

使用工具時請用以下格式:
<function_calls>
<invoke name="工具名">
<parameter name="參數名">參數值</parameter>
</invoke>
</function_calls>

用戶請求: {prompt}
"""
        }]
        
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.k2_model,
                messages=messages,
                temperature=0.6,
                max_completion_tokens=1024
            )
            
            response = completion.choices[0].message.content
            
            # 解析工具調用
            tools = self._extract_tools(response)
            
            return {
                "response": response,
                "tools": tools,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"K2 生成失敗: {e}")
            return {
                "response": f"錯誤: {str(e)}",
                "tools": [],
                "success": False
            }
    
    def _extract_tools(self, response: str) -> List[str]:
        """提取工具調用"""
        import re
        tools = []
        
        # 查找所有 invoke 標籤
        invokes = re.findall(r'<invoke name="([^"]+)">', response)
        tools.extend(invokes)
        
        return list(set(tools))  # 去重
    
    def calculate_similarity(self, response1: str, response2: str) -> float:
        """計算兩個回應的相似度（簡化版）"""
        # 基於關鍵詞重疊的簡單相似度
        words1 = set(response1.lower().split())
        words2 = set(response2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union
    
    def run_comparison_tests(self) -> Dict:
        """執行比較測試"""
        results = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_cases": [],
            "overall_metrics": {}
        }
        
        total_similarity = 0
        tool_accuracy = 0
        successful_tests = 0
        
        for test_case in self.test_cases:
            logger.info(f"\n🧪 測試案例: {test_case['id']} - {test_case['category']}")
            logger.info(f"📝 提示: {test_case['prompt']}")
            
            # 生成 K2 回應
            k2_result = self.generate_k2_response(
                test_case['prompt'], 
                include_tools=len(test_case['expected_tools']) > 0
            )
            
            if k2_result['success']:
                logger.info(f"✅ K2 回應成功")
                logger.info(f"🛠️ 工具調用: {k2_result['tools']}")
                
                # 計算工具準確性
                if test_case['expected_tools']:
                    expected_set = set(test_case['expected_tools'])
                    actual_set = set(k2_result['tools'])
                    tool_match = len(expected_set & actual_set) / len(expected_set)
                else:
                    tool_match = 1.0 if not k2_result['tools'] else 0.0
                
                # 獲取 Claude 模擬回應（實際應調用 API）
                claude_response = self.claude_responses.get(
                    test_case['id'], 
                    {"response": "模擬回應", "tools": []}
                )
                
                # 計算相似度
                similarity = self.calculate_similarity(
                    k2_result['response'], 
                    claude_response['response']
                )
                
                # 記錄結果
                test_result = {
                    "test_id": test_case['id'],
                    "category": test_case['category'],
                    "prompt": test_case['prompt'],
                    "k2_response": k2_result['response'][:500] + "...",
                    "k2_tools": k2_result['tools'],
                    "expected_tools": test_case['expected_tools'],
                    "tool_accuracy": tool_match,
                    "semantic_similarity": similarity,
                    "success": True
                }
                
                total_similarity += similarity
                tool_accuracy += tool_match
                successful_tests += 1
                
            else:
                test_result = {
                    "test_id": test_case['id'],
                    "category": test_case['category'],
                    "prompt": test_case['prompt'],
                    "error": k2_result['response'],
                    "success": False
                }
            
            results["test_cases"].append(test_result)
            
            # 延遲避免速率限制
            time.sleep(1)
        
        # 計算總體指標
        if successful_tests > 0:
            results["overall_metrics"] = {
                "average_similarity": total_similarity / successful_tests,
                "average_tool_accuracy": tool_accuracy / successful_tests,
                "success_rate": successful_tests / len(self.test_cases),
                "total_tests": len(self.test_cases),
                "successful_tests": successful_tests
            }
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """生成測試報告"""
        report = f"""
# K2 與 Claude Code 比較測試報告

測試時間: {results['test_time']}

## 總體指標

- **測試成功率**: {results['overall_metrics']['success_rate']:.1%}
- **平均語義相似度**: {results['overall_metrics']['average_similarity']:.1%}
- **工具調用準確率**: {results['overall_metrics']['average_tool_accuracy']:.1%}
- **總測試數**: {results['overall_metrics']['total_tests']}
- **成功測試數**: {results['overall_metrics']['successful_tests']}

## 詳細測試結果

"""
        
        for test in results['test_cases']:
            if test['success']:
                report += f"""
### {test['test_id']} - {test['category']}

**提示**: {test['prompt']}

**K2 工具調用**: {', '.join(test['k2_tools']) if test['k2_tools'] else '無'}

**預期工具**: {', '.join(test['expected_tools']) if test['expected_tools'] else '無'}

**工具準確率**: {test['tool_accuracy']:.1%}

**語義相似度**: {test['semantic_similarity']:.1%}

---
"""
            else:
                report += f"""
### {test['test_id']} - {test['category']} ❌

**錯誤**: {test['error']}

---
"""
        
        return report


def main():
    """主函數"""
    api_key = "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"
    
    logger.info("🚀 啟動 K2 與 Claude Code 比較系統")
    
    # 創建比較引擎
    engine = K2ClaudeComparisonEngine(api_key)
    
    # 執行測試
    results = engine.run_comparison_tests()
    
    # 生成報告
    report = engine.generate_report(results)
    
    # 保存結果
    with open("k2_claude_comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    with open("k2_claude_comparison_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    # 打印摘要
    logger.info("\n" + "="*50)
    logger.info("📊 測試完成！")
    logger.info(f"✅ 成功率: {results['overall_metrics']['success_rate']:.1%}")
    logger.info(f"🎯 平均相似度: {results['overall_metrics']['average_similarity']:.1%}")
    logger.info(f"🛠️ 工具準確率: {results['overall_metrics']['average_tool_accuracy']:.1%}")
    logger.info("\n詳細報告已保存至:")
    logger.info("- k2_claude_comparison_results.json")
    logger.info("- k2_claude_comparison_report.md")


if __name__ == "__main__":
    main()