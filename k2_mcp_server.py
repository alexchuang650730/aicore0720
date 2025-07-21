#!/usr/bin/env python3
"""
K2 MCP Server - 在 Claude Code 中使用 K2 訓練
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

class K2MCPServer:
    def __init__(self):
        self.training_system = EnhancedIntentTrainingSystem()
        self.continuous_learning = IntegratedContinuousLearning()
        
    def handle_request(self, request):
        """處理 MCP 請求"""
        method = request.get("method", "")
        
        if method == "k2/predict":
            # K2 意圖預測
            text = request.get("params", {}).get("text", "")
            result = self.training_system.predict_intent_enhanced(text)
            return {
                "intent": result["intent"],
                "confidence": result["confidence"],
                "tools": result["suggested_tools"]
            }
            
        elif method == "k2/train":
            # 添加訓練樣本
            sample = request.get("params", {})
            self.continuous_learning.learn_from_interaction(sample)
            return {"status": "added", "total_samples": self.continuous_learning.stats["total_processed"]}
            
        elif method == "k2/status":
            # 獲取訓練狀態
            return {
                "model_version": self.training_system.model.get("version", 0),
                "accuracy": self.training_system.get_current_accuracy(),
                "total_samples": len(self.training_system.training_data),
                "training_active": True
            }
            
        return {"error": "Unknown method"}

if __name__ == "__main__":
    server = K2MCPServer()
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
