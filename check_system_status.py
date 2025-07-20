#!/usr/bin/env python3
"""
檢查訓練系統狀態
"""

import subprocess
import psutil
import json
from pathlib import Path
from datetime import datetime


def check_system_status():
    """檢查所有訓練系統組件狀態"""
    
    print("🔍 檢查訓練系統狀態...")
    print("=" * 60)
    
    # 1. 檢查Python進程
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(keyword in cmdline for keyword in ['unified', 'collector', 'replay', 'k2']):
                    python_processes.append({
                        'pid': proc.info['pid'],
                        'script': cmdline.split()[-1] if cmdline.split() else 'unknown'
                    })
        except:
            pass
    
    print("📊 運行中的訓練進程:")
    if python_processes:
        for proc in python_processes:
            print(f"  ✅ PID {proc['pid']}: {proc['script']}")
    else:
        print("  ❌ 沒有發現訓練進程")
    
    # 2. 檢查最新的日誌
    print("\n📝 最新日誌狀態:")
    log_file = Path("unified_k2_training.log")
    if log_file.exists():
        # 獲取最後幾行
        result = subprocess.run(['tail', '-n', '5', str(log_file)], 
                              capture_output=True, text=True)
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if '目標達成率' in line:
                    print(f"  {line}")
                elif 'Claude Code相似度' in line:
                    print(f"  {line}")
    
    # 3. 檢查訓練數據
    print("\n💾 訓練數據統計:")
    data_dir = Path("data")
    
    # 統計replay文件
    replay_files = list(data_dir.glob("**/replay_*.json"))
    print(f"  - Replay文件: {len(replay_files)} 個")
    
    # 統計訓練樣本
    training_samples = 0
    for f in data_dir.glob("**/*training*.jsonl"):
        try:
            with open(f, 'r') as file:
                training_samples += sum(1 for _ in file)
        except:
            pass
    print(f"  - 訓練樣本: {training_samples} 條")
    
    # 4. 檢查準確率指標
    print("\n📈 當前性能指標:")
    metrics_file = Path("accuracy_metrics.json")
    if metrics_file.exists():
        try:
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
                print(f"  - 工具調用準確率: {metrics.get('tool_call_accuracy', 'N/A')}%")
                print(f"  - 語義相似度: {metrics.get('semantic_similarity', 'N/A')}%")
        except:
            print("  - 指標文件暫無數據")
    else:
        print("  - 等待生成指標...")
    
    # 5. 系統建議
    print("\n💡 系統建議:")
    if not python_processes:
        print("  ⚠️  建議運行: python3 start_optimized_training.py")
    else:
        print("  ✅ 系統運行正常")
    
    if training_samples < 1000:
        print("  ⚠️  訓練樣本較少，建議處理更多replay數據")
    
    print("\n🎯 3天目標進度:")
    print("  Day 1 (今天): 80% 準確率")
    print("  Day 2 (明天): 85% 準確率") 
    print("  Day 3 (後天): 89% 準確率")
    
    print("=" * 60)
    print(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    check_system_status()