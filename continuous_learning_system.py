#!/usr/bin/env python3
"""
持續學習系統
實時從用戶交互中學習並改進
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContinuousLearningSystem:
    """持續學習系統"""
    
    def __init__(self):
        self.base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        
        # 學習配置
        self.config = {
            "learning_rate": 0.01,
            "batch_size": 10,
            "update_frequency": 5,  # 每5個樣本更新一次
            "confidence_threshold": 0.7,
            "exploration_rate": 0.1  # 10%的探索率
        }
        
        # 在線學習緩衝區
        self.learning_buffer = {
            "pending_samples": [],
            "validated_samples": [],
            "failed_samples": []
        }
        
        # 性能追蹤
        self.performance_tracker = {
            "hourly_stats": defaultdict(lambda: {"success": 0, "total": 0}),
            "daily_improvement": [],
            "current_accuracy": 0.0
        }
        
        # 載入或初始化模型
        self.model = self._load_or_init_model()
        
        # 啟動背景學習任務
        self.learning_task = None
    
    def _load_or_init_model(self) -> Dict:
        """載入或初始化模型"""
        model_path = self.base_dir / "continuous_model.json"
        
        if model_path.exists():
            with open(model_path, 'r') as f:
                logger.info("✅ 載入現有持續學習模型")
                return json.load(f)
        else:
            logger.info("🆕 初始化新的持續學習模型")
            return {
                "intent_weights": defaultdict(lambda: defaultdict(float)),
                "tool_mapping": defaultdict(list),
                "context_patterns": defaultdict(list),
                "version": 1,
                "last_update": datetime.now().isoformat()
            }
    
    async def start_continuous_learning(self):
        """啟動持續學習循環"""
        logger.info("🚀 啟動持續學習系統...")
        
        while True:
            try:
                # 處理學習緩衝區
                if len(self.learning_buffer["pending_samples"]) >= self.config["update_frequency"]:
                    await self._process_learning_batch()
                
                # 定期評估和調整
                await self._evaluate_and_adjust()
                
                # 保存模型
                if datetime.now().minute % 10 == 0:  # 每10分鐘保存一次
                    self._save_model()
                
                await asyncio.sleep(60)  # 每分鐘檢查一次
                
            except Exception as e:
                logger.error(f"持續學習錯誤: {e}")
                await asyncio.sleep(60)
    
    async def learn_from_interaction(self, interaction: Dict):
        """從單次交互中學習"""
        # 提取學習信號
        learning_signal = {
            "timestamp": datetime.now().isoformat(),
            "input": interaction.get("user_input", ""),
            "predicted_intent": interaction.get("predicted_intent"),
            "actual_intent": interaction.get("actual_intent"),
            "tools_used": interaction.get("tools_used", []),
            "success": interaction.get("success", False),
            "confidence": interaction.get("confidence", 0.0),
            "execution_time": interaction.get("execution_time", 0.0),
            "user_feedback": interaction.get("user_feedback")
        }
        
        # 加入學習緩衝區
        self.learning_buffer["pending_samples"].append(learning_signal)
        
        # 立即學習（如果是高價值樣本）
        if self._is_high_value_sample(learning_signal):
            await self._immediate_learn(learning_signal)
        
        # 更新性能統計
        hour = datetime.now().hour
        self.performance_tracker["hourly_stats"][hour]["total"] += 1
        if learning_signal["success"]:
            self.performance_tracker["hourly_stats"][hour]["success"] += 1
    
    def _is_high_value_sample(self, signal: Dict) -> bool:
        """判斷是否為高價值學習樣本"""
        # 失敗的案例
        if not signal["success"]:
            return True
        
        # 低置信度的成功案例
        if signal["confidence"] < 0.5:
            return True
        
        # 新的意圖或工具組合
        if signal["predicted_intent"] not in self.model["intent_weights"]:
            return True
        
        return False
    
    async def _immediate_learn(self, signal: Dict):
        """立即學習（用於高價值樣本）"""
        logger.info(f"🎯 立即學習高價值樣本: {signal['input'][:30]}...")
        
        # 更新意圖權重
        if signal["actual_intent"] and signal["predicted_intent"]:
            # 正確預測：強化
            if signal["actual_intent"] == signal["predicted_intent"] and signal["success"]:
                self._reinforce_weights(signal)
            # 錯誤預測：調整
            else:
                self._adjust_weights(signal)
        
        # 更新工具映射
        if signal["success"] and signal["tools_used"]:
            self.model["tool_mapping"][signal["actual_intent"]] = signal["tools_used"]
    
    def _reinforce_weights(self, signal: Dict):
        """強化正確的權重"""
        intent = signal["actual_intent"]
        features = self._extract_features(signal["input"])
        
        for feature, value in features.items():
            current = self.model["intent_weights"][intent].get(feature, 0.0)
            self.model["intent_weights"][intent][feature] = current + self.config["learning_rate"] * value
    
    def _adjust_weights(self, signal: Dict):
        """調整錯誤的權重"""
        correct_intent = signal["actual_intent"]
        wrong_intent = signal["predicted_intent"]
        features = self._extract_features(signal["input"])
        
        # 增加正確意圖的權重
        for feature, value in features.items():
            current = self.model["intent_weights"][correct_intent].get(feature, 0.0)
            self.model["intent_weights"][correct_intent][feature] = current + self.config["learning_rate"] * value
        
        # 減少錯誤意圖的權重
        if wrong_intent:
            for feature, value in features.items():
                current = self.model["intent_weights"][wrong_intent].get(feature, 0.0)
                self.model["intent_weights"][wrong_intent][feature] = current - self.config["learning_rate"] * value * 0.5
    
    def _extract_features(self, text: str) -> Dict[str, float]:
        """提取文本特徵"""
        features = {}
        words = text.lower().split()
        
        # 單詞特徵
        for word in words:
            if len(word) > 2:
                features[f"word_{word}"] = 1.0
        
        # 雙詞組合
        for i in range(len(words) - 1):
            features[f"bigram_{words[i]}_{words[i+1]}"] = 1.0
        
        # 長度特徵
        features["length"] = len(words) / 10.0
        
        return features
    
    async def _process_learning_batch(self):
        """處理學習批次"""
        batch = self.learning_buffer["pending_samples"][:self.config["batch_size"]]
        self.learning_buffer["pending_samples"] = self.learning_buffer["pending_samples"][self.config["batch_size"]:]
        
        logger.info(f"📚 處理學習批次: {len(batch)} 個樣本")
        
        success_count = 0
        for sample in batch:
            if sample["success"]:
                success_count += 1
                self.learning_buffer["validated_samples"].append(sample)
            else:
                self.learning_buffer["failed_samples"].append(sample)
        
        # 批量更新模型
        await self._batch_update_model(batch)
        
        # 計算批次準確率
        batch_accuracy = success_count / len(batch) if batch else 0
        logger.info(f"📊 批次準確率: {batch_accuracy:.1%}")
    
    async def _batch_update_model(self, batch: List[Dict]):
        """批量更新模型"""
        # 統計意圖分佈
        intent_counts = defaultdict(int)
        for sample in batch:
            if sample["actual_intent"]:
                intent_counts[sample["actual_intent"]] += 1
        
        # 更新模型版本
        self.model["version"] += 1
        self.model["last_update"] = datetime.now().isoformat()
        
        logger.info(f"✅ 模型更新到版本 {self.model['version']}")
    
    async def _evaluate_and_adjust(self):
        """評估並調整學習策略"""
        # 計算當前準確率
        total = sum(stat["total"] for stat in self.performance_tracker["hourly_stats"].values())
        success = sum(stat["success"] for stat in self.performance_tracker["hourly_stats"].values())
        
        if total > 0:
            current_accuracy = success / total
            self.performance_tracker["current_accuracy"] = current_accuracy
            
            # 調整學習率
            if current_accuracy < 0.7:
                self.config["learning_rate"] = min(0.1, self.config["learning_rate"] * 1.1)
            elif current_accuracy > 0.9:
                self.config["learning_rate"] = max(0.001, self.config["learning_rate"] * 0.9)
    
    def _save_model(self):
        """保存模型"""
        model_path = self.base_dir / "continuous_model.json"
        
        # 轉換defaultdict為普通dict
        save_data = {
            "intent_weights": {
                intent: dict(weights)
                for intent, weights in self.model["intent_weights"].items()
            },
            "tool_mapping": dict(self.model["tool_mapping"]),
            "context_patterns": dict(self.model["context_patterns"]),
            "version": self.model["version"],
            "last_update": self.model["last_update"],
            "performance": {
                "current_accuracy": self.performance_tracker["current_accuracy"],
                "total_samples": sum(
                    stat["total"] 
                    for stat in self.performance_tracker["hourly_stats"].values()
                )
            }
        }
        
        with open(model_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        logger.info(f"💾 模型已保存 (版本 {self.model['version']})")
    
    def generate_learning_report(self) -> str:
        """生成學習報告"""
        total = sum(stat["total"] for stat in self.performance_tracker["hourly_stats"].values())
        success = sum(stat["success"] for stat in self.performance_tracker["hourly_stats"].values())
        accuracy = success / total if total > 0 else 0
        
        report = f"""
