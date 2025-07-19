#!/usr/bin/env python3
"""
Manus Replay 數據收集腳本
使用方法：
1. 確保 Chrome 或 Safari 已登錄 Manus
2. 在 replay_urls.txt 中添加要收集的 URLs
3. 運行此腳本
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_collection.attach_existing_browser_collector import AttachBrowserCollector

def main():
    # 讀取 URLs
    urls_file = "replay_urls.txt"
    if not os.path.exists(urls_file):
        with open(urls_file, 'w') as f:
            f.write("# 在下面添加 Manus replay URLs，每行一個\n")
            f.write("# https://manus.im/share/xxx?replay=1\n")
            f.write("https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1\n")
        print(f"請在 {urls_file} 中添加要收集的 URLs")
        return
    
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("沒有找到 URLs")
        return
    
    print(f"準備收集 {len(urls)} 個 replays")
    
    # 選擇收集模式
    print("\n選擇收集模式：")
    print("1. 只用 Chrome")
    print("2. 只用 Safari")
    print("3. 混合模式（根據每個 URL 選擇瀏覽器）")
    print("4. 兩個都收集（先 Chrome 後 Safari）")
    
    mode = input("\n選擇 (1-4) [默認: 1]: ").strip() or "1"
    
    if mode == "1":
        # 只用 Chrome
        collector = AttachBrowserCollector(browser_type="chrome")
        results = collector.collect_replays(urls)
    elif mode == "2":
        # 只用 Safari
        collector = AttachBrowserCollector(browser_type="safari")
        results = collector.collect_replays(urls)
    elif mode == "3":
        # 混合模式
        chrome_urls = []
        safari_urls = []
        
        print("\n為每個 URL 選擇瀏覽器（c=Chrome, s=Safari）：")
        for url in urls:
            choice = input(f"{url[:50]}... (c/s) [默認: c]: ").strip().lower() or "c"
            if choice == "s":
                safari_urls.append(url)
            else:
                chrome_urls.append(url)
        
        results = {'successful': 0, 'failed': 0, 'data': [], 'errors': []}
        
        if chrome_urls:
            print(f"\n使用 Chrome 收集 {len(chrome_urls)} 個 URLs...")
            chrome_collector = AttachBrowserCollector(browser_type="chrome")
            chrome_results = chrome_collector.collect_replays(chrome_urls)
            results['successful'] += chrome_results.get('successful', 0)
            results['failed'] += chrome_results.get('failed', 0)
            results['data'].extend(chrome_results.get('data', []))
            results['errors'].extend(chrome_results.get('errors', []))
        
        if safari_urls:
            print(f"\n使用 Safari 收集 {len(safari_urls)} 個 URLs...")
            safari_collector = AttachBrowserCollector(browser_type="safari")
            safari_results = safari_collector.collect_replays(safari_urls)
            results['successful'] += safari_results.get('successful', 0)
            results['failed'] += safari_results.get('failed', 0)
            results['data'].extend(safari_results.get('data', []))
            results['errors'].extend(safari_results.get('errors', []))
    else:
        # 兩個都收集
        results = {'successful': 0, 'failed': 0, 'data': [], 'errors': []}
        
        print("\n使用 Chrome 收集...")
        chrome_collector = AttachBrowserCollector(browser_type="chrome")
        chrome_results = chrome_collector.collect_replays(urls)
        results['successful'] += chrome_results.get('successful', 0)
        results['failed'] += chrome_results.get('failed', 0)
        results['data'].extend(chrome_results.get('data', []))
        
        print("\n使用 Safari 收集...")
        safari_collector = AttachBrowserCollector(browser_type="safari")
        safari_results = safari_collector.collect_replays(urls)
        results['successful'] += safari_results.get('successful', 0)
        results['failed'] += safari_results.get('failed', 0)
        results['data'].extend(safari_results.get('data', []))
    
    print(f"\n收集完成！")
    print(f"成功: {results['successful']}")
    print(f"失敗: {results['failed']}")
    
    # 合併數據報告
    if results['data']:
        total_messages = sum(d.get('message_count', 0) for d in results['data'])
        total_pairs = sum(len(d.get('training_pairs', [])) for d in results['data'])
        print(f"總消息數: {total_messages}")
        print(f"訓練對數: {total_pairs}")

if __name__ == "__main__":
    main()