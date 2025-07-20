#!/usr/bin/env python3
import json
from datetime import datetime
import time

def monitor_accuracy():
    while True:
        try:
            # 讀取最新的準確率數據
            with open('accuracy_metrics.json', 'r') as f:
                metrics = json.load(f)
            
            current_accuracy = metrics.get('tool_call_accuracy', 0)
            target_accuracy = 89
            
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] 當前準確率: {current_accuracy:.1f}% | 目標: {target_accuracy}% | 進度: {'█' * int(current_accuracy/2)}{'░' * (50-int(current_accuracy/2))}", end='')
            
        except:
            print("\r等待數據...", end='')
        
        time.sleep(5)

if __name__ == "__main__":
    monitor_accuracy()
