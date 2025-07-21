#!/usr/bin/env python3
"""
意圖理解訓練系統
通過真實數據訓練提升意圖理解準確率
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentTrainingSystem:
    """意圖理解訓練系統"""
    
    def __init__(self):
        self.base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        
        # 訓練數據集
        self.training_data = self._load_training_data()
        
        # 意圖模型參數（可學習的）
        self.model_params = {
            "keyword_weights": defaultdict(lambda: defaultdict(float)),
            "pattern_importance": defaultdict(float),
            "context_relevance": defaultdict(float),
            "confidence_threshold": 0.4,  # 降低初始閾值
            "learning_rate": 0.1
        }
        
        # 性能指標
        self.metrics = {
            "training_iterations": 0,
            "current_accuracy": 0.0,
            "confusion_matrix": defaultdict(lambda: defaultdict(int))
        }
    
    def _load_training_data(self) -> List[Dict]:
        """載入訓練數據"""
        # 真實的訓練樣本
        return [
            # READ_CODE 樣本
            {"text": "幫我看看config.json文件的內容", "intent": "read_code"},
            {"text": "顯示main.py的代碼", "intent": "read_code"},
            {"text": "讀取package.json", "intent": "read_code"},
            {"text": "查看README文件", "intent": "read_code"},
            {"text": "打開test.js看看", "intent": "read_code"},
            
            # WRITE_CODE 樣本
            {"text": "創建一個新的Python腳本來處理數據", "intent": "write_code"},
            {"text": "寫一個函數計算斐波那契數列", "intent": "write_code"},
            {"text": "幫我實現一個排序算法", "intent": "write_code"},
            {"text": "新建一個React組件", "intent": "write_code"},
            {"text": "生成一個配置文件模板", "intent": "write_code"},
            
            # EDIT_CODE 樣本
            {"text": "修改端口號為8080", "intent": "edit_code"},
            {"text": "把變量名從foo改成bar", "intent": "edit_code"},
            {"text": "更新版本號到2.0", "intent": "edit_code"},
            {"text": "替換所有的console.log為logger.info", "intent": "edit_code"},
            {"text": "改一下這個函數的參數", "intent": "edit_code"},
            
            # DEBUG_ERROR 樣本
            {"text": "為什麼這段代碼會報錯？", "intent": "debug_error"},
            {"text": "TypeError是什麼意思", "intent": "debug_error"},
            {"text": "幫我分析這個錯誤", "intent": "debug_error"},
            {"text": "調試一下這個問題", "intent": "debug_error"},
            {"text": "程序崩潰了，怎麼回事", "intent": "debug_error"},
            
            # FIX_BUG 樣本
            {"text": "修復登錄功能的bug", "intent": "fix_bug"},
            {"text": "解決內存洩漏問題", "intent": "fix_bug"},
            {"text": "修正這個語法錯誤", "intent": "fix_bug"},
            {"text": "處理一下空指針異常", "intent": "fix_bug"},
            {"text": "糾正邏輯錯誤", "intent": "fix_bug"},
            
            # SEARCH_CODE 樣本
            {"text": "搜索所有包含TODO的文件", "intent": "search_code"},
            {"text": "找出所有使用axios的地方", "intent": "search_code"},
            {"text": "查找函數定義", "intent": "search_code"},
            {"text": "grep error關鍵字", "intent": "search_code"},
            {"text": "尋找配置項", "intent": "search_code"},
            
            # RUN_TEST 樣本
            {"text": "運行測試看看結果", "intent": "run_test"},
            {"text": "執行單元測試", "intent": "run_test"},
            {"text": "跑一下test suite", "intent": "run_test"},
            {"text": "pytest一下", "intent": "run_test"},
            {"text": "測試覆蓋率如何", "intent": "run_test"},
            
            # RUN_COMMAND 樣本
            {"text": "執行npm install", "intent": "run_command"},
            {"text": "運行build腳本", "intent": "run_command"},
            {"text": "啟動開發服務器", "intent": "run_command"},
            {"text": "執行git status", "intent": "run_command"},
            {"text": "運行docker compose up", "intent": "run_command"},
        ]
    
    def extract_features(self, text: str) -> Dict[str, float]:
        """提取文本特徵"""
        features = defaultdict(float)
        
        # 轉換為小寫
        text_lower = text.lower()
        words = text_lower.split()
        
        # 1. 單詞特徵
        for word in words:
            if len(word) > 2:  # 忽略太短的詞
                features[f"word_{word}"] = 1.0
        
        # 2. 雙詞組合特徵
        for i in range(len(words) - 1):
            bigram = f"{words[i]}_{words[i+1]}"
            features[f"bigram_{bigram}"] = 1.0
        
        # 3. 特殊標記特徵
        if "?" in text:
            features["has_question"] = 1.0
        if "." in text:
            features["has_dot"] = 1.0
        if any(word in text_lower for word in ["文件", "file", ".py", ".js", ".json"]):
            features["has_file_reference"] = 1.0
        
        # 4. 動詞特徵
        action_verbs = ["看", "讀", "寫", "創建", "修改", "改", "修復", "搜索", "找", "運行", "執行"]
        for verb in action_verbs:
            if verb in text:
                features[f"verb_{verb}"] = 1.0
        
        # 5. 長度特徵
        features["length"] = len(words) / 10.0  # 歸一化
        
        return dict(features)
    
    def train_model(self, epochs: int = 10):
        """訓練意圖理解模型"""
        logger.info(f"開始訓練，共{epochs}輪...")
        
        for epoch in range(epochs):
            correct_predictions = 0
            total_predictions = len(self.training_data)
            
            # 打亂數據
            import random
            random.shuffle(self.training_data)
            
            for sample in self.training_data:
                text = sample["text"]
                true_intent = sample["intent"]
                
                # 提取特徵
                features = self.extract_features(text)
                
                # 預測
                predicted_intent, confidence = self.predict_intent(features)
                
                # 更新模型
                if predicted_intent == true_intent:
                    correct_predictions += 1
                else:
                    # 學習錯誤
                    self.update_weights(features, true_intent, predicted_intent)
                
                # 更新混淆矩陣
                self.metrics["confusion_matrix"][true_intent][predicted_intent] += 1
            
            # 計算準確率
            accuracy = correct_predictions / total_predictions
            self.metrics["current_accuracy"] = accuracy
            self.metrics["training_iterations"] = epoch + 1
            
            logger.info(f"Epoch {epoch + 1}: 準確率 = {accuracy:.2%}")
    
    def predict_intent(self, features: Dict[str, float]) -> Tuple[str, float]:
        """預測意圖"""
        intent_scores = defaultdict(float)
        
        # 計算每個意圖的分數
        for feature, value in features.items():
            for intent in ["read_code", "write_code", "edit_code", "debug_error", 
                          "fix_bug", "search_code", "run_test", "run_command"]:
                # 使用 defaultdict 來避免 KeyError
                weight = self.model_params["keyword_weights"][intent].get(feature, 0.0)
                intent_scores[intent] += weight * value
        
        # 找出最高分的意圖
        if not intent_scores:
            return "unknown", 0.0
        
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # 計算置信度（簡化的softmax）
        total_score = sum(np.exp(score) for score in intent_scores.values())
        confidence = np.exp(best_intent[1]) / total_score if total_score > 0 else 0.0
        
        return best_intent[0], confidence
    
    def update_weights(self, features: Dict[str, float], true_intent: str, predicted_intent: str):
        """更新權重"""
        learning_rate = self.model_params["learning_rate"]
        
        # 增加正確意圖的權重
        for feature, value in features.items():
            self.model_params["keyword_weights"][true_intent][feature] += learning_rate * value
        
        # 減少錯誤意圖的權重
        if predicted_intent != "unknown":
            for feature, value in features.items():
                self.model_params["keyword_weights"][predicted_intent][feature] -= learning_rate * value * 0.5
    
    def evaluate_on_test_set(self, test_data: List[Dict]) -> Dict[str, float]:
        """在測試集上評估"""
        correct = 0
        total = len(test_data)
        
        predictions = []
        
        for sample in test_data:
            text = sample["text"]
            true_intent = sample["intent"]
            
            features = self.extract_features(text)
            predicted_intent, confidence = self.predict_intent(features)
            
            if predicted_intent == true_intent:
                correct += 1
            
            predictions.append({
                "text": text,
                "true": true_intent,
                "predicted": predicted_intent,
                "confidence": confidence,
                "correct": predicted_intent == true_intent
            })
        
        accuracy = correct / total if total > 0 else 0.0
        
        return {
            "accuracy": accuracy,
            "predictions": predictions
        }
    
    def save_model(self, path: str = "intent_model.json"):
        """保存模型"""
        model_data = {
            "params": {
                "keyword_weights": {
                    intent: dict(weights)
                    for intent, weights in self.model_params["keyword_weights"].items()
                },
                "confidence_threshold": self.model_params["confidence_threshold"]
            },
            "metrics": dict(self.metrics)
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"模型已保存到: {path}")
    
    def demonstrate_improved_understanding(self):
        """演示改進後的意圖理解"""
        # 訓練模型
        self.train_model(epochs=20)
        
        # 測試案例
        test_cases = [
            {"text": "幫我看看config.json文件的內容", "intent": "read_code"},
            {"text": "創建一個處理用戶輸入的函數", "intent": "write_code"},
            {"text": "把所有的var改成let", "intent": "edit_code"},
            {"text": "程序拋出異常了", "intent": "debug_error"},
            {"text": "修復內存洩漏", "intent": "fix_bug"},
            {"text": "找找哪裡用了deprecated的API", "intent": "search_code"},
            {"text": "運行所有測試用例", "intent": "run_test"},
            {"text": "執行部署腳本", "intent": "run_command"}
        ]
        
        print("\n" + "=" * 60)
        print("訓練後的意圖理解測試")
        print("=" * 60)
        
        results = self.evaluate_on_test_set(test_cases)
        
        for pred in results["predictions"]:
            status = "✅" if pred["correct"] else "❌"
            print(f"\n{status} 輸入: {pred['text']}")
            print(f"   真實意圖: {pred['true']}")
            print(f"   預測意圖: {pred['predicted']}")
            print(f"   置信度: {pred['confidence']:.2f}")
        
        print("\n" + "=" * 60)
        print(f"測試準確率: {results['accuracy'] * 100:.1f}%")
        print(f"訓練準確率: {self.metrics['current_accuracy'] * 100:.1f}%")
        
        # 保存模型
        self.save_model()


def main():
    """主函數"""
    trainer = IntentTrainingSystem()
    trainer.demonstrate_improved_understanding()
    
    # 創建意圖理解改進報告
    report = f"""
# 意圖理解改進報告

## 訓練結果
- 訓練樣本數: {len(trainer.training_data)}
- 訓練輪次: {trainer.metrics['training_iterations']}
- 最終準確率: {trainer.metrics['current_accuracy'] * 100:.1f}%

## 關鍵改進
1. **特徵工程**: 提取單詞、雙詞組合、動詞等特徵
2. **權重學習**: 通過梯度下降更新特徵權重
3. **置信度計算**: 使用softmax歸一化
4. **錯誤學習**: 從錯誤預測中調整權重

## 實際應用建議
1. 收集更多真實用戶數據
2. 引入預訓練語言模型
3. 添加上下文記憶機制
4. 實施在線學習
5. A/B測試不同模型版本
"""
    
    with open("intent_improvement_report.md", "w") as f:
        f.write(report)


if __name__ == "__main__":
    main()