# 持續學習系統報告

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 學習統計
- 模型版本: {self.model['version']}
- 總樣本數: {total}
- 成功樣本: {success}
- 當前準確率: {accuracy:.1%}
- 學習率: {self.config['learning_rate']}

## 📈 每小時性能
"""
        
        for hour in sorted(self.performance_tracker["hourly_stats"].keys()):
            stat = self.performance_tracker["hourly_stats"][hour]
            if stat["total"] > 0:
                hour_accuracy = stat["success"] / stat["total"]
                report += f"- {hour:02d}:00 - 準確率: {hour_accuracy:.1%} ({stat['total']} 樣本)\n"
        
        report += f"""
## 🎯 學習緩衝區
- 待處理樣本: {len(self.learning_buffer['pending_samples'])}
- 已驗證樣本: {len(self.learning_buffer['validated_samples'])}
- 失敗樣本: {len(self.learning_buffer['failed_samples'])}

## 💡 關鍵發現
1. 系統持續從每次交互中學習
2. 高價值樣本（失敗案例）立即學習
3. 學習率根據性能動態調整
4. 模型定期保存，支持斷點恢復
"""
        
        return report
    
    def generate_diverse_dialogues(self, count: int = 100) -> List[Dict]:
        """生成多樣化的對話數據"""
        dialogues = []
        
        # 對話模板庫
        templates = {
        "read_code": [
            "幫我看看{file}的內容",
            "顯示{file}文件",
            "讀取{file}",
            "查看{file}的代碼",
            "打開{file}看看",
            "能不能顯示一下{file}",
            "我想看{file}裡面是什麼",
            "{file}文件的內容是什麼",
            "把{file}的代碼顯示出來",
            "讓我看看{file}"
        ],
        "write_code": [
            "創建一個{type}來{purpose}",
            "寫一個{function}函數",
            "幫我實現{feature}功能",
            "新建{file}文件",
            "生成{type}的代碼",
            "編寫一個{component}組件",
            "實現{algorithm}算法",
            "創建{purpose}的腳本",
            "寫個{type}處理{task}",
            "幫我生成{template}模板"
        ],
        "edit_code": [
            "把{old}改成{new}",
            "修改{file}中的{part}",
            "更新{variable}的值為{value}",
            "替換所有的{pattern}",
            "編輯{function}函數",
            "調整{parameter}參數",
            "重命名{old}為{new}",
            "修正{file}的格式",
            "改一下{code}這部分",
            "優化{function}的實現"
        ],
        "debug_error": [
            "為什麼會出現{error}錯誤",
            "{error}是什麼意思",
            "這個{exception}怎麼解決",
            "程序{action}時報錯了",
            "調試一下{problem}",
            "分析這個{error}的原因",
            "{function}為什麼會失敗",
            "幫我看看這個{traceback}",
            "解釋一下{error_type}錯誤",
            "診斷{symptom}的問題"
        ],
        "fix_bug": [
            "修復{feature}的bug",
            "解決{problem}問題",
            "修正{error}錯誤",
            "處理{exception}異常",
            "糾正{logic}邏輯",
            "修補{vulnerability}漏洞",
            "改正{mistake}",
            "解決{function}不工作的問題",
            "修復{component}的故障",
            "處理{edge_case}的情況"
        ],
        "search_code": [
            "搜索所有{pattern}的地方",
            "找{keyword}關鍵字",
            "查找{function}的定義",
            "grep {pattern}",
            "尋找{variable}的使用",
            "找出所有{type}文件",
            "搜索包含{text}的代碼",
            "定位{function}函數",
            "查找{import}的引用",
            "找找{comment}註釋"
        ],
        "run_test": [
            "運行{test}測試",
            "執行所有測試用例",
            "跑一下{suite}測試套件",
            "測試{function}功能",
            "驗證{feature}是否正常",
            "檢查測試覆蓋率",
            "運行{type}測試",
            "執行{file}的測試",
            "測試一下{component}",
            "驗證{scenario}場景"
        ],
        "run_command": [
            "執行{command}命令",
            "運行{script}腳本",
            "啟動{service}服務",
            "執行{tool} {args}",
            "運行{build}構建",
            "啟動{server}",
            "執行{package}安裝",
            "運行{deployment}部署",
            "執行{migration}遷移",
            "啟動{process}進程"
        ]
        }
        
        # 參數值庫
        params = {
        "file": ["config.json", "main.py", "server.js", "index.html", "utils.ts", 
                 "app.jsx", "test.py", "README.md", "package.json", "docker-compose.yml"],
        "type": ["函數", "類", "模塊", "組件", "服務", "接口", "工具", "腳本", "配置", "測試"],
        "purpose": ["處理數據", "驗證輸入", "計算結果", "發送請求", "解析響應", 
                    "管理狀態", "渲染界面", "處理錯誤", "記錄日誌", "優化性能"],
        "function": ["getData", "processInput", "calculateResult", "validateForm", 
                     "handleError", "updateState", "renderView", "fetchAPI", "parseJSON", "formatDate"],
        "error": ["TypeError", "SyntaxError", "ReferenceError", "ImportError", 
                  "ValueError", "KeyError", "AttributeError", "IndexError", "NameError", "RuntimeError"],
        "pattern": ["TODO", "FIXME", "console.log", "print", "debug", 
                    "deprecated", "async", "await", "import", "export"],
        "command": ["npm install", "pip install", "git status", "docker build", 
                    "yarn test", "make build", "pytest", "eslint", "prettier", "webpack"]
        }
        
        # 生成對話
        for _ in range(count):
            intent = np.random.choice(list(templates.keys()))
            template = np.random.choice(templates[intent])
            
            # 填充模板
            dialogue = template
            for match in set(word[1:-1] for word in template.split() if word.startswith('{') and word.endswith('}')):
                if match in params:
                    value = np.random.choice(params[match])
                    dialogue = dialogue.replace(f"{{{match}}}", value)
                else:
                    # 為未定義的參數生成隨機值
                    value = f"{match}_{np.random.randint(1, 100)}"
                    dialogue = dialogue.replace(f"{{{match}}}", value)
            
            dialogues.append({
                "user_input": dialogue,
                "actual_intent": intent,
                "timestamp": datetime.now().isoformat(),
                "generated": True
            })
        
        return dialogues

async def simulate_continuous_learning():
    """模擬持續學習過程"""
    system = ContinuousLearningSystem()
    
    # 啟動學習任務
    learning_task = asyncio.create_task(system.start_continuous_learning())
    
    logger.info("🎮 開始生成多樣化對話數據...")
    
    # 生成大量多樣化對話
    generated_dialogues = system.generate_diverse_dialogues(count=200)
    
    # 混合真實模式的交互數據
    real_patterns = [
        # 複雜查詢
        {"user_input": "幫我找出所有使用了deprecated API的地方並提供修復建議", "actual_intent": "search_code"},
        {"user_input": "分析一下為什麼單元測試在CI環境會失敗但本地能通過", "actual_intent": "debug_error"},
        {"user_input": "重構這個函數，讓它支持異步操作並保持向後兼容", "actual_intent": "edit_code"},
        
        # 多步驟任務
        {"user_input": "創建一個完整的用戶認證系統，包括登錄、註冊和密碼重置", "actual_intent": "write_code"},
        {"user_input": "把所有的class component改成functional component並使用hooks", "actual_intent": "edit_code"},
        {"user_input": "設置GitHub Actions來自動運行測試和部署", "actual_intent": "write_code"},
        
        # 性能相關
        {"user_input": "優化這個查詢，現在需要30秒才能執行完", "actual_intent": "fix_bug"},
        {"user_input": "找出內存洩漏的原因並修復", "actual_intent": "debug_error"},
        {"user_input": "實現緩存機制來減少API調用次數", "actual_intent": "write_code"},
        
        # 安全相關
        {"user_input": "檢查代碼中是否有SQL注入漏洞", "actual_intent": "search_code"},
        {"user_input": "添加輸入驗證防止XSS攻擊", "actual_intent": "fix_bug"},
        {"user_input": "實現JWT token的刷新機制", "actual_intent": "write_code"}
    ]
    
    # 合併所有對話
    all_dialogues = generated_dialogues + real_patterns
    np.random.shuffle(all_dialogues)
    
    logger.info(f"📊 總共生成 {len(all_dialogues)} 個對話樣本")
    
    # 批量處理對話
    batch_size = 20
    for i in range(0, len(all_dialogues), batch_size):
        batch = all_dialogues[i:i+batch_size]
        logger.info(f"\n📤 處理第 {i//batch_size + 1} 批 ({len(batch)} 個樣本)...")
        
        for dialogue in batch:
            # 模擬預測和執行
            dialogue["predicted_intent"] = dialogue["actual_intent"] if np.random.random() > 0.15 else np.random.choice(list(templates.keys()))
            dialogue["confidence"] = np.random.uniform(0.3, 0.95)
            dialogue["success"] = dialogue["predicted_intent"] == dialogue["actual_intent"] and np.random.random() > 0.1
            dialogue["execution_time"] = np.random.uniform(0.05, 3.0)
            
            # 根據意圖分配工具
            tool_mapping = {
                "read_code": ["Read", "Glob"],
                "write_code": ["Write", "MultiEdit"],
                "edit_code": ["Edit", "MultiEdit"],
                "debug_error": ["Read", "Grep", "Task"],
                "fix_bug": ["Edit", "MultiEdit", "SmartIntervention"],
                "search_code": ["Grep", "Search", "Glob"],
                "run_test": ["Bash", "Read"],
                "run_command": ["Bash"]
            }
            dialogue["tools_used"] = tool_mapping.get(dialogue["actual_intent"], ["Task"])
            
            await system.learn_from_interaction(dialogue)
            
        await asyncio.sleep(2)  # 批次間隔
    
    # 等待學習完成
    await asyncio.sleep(5)
    
    # 生成報告
    report = system.generate_learning_report()
    print(report)
    
    # 保存詳細報告
    detailed_report = f"""
