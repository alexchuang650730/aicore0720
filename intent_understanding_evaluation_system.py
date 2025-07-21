#!/usr/bin/env python3
"""
意圖理解評估系統
專注於工具調用準確率和意圖理解評分
目標：第一階段達到100%工具調用準確率
"""

import json
import logging
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from groq import Groq
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentType(Enum):
    """用戶意圖類型"""
    CODE_GENERATION = "代碼生成"
    FILE_OPERATION = "文件操作"
    CODE_ANALYSIS = "代碼分析"
    CODE_REFACTOR = "代碼重構"
    PROJECT_SETUP = "專案設置"
    DEBUG_HELP = "調試幫助"
    SEARCH_CODE = "搜索代碼"
    RUN_COMMAND = "執行命令"
    DOCUMENTATION = "文檔編寫"
    TESTING = "測試相關"


@dataclass
class IntentEvaluation:
    """意圖評估結果"""
    intent_type: IntentType
    confidence: float  # 意圖識別信心度 0-1
    tool_accuracy: float  # 工具調用準確率 0-1
    tool_sequence_correct: bool  # 工具調用順序是否正確
    missing_tools: List[str]  # 缺失的工具
    extra_tools: List[str]  # 多餘的工具
    intent_fulfillment: float  # 意圖滿足度 0-1


