#!/usr/bin/env python3
"""
啟動Claude持續學習測試系統
與Real Collector配合工作，生成大量高質量訓練數據
"""

import asyncio
import subprocess
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """主啟動函數"""
    print("🚀 Claude持續學習測試系統啟動器")
    print("="*60)
    
    # 檢查Real Collector狀態
    print("🔍 檢查Real Collector狀態...")
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    
    real_collector_running = False
    if 'unified_realtime_k2_fixed' in result.stdout:
        print("✅ Real Collector正在運行")
        real_collector_running = True
    else:
        print("⚠️ Real Collector未運行，建議先啟動")
    
    # 檢查數據目錄
    data_dir = Path("data/continuous_learning_sessions")
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"📂 數據目錄: {data_dir}")
    
    print("\n🎯 系統配置:")
    print("- 每日運行16小時")
    print("- 每30秒生成一個訓練對話")
    print("- 覆蓋所有Claude本地命令")
    print("- 自動檢測並配合Real Collector")
    
    print("\n🔄 啟動選項:")
    print("1. 啟動持續學習系統")
    print("2. 啟動持續學習 + Real Collector")
    print("3. 僅測試運行30分鐘")
    print("4. 檢查現有數據")
    
    try:
        choice = input("\n請選擇 (1-4): ")
    except EOFError:
        print("🤖 非交互模式下自動選擇模式2: 啟動持續學習 + Real Collector")
        choice = "2"
    
    if choice == "1":
        print("🚀 啟動持續學習系統...")
        subprocess.run(['python3', 'claude_continuous_learning_test.py'])
        
    elif choice == "2":
        print("🚀 啟動Real Collector + 持續學習系統...")
        
        # 先啟動Real Collector（如果未運行）
        if not real_collector_running:
            print("🔧 啟動Real Collector...")
            subprocess.Popen(['nohup', 'python3', 'unified_realtime_k2_fixed.py'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            time.sleep(5)  # 等待啟動
        
        # 啟動持續學習
        subprocess.run(['python3', 'claude_continuous_learning_test.py'])
        
    elif choice == "3":
        print("🧪 測試運行30分鐘...")
        # 可以添加測試模式的實現
        
    elif choice == "4":
        print("📊 檢查現有數據...")
        # 檢查數據統計
        json_files = list(data_dir.glob("*.json"))
        print(f"已生成對話數據: {len(json_files)} 個文件")
        
        if json_files:
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"最新文件: {latest_file.name}")
    
    else:
        print("❌ 無效選擇")

if __name__ == "__main__":
    asyncio.run(main())