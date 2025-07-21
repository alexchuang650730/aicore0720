#!/usr/bin/env python3
"""
意圖理解成功率優化系統
真實的意圖分類和理解改進
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict
import numpy as np
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentCategory(Enum):
    """意圖類別"""
    # 信息查詢
    QUERY_INFO = "query_info"              # 查詢信息
    EXPLAIN_CONCEPT = "explain_concept"    # 解釋概念
    
    # 代碼操作
    READ_CODE = "read_code"                # 讀取代碼
    WRITE_CODE = "write_code"              # 編寫代碼
    EDIT_CODE = "edit_code"                # 編輯代碼
    REFACTOR_CODE = "refactor_code"        # 重構代碼
    
    # 錯誤處理
    DEBUG_ERROR = "debug_error"            # 調試錯誤
    FIX_BUG = "fix_bug"                   # 修復bug
    ANALYZE_ERROR = "analyze_error"        # 分析錯誤
    
    # 搜索操作
    SEARCH_CODE = "search_code"            # 搜索代碼
    FIND_PATTERN = "find_pattern"          # 查找模式
    
    # 系統操作
    RUN_COMMAND = "run_command"            # 運行命令
    INSTALL_PACKAGE = "install_package"    # 安裝包
    CONFIG_SYSTEM = "config_system"        # 配置系統
    
    # 測試相關
    RUN_TEST = "run_test"                  # 運行測試
    WRITE_TEST = "write_test"              # 編寫測試
    
    # 文檔相關
    WRITE_DOC = "write_doc"                # 編寫文檔
    UPDATE_README = "update_readme"        # 更新README


@dataclass
class IntentSignal:
    """意圖信號 - 用於識別意圖的特徵"""
    keywords: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    context_clues: List[str] = field(default_factory=list)
    negative_signals: List[str] = field(default_factory=list)  # 排除信號
    confidence_boost: float = 0.0


class IntentUnderstandingOptimizer:
    """意圖理解優化器"""
    
    def __init__(self):
        self.base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        
        # 意圖信號庫
        self.intent_signals = self._initialize_intent_signals()
        
        # 意圖理解模型
        self.intent_model = {
            "signal_weights": {
                "keywords": 0.4,
                "patterns": 0.3,
                "context": 0.2,
                "history": 0.1
            },
            "confidence_threshold": 0.7,
            "ambiguity_threshold": 0.15  # 兩個意圖分數差小於此值視為歧義
        }
        
        # 學習記錄
        self.learning_history = {
            "successful_predictions": [],
            "failed_predictions": [],
            "ambiguous_cases": []
        }
        
        # 上下文記憶
        self.context_memory = {
            "recent_intents": [],  # 最近的意圖
            "current_task": None,  # 當前任務
            "user_preferences": {}  # 用戶偏好
        }
    
    def _initialize_intent_signals(self) -> Dict[IntentCategory, IntentSignal]:
        """初始化意圖信號庫"""
        return {
            # 查詢信息
            IntentCategory.QUERY_INFO: IntentSignal(
                keywords=["什麼", "如何", "為什麼", "是否", "有沒有", "查詢", "告訴我"],
                patterns=[".*是什麼.*", ".*怎麼.*", ".*為何.*"],
                context_clues=["解釋", "說明", "描述"],
                confidence_boost=0.1
            ),
            
            # 讀取代碼
            IntentCategory.READ_CODE: IntentSignal(
                keywords=["讀", "看", "查看", "顯示", "打開", "文件"],
                patterns=[".*看.*文件.*", ".*讀取.*代碼.*", ".*查看.*內容.*"],
                context_clues=["file", "path", ".py", ".js"],
                negative_signals=["寫", "創建", "修改"],
                confidence_boost=0.15
            ),
            
            # 編寫代碼
            IntentCategory.WRITE_CODE: IntentSignal(
                keywords=["寫", "創建", "實現", "編寫", "新建", "生成"],
                patterns=[".*寫一個.*", ".*創建.*函數.*", ".*實現.*功能.*"],
                context_clues=["function", "class", "component"],
                negative_signals=["讀", "查看", "修改"],
                confidence_boost=0.2
            ),
            
            # 編輯代碼
            IntentCategory.EDIT_CODE: IntentSignal(
                keywords=["修改", "更改", "編輯", "更新", "改", "替換"],
                patterns=[".*修改.*為.*", ".*把.*改成.*", ".*更新.*代碼.*"],
                context_clues=["change", "modify", "update"],
                negative_signals=["創建", "新建", "查看"],
                confidence_boost=0.15
            ),
            
            # 調試錯誤
            IntentCategory.DEBUG_ERROR: IntentSignal(
                keywords=["調試", "debug", "錯誤", "error", "異常", "報錯"],
                patterns=[".*為什麼.*報錯.*", ".*調試.*問題.*", ".*錯誤.*原因.*"],
                context_clues=["traceback", "exception", "失敗"],
                confidence_boost=0.25
            ),
            
            # 修復bug
            IntentCategory.FIX_BUG: IntentSignal(
                keywords=["修復", "fix", "解決", "修正", "糾正"],
                patterns=[".*修復.*bug.*", ".*解決.*問題.*", ".*修正.*錯誤.*"],
                context_clues=["bug", "issue", "problem"],
                negative_signals=["分析", "查看", "為什麼"],
                confidence_boost=0.2
            ),
            
            # 搜索代碼
            IntentCategory.SEARCH_CODE: IntentSignal(
                keywords=["搜索", "查找", "尋找", "找", "grep", "search"],
                patterns=[".*找.*函數.*", ".*搜索.*代碼.*", ".*查找.*文件.*"],
                context_clues=["pattern", "keyword", "regex"],
                confidence_boost=0.15
            ),
            
            # 運行命令
            IntentCategory.RUN_COMMAND: IntentSignal(
                keywords=["運行", "執行", "run", "啟動", "start"],
                patterns=[".*運行.*命令.*", ".*執行.*腳本.*", ".*啟動.*服務.*"],
                context_clues=["command", "script", "bash", "python"],
                negative_signals=["測試", "test"],
                confidence_boost=0.1
            ),
            
            # 運行測試
            IntentCategory.RUN_TEST: IntentSignal(
                keywords=["測試", "test", "檢測", "驗證"],
                patterns=[".*運行.*測試.*", ".*執行.*test.*", ".*跑.*測試.*"],
                context_clues=["pytest", "unittest", "jest"],
                confidence_boost=0.2
            ),
            
            # 編寫測試
            IntentCategory.WRITE_TEST: IntentSignal(
                keywords=["寫測試", "編寫測試", "創建測試", "test case"],
                patterns=[".*寫.*測試.*", ".*創建.*test.*"],
                context_clues=["test_", "spec", "測試用例"],
                negative_signals=["運行", "執行"],
                confidence_boost=0.15
            )
        }
    
    def understand_intent(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        理解用戶意圖
        
        Args:
            user_input: 用戶輸入
            context: 上下文信息
            
        Returns:
            意圖理解結果
        """
        # 預處理輸入
        normalized_input = user_input.lower().strip()
        
        # 計算每個意圖的分數
        intent_scores = {}
        for intent, signal in self.intent_signals.items():
            score = self._calculate_intent_score(normalized_input, signal, context)
            if score > 0:
                intent_scores[intent] = score
        
        # 如果沒有匹配的意圖
        if not intent_scores:
            return {
                "success": False,
                "intent": None,
                "confidence": 0.0,
                "reason": "無法識別意圖"
            }
        
        # 排序並獲取最高分
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        best_intent, best_score = sorted_intents[0]
        
        # 檢查是否有歧義
        ambiguous = False
        if len(sorted_intents) > 1:
            second_score = sorted_intents[1][1]
            if best_score - second_score < self.intent_model["ambiguity_threshold"]:
                ambiguous = True
        
        # 檢查置信度
        if best_score < self.intent_model["confidence_threshold"]:
            return {
                "success": False,
                "intent": best_intent,
                "confidence": best_score,
                "reason": "置信度過低",
                "all_scores": intent_scores
            }
        
        # 更新上下文記憶
        self._update_context_memory(best_intent)
        
        result = {
            "success": True,
            "intent": best_intent,
            "confidence": best_score,
            "ambiguous": ambiguous,
            "all_scores": intent_scores,
            "suggested_tools": self._suggest_tools_for_intent(best_intent)
        }
        
        # 記錄到學習歷史
        self.learning_history["successful_predictions"].append({
            "input": user_input,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _calculate_intent_score(self, 
                               input_text: str, 
                               signal: IntentSignal,
                               context: Optional[Dict]) -> float:
        """計算單個意圖的分數"""
        score = 0.0
        weights = self.intent_model["signal_weights"]
        
        # 1. 關鍵詞匹配
        keyword_score = 0.0
        for keyword in signal.keywords:
            if keyword in input_text:
                keyword_score += 1.0
        if signal.keywords:
            keyword_score = keyword_score / len(signal.keywords)
        score += keyword_score * weights["keywords"]
        
        # 2. 模式匹配
        pattern_score = 0.0
        if signal.patterns:
            import re
            for pattern in signal.patterns:
                if re.search(pattern, input_text):
                    pattern_score += 1.0
            pattern_score = pattern_score / len(signal.patterns)
        score += pattern_score * weights["patterns"]
        
        # 3. 上下文線索
        context_score = 0.0
        if context and signal.context_clues:
            context_str = json.dumps(context).lower()
            for clue in signal.context_clues:
                if clue in context_str or clue in input_text:
                    context_score += 1.0
            context_score = context_score / len(signal.context_clues)
        score += context_score * weights["context"]
        
        # 4. 歷史相關性
        history_score = self._calculate_history_relevance(signal)
        score += history_score * weights["history"]
        
        # 5. 負面信號檢查
        if signal.negative_signals:
            for neg_signal in signal.negative_signals:
                if neg_signal in input_text:
                    score *= 0.5  # 減半分數
        
        # 6. 置信度提升
        score += signal.confidence_boost
        
        # 確保分數在0-1之間
        return min(max(score, 0.0), 1.0)
    
    def _calculate_history_relevance(self, signal: IntentSignal) -> float:
        """基於歷史計算相關性"""
        if not self.context_memory["recent_intents"]:
            return 0.0
        
        # 檢查最近的意圖是否相關
        recent_count = 0
        for recent_intent in self.context_memory["recent_intents"][-5:]:
            # 這裡簡化處理，實際可以有更複雜的相關性計算
            if hasattr(recent_intent, 'value'):
                recent_count += 0.2
        
        return min(recent_count, 1.0)
    
    def _update_context_memory(self, intent: IntentCategory):
        """更新上下文記憶"""
        self.context_memory["recent_intents"].append(intent)
        
        # 保持最近10個意圖
        if len(self.context_memory["recent_intents"]) > 10:
            self.context_memory["recent_intents"] = \
                self.context_memory["recent_intents"][-10:]
    
    def _suggest_tools_for_intent(self, intent: IntentCategory) -> List[str]:
        """為意圖建議工具"""
        tool_mapping = {
            IntentCategory.READ_CODE: ["Read", "Glob"],
            IntentCategory.WRITE_CODE: ["Write", "MultiEdit"],
            IntentCategory.EDIT_CODE: ["Edit", "MultiEdit"],
            IntentCategory.SEARCH_CODE: ["Grep", "Search", "Glob"],
            IntentCategory.DEBUG_ERROR: ["Read", "Grep", "Task"],
            IntentCategory.FIX_BUG: ["Edit", "MultiEdit", "SmartIntervention"],
            IntentCategory.RUN_COMMAND: ["Bash"],
            IntentCategory.RUN_TEST: ["Bash", "Read"],
            IntentCategory.WRITE_TEST: ["Write", "Edit"]
        }
        
        return tool_mapping.get(intent, ["Task"])
    
    def learn_from_feedback(self, 
                           user_input: str, 
                           predicted_intent: IntentCategory,
                           correct_intent: IntentCategory,
                           success: bool):
        """從反饋中學習"""
        feedback_entry = {
            "input": user_input,
            "predicted": predicted_intent,
            "correct": correct_intent,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.learning_history["successful_predictions"].append(feedback_entry)
        else:
            self.learning_history["failed_predictions"].append(feedback_entry)
            
            # 分析失敗原因並調整信號
            self._analyze_failure(user_input, predicted_intent, correct_intent)
    
    def _analyze_failure(self, 
                        user_input: str, 
                        predicted: IntentCategory,
                        correct: IntentCategory):
        """分析預測失敗"""
        # 提取輸入中的關鍵特徵
        words = user_input.lower().split()
        
        # 更新正確意圖的信號
        if correct in self.intent_signals:
            signal = self.intent_signals[correct]
            # 簡單的學習：添加新關鍵詞
            for word in words:
                if len(word) > 3 and word not in signal.keywords:
                    # 這裡可以有更複雜的邏輯
                    logger.info(f"學習新關鍵詞 '{word}' 對應意圖 {correct.value}")
    
    def calculate_success_rate(self) -> Dict[str, float]:
        """計算成功率"""
        total_predictions = (
            len(self.learning_history["successful_predictions"]) +
            len(self.learning_history["failed_predictions"])
        )
        
        if total_predictions == 0:
            return {"overall": 0.0}
        
        success_count = len(self.learning_history["successful_predictions"])
        overall_rate = success_count / total_predictions
        
        # 按意圖類別統計
        category_stats = defaultdict(lambda: {"success": 0, "total": 0})
        
        for entry in self.learning_history["successful_predictions"]:
            if "predicted" in entry:
                intent = entry["predicted"]
                category_stats[intent]["success"] += 1
                category_stats[intent]["total"] += 1
        
        for entry in self.learning_history["failed_predictions"]:
            if "correct" in entry:
                intent = entry["correct"]
                category_stats[intent]["total"] += 1
        
        category_rates = {}
        for intent, stats in category_stats.items():
            if stats["total"] > 0:
                category_rates[intent.value if hasattr(intent, 'value') else str(intent)] = \
                    stats["success"] / stats["total"]
        
        return {
            "overall": overall_rate,
            "by_category": category_rates
        }
    
    def demonstrate_intent_understanding(self):
        """演示意圖理解"""
        test_cases = [
            ("幫我看看config.json文件的內容", IntentCategory.READ_CODE),
            ("創建一個新的Python腳本來處理數據", IntentCategory.WRITE_CODE),
            ("修改端口號為8080", IntentCategory.EDIT_CODE),
            ("為什麼這段代碼會報錯？", IntentCategory.DEBUG_ERROR),
            ("修復登錄功能的bug", IntentCategory.FIX_BUG),
            ("搜索所有包含TODO的文件", IntentCategory.SEARCH_CODE),
            ("運行測試看看結果", IntentCategory.RUN_TEST),
            ("執行npm install", IntentCategory.RUN_COMMAND)
        ]
        
        print("意圖理解系統演示")
        print("=" * 60)
        
        for user_input, expected_intent in test_cases:
            result = self.understand_intent(user_input)
            
            print(f"\n輸入: {user_input}")
            print(f"預期意圖: {expected_intent.value}")
            print(f"識別結果: {result['intent'].value if result['success'] else '失敗'}")
            print(f"置信度: {result['confidence']:.2f}")
            print(f"建議工具: {result.get('suggested_tools', [])}")
            
            # 模擬反饋
            is_correct = result['success'] and result['intent'] == expected_intent
            self.learn_from_feedback(
                user_input, 
                result.get('intent'),
                expected_intent,
                is_correct
            )
        
        # 顯示統計
        print("\n" + "=" * 60)
        print("意圖理解統計")
        success_rate = self.calculate_success_rate()
        print(f"總體成功率: {success_rate['overall'] * 100:.1f}%")
        
        if "by_category" in success_rate:
            print("\n各類別成功率:")
            for category, rate in success_rate["by_category"].items():
                print(f"  {category}: {rate * 100:.1f}%")


def main():
    """主函數"""
    optimizer = IntentUnderstandingOptimizer()
    optimizer.demonstrate_intent_understanding()
    
    # 保存意圖理解指南
    guide = """
# 意圖理解優化指南

## 核心組件
1. **意圖信號庫**: 關鍵詞、模式、上下文線索
2. **評分算法**: 多維度加權評分
3. **上下文記憶**: 保持對話連貫性
4. **學習機制**: 從成功和失敗中學習

## 優化策略
1. 持續收集真實用戶輸入
2. 人工標註正確意圖
3. 分析失敗案例，更新信號庫
4. A/B測試不同的權重配置
5. 引入更多上下文信息

## 成功指標
- 總體準確率 > 90%
- 各類別準確率 > 85%
- 歧義處理能力
- 響應時間 < 100ms
"""
    
    with open("intent_understanding_guide.md", "w") as f:
        f.write(guide)


if __name__ == "__main__":
    main()