#!/usr/bin/env python3
"""
提取 Manus 左側邊欄的所有任務
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import json
from pathlib import Path
from datetime import datetime

def extract_sidebar_tasks():
    print("🚀 提取 Manus 側邊欄任務")
    
    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    
    output_dir = Path("./data/manus_sidebar")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 登錄
        driver.get("https://manus.im/login")
        print("請登錄並進入任務頁面...")
        input("準備好後按 Enter...")
        
        print("\n🔍 分析左側邊欄...")
        
        # 查找左側的數字導航
        all_tasks = []
        
        # 方法1: 查找數字標記（五、四、三等）
        chinese_numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        
        for num in chinese_numbers:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{num}')]")
            for elem in elements:
                try:
                    # 檢查是否是側邊欄元素
                    parent = elem.find_element(By.XPATH, "..")
                    if parent.tag_name == 'a' or elem.tag_name == 'a':
                        link = parent if parent.tag_name == 'a' else elem
                        href = link.get_attribute('href')
                        if href and '/app/' in href:
                            task_id = href.split('/app/')[-1].split('?')[0]
                            all_tasks.append({
                                'number': num,
                                'id': task_id,
                                'href': href,
                                'text': elem.text
                            })
                            print(f"找到任務 {num}: {task_id}")
                except:
                    pass
        
        # 方法2: 執行 JavaScript 查找所有側邊欄連結
        js_tasks = driver.execute_script("""
            const tasks = [];
            
            // 查找左側面板
            const leftPanel = document.querySelector('.left-panel, aside, [class*="sidebar"], nav');
            if (leftPanel) {
                // 查找所有連結
                leftPanel.querySelectorAll('a').forEach((link, index) => {
                    if (link.href && link.href.includes('/app/')) {
                        const match = link.href.match(/\\/app\\/([^\\/\\?]+)/);
                        if (match) {
                            tasks.push({
                                index: index,
                                id: match[1],
                                href: link.href,
                                text: link.innerText || link.textContent || '',
                                className: link.className
                            });
                        }
                    }
                });
            }
            
            // 也查找主要區域的導航
            document.querySelectorAll('nav a, .navigation a').forEach((link, index) => {
                if (link.href && link.href.includes('/app/')) {
                    const match = link.href.match(/\\/app\\/([^\\/\\?]+)/);
                    if (match) {
                        tasks.push({
                            index: index + 100,
                            id: match[1],
                            href: link.href,
                            text: link.innerText || '',
                            source: 'navigation'
                        });
                    }
                }
            });
            
            return tasks;
        """)
        
        print(f"\nJavaScript 找到 {len(js_tasks)} 個任務")
        
        # 合併結果
        task_map = {}
        for task in all_tasks:
            task_map[task['id']] = task
        
        for task in js_tasks:
            if task['id'] not in task_map:
                task_map[task['id']] = task
        
        final_tasks = list(task_map.values())
        print(f"\n✅ 總共找到 {len(final_tasks)} 個獨特任務")
        
        # 保存結果
        if final_tasks:
            # 保存任務列表
            tasks_file = output_dir / "sidebar_tasks.json"
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total': len(final_tasks),
                    'tasks': final_tasks,
                    'extracted_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            # 生成 replay URLs
            urls_file = output_dir / "replay_urls.txt"
            with open(urls_file, 'w') as f:
                f.write(f"# Manus 側邊欄任務 - {len(final_tasks)} 個\n")
                f.write(f"# 提取時間: {datetime.now().isoformat()}\n\n")
                
                for i, task in enumerate(final_tasks):
                    text = task.get('text', task.get('number', f'Task {i+1}'))
                    f.write(f"# {i+1}. {text}\n")
                    f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
            
            print(f"\n💾 已保存:")
            print(f"  任務: {tasks_file}")
            print(f"  URLs: {urls_file}")
            
            # 顯示任務列表
            print(f"\n📋 任務列表:")
            for task in final_tasks:
                print(f"  - {task.get('text', task.get('number', 'Unknown'))}: {task['id'][:20]}...")
        
        # 提示：手動點擊
        print("\n💡 提示：")
        print("如果沒有找到所有任務，請嘗試：")
        print("1. 點擊左側的數字（五、四、三等）")
        print("2. 滾動左側面板")
        print("3. 點擊「查看更多」或類似按鈕")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        input("\n按 Enter 關閉...")
        driver.quit()

if __name__ == "__main__":
    extract_sidebar_tasks()