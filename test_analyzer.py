#!/usr/bin/env python3
"""
測試 Manus 分析器
使用已收集的第一個 URL 進行測試
"""

import subprocess
import sys
from pathlib import Path

def test_analyzer():
    """測試分析器功能"""
    
    # 讀取第一個 URL
    urls = []
    if Path('manus_tasks_manual.txt').exists():
        with open('manus_tasks_manual.txt', 'r') as f:
            for line in f:
                if line.strip().startswith('http'):
                    urls.append(line.strip())
                    if len(urls) >= 1:  # 只取第一個
                        break
    
    if not urls:
        print("❌ 未找到測試 URL")
        return
    
    test_url = urls[0]
    print(f"🔍 測試 URL: {test_url}")
    
    # 創建測試輸出目錄
    output_dir = "manus_test_output"
    Path(output_dir).mkdir(exist_ok=True)
    
    # 運行分析器
    cmd = [
        sys.executable,
        "manus_enhanced_analyzer.py",
        "--url", test_url,
        "--output-dir", output_dir
    ]
    
    print(f"\n🚀 執行命令: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        # 執行分析
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print("\n" + "=" * 60)
        
        # 檢查輸出文件
        output_files = list(Path(output_dir).glob("manus_*"))
        if output_files:
            print(f"\n✅ 生成了 {len(output_files)} 個輸出文件:")
            for f in output_files:
                print(f"  - {f.name}")
        else:
            print("\n❌ 未生成輸出文件")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("\n❌ 分析超時（60秒）")
        return False
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        return False

if __name__ == "__main__":
    print("🎯 開始測試 Manus 增強分析器")
    print("=" * 60)
    
    success = test_analyzer()
    
    if success:
        print("\n✅ 測試完成！")
    else:
        print("\n❌ 測試失敗")