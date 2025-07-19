#!/usr/bin/env python3
"""
啟動訓練數據收集
在每次 Claude Code 會話開始時運行此腳本
"""

import sys
import os
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def start_collection():
    """啟動訓練數據收集"""
    try:
        # 導入並啟動收集器
        from core.components.memoryrag_mcp.claude_code_hook import get_hook, capture_claude_interaction
        
        hook = get_hook()
        print("🤖 訓練數據收集已啟動!")
        print(f"   - 收集器狀態: {'啟用' if hook.enabled else '禁用'}")
        print(f"   - 數據存儲: {hook.session_data.get('start_time', 'N/A')}")
        
        # 設置環境變量標記
        os.environ['CLAUDE_CODE_TRAINING'] = '1'
        
        # 收集當前這次交互
        capture_claude_interaction(
            user_message="啟動訓練數據收集",
            assistant_response="訓練數據收集系統已成功啟動，將自動收集後續的所有交互數據用於 K2 模型訓練。",
            tools_used=["auto_training_collector"],
            context={"action": "system_startup", "component": "training_collection"}
        )
        
        return True
        
    except Exception as e:
        print(f"❌ 啟動收集器失敗: {e}")
        return False

if __name__ == "__main__":
    start_collection()