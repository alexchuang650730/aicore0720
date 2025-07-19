#!/usr/bin/env python3
"""
簡化的 Manus 收集腳本
確保在正確的頁面收集數據
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from pathlib import Path
from datetime import datetime

def collect_manus_data():
    print("🚀 Manus 數據收集器")
    
    # 設置瀏覽器
    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    
    output_dir = Path("./data/manus_chrome")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 步驟1：訪問 Manus
        print("\n步驟1：訪問 Manus 登錄頁面")
        driver.get("https://manus.im/login")
        
        print("請完成登錄...")
        input("登錄成功後，按 Enter 繼續...")
        
        # 步驟2：確認在應用頁面
        current_url = driver.current_url
        print(f"\n當前 URL: {current_url}")
        
        if '/app/' not in current_url:
            print("❌ 您還不在應用頁面")
            print("請點擊任意一個對話/任務進入應用頁面")
            input("進入應用頁面後，按 Enter 繼續...")
            current_url = driver.current_url
            print(f"新 URL: {current_url}")
        
        # 步驟3：等待頁面完全加載
        print("\n等待頁面加載...")
        time.sleep(3)
        
        # 步驟4：診斷頁面結構
        print("\n🔍 分析頁面結構...")
        
        # 保存截圖
        driver.save_screenshot(str(output_dir / "manus_app_page.png"))
        
        # 嘗試各種方法提取任務
        tasks = []
        
        # 方法1：執行 JavaScript 提取
        print("\n嘗試方法1：JavaScript 提取...")
        js_result = driver.execute_script("""
            const tasks = [];
            
            // 查找所有可能包含任務的元素
            const allElements = document.querySelectorAll('*');
            const taskElements = [];
            
            allElements.forEach(el => {
                // 檢查是否有指向 /app/ 的連結
                const links = el.querySelectorAll('a[href*="/app/"]');
                if (links.length > 0) {
                    taskElements.push(el);
                }
                
                // 檢查元素本身是否是連結
                if (el.tagName === 'A' && el.href && el.href.includes('/app/')) {
                    const taskId = el.href.match(/\\/app\\/([^\\/\\?]+)/);
                    if (taskId) {
                        tasks.push({
                            id: taskId[1],
                            text: el.innerText || el.textContent || 'Untitled',
                            href: el.href,
                            className: el.className,
                            parentClassName: el.parentElement ? el.parentElement.className : ''
                        });
                    }
                }
            });
            
            // 也嘗試從側邊欄查找
            const sidebar = document.querySelector('aside, .sidebar, [class*="sidebar"], .left-panel, .side-panel');
            if (sidebar) {
                console.log('找到側邊欄:', sidebar.className);
                const sidebarLinks = sidebar.querySelectorAll('a');
                sidebarLinks.forEach(link => {
                    if (link.href && link.href.includes('/app/')) {
                        const taskId = link.href.match(/\\/app\\/([^\\/\\?]+)/);
                        if (taskId) {
                            tasks.push({
                                id: taskId[1],
                                text: link.innerText || 'Untitled',
                                href: link.href,
                                source: 'sidebar'
                            });
                        }
                    }
                });
            }
            
            return {
                tasks: tasks,
                pageInfo: {
                    url: window.location.href,
                    title: document.title,
                    hasAside: !!document.querySelector('aside'),
                    hasSidebar: !!document.querySelector('.sidebar, [class*="sidebar"]'),
                    totalLinks: document.querySelectorAll('a').length,
                    appLinks: document.querySelectorAll('a[href*="/app/"]').length
                }
            };
        """)
        
        print(f"JavaScript 結果: 找到 {len(js_result['tasks'])} 個任務")
        print(f"頁面信息: {js_result['pageInfo']}")
        
        if js_result['tasks']:
            tasks = js_result['tasks']
        
        # 方法2：手動查找
        if not tasks:
            print("\n嘗試方法2：Selenium 查找...")
            
            # 嘗試點擊展開側邊欄（如果需要）
            try:
                menu_button = driver.find_element(By.CSS_SELECTOR, '[class*="menu"], [class*="toggle"], [aria-label*="menu"]')
                menu_button.click()
                time.sleep(1)
                print("✅ 點擊了菜單按鈕")
            except:
                pass
            
            # 查找連結
            links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/app/"]')
            print(f"找到 {len(links)} 個 app 連結")
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    text = link.text or 'Untitled'
                    if '/app/' in href:
                        task_id = href.split('/app/')[-1].split('?')[0]
                        tasks.append({
                            'id': task_id,
                            'text': text,
                            'href': href
                        })
                except:
                    pass
        
        # 保存結果
        print(f"\n✅ 總共找到 {len(tasks)} 個任務")
        
        if tasks:
            # 去重
            unique_tasks = {}
            for task in tasks:
                unique_tasks[task['id']] = task
            
            tasks = list(unique_tasks.values())
            print(f"去重後: {len(tasks)} 個任務")
            
            # 保存任務列表
            tasks_file = output_dir / "extracted_tasks.json"
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total': len(tasks),
                    'tasks': tasks,
                    'extracted_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            # 生成 replay URLs
            urls_file = output_dir / "replay_urls.txt"
            with open(urls_file, 'w') as f:
                f.write(f"# 提取的 {len(tasks)} 個 Manus 任務\n")
                f.write(f"# 提取時間: {datetime.now().isoformat()}\n\n")
                
                for i, task in enumerate(tasks):
                    f.write(f"# {i+1}. {task['text'][:50]}\n")
                    f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
            
            print(f"\n💾 數據已保存:")
            print(f"  任務列表: {tasks_file}")
            print(f"  Replay URLs: {urls_file}")
            
            # 顯示前幾個任務
            print("\n📋 前5個任務:")
            for i, task in enumerate(tasks[:5]):
                print(f"  {i+1}. {task['text'][:50]}")
                
        else:
            print("\n❌ 未找到任務")
            print("可能的原因：")
            print("1. 頁面結構不同")
            print("2. 需要滾動加載")
            print("3. 任務在其他頁面")
            
            # 保存頁面源碼用於調試
            with open(output_dir / "page_source.html", 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"\n已保存頁面源碼用於分析: {output_dir}/page_source.html")
            
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        
    finally:
        input("\n按 Enter 關閉瀏覽器...")
        driver.quit()

if __name__ == "__main__":
    collect_manus_data()