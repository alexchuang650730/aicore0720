#!/usr/bin/env python3
"""
自動啟動訓練數據收集
通過環境檢測和導入掛鉤自動啟動
"""

import os
import sys
import atexit
from pathlib import Path
import json
from datetime import datetime

# 檢測 Claude Code 環境
def is_claude_code_environment():
    """檢測是否在 Claude Code 環境中"""
    indicators = [
        # 環境變量檢測
        os.environ.get('CLAUDE_CODE_SESSION'),
        os.environ.get('ANTHROPIC_API_KEY'),
        
        # 進程名檢測
        'claude' in ' '.join(sys.argv).lower(),
        'claude' in sys.executable.lower(),
        
        # 工作目錄檢測
        'claude' in os.getcwd().lower(),
        
        # 父進程檢測（如果可用）
        any('claude' in str(arg).lower() for arg in sys.argv),
    ]
    
    return any(indicators)

def setup_auto_collection():
    """設置自動收集"""
    if not is_claude_code_environment():
        return False
    
    try:
        # 設置環境變量
        os.environ['CLAUDE_CODE_TRAINING'] = '1'
        os.environ['TRAINING_AUTO_START'] = '1'
        
        # 導入並啟動收集系統
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from core.components.memoryrag_mcp.claude_code_hook import get_hook, capture_claude_interaction
        from core.components.memoryrag_mcp.auto_training_collector import get_current_session_summary
        
        hook = get_hook()
        
        # 記錄啟動信息
        start_info = {
            'auto_start_time': datetime.now().isoformat(),
            'process_id': os.getpid(),
            'working_directory': os.getcwd(),
            'python_executable': sys.executable,
            'argv': sys.argv,
            'hook_enabled': hook.enabled
        }
        
        # 保存啟動日誌
        log_file = project_root / "data/claude_conversations/auto_start_log.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(start_info)
        
        # 只保留最近10次啟動記錄
        logs = logs[-10:]
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        # 收集自動啟動事件
        capture_claude_interaction(
            user_message="系統自動檢測到 Claude Code 環境，啟動訓練數據收集",
            assistant_response=f"自動啟動訓練數據收集成功。收集器狀態: {'啟用' if hook.enabled else '禁用'}。開始收集所有交互數據用於 K2 模型訓練。",
            tools_used=["auto_start", "environment_detection"],
            context={
                "auto_start": True,
                "detection_method": "environment_analysis",
                "start_time": start_info['auto_start_time']
            }
        )
        
        # 註冊退出處理
        def on_exit():
            try:
                summary = get_current_session_summary()
                print(f"\n🎓 訓練數據收集會話結束")
                print(f"   - 收集交互數: {summary.get('total_interactions', 0)}")
                print(f"   - 使用工具數: {len(summary.get('tools_used', []))}")
                print(f"   - 數據文件: {summary.get('data_file', 'N/A')}")
            except:
                pass
        
        atexit.register(on_exit)
        
        return True
        
    except Exception as e:
        print(f"自動啟動收集失敗: {e}")
        return False

# 在模塊導入時自動執行
if __name__ != "__main__":
    try:
        if setup_auto_collection():
            pass  # 靜默啟動
    except:
        pass  # 靜默失敗

if __name__ == "__main__":
    # 直接運行時顯示詳細信息
    print("🔍 檢測 Claude Code 環境...")
    
    is_claude = is_claude_code_environment()
    print(f"   Claude Code 環境: {'是' if is_claude else '否'}")
    
    if is_claude:
        print("🚀 啟動自動收集...")
        success = setup_auto_collection()
        print(f"   啟動結果: {'成功' if success else '失敗'}")
    else:
        print("💡 提示: 在 Claude Code 環境中自動啟動收集")
    
    # 顯示環境信息
    print(f"\n🔧 環境信息:")
    print(f"   工作目錄: {os.getcwd()}")
    print(f"   Python: {sys.executable}")
    print(f"   參數: {' '.join(sys.argv)}")
    print(f"   環境變量 CLAUDE_CODE_SESSION: {os.environ.get('CLAUDE_CODE_SESSION', '未設置')}")
    print(f"   環境變量 ANTHROPIC_API_KEY: {'已設置' if os.environ.get('ANTHROPIC_API_KEY') else '未設置'}")