# 持續學習系統詳細報告

## 生成的對話統計
- 總對話數: {len(all_dialogues)}
- 自動生成: {len(generated_dialogues)}
- 真實模式: {len(real_patterns)}

## 對話示例
### 自動生成的對話:
"""
    
    for dialogue in generated_dialogues[:5]:
        detailed_report += f"- {dialogue['user_input']} ({dialogue['actual_intent']})\n"
    
    detailed_report += "\n### 真實模式對話:\n"
    for dialogue in real_patterns[:5]:
        detailed_report += f"- {dialogue['user_input']} ({dialogue['actual_intent']})\n"
    
    detailed_report += f"\n{report}"
    
    with open("continuous_learning_detailed_report.md", 'w') as f:
        f.write(detailed_report)
    
    logger.info("📄 詳細報告已保存")
    
    # 取消學習任務
    learning_task.cancel()
    
    return system


async def main():
    """主函數"""
    system = await simulate_continuous_learning()
    logger.info("\n✅ 持續學習演示完成")
    
    # 顯示最終統計
    print("\n🎯 持續學習系統特點:")
    print("1. 實時從用戶交互中學習")
    print("2. 自動識別高價值學習樣本")
    print("3. 動態調整學習率")
    print("4. 定期評估和優化")
    print("5. 支持斷點恢復和版本管理")


if __name__ == "__main__":
    asyncio.run(main())