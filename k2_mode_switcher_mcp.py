#!/usr/bin/env python3
"""
K2 Mode Switcher MCP - 支持 K2/Claude Code 模式切換
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加 aicore 路徑
sys.path.append(os.environ.get('AICORE_DIR', '/Users/alexchuang/alexchuangtest/aicore0720'))

from intent_training_system_enhanced import EnhancedIntentTrainingSystem
from integrated_continuous_learning import IntegratedContinuousLearning

class K2ModeSwitcherMCP:
    def __init__(self):
        self.training_system = EnhancedIntentTrainingSystem()
        self.continuous_learning = IntegratedContinuousLearning()
        
        # 模式狀態
        self.mode = "hybrid"  # "k2", "claude", "hybrid"
        self.k2_confidence_threshold = 0.7
        
        # 模式切換關鍵詞
        self.mode_keywords = {
            "k2": ["使用K2", "切換到K2", "K2模式", "use k2", "k2 mode"],
            "claude": ["使用Claude", "切換到Claude", "Claude模式", "use claude", "claude mode"],
            "hybrid": ["混合模式", "智能模式", "自動選擇", "hybrid mode", "auto mode"]
        }
        
    def check_mode_switch(self, text):
        """檢查是否需要切換模式"""
        text_lower = text.lower()
        
        for mode, keywords in self.mode_keywords.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                self.mode = mode
                return True, mode
        
        return False, self.mode
        
    def handle_request(self, request):
        """處理 MCP 請求"""
        method = request.get("method", "")
        
        if method == "k2/predict":
            # 檢查是否需要切換模式
            text = request.get("params", {}).get("text", "")
            switched, new_mode = self.check_mode_switch(text)
            
            if switched:
                return {
                    "mode_switched": True,
                    "new_mode": new_mode,
                    "message": f"已切換到 {new_mode} 模式"
                }
            
            # 根據當前模式處理
            if self.mode == "k2":
                # 純 K2 模式
                result = self.training_system.predict_intent_enhanced(text)
                return {
                    "mode": "k2",
                    "intent": result["intent"],
                    "confidence": result["confidence"],
                    "tools": result["suggested_tools"],
                    "use_k2": True
                }
                
            elif self.mode == "claude":
                # 純 Claude 模式
                return {
                    "mode": "claude",
                    "use_k2": False,
                    "message": "使用 Claude Code 原生模式"
                }
                
            else:  # hybrid
                # 混合模式：根據置信度決定
                result = self.training_system.predict_intent_enhanced(text)
                use_k2 = result["confidence"] >= self.k2_confidence_threshold
                
                return {
                    "mode": "hybrid",
                    "intent": result["intent"],
                    "confidence": result["confidence"],
                    "tools": result["suggested_tools"] if use_k2 else [],
                    "use_k2": use_k2,
                    "fallback_reason": "低置信度" if not use_k2 else None
                }
                
        elif method == "k2/switch_mode":
            # 直接切換模式
            new_mode = request.get("params", {}).get("mode", "hybrid")
            if new_mode in ["k2", "claude", "hybrid"]:
                self.mode = new_mode
                return {
                    "status": "success",
                    "mode": self.mode,
                    "message": f"已切換到 {self.mode} 模式"
                }
            else:
                return {"status": "error", "message": "無效的模式"}
                
        elif method == "k2/get_mode":
            # 獲取當前模式
            return {
                "mode": self.mode,
                "threshold": self.k2_confidence_threshold,
                "keywords": self.mode_keywords
            }
            
        elif method == "k2/set_threshold":
            # 設置置信度閾值
            threshold = request.get("params", {}).get("threshold", 0.7)
            if 0 <= threshold <= 1:
                self.k2_confidence_threshold = threshold
                return {
                    "status": "success",
                    "threshold": self.k2_confidence_threshold
                }
            else:
                return {"status": "error", "message": "閾值必須在 0-1 之間"}
                
        elif method == "k2/train":
            # 添加訓練樣本
            sample = request.get("params", {})
            self.continuous_learning.learn_from_interaction(sample)
            return {"status": "added", "total_samples": self.continuous_learning.stats["total_processed"]}
            
        elif method == "k2/status":
            # 獲取訓練狀態
            return {
                "mode": self.mode,
                "model_version": self.training_system.model.get("version", 0),
                "accuracy": self.training_system.get_current_accuracy(),
                "total_samples": len(self.training_system.training_data),
                "training_active": True,
                "confidence_threshold": self.k2_confidence_threshold
            }
            
        return {"error": "Unknown method"}

if __name__ == "__main__":
    server = K2ModeSwitcherMCP()
    # MCP 協議處理循環
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()