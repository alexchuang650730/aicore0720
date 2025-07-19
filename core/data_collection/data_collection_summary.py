#!/usr/bin/env python3
"""
數據收集進度總結
"""

from pathlib import Path
import json
from datetime import datetime

def count_manus_tasks():
    """統計 Manus 任務數量"""
    count = 0
    with open('manus_tasks_manual.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('# 任務'):
                count += 1
    return count

def check_claude_data():
    """檢查 Claude 數據"""
    claude_dir = Path('./data/claude_conversations')
    if claude_dir.exists():
        files = list(claude_dir.glob('*.json'))
        return len(files)
    return 0

def main():
    print("=" * 60)
    print("📊 數據收集進度總結")
    print("=" * 60)
    print(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Manus 任務統計
    manus_count = count_manus_tasks()
    print(f"🎯 Manus 任務收集:")
    print(f"   已收集: {manus_count} 個任務")
    print(f"   目標: 200 個任務")
    print(f"   進度: {manus_count/200*100:.1f}%")
    
    if manus_count >= 200:
        print(f"   ✅ 已達成目標！")
    else:
        print(f"   還需: {200 - manus_count} 個任務")
    
    # Claude 對話統計
    claude_files = check_claude_data()
    print(f"\n🤖 Claude 對話處理:")
    print(f"   已處理: {claude_files} 個對話文件")
    print(f"   ✅ 已生成訓練樣本和分析報告")
    
    # 工具開發統計
    print(f"\n🔧 已開發工具:")
    tools = [
        "manus_precise_sidebar_collector.py - 精確側邊欄收集器",
        "manus_interactive_collector.py - 互動式收集器", 
        "manus_simple_scroll_collector.py - 簡單滾動收集器",
        "manus_manual_scroll_auto_collect.py - 手動滾動自動收集",
        "manus_advanced_analyzer.py - 高級分析器",
        "claude_conversation_processor.py - Claude 對話處理器",
        "manus_tool_usage_extractor.py - 工具使用提取器"
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool}")
    
    # 下一步建議
    print(f"\n📝 下一步建議:")
    if manus_count < 200:
        print(f"   1. 繼續收集 Manus 任務直到 200 個")
    else:
        print(f"   1. ✅ Manus 任務收集已完成")
        
    print(f"   2. 運行 manus_advanced_analyzer.py 分析所有任務")
    print(f"   3. 整合 Manus 和 Claude 數據生成訓練集")
    print(f"   4. 提取工具使用模式用於 K2 優化")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()