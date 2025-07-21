#!/usr/bin/env python3
"""
增強版意圖理解訓練系統
使用所有可用的對話數據進行訓練
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict
import random
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedIntentTrainingSystem:
    """增強版意圖理解訓練系統"""
    
    def __init__(self):
        self.base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        
        # 意圖映射（用於參考，不是直接的字典）
        self.intent_keywords = {
            "read_code": ["看", "讀", "顯示", "查看", "打開", "show", "read", "display", "view"],
            "write_code": ["創建", "寫", "新建", "生成", "create", "write", "new", "generate"],
            "edit_code": ["修改", "改", "更新", "替換", "edit", "modify", "update", "replace"],
            "debug_error": ["錯誤", "error", "異常", "exception", "報錯", "debug"],
            "fix_bug": ["修復", "fix", "解決", "處理", "糾正", "solve"],
            "search_code": ["搜索", "找", "查找", "尋找", "search", "find", "grep"],
            "run_test": ["測試", "test", "單元測試", "pytest", "運行測試"],
            "run_command": ["執行", "運行", "run", "execute", "npm", "git", "docker"]
        }
        
        # 初始化訓練數據列表
        self.training_data = []
        
        # 意圖模型參數
        self.model_params = {
            "keyword_weights": defaultdict(lambda: defaultdict(float)),
            "pattern_importance": defaultdict(float),
            "context_relevance": defaultdict(float),
            "intent_priors": defaultdict(float),
            "confidence_threshold": 0.3,
            "learning_rate": 0.05,
            "regularization": 0.001
        }
        
        # 性能指標
        self.metrics = {
            "training_iterations": 0,
            "current_accuracy": 0.0,
            "confusion_matrix": defaultdict(lambda: defaultdict(int)),
            "intent_distribution": defaultdict(int),
            "feature_importance": defaultdict(float)
        }
        
        # 載入所有訓練數據
        self.load_all_training_data()
        
        logger.info(f"初始化完成，載入 {len(self.training_data)} 個訓練樣本")
    
    def load_all_training_data(self):
        """載入所有可用的訓練數據"""
        loaded_count = 0
        
        # 1. 載入 enhanced_extracted_chats
        enhanced_chats_dir = self.base_dir / "data" / "enhanced_extracted_chats"
        if enhanced_chats_dir.exists():
            for json_file in enhanced_chats_dir.glob("enhanced_*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._extract_training_samples_from_conversation(data)
                        loaded_count += 1
                except Exception as e:
                    logger.warning(f"載入 {json_file} 失敗: {e}")
        
        # 2. 載入 enhanced_replays
        enhanced_replays_dir = self.base_dir / "data" / "enhanced_replays"
        if enhanced_replays_dir.exists():
            for json_file in enhanced_replays_dir.glob("replay_*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._extract_training_samples_from_conversation(data)
                        loaded_count += 1
                except Exception as e:
                    logger.warning(f"載入 {json_file} 失敗: {e}")
        
        # 3. 載入 JSONL 訓練數據
        jsonl_files = [
            "data/k2_training_enhanced/k2_training_batch_20250721_015022.jsonl",
            "data/k2_training_enhanced/k2_training_batch_20250721_015023.jsonl",
            "data/comprehensive_training/k2_comprehensive_training_20250720_210316.jsonl",
            "data/comprehensive_training/deepswe_comprehensive_training_20250720_210316.jsonl"
        ]
        
        for jsonl_path in jsonl_files:
            full_path = self.base_dir / jsonl_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                self._extract_training_samples_from_jsonl(data)
                    loaded_count += 1
                except Exception as e:
                    logger.warning(f"載入 {jsonl_path} 失敗: {e}")
        
        # 4. 添加硬編碼的高質量樣本
        self._add_hardcoded_samples()
        
        logger.info(f"成功載入 {loaded_count} 個數據文件，共 {len(self.training_data)} 個訓練樣本")
        
        # 統計意圖分布
        for sample in self.training_data:
            self.metrics["intent_distribution"][sample["intent"]] += 1
        
        logger.info("意圖分布統計:")
        for intent, count in self.metrics["intent_distribution"].items():
            logger.info(f"  {intent}: {count} ({count/len(self.training_data)*100:.1f}%)")
    
    def _extract_training_samples_from_conversation(self, data: Dict):
        """從對話數據中提取訓練樣本"""
        if "conversation" in data:
            for msg in data.get("conversation", []):
                if msg.get("role") == "user":
                    text = msg.get("content", "")
                    intent = self._infer_intent_from_text(text)
                    if intent and intent != "unknown":
                        self.training_data.append({
                            "text": text,
                            "intent": intent,
                            "source": "conversation"
                        })
    
    def _extract_training_samples_from_jsonl(self, data):
        """從JSONL數據中提取訓練樣本"""
        # 如果data是字符串，嘗試解析為JSON
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                return
        
        # 處理不同格式的JSONL數據
        if isinstance(data, dict):
            if "messages" in data:
                for msg in data["messages"]:
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        text = msg.get("content", "")
                        intent = self._infer_intent_from_text(text)
                        if intent and intent != "unknown":
                            self.training_data.append({
                                "text": text,
                                "intent": intent,
                                "source": "jsonl"
                            })
            elif "prompt" in data:
                text = data.get("prompt", "")
                intent = self._infer_intent_from_text(text)
                if intent and intent != "unknown":
                    self.training_data.append({
                        "text": text,
                        "intent": intent,
                        "source": "jsonl"
                    })
    
    def _infer_intent_from_text(self, text: str) -> str:
        """根據文本內容推斷意圖"""
        text_lower = text.lower()
        
        # 基於關鍵詞的意圖推斷
        for keywords, intent in [
            (["看", "讀", "顯示", "查看", "打開", "show", "read", "display", "view", "檢視", "瀏覽"], "read_code"),
            (["創建", "寫", "新建", "生成", "create", "write", "new", "generate", "建立", "實現"], "write_code"),
            (["修改", "改", "更新", "替換", "edit", "modify", "update", "replace", "變更", "調整"], "edit_code"),
            (["錯誤", "error", "異常", "exception", "報錯", "debug", "崩潰", "失敗"], "debug_error"),
            (["修復", "fix", "解決", "處理", "糾正", "solve", "修正", "解決"], "fix_bug"),
            (["搜索", "找", "查找", "尋找", "search", "find", "grep", "定位", "檢索"], "search_code"),
            (["測試", "test", "單元測試", "pytest", "運行測試", "驗證", "檢測"], "run_test"),
            (["執行", "運行", "run", "execute", "npm", "git", "docker", "啟動", "命令"], "run_command")
        ]:
            if any(keyword in text_lower for keyword in keywords):
                return intent
        
        # 基於文件擴展名的推斷
        file_extensions = [".py", ".js", ".json", ".yaml", ".yml", ".md", ".txt", ".sh", ".jsx", ".tsx"]
        if any(ext in text_lower for ext in file_extensions):
            if any(word in text_lower for word in ["看", "讀", "查看", "show", "read", "view"]):
                return "read_code"
            elif any(word in text_lower for word in ["創建", "新建", "create", "new"]):
                return "write_code"
        
        return "unknown"
    
    def _add_hardcoded_samples(self):
        """添加高質量的硬編碼樣本"""
        hardcoded_samples = [
            # READ_CODE 樣本
            {"text": "幫我看看config.json文件的內容", "intent": "read_code"},
            {"text": "顯示main.py的代碼", "intent": "read_code"},
            {"text": "讀取package.json", "intent": "read_code"},
            {"text": "查看README文件", "intent": "read_code"},
            {"text": "打開test.js看看", "intent": "read_code"},
            {"text": "檢視app.py的實現", "intent": "read_code"},
            {"text": "瀏覽一下index.html", "intent": "read_code"},
            
            # WRITE_CODE 樣本
            {"text": "創建一個新的Python腳本來處理數據", "intent": "write_code"},
            {"text": "寫一個函數計算斐波那契數列", "intent": "write_code"},
            {"text": "幫我實現一個排序算法", "intent": "write_code"},
            {"text": "新建一個React組件", "intent": "write_code"},
            {"text": "生成一個配置文件模板", "intent": "write_code"},
            {"text": "建立一個數據庫連接類", "intent": "write_code"},
            {"text": "實現用戶認證功能", "intent": "write_code"},
            
            # EDIT_CODE 樣本
            {"text": "修改端口號為8080", "intent": "edit_code"},
            {"text": "把變量名從foo改成bar", "intent": "edit_code"},
            {"text": "更新版本號到2.0", "intent": "edit_code"},
            {"text": "替換所有的console.log為logger.info", "intent": "edit_code"},
            {"text": "改一下這個函數的參數", "intent": "edit_code"},
            {"text": "調整縮進為4個空格", "intent": "edit_code"},
            {"text": "變更API端點路徑", "intent": "edit_code"},
            
            # DEBUG_ERROR 樣本
            {"text": "為什麼這段代碼會報錯？", "intent": "debug_error"},
            {"text": "TypeError是什麼意思", "intent": "debug_error"},
            {"text": "幫我分析這個錯誤", "intent": "debug_error"},
            {"text": "調試一下這個問題", "intent": "debug_error"},
            {"text": "程序崩潰了，怎麼回事", "intent": "debug_error"},
            {"text": "解釋一下這個異常", "intent": "debug_error"},
            {"text": "追蹤錯誤來源", "intent": "debug_error"},
            
            # FIX_BUG 樣本
            {"text": "修復登錄功能的bug", "intent": "fix_bug"},
            {"text": "解決內存洩漏問題", "intent": "fix_bug"},
            {"text": "修正這個語法錯誤", "intent": "fix_bug"},
            {"text": "處理一下空指針異常", "intent": "fix_bug"},
            {"text": "糾正邏輯錯誤", "intent": "fix_bug"},
            {"text": "解決循環引用問題", "intent": "fix_bug"},
            {"text": "修復數據不一致的問題", "intent": "fix_bug"},
            
            # SEARCH_CODE 樣本
            {"text": "搜索所有包含TODO的文件", "intent": "search_code"},
            {"text": "找出所有使用axios的地方", "intent": "search_code"},
            {"text": "查找函數定義", "intent": "search_code"},
            {"text": "grep error關鍵字", "intent": "search_code"},
            {"text": "尋找配置項", "intent": "search_code"},
            {"text": "定位變量聲明位置", "intent": "search_code"},
            {"text": "檢索API調用", "intent": "search_code"},
            
            # RUN_TEST 樣本
            {"text": "運行測試看看結果", "intent": "run_test"},
            {"text": "執行單元測試", "intent": "run_test"},
            {"text": "跑一下test suite", "intent": "run_test"},
            {"text": "pytest一下", "intent": "run_test"},
            {"text": "測試覆蓋率如何", "intent": "run_test"},
            {"text": "驗證功能是否正常", "intent": "run_test"},
            {"text": "檢測代碼質量", "intent": "run_test"},
            
            # RUN_COMMAND 樣本
            {"text": "執行npm install", "intent": "run_command"},
            {"text": "運行build腳本", "intent": "run_command"},
            {"text": "啟動開發服務器", "intent": "run_command"},
            {"text": "執行git status", "intent": "run_command"},
            {"text": "運行docker compose up", "intent": "run_command"},
            {"text": "啟動應用程序", "intent": "run_command"},
            {"text": "執行部署命令", "intent": "run_command"},
        ]
        
        for sample in hardcoded_samples:
            sample["source"] = "hardcoded"
            self.training_data.append(sample)
    
    def extract_features(self, text: str) -> Dict[str, float]:
        """提取文本特徵（增強版）"""
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
        
        # 3. 三詞組合特徵
        for i in range(len(words) - 2):
            trigram = f"{words[i]}_{words[i+1]}_{words[i+2]}"
            features[f"trigram_{trigram}"] = 0.5
        
        # 4. 特殊標記特徵
        if "?" in text:
            features["has_question"] = 1.0
        if "." in text:
            features["has_dot"] = 1.0
        if any(ext in text_lower for ext in [".py", ".js", ".json", ".yaml", ".md"]):
            features["has_file_reference"] = 1.0
        
        # 5. 動詞特徵（擴展）
        action_verbs = {
            "read_code": ["看", "讀", "顯示", "查看", "打開", "show", "read", "display", "view"],
            "write_code": ["創建", "寫", "新建", "生成", "create", "write", "new", "generate"],
            "edit_code": ["修改", "改", "更新", "替換", "edit", "modify", "update", "replace"],
            "debug_error": ["錯誤", "error", "異常", "exception", "報錯", "debug"],
            "fix_bug": ["修復", "fix", "解決", "處理", "糾正", "solve"],
            "search_code": ["搜索", "找", "查找", "尋找", "search", "find", "grep"],
            "run_test": ["測試", "test", "驗證", "檢測"],
            "run_command": ["執行", "運行", "run", "execute", "啟動"]
        }
        
        for intent, verbs in action_verbs.items():
            for verb in verbs:
                if verb in text_lower:
                    features[f"verb_{intent}_{verb}"] = 1.0
        
        # 6. 長度特徵
        features["length"] = len(words) / 10.0  # 歸一化
        features["char_length"] = len(text) / 100.0
        
        # 7. 上下文特徵
        if any(word in text_lower for word in ["幫我", "請", "可以", "能否"]):
            features["polite_request"] = 1.0
        
        # 8. 技術詞彙特徵
        tech_terms = ["函數", "變量", "類", "方法", "參數", "返回值", "api", "端口", "配置", "模塊"]
        for term in tech_terms:
            if term in text_lower:
                features[f"tech_{term}"] = 1.0
        
        return dict(features)
    
    def train_model(self, epochs: int = 50, batch_size: int = 32):
        """訓練意圖理解模型（增強版）"""
        logger.info(f"開始訓練，共{epochs}輪，批次大小{batch_size}...")
        
        # 分割訓練集和驗證集
        random.shuffle(self.training_data)
        split_idx = int(len(self.training_data) * 0.8)
        train_data = self.training_data[:split_idx]
        val_data = self.training_data[split_idx:]
        
        logger.info(f"訓練集: {len(train_data)} 樣本，驗證集: {len(val_data)} 樣本")
        
        best_val_accuracy = 0.0
        patience = 5
        no_improvement_count = 0
        
        for epoch in range(epochs):
            # 訓練階段
            correct_predictions = 0
            total_predictions = 0
            
            # 打亂訓練數據
            random.shuffle(train_data)
            
            # 批次訓練
            for i in range(0, len(train_data), batch_size):
                batch = train_data[i:i+batch_size]
                
                for sample in batch:
                    text = sample["text"]
                    true_intent = sample["intent"]
                    
                    # 提取特徵
                    features = self.extract_features(text)
                    
                    # 預測
                    predicted_intent, confidence = self.predict_intent(features)
                    
                    # 更新模型
                    if predicted_intent == true_intent:
                        correct_predictions += 1
                        # 強化正確預測
                        self.reinforce_correct_prediction(features, true_intent, confidence)
                    else:
                        # 學習錯誤
                        self.update_weights(features, true_intent, predicted_intent)
                    
                    total_predictions += 1
                    
                    # 更新混淆矩陣
                    self.metrics["confusion_matrix"][true_intent][predicted_intent] += 1
            
            # 計算訓練準確率
            train_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
            
            # 驗證階段
            val_results = self.evaluate_on_test_set(val_data)
            val_accuracy = val_results["accuracy"]
            
            # 更新指標
            self.metrics["current_accuracy"] = train_accuracy
            self.metrics["training_iterations"] = epoch + 1
            
            # 學習率衰減
            if epoch > 0 and epoch % 10 == 0:
                self.model_params["learning_rate"] *= 0.9
            
            logger.info(f"Epoch {epoch + 1}: 訓練準確率 = {train_accuracy:.2%}, 驗證準確率 = {val_accuracy:.2%}")
            
            # 早停檢查
            if val_accuracy > best_val_accuracy:
                best_val_accuracy = val_accuracy
                no_improvement_count = 0
                # 保存最佳模型
                self.save_model("best_intent_model.json")
            else:
                no_improvement_count += 1
                if no_improvement_count >= patience:
                    logger.info(f"驗證準確率已{patience}輪未提升，提前停止訓練")
                    break
            
            # 定期保存檢查點
            if (epoch + 1) % 10 == 0:
                self.save_model(f"intent_model_checkpoint_epoch{epoch+1}.json")
    
    def reinforce_correct_prediction(self, features: Dict[str, float], intent: str, confidence: float):
        """強化正確的預測"""
        # 如果置信度較低，仍然需要強化
        if confidence < 0.8:
            reinforcement_rate = self.model_params["learning_rate"] * 0.3
            for feature, value in features.items():
                self.model_params["keyword_weights"][intent][feature] += reinforcement_rate * value
    
    def predict_intent(self, features: Dict[str, float]) -> Tuple[str, float]:
        """預測意圖（增強版）"""
        intent_scores = defaultdict(float)
        
        # 所有可能的意圖
        all_intents = ["read_code", "write_code", "edit_code", "debug_error", 
                      "fix_bug", "search_code", "run_test", "run_command"]
        
        # 計算每個意圖的分數
        for intent in all_intents:
            # 基礎分數
            base_score = self.model_params["intent_priors"].get(intent, 0.0)
            
            # 特徵分數
            for feature, value in features.items():
                weight = self.model_params["keyword_weights"][intent].get(feature, 0.0)
                intent_scores[intent] += weight * value
            
            # 加上基礎分數和正則化
            intent_scores[intent] += base_score
            intent_scores[intent] -= self.model_params["regularization"] * sum(
                abs(w) for w in self.model_params["keyword_weights"][intent].values()
            )
        
        # 找出最高分的意圖
        if not intent_scores:
            return "unknown", 0.0
        
        # Softmax 計算置信度
        max_score = max(intent_scores.values())
        exp_scores = {intent: np.exp(score - max_score) for intent, score in intent_scores.items()}
        total_exp = sum(exp_scores.values())
        
        probabilities = {intent: exp_score / total_exp for intent, exp_score in exp_scores.items()}
        
        # 選擇最高概率的意圖
        best_intent = max(probabilities.items(), key=lambda x: x[1])
        
        return best_intent[0], best_intent[1]
    
    def update_weights(self, features: Dict[str, float], true_intent: str, predicted_intent: str):
        """更新權重（增強版）"""
        learning_rate = self.model_params["learning_rate"]
        
        # 增加正確意圖的權重
        for feature, value in features.items():
            self.model_params["keyword_weights"][true_intent][feature] += learning_rate * value
            # 更新特徵重要性
            self.metrics["feature_importance"][feature] += abs(learning_rate * value)
        
        # 減少錯誤意圖的權重
        if predicted_intent != "unknown":
            for feature, value in features.items():
                self.model_params["keyword_weights"][predicted_intent][feature] -= learning_rate * value * 0.7
        
        # 更新意圖先驗概率
        self.model_params["intent_priors"][true_intent] += learning_rate * 0.1
        if predicted_intent != "unknown":
            self.model_params["intent_priors"][predicted_intent] -= learning_rate * 0.05
    
    def evaluate_on_test_set(self, test_data: List[Dict]) -> Dict[str, float]:
        """在測試集上評估"""
        correct = 0
        total = len(test_data)
        
        predictions = []
        intent_correct_counts = defaultdict(int)
        intent_total_counts = defaultdict(int)
        
        for sample in test_data:
            text = sample["text"]
            true_intent = sample["intent"]
            
            features = self.extract_features(text)
            predicted_intent, confidence = self.predict_intent(features)
            
            intent_total_counts[true_intent] += 1
            
            if predicted_intent == true_intent:
                correct += 1
                intent_correct_counts[true_intent] += 1
            
            predictions.append({
                "text": text,
                "true": true_intent,
                "predicted": predicted_intent,
                "confidence": confidence,
                "correct": predicted_intent == true_intent
            })
        
        accuracy = correct / total if total > 0 else 0.0
        
        # 計算每個意圖的準確率
        intent_accuracies = {}
        for intent in intent_total_counts:
            if intent_total_counts[intent] > 0:
                intent_accuracies[intent] = intent_correct_counts[intent] / intent_total_counts[intent]
            else:
                intent_accuracies[intent] = 0.0
        
        return {
            "accuracy": accuracy,
            "predictions": predictions,
            "intent_accuracies": intent_accuracies
        }
    
    def save_model(self, path: str = "enhanced_intent_model.json"):
        """保存模型"""
        # 轉換 defaultdict 為普通 dict
        model_data = {
            "params": {
                "keyword_weights": {
                    intent: dict(weights)
                    for intent, weights in self.model_params["keyword_weights"].items()
                },
                "intent_priors": dict(self.model_params["intent_priors"]),
                "confidence_threshold": self.model_params["confidence_threshold"],
                "learning_rate": self.model_params["learning_rate"],
                "regularization": self.model_params["regularization"]
            },
            "metrics": {
                "training_iterations": self.metrics["training_iterations"],
                "current_accuracy": self.metrics["current_accuracy"],
                "intent_distribution": dict(self.metrics["intent_distribution"]),
                "feature_importance": dict(sorted(
                    self.metrics["feature_importance"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:100])  # 保存前100個重要特徵
            },
            "training_info": {
                "total_samples": len(self.training_data),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"模型已保存到: {path}")
    
    def demonstrate_improved_understanding(self):
        """演示改進後的意圖理解"""
        # 訓練模型
        self.train_model(epochs=30, batch_size=64)
        
        # 測試案例（包含更多樣化的例子）
        test_cases = [
            # 原始測試案例
            {"text": "幫我看看config.json文件的內容", "intent": "read_code"},
            {"text": "創建一個處理用戶輸入的函數", "intent": "write_code"},
            {"text": "把所有的var改成let", "intent": "edit_code"},
            {"text": "程序拋出異常了", "intent": "debug_error"},
            {"text": "修復內存洩漏", "intent": "fix_bug"},
            {"text": "找找哪裡用了deprecated的API", "intent": "search_code"},
            {"text": "運行所有測試用例", "intent": "run_test"},
            {"text": "執行部署腳本", "intent": "run_command"},
            
            # 新增測試案例
            {"text": "顯示一下server.py的實現", "intent": "read_code"},
            {"text": "我想建立一個新的數據模型", "intent": "write_code"},
            {"text": "需要更新配置文件中的數據庫連接", "intent": "edit_code"},
            {"text": "為什麼會出現undefined錯誤", "intent": "debug_error"},
            {"text": "解決登錄頁面的跳轉問題", "intent": "fix_bug"},
            {"text": "檢索所有import語句", "intent": "search_code"},
            {"text": "驗證API接口是否正常工作", "intent": "run_test"},
            {"text": "啟動本地開發環境", "intent": "run_command"}
        ]
        
        print("\n" + "=" * 80)
        print("增強版意圖理解測試")
        print("=" * 80)
        
        results = self.evaluate_on_test_set(test_cases)
        
        for pred in results["predictions"]:
            status = "✅" if pred["correct"] else "❌"
            print(f"\n{status} 輸入: {pred['text']}")
            print(f"   真實意圖: {pred['true']}")
            print(f"   預測意圖: {pred['predicted']}")
            print(f"   置信度: {pred['confidence']:.2f}")
        
        print("\n" + "=" * 80)
        print(f"測試準確率: {results['accuracy'] * 100:.1f}%")
        print(f"訓練準確率: {self.metrics['current_accuracy'] * 100:.1f}%")
        print(f"總訓練樣本數: {len(self.training_data)}")
        
        # 顯示每個意圖的準確率
        print("\n各意圖準確率:")
        for intent, acc in results["intent_accuracies"].items():
            print(f"  {intent}: {acc * 100:.1f}%")
        
        # 保存最終模型
        self.save_model("enhanced_intent_model_final.json")
        
        # 創建詳細報告
        self.create_detailed_report()
    
    def create_detailed_report(self):
        """創建詳細的訓練報告"""
        report = f"""# 增強版意圖理解訓練報告

