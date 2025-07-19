#!/usr/bin/env python3
"""
診斷 Manus 頁面結構
幫助找到正確的選擇器
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import json

def diagnose_manus():
    print("🔍 診斷 Manus 頁面結構...")
    
    # 設置瀏覽器
    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    
    try:
        # 訪問 Manus
        url = input("請輸入 Manus URL: ").strip()
        driver.get(url)
        
        print("\n請登錄 Manus，然後按 Enter 繼續...")
        input()
        
        # 截圖
        driver.save_screenshot("manus_page.png")
        print("✅ 已保存截圖: manus_page.png")
        
        # 診斷頁面結構
        print("\n🔍 分析頁面結構...")
        
        # 執行診斷腳本
        diagnosis = driver.execute_script("""
            const result = {
                url: window.location.href,
                title: document.title,
                bodyClasses: document.body.className,
                possibleTaskLists: [],
                possibleTasks: [],
                links: []
            };
            
            // 查找可能的任務列表容器
            const listSelectors = [
                '.conversation-list',
                '.task-list',
                '.sidebar',
                '[class*="list"]',
                '[class*="conversation"]',
                '[class*="task"]',
                '[class*="chat"]',
                '[class*="thread"]',
                '.left-panel',
                '.side-panel',
                'aside',
                'nav'
            ];
            
            listSelectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    result.possibleTaskLists.push({
                        selector: selector,
                        count: elements.length,
                        firstClass: elements[0].className,
                        hasLinks: elements[0].querySelectorAll('a').length
                    });
                }
            });
            
            // 查找所有包含 /app/ 的連結
            document.querySelectorAll('a[href*="/app/"]').forEach(link => {
                const parent = link.parentElement;
                result.links.push({
                    href: link.href,
                    text: link.innerText.substring(0, 50),
                    parentClass: parent.className,
                    parentTag: parent.tagName
                });
            });
            
            // 查找可能的任務項目
            const taskSelectors = [
                'a[href*="/app/"]',
                '[onclick*="app"]',
                '[data-conversation-id]',
                '[data-task-id]',
                '[data-thread-id]'
            ];
            
            taskSelectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    result.possibleTasks.push({
                        selector: selector,
                        count: elements.length,
                        sample: elements[0].outerHTML.substring(0, 200)
                    });
                }
            });
            
            return result;
        """)
        
        # 保存診斷結果
        with open('manus_diagnosis.json', 'w', encoding='utf-8') as f:
            json.dump(diagnosis, f, ensure_ascii=False, indent=2)
            
        print("\n📊 診斷結果:")
        print(f"URL: {diagnosis['url']}")
        print(f"標題: {diagnosis['title']}")
        print(f"\n可能的任務列表容器: {len(diagnosis['possibleTaskLists'])}")
        for item in diagnosis['possibleTaskLists'][:5]:
            print(f"  - {item['selector']}: {item['count']} 個元素, {item['hasLinks']} 個連結")
            
        print(f"\n找到的 /app/ 連結: {len(diagnosis['links'])}")
        for link in diagnosis['links'][:5]:
            print(f"  - {link['text']}: {link['href']}")
            
        print(f"\n✅ 詳細診斷已保存到 manus_diagnosis.json")
        
        # 嘗試更具體的提取
        print("\n🔍 嘗試提取任務...")
        
        # 手動檢查一些常見結構
        selectors_to_try = [
            "a[href*='/app/']",
            ".conversation-item a",
            ".task-item a",
            "[class*='conversation'] a",
            "[class*='task'] a",
            ".sidebar a[href*='/app/']"
        ]
        
        for selector in selectors_to_try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"\n✅ 使用選擇器 '{selector}' 找到 {len(elements)} 個任務")
                for i, elem in enumerate(elements[:3]):
                    print(f"  {i+1}. {elem.text[:50]}")
                break
                
    finally:
        input("\n按 Enter 關閉瀏覽器...")
        driver.quit()

if __name__ == "__main__":
    diagnose_manus()