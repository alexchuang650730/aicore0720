#!/usr/bin/env python3
"""
真實的工具調用率和意圖理解率計算公式
不是模擬，是實際可測量的指標
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolCallEvent:
    """工具調用事件"""
    timestamp: datetime
    user_request: str
    expected_tools: List[str]  # 預期應該調用的工具
    actual_tools: List[str]    # 實際調用的工具
    success: bool             # 是否成功完成任務
    error: str = None         # 錯誤信息（如果有）


@dataclass
class IntentEvent:
    """意圖理解事件"""
    timestamp: datetime
    user_input: str
    true_intent: str          # 真實意圖（人工標註）
    predicted_intent: str     # 預測意圖
    confidence: float         # 置信度
    action_taken: str         # 採取的行動
    outcome: str             # 結果


class RealMetricsCalculator:
    """真實指標計算器"""
    
    def __init__(self):
        self.tool_call_events: List[ToolCallEvent] = []
        self.intent_events: List[IntentEvent] = []
    
    # ==================== 工具調用率公式 ====================
    
    def calculate_tool_call_accuracy(self) -> Dict[str, float]:
        """
        工具調用準確率 = 正確工具調用次數 / 總工具調用次數
        
        細分指標：
        1. 精確匹配率：完全匹配預期工具集
        2. 召回率：找到所有必需工具
        3. 精確率：沒有調用多餘工具
        4. F1分數：綜合評分
        """
        
        if not self.tool_call_events:
            return {"error": "無數據"}
        
        total_calls = len(self.tool_call_events)
        exact_matches = 0
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for event in self.tool_call_events:
            expected_set = set(event.expected_tools)
            actual_set = set(event.actual_tools)
            
            # 精確匹配
            if expected_set == actual_set and event.success:
                exact_matches += 1
            
            # 計算TP, FP, FN
            tp = len(expected_set & actual_set)  # 正確調用的工具
            fp = len(actual_set - expected_set)  # 多餘調用的工具
            fn = len(expected_set - actual_set)  # 遺漏的工具
            
            true_positives += tp
            false_positives += fp
            false_negatives += fn
        
        # 計算各項指標
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "total_calls": total_calls,
            "exact_match_rate": (exact_matches / total_calls) * 100,
            "precision": precision * 100,
            "recall": recall * 100,
            "f1_score": f1_score * 100,
            "success_rate": sum(1 for e in self.tool_call_events if e.success) / total_calls * 100
        }
    
    def get_tool_call_formula(self) -> str:
        """獲取工具調用率公式說明"""
        return """
工具調用準確率計算公式：

1. 精確匹配率 = (完全正確的工具調用次數 / 總調用次數) × 100%
   - 調用的工具集完全等於預期工具集
   - 且任務成功完成

2. 精確率(Precision) = TP / (TP + FP) × 100%
   - TP: 正確調用的工具數
   - FP: 多餘調用的工具數

3. 召回率(Recall) = TP / (TP + FN) × 100%
   - FN: 應該調用但遺漏的工具數

4. F1分數 = 2 × (Precision × Recall) / (Precision + Recall) × 100%

5. 任務成功率 = (成功完成的任務數 / 總任務數) × 100%

綜合工具調用率 = 0.4×精確匹配率 + 0.3×F1分數 + 0.3×任務成功率
"""
    
    # ==================== 意圖理解率公式 ====================
    
    def calculate_intent_understanding(self) -> Dict[str, float]:
        """
        意圖理解準確率 = 正確理解的意圖數 / 總意圖數
        
        細分指標：
        1. 意圖分類準確率
        2. 置信度校準度
        3. 行動正確率
        4. 結果滿意度
        """
        
        if not self.intent_events:
            return {"error": "無數據"}
        
        total_intents = len(self.intent_events)
        correct_intents = sum(1 for e in self.intent_events if e.true_intent == e.predicted_intent)
        
        # 計算置信度校準
        confidence_buckets = {}
        for event in self.intent_events:
            bucket = int(event.confidence * 10) / 10  # 0.1為一個區間
            if bucket not in confidence_buckets:
                confidence_buckets[bucket] = {"total": 0, "correct": 0}
            confidence_buckets[bucket]["total"] += 1
            if event.true_intent == event.predicted_intent:
                confidence_buckets[bucket]["correct"] += 1
        
        # 計算ECE (Expected Calibration Error)
        ece = 0
        for bucket, stats in confidence_buckets.items():
            if stats["total"] > 0:
                accuracy = stats["correct"] / stats["total"]
                weight = stats["total"] / total_intents
                ece += weight * abs(bucket - accuracy)
        
        # 行動正確率（意圖對但行動錯也算失敗）
        correct_actions = sum(1 for e in self.intent_events 
                            if e.true_intent == e.predicted_intent 
                            and e.outcome == "success")
        
        return {
            "total_intents": total_intents,
            "intent_accuracy": (correct_intents / total_intents) * 100,
            "action_accuracy": (correct_actions / total_intents) * 100,
            "calibration_error": ece * 100,
            "average_confidence": sum(e.confidence for e in self.intent_events) / total_intents * 100
        }
    
    def get_intent_understanding_formula(self) -> str:
        """獲取意圖理解率公式說明"""
        return """