## 訓練概況
- 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 總訓練樣本數: {len(self.training_data)}
- 訓練輪次: {self.metrics['training_iterations']}
- 最終準確率: {self.metrics['current_accuracy'] * 100:.1f}%

## 數據來源分布
"""
        
        # 統計數據來源
        source_counts = defaultdict(int)
        for sample in self.training_data:
            source_counts[sample.get("source", "unknown")] += 1
        
        for source, count in source_counts.items():
            report += f"- {source}: {count} ({count/len(self.training_data)*100:.1f}%)\n"
        
        report += f"""
## 意圖分布
"""
        for intent, count in sorted(self.metrics["intent_distribution"].items()):
            report += f"- {intent}: {count} ({count/len(self.training_data)*100:.1f}%)\n"
        
        report += f"""
## 重要特徵 (Top 20)
"""
        for i, (feature, importance) in enumerate(list(self.metrics["feature_importance"].items())[:20]):
            report += f"{i+1}. {feature}: {importance:.3f}\n"
        
        report += f"""
## 改進要點
1. **大規模數據集成**: 整合了{len(self.training_data)}個訓練樣本，包括:
   - enhanced_extracted_chats: 對話數據
   - enhanced_replays: 重播數據
   - JSONL訓練文件: K2和DeepSWE數據
   - 硬編碼高質量樣本

2. **增強特徵工程**:
   - 單詞、雙詞、三詞組合特徵
   - 動詞-意圖關聯特徵
   - 技術詞彙特徵
   - 上下文和禮貌用語特徵

3. **改進的訓練策略**:
   - 批次訓練提高效率
   - 早停機制防止過擬合
   - 學習率衰減
   - 正則化防止過擬合

4. **模型優化**:
   - Softmax置信度計算
   - 意圖先驗概率
   - 特徵重要性追蹤
   - 強化正確預測機制

## 實際應用建議
1. **持續數據收集**: 繼續收集真實用戶對話數據
2. **模型更新**: 定期重新訓練以適應新的使用模式
3. **A/B測試**: 對比測試不同版本的模型
4. **整合深度學習**: 考慮引入BERT等預訓練模型
5. **實時學習**: 實現在線學習機制
"""
        
        with open("enhanced_intent_training_report.md", "w", encoding='utf-8') as f:
            f.write(report)
        
        logger.info("詳細報告已生成: enhanced_intent_training_report.md")


def main():
    """主函數"""
    print("開始增強版意圖理解訓練...")
    trainer = EnhancedIntentTrainingSystem()
    trainer.demonstrate_improved_understanding()


if __name__ == "__main__":
    main()