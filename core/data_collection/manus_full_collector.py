#!/usr/bin/env python3
"""
Manus 完整收集器
包含滾動和展開側邊欄功能
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import json
from pathlib import Path
from datetime import datetime

def collect_all_manus_tasks():
    print("🚀 Manus 完整數據收集器")
    
    # 設置瀏覽器
    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    
    output_dir = Path("./data/manus_complete")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 步驟1：登錄
        print("\n步驟1：訪問 Manus")
        driver.get("https://manus.im/login")
        
        print("請完成登錄並進入應用頁面...")
        print("提示：登錄後點擊任意對話進入 /app/ 頁面")
        input("準備好後，按 Enter 繼續...")
        
        current_url = driver.current_url
        print(f"\n當前 URL: {current_url}")
        
        # 步驟2：查找並打開側邊欄
        print("\n步驟2：查找側邊欄...")
        
        # 嘗試找到並點擊菜單按鈕
        menu_selectors = [
            '[aria-label*="menu"]',
            '[class*="menu-button"]',
            '[class*="hamburger"]',
            '[class*="toggle"]',
            'button[class*="menu"]',
            'svg[class*="menu"]',
            '[data-testid*="menu"]'
        ]
        
        menu_clicked = False
        for selector in menu_selectors:
            try:
                menu_btn = driver.find_element(By.CSS_SELECTOR, selector)
                menu_btn.click()
                print(f"✅ 點擊了菜單按鈕: {selector}")
                time.sleep(2)
                menu_clicked = True
                break
            except:
                continue
        
        if not menu_clicked:
            print("未找到菜單按鈕，繼續查找任務...")
        
        # 步驟3：收集所有任務
        print("\n步驟3：收集任務...")
        
        all_tasks = {}
        previous_count = 0
        scroll_attempts = 0
        max_scrolls = 30
        
        while scroll_attempts < max_scrolls:
            # 執行 JavaScript 收集當前可見的任務
            js_result = driver.execute_script("""
                const tasks = new Map();
                
                // 方法1: 查找所有 /app/ 連結
                document.querySelectorAll('a[href*="/app/"]').forEach(link => {
                    const href = link.href;
                    const match = href.match(/\\/app\\/([^\\/\\?]+)/);
                    if (match && match[1]) {
                        const taskId = match[1];
                        // 獲取最接近的文本內容
                        let text = link.innerText || link.textContent;
                        if (!text) {
                            // 嘗試從父元素獲取文本
                            let parent = link.parentElement;
                            let depth = 0;
                            while (parent && !text && depth < 3) {
                                text = parent.innerText || parent.textContent;
                                parent = parent.parentElement;
                                depth++;
                            }
                        }
                        tasks.set(taskId, {
                            id: taskId,
                            text: (text || 'Untitled').trim().substring(0, 100),
                            href: href,
                            selector: 'a[href*="/app/"]'
                        });
                    }
                });
                
                // 方法2: 查找可能的任務容器
                const containerSelectors = [
                    '.conversation-item',
                    '.task-item',
                    '.thread-item',
                    '[class*="conversation"]',
                    '[class*="task"]',
                    '[class*="thread"]',
                    '.sidebar-item',
                    '.list-item'
                ];
                
                containerSelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(item => {
                        const link = item.querySelector('a');
                        if (link && link.href && link.href.includes('/app/')) {
                            const match = link.href.match(/\\/app\\/([^\\/\\?]+)/);
                            if (match && match[1]) {
                                const taskId = match[1];
                                const text = item.innerText || item.textContent || 'Untitled';
                                tasks.set(taskId, {
                                    id: taskId,
                                    text: text.trim().substring(0, 100),
                                    href: link.href,
                                    selector: selector
                                });
                            }
                        }
                    });
                });
                
                return Array.from(tasks.values());
            """)
            
            # 添加新任務
            for task in js_result:
                all_tasks[task['id']] = task
            
            current_count = len(all_tasks)
            print(f"當前找到: {current_count} 個任務")
            
            # 檢查是否有新任務
            if current_count == previous_count:
                scroll_attempts += 1
                if scroll_attempts > 3:
                    print("沒有發現新任務，停止滾動")
                    break
            else:
                scroll_attempts = 0
                previous_count = current_count
            
            # 嘗試多種滾動方法
            
            # 方法1: 滾動側邊欄
            try:
                sidebar = driver.find_element(By.CSS_SELECTOR, 'aside, .sidebar, [class*="sidebar"], .left-panel, .side-panel')
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
                print("滾動側邊欄...")
            except:
                pass
            
            # 方法2: 滾動整個頁面
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            
            # 方法3: 使用鍵盤
            actions = ActionChains(driver)
            actions.send_keys(Keys.END).perform()
            
            # 等待加載
            time.sleep(2)
        
        # 轉換為列表
        tasks = list(all_tasks.values())
        print(f"\n✅ 總共找到 {len(tasks)} 個任務")
        
        if tasks:
            # 保存結果
            tasks_file = output_dir / "all_tasks.json"
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total': len(tasks),
                    'tasks': tasks,
                    'extracted_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            # 生成 replay URLs
            urls_file = output_dir / "replay_urls.txt"
            with open(urls_file, 'w') as f:
                f.write(f"# Manus 完整任務列表 - {len(tasks)} 個任務\n")
                f.write(f"# 提取時間: {datetime.now().isoformat()}\n\n")
                
                for i, task in enumerate(tasks):
                    f.write(f"# {i+1}. {task['text'][:80]}\n")
                    f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
            
            print(f"\n💾 數據已保存:")
            print(f"  任務列表: {tasks_file}")
            print(f"  Replay URLs: {urls_file}")
            
            # 顯示統計
            print(f"\n📊 統計信息:")
            print(f"  總任務數: {len(tasks)}")
            
            # 顯示前後幾個任務
            print(f"\n📋 前5個任務:")
            for i, task in enumerate(tasks[:5]):
                print(f"  {i+1}. {task['text'][:60]}")
            
            if len(tasks) > 5:
                print(f"\n📋 最後5個任務:")
                for i, task in enumerate(tasks[-5:], len(tasks)-4):
                    print(f"  {i}. {task['text'][:60]}")
        
        # 步驟4：詢問是否收集對話內容
        if tasks and len(tasks) > 1:
            collect_all = input(f"\n是否收集所有 {len(tasks)} 個任務的對話內容？(y/n) [默認: n]: ").strip().lower()
            
            if collect_all == 'y':
                print("\n開始收集對話內容...")
                conversations = []
                
                for i, task in enumerate(tasks[:10]):  # 先收集前10個
                    print(f"\n收集 {i+1}/10: {task['text'][:50]}")
                    
                    # 在新標籤頁打開
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    # 訪問任務頁面
                    driver.get(task['href'])
                    time.sleep(3)
                    
                    # 提取對話
                    conv_data = driver.execute_script("""
                        const messages = [];
                        document.querySelectorAll('[class*="message"]').forEach((msg, i) => {
                            messages.push({
                                role: i % 2 === 0 ? 'user' : 'assistant',
                                content: msg.innerText || msg.textContent
                            });
                        });
                        return {
                            taskId: arguments[0],
                            taskText: arguments[1],
                            messages: messages,
                            messageCount: messages.length
                        };
                    """, task['id'], task['text'])
                    
                    conversations.append(conv_data)
                    
                    # 關閉標籤頁
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                
                # 保存對話
                conv_file = output_dir / "conversations_sample.json"
                with open(conv_file, 'w', encoding='utf-8') as f:
                    json.dump(conversations, f, ensure_ascii=False, indent=2)
                
                print(f"\n✅ 已收集 {len(conversations)} 個對話樣本")
                print(f"保存到: {conv_file}")
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        input("\n按 Enter 關閉瀏覽器...")
        driver.quit()

if __name__ == "__main__":
    collect_all_manus_tasks()