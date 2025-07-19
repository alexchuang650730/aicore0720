#!/usr/bin/env python3
"""
自動運行 Playwright 收集器
"""

import asyncio
from manus_playwright_collector import ManusPlaywrightCollector

async def main():
    print("=" * 60)
    print("🎯 開始 Manus Playwright 數據收集")
    print("=" * 60)
    
    # 使用無頭模式自動運行
    collector = ManusPlaywrightCollector(headless=True)
    
    tasks = collector._load_tasks()
    print(f"\n總共有 {len(tasks)} 個任務待收集")
    
    # 只收集前 5 個任務作為測試
    print("\n先測試前 5 個任務...")
    
    # 臨時修改任務列表
    original_tasks_file = collector.tasks_file
    test_tasks = tasks[:5]
    
    # 創建測試任務文件
    test_file = collector.output_dir / 'test_tasks.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        for i, task in enumerate(test_tasks, 1):
            f.write(f"# 任務 {i}\n")
            f.write(f"{task['url']}\n\n")
    
    # 使用測試文件
    collector.tasks_file = test_file
    
    try:
        results = await collector.collect_tasks()
        
        # 分析結果
        success_count = sum(1 for r in results if r['success'])
        print(f"\n測試結果:")
        print(f"- 成功: {success_count}/5")
        print(f"- 失敗: {5-success_count}/5")
        
        if success_count > 0:
            print("\n成功提取的對話示例:")
            for r in results:
                if r['success']:
                    conv = r['conversation']
                    print(f"\n標題: {conv['title']}")
                    print(f"消息數: {len(conv['messages'])}")
                    if conv['messages']:
                        print(f"第一條消息: {conv['messages'][0]['content'][:100]}...")
                    break
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())