意圖理解準確率計算公式：

1. 基礎意圖準確率 = (正確預測的意圖數 / 總意圖數) × 100%

2. 行動準確率 = (意圖正確且行動成功數 / 總意圖數) × 100%

3. 置信度校準誤差(ECE) = Σ(|置信度 - 實際準確率| × 權重)
   - 越低越好，表示置信度與實際準確率越接近

4. 意圖類別準確率：
   - 信息查詢類: 正確數/總數
   - 任務執行類: 正確數/總數
   - 問題解決類: 正確數/總數
   - 創意生成類: 正確數/總數

綜合意圖理解率 = 0.5×基礎意圖準確率 + 0.3×行動準確率 + 0.2×(100-ECE)
"""
    
    # ==================== 實際測量示例 ====================
    
    def add_real_measurement_example(self):
        """添加真實測量示例"""
        
        # 工具調用示例
        self.tool_call_events.append(ToolCallEvent(
            timestamp=datetime.now(),
            user_request="讀取config.json文件並修改port為8080",
            expected_tools=["Read", "Edit"],
            actual_tools=["Read", "Edit"],
            success=True
        ))
        
        self.tool_call_events.append(ToolCallEvent(
            timestamp=datetime.now(),
            user_request="搜索所有包含'error'的日誌文件",
            expected_tools=["Grep"],
            actual_tools=["Glob", "Read", "Grep"],  # 調用了多餘的工具
            success=True
        ))
        
        # 意圖理解示例
        self.intent_events.append(IntentEvent(
            timestamp=datetime.now(),
            user_input="幫我看看這個bug怎麼修",
            true_intent="debug_assistance",
            predicted_intent="debug_assistance",
            confidence=0.85,
            action_taken="analyze_error_and_suggest_fix",
            outcome="success"
        ))
        
        self.intent_events.append(IntentEvent(
            timestamp=datetime.now(),
            user_input="創建一個新的React組件",
            true_intent="code_generation",
            predicted_intent="file_creation",  # 理解偏差
            confidence=0.70,
            action_taken="create_empty_file",
            outcome="partial_success"
        ))
    
    def demonstrate_calculation(self):
        """演示計算過程"""
        # 添加示例數據
        self.add_real_measurement_example()
        
        print("=" * 60)
        print("真實指標計算演示")
        print("=" * 60)
        
        # 工具調用率
        print("\n【工具調用準確率】")
        print(self.get_tool_call_formula())
        
        tool_metrics = self.calculate_tool_call_accuracy()
        print("\n實際計算結果:")
        for key, value in tool_metrics.items():
            if key != "total_calls":
                print(f"  {key}: {value:.1f}%")
            else:
                print(f"  {key}: {value}")
        
        # 意圖理解率
        print("\n" + "=" * 60)
        print("\n【意圖理解準確率】")
        print(self.get_intent_understanding_formula())
        
        intent_metrics = self.calculate_intent_understanding()
        print("\n實際計算結果:")
        for key, value in intent_metrics.items():
            if key != "total_intents":
                print(f"  {key}: {value:.1f}%")
            else:
                print(f"  {key}: {value}")
        
        # 綜合評分
        print("\n" + "=" * 60)
        print("\n【綜合評分】")
        
        tool_score = (
            0.4 * tool_metrics.get("exact_match_rate", 0) +
            0.3 * tool_metrics.get("f1_score", 0) +
            0.3 * tool_metrics.get("success_rate", 0)
        )
        
        intent_score = (
            0.5 * intent_metrics.get("intent_accuracy", 0) +
            0.3 * intent_metrics.get("action_accuracy", 0) +
            0.2 * (100 - intent_metrics.get("calibration_error", 0))
        )
        
        print(f"工具調用綜合得分: {tool_score:.1f}%")
        print(f"意圖理解綜合得分: {intent_score:.1f}%")
        print(f"總體AI助手得分: {(tool_score + intent_score) / 2:.1f}%")


def main():
    """主函數"""
    calculator = RealMetricsCalculator()
    calculator.demonstrate_calculation()
    
    # 保存公式文檔
    with open("metrics_formulas.md", "w") as f:
        f.write("# AI助手評估指標公式\n\n")
        f.write("## 工具調用準確率\n")
        f.write(calculator.get_tool_call_formula())
        f.write("\n\n## 意圖理解準確率\n")
        f.write(calculator.get_intent_understanding_formula())
        f.write("\n\n## 如何實際測量\n")
        f.write("""
1. 收集真實的用戶請求和系統響應
2. 人工標註預期工具和真實意圖
3. 記錄系統實際調用的工具和預測的意圖
4. 使用上述公式計算各項指標
5. 定期評估和優化

這些是真實的、可測量的指標，不是模擬值。
""")


if __name__ == "__main__":
    main()