class IntentUnderstandingEvaluator:
    """意圖理解評估器"""
    
    def __init__(self, groq_api_key: str):
        self.groq_client = Groq(api_key=groq_api_key)
        self.k2_model = "moonshotai/kimi-k2-instruct"
        
        # 意圖到工具的映射規則
        self.intent_tool_mapping = {
            IntentType.CODE_GENERATION: {
                "required": [],
                "optional": ["Write"],
                "sequence": []
            },
            IntentType.FILE_OPERATION: {
                "required": ["Read"],
                "optional": ["Grep", "Glob", "LS"],
                "sequence": ["Read"]  # Read 通常先執行
            },
            IntentType.CODE_ANALYSIS: {
                "required": ["Read"],
                "optional": ["Grep", "Glob", "Task"],
                "sequence": ["Read", "Grep"]
            },
            IntentType.CODE_REFACTOR: {
                "required": ["Read", "Edit"],
                "optional": ["MultiEdit", "Write"],
                "sequence": ["Read", "Edit"]  # 先讀後改
            },
            IntentType.PROJECT_SETUP: {
                "required": ["Bash"],
                "optional": ["Write", "Edit"],
                "sequence": ["Bash", "Write"]  # 先創建目錄後寫文件
            },
            IntentType.DEBUG_HELP: {
                "required": [],
                "optional": ["Read", "Grep", "Bash"],
                "sequence": []
            },
            IntentType.SEARCH_CODE: {
                "required": ["Grep"],
                "optional": ["Glob", "Task", "Read"],
                "sequence": ["Grep"]  # Grep 是主要工具
            },
            IntentType.RUN_COMMAND: {
                "required": ["Bash"],
                "optional": [],
                "sequence": ["Bash"]
            },
            IntentType.DOCUMENTATION: {
                "required": ["Write"],
                "optional": ["Read", "Edit"],
                "sequence": []
            },
            IntentType.TESTING: {
                "required": ["Bash"],
                "optional": ["Read", "Write", "Edit"],
                "sequence": ["Bash"]  # 運行測試
            }
        }
        
        # 測試案例（包含更多意圖理解場景）
        self.test_cases = self._create_comprehensive_test_cases()
    
    def _create_comprehensive_test_cases(self) -> List[Dict]:
        """創建全面的測試案例"""
        return [
            # 文件操作意圖
            {
                "id": "file_read_analyze",
                "prompt": "請幫我讀取 main.py 文件並找出所有的函數定義",
                "intent": IntentType.FILE_OPERATION,
                "expected_tools": ["Read", "Grep"],
                "tool_sequence": ["Read", "Grep"]
            },
            {
                "id": "search_pattern",
                "prompt": "在所有 Python 文件中搜索包含 'TODO' 的註釋",
                "intent": IntentType.SEARCH_CODE,
                "expected_tools": ["Grep"],
                "tool_sequence": ["Grep"]
            },
            {
                "id": "refactor_code",
                "prompt": "將 config.py 中的所有 print 語句改為 logger.info",
                "intent": IntentType.CODE_REFACTOR,
                "expected_tools": ["Read", "Edit"],
                "tool_sequence": ["Read", "Edit"]
            },
            {
                "id": "create_project",
                "prompt": "創建一個新的 Flask 專案，包含基本的目錄結構和配置文件",
                "intent": IntentType.PROJECT_SETUP,
                "expected_tools": ["Bash", "Write"],
                "tool_sequence": ["Bash", "Write"]
            },
            {
                "id": "run_tests",
                "prompt": "運行所有的單元測試並顯示覆蓋率報告",
                "intent": IntentType.TESTING,
                "expected_tools": ["Bash"],
                "tool_sequence": ["Bash"]
            },
            {
                "id": "analyze_error",
                "prompt": "分析這個錯誤並給出解決方案: ImportError: No module named 'requests'",
                "intent": IntentType.DEBUG_HELP,
                "expected_tools": [],  # 可能不需要工具，只需分析
                "tool_sequence": []
            },
            {
                "id": "multi_file_refactor",
                "prompt": "將所有文件中的類名 UserManager 改為 UserService",
                "intent": IntentType.CODE_REFACTOR,
                "expected_tools": ["Grep", "Read", "Edit"],
                "tool_sequence": ["Grep", "Read", "Edit"]
            },
            {
                "id": "complex_search",
                "prompt": "找出所有定義了 async 函數但沒有使用 await 的文件",
                "intent": IntentType.SEARCH_CODE,
                "expected_tools": ["Grep", "Read"],
                "tool_sequence": ["Grep", "Read"]
            },
            {
                "id": "create_documentation",
                "prompt": "為這個專案創建一個詳細的 README.md 文件",
                "intent": IntentType.DOCUMENTATION,
                "expected_tools": ["Write"],
                "tool_sequence": ["Write"]
            },
            {
                "id": "install_dependencies",
                "prompt": "安裝 requirements.txt 中的所有依賴並確保沒有版本衝突",
                "intent": IntentType.RUN_COMMAND,
                "expected_tools": ["Bash"],
                "tool_sequence": ["Bash"]
            }
        ]
    
    def _detect_intent(self, prompt: str) -> Tuple[IntentType, float]:
        """檢測用戶意圖"""
        # 關鍵詞映射
        intent_keywords = {
            IntentType.FILE_OPERATION: ["讀取", "打開", "查看", "文件", "內容"],
            IntentType.SEARCH_CODE: ["搜索", "查找", "尋找", "grep", "包含"],
            IntentType.CODE_REFACTOR: ["重構", "修改", "改為", "替換", "更新"],
            IntentType.PROJECT_SETUP: ["創建", "專案", "項目", "結構", "初始化"],
            IntentType.TESTING: ["測試", "運行", "pytest", "覆蓋率", "單元測試"],
            IntentType.DEBUG_HELP: ["錯誤", "異常", "調試", "解決", "分析"],
            IntentType.CODE_GENERATION: ["寫", "生成", "創建函數", "實現"],
            IntentType.RUN_COMMAND: ["執行", "運行", "安裝", "命令"],
            IntentType.DOCUMENTATION: ["文檔", "README", "說明", "註釋"],
            IntentType.CODE_ANALYSIS: ["分析", "理解", "解釋", "檢查"]
        }
        
        prompt_lower = prompt.lower()
        intent_scores = {}
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in prompt_lower)
            intent_scores[intent] = score
        
        # 找出最高分的意圖
        best_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[best_intent]
        
        # 計算信心度（基於關鍵詞匹配數量）
        confidence = min(max_score / 3.0, 1.0) if max_score > 0 else 0.3
        
        return best_intent, confidence
    
    def _extract_tools_from_response(self, response: str) -> List[str]:
        """從回應中提取工具調用"""
        import re
        tools = []
        
        # 提取 <invoke name="..."> 格式
        invokes = re.findall(r'<invoke name="([^"]+)">', response)
        tools.extend(invokes)
        
        # 提取 function_calls 格式
        func_calls = re.findall(r'<function_calls>.*?name="([^"]+)".*?</function_calls>', 
                               response, re.DOTALL)
        tools.extend(func_calls)
        
        return tools
    
    def evaluate_intent_understanding(self, 
                                    prompt: str, 
                                    response: str,
                                    expected_intent: IntentType,
                                    expected_tools: List[str]) -> IntentEvaluation:
        """評估意圖理解和工具調用"""
        
        # 檢測意圖
        detected_intent, confidence = self._detect_intent(prompt)
        
        # 提取實際使用的工具
        actual_tools = self._extract_tools_from_response(response)
        
        # 獲取意圖對應的工具規則
        tool_rules = self.intent_tool_mapping.get(expected_intent, {})
        required_tools = set(tool_rules.get("required", []))
        optional_tools = set(tool_rules.get("optional", []))
        expected_sequence = tool_rules.get("sequence", [])
        
        # 計算工具準確率
        expected_set = set(expected_tools)
        actual_set = set(actual_tools)
        
        # 找出缺失和多餘的工具
        missing_tools = list(expected_set - actual_set)
        extra_tools = list(actual_set - expected_set - optional_tools)
        
        # 計算工具準確率
        if not expected_tools:
            tool_accuracy = 1.0 if not actual_tools else 0.5
        else:
            correct_tools = len(expected_set & actual_set)
            tool_accuracy = correct_tools / len(expected_set)
            
            # 如果有多餘的工具，扣分
            if extra_tools:
                tool_accuracy *= 0.8
        
        # 檢查工具調用順序
        sequence_correct = True
        if expected_sequence and actual_tools:
            # 檢查關鍵工具的順序
            for i, tool in enumerate(expected_sequence):
                if tool in actual_tools:
                    actual_index = actual_tools.index(tool)
                    # 檢查是否按順序出現
                    for j in range(i):
                        if expected_sequence[j] in actual_tools:
                            prev_index = actual_tools.index(expected_sequence[j])
                            if prev_index > actual_index:
                                sequence_correct = False
                                break
        
        # 計算意圖滿足度
        intent_fulfillment = 0.0
        
        # 意圖匹配權重 40%
        if detected_intent == expected_intent:
            intent_fulfillment += 0.4
        
        # 工具準確率權重 40%
        intent_fulfillment += tool_accuracy * 0.4
        
        # 工具順序權重 20%
        if sequence_correct:
            intent_fulfillment += 0.2
        
        return IntentEvaluation(
            intent_type=detected_intent,
            confidence=confidence,
            tool_accuracy=tool_accuracy,
            tool_sequence_correct=sequence_correct,
            missing_tools=missing_tools,
            extra_tools=extra_tools,
            intent_fulfillment=intent_fulfillment
        )
    
    def generate_k2_response_with_intent(self, prompt: str, intent: IntentType) -> Dict:
        """生成帶有意圖理解的K2回應"""
        
        # 構建提示，強調工具使用
        tool_rules = self.intent_tool_mapping.get(intent, {})
        required_tools = tool_rules.get("required", [])
        
        enhanced_prompt = f"""
你是一個精確的編程助手。用戶的意圖是：{intent.value}

必須使用的工具：{', '.join(required_tools) if required_tools else '根據需要選擇'}

可用工具：
- Read: 讀取文件內容
- Write: 寫入新文件
- Edit/MultiEdit: 編輯現有文件
- Grep: 搜索文件內容
- Glob: 查找文件
- Bash: 執行命令
- Task: 複雜任務代理

使用工具時請用以下格式：
<function_calls>
<invoke name="工具名">
<parameter name="參數名">參數值</parameter>
</invoke>
</function_calls>

用戶請求: {prompt}
"""
        
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.k2_model,
                messages=[{"role": "user", "content": enhanced_prompt}],
                temperature=0.3,  # 降低溫度以提高一致性
                max_completion_tokens=1024
            )
            
            response = completion.choices[0].message.content
            tools = self._extract_tools_from_response(response)
            
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
    
    def run_intent_evaluation_suite(self) -> Dict:
        """運行完整的意圖評估套件"""
        results = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": [],
            "intent_metrics": {},
            "overall_metrics": {}
        }
        
        # 按意圖類型統計
        intent_stats = {intent: {"total": 0, "accuracy": 0, "fulfillment": 0} 
                       for intent in IntentType}
        
        total_tool_accuracy = 0
        total_intent_fulfillment = 0
        successful_tests = 0
        
        for test_case in self.test_cases:
            logger.info(f"\n🧪 測試: {test_case['id']} - {test_case['intent'].value}")
            logger.info(f"📝 提示: {test_case['prompt']}")
            
            # 生成K2回應
            k2_result = self.generate_k2_response_with_intent(
                test_case['prompt'],
                test_case['intent']
            )
            
            if k2_result['success']:
                # 評估意圖理解
                evaluation = self.evaluate_intent_understanding(
                    test_case['prompt'],
                    k2_result['response'],
                    test_case['intent'],
                    test_case['expected_tools']
                )
                
                logger.info(f"✅ 工具準確率: {evaluation.tool_accuracy:.1%}")
                logger.info(f"🎯 意圖滿足度: {evaluation.intent_fulfillment:.1%}")
                
                # 記錄結果
                test_result = {
                    "test_id": test_case['id'],
                    "prompt": test_case['prompt'],
                    "intent": test_case['intent'].value,
                    "detected_intent": evaluation.intent_type.value,
                    "confidence": evaluation.confidence,
                    "expected_tools": test_case['expected_tools'],
                    "actual_tools": k2_result['tools'],
                    "tool_accuracy": evaluation.tool_accuracy,
                    "sequence_correct": evaluation.tool_sequence_correct,
                    "missing_tools": evaluation.missing_tools,
                    "extra_tools": evaluation.extra_tools,
                    "intent_fulfillment": evaluation.intent_fulfillment,
                    "response_preview": k2_result['response'][:200] + "..."
                }
                
                results["test_results"].append(test_result)
                
                # 更新統計
                intent_stats[test_case['intent']]["total"] += 1
                intent_stats[test_case['intent']]["accuracy"] += evaluation.tool_accuracy
                intent_stats[test_case['intent']]["fulfillment"] += evaluation.intent_fulfillment
                
                total_tool_accuracy += evaluation.tool_accuracy
                total_intent_fulfillment += evaluation.intent_fulfillment
                successful_tests += 1
                
            else:
                results["test_results"].append({
                    "test_id": test_case['id'],
                    "error": k2_result['response'],
                    "success": False
                })
            
            time.sleep(1)  # 避免速率限制
        
        # 計算總體指標
        if successful_tests > 0:
            results["overall_metrics"] = {
                "average_tool_accuracy": total_tool_accuracy / successful_tests,
                "average_intent_fulfillment": total_intent_fulfillment / successful_tests,
                "success_rate": successful_tests / len(self.test_cases),
                "total_tests": len(self.test_cases),
                "successful_tests": successful_tests
            }
            
            # 計算每個意圖類型的平均值
            for intent, stats in intent_stats.items():
                if stats["total"] > 0:
                    results["intent_metrics"][intent.value] = {
                        "average_accuracy": stats["accuracy"] / stats["total"],
                        "average_fulfillment": stats["fulfillment"] / stats["total"],
                        "test_count": stats["total"]
                    }
        
        return results
    
    def generate_improvement_plan(self, results: Dict) -> str:
        """生成改進計劃"""
        plan = """
# 意圖理解改進計劃

## 當前狀態
"""
        
        metrics = results["overall_metrics"]
        plan += f"""
- **平均工具準確率**: {metrics['average_tool_accuracy']:.1%}
- **平均意圖滿足度**: {metrics['average_intent_fulfillment']:.1%}
- **測試成功率**: {metrics['success_rate']:.1%}

## 分意圖類型分析
"""
        
        # 找出需要改進的意圖類型
        improvement_needed = []
        
        for intent_type, metrics in results["intent_metrics"].items():
            plan += f"\n### {intent_type}\n"
            plan += f"- 工具準確率: {metrics['average_accuracy']:.1%}\n"
            plan += f"- 意圖滿足度: {metrics['average_fulfillment']:.1%}\n"
            
            if metrics['average_accuracy'] < 0.9:
                improvement_needed.append((intent_type, metrics['average_accuracy']))
        
        # 生成具體改進建議
        plan += "\n## 改進策略\n\n"
        
        if improvement_needed:
            plan += "### 優先改進項目\n"
            for intent_type, accuracy in sorted(improvement_needed, key=lambda x: x[1]):
                plan += f"\n**{intent_type}** (當前準確率: {accuracy:.1%})\n"
                
                # 分析常見錯誤
                intent_errors = [r for r in results["test_results"] 
                               if r.get("intent") == intent_type and r.get("tool_accuracy", 0) < 1.0]
                
                if intent_errors:
                    plan += "常見問題:\n"
                    for error in intent_errors[:3]:
                        if error.get("missing_tools"):
                            plan += f"- 缺失工具: {', '.join(error['missing_tools'])}\n"
                        if error.get("extra_tools"):
                            plan += f"- 多餘工具: {', '.join(error['extra_tools'])}\n"
        
        # 訓練建議
        plan += """
### 訓練建議

1. **增強工具選擇訓練**
   - 收集更多包含正確工具調用的對話
   - 為每個意圖類型創建專門的訓練數據
   - 強化工具調用順序的學習

2. **意圖識別優化**
   - 擴充意圖關鍵詞庫
   - 使用更複雜的意圖分類模型
   - 增加上下文理解能力

3. **漸進式改進路徑**
   - 第一階段：達到90%工具準確率
   - 第二階段：達到95%工具準確率
   - 第三階段：達到100%工具準確率
"""
        
        return plan


def main():
    """主函數"""
    api_key = os.getenv("GROQ_API_KEY", "your-api-key-here")
    
    logger.info("🚀 啟動意圖理解評估系統")
    logger.info("🎯 目標：第一階段達到100%工具調用準確率")
    
    # 創建評估器
    evaluator = IntentUnderstandingEvaluator(api_key)
    
    # 運行評估
    results = evaluator.run_intent_evaluation_suite()
    
    # 生成改進計劃
    improvement_plan = evaluator.generate_improvement_plan(results)
    
    # 保存結果
    with open("intent_evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    with open("intent_improvement_plan.md", "w", encoding="utf-8") as f:
        f.write(improvement_plan)
    
    # 生成詳細報告
    report = f"""
# 意圖理解評估報告

測試時間: {results['test_time']}

## 總體指標

- **平均工具準確率**: {results['overall_metrics']['average_tool_accuracy']:.1%}
- **平均意圖滿足度**: {results['overall_metrics']['average_intent_fulfillment']:.1%}
- **距離目標差距**: {100 - results['overall_metrics']['average_tool_accuracy']*100:.1f}%

## 詳細測試結果
"""
    
    for test in results['test_results']:
        if test.get('success', True):
            report += f"""
### {test['test_id']}

- **提示**: {test['prompt']}
- **意圖**: {test['intent']} → {test['detected_intent']}
- **工具準確率**: {test['tool_accuracy']:.1%}
- **預期工具**: {', '.join(test['expected_tools']) if test['expected_tools'] else '無'}
- **實際工具**: {', '.join(test['actual_tools']) if test['actual_tools'] else '無'}
- **缺失工具**: {', '.join(test['missing_tools']) if test['missing_tools'] else '無'}
- **順序正確**: {'✅' if test['sequence_correct'] else '❌'}

---
"""
    
    with open("intent_evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    # 打印摘要
    logger.info("\n" + "="*50)
    logger.info("📊 評估完成！")
    logger.info(f"🎯 工具準確率: {results['overall_metrics']['average_tool_accuracy']:.1%}")
    logger.info(f"📈 意圖滿足度: {results['overall_metrics']['average_intent_fulfillment']:.1%}")
    logger.info(f"🚀 距離100%目標: {100 - results['overall_metrics']['average_tool_accuracy']*100:.1f}%")
    logger.info("\n詳細報告已保存至:")
    logger.info("- intent_evaluation_results.json")
    logger.info("- intent_evaluation_report.md")
    logger.info("- intent_improvement_plan.md")


if __name__ == "__main__":
    main()