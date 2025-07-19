#!/usr/bin/env python3
"""
Manus 調試收集器
診斷頁面結構，找出為什麼無法收集到任務
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime

print("🔍 Manus 調試診斷工具\n")

# 啟動瀏覽器
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)
driver.maximize_window()

try:
    # 訪問 Manus
    driver.get("https://manus.im/login")
    
    print("請完成以下操作：")
    print("1. 登錄 Manus")
    print("2. 進入有左側任務列表的對話頁面")
    print("3. 確保能看到多個任務（五、四、三等）")
    input("\n完成後按 Enter 開始診斷...")
    
    print("\n開始診斷...\n")
    
    # 診斷 1: 基本信息
    basic_info = driver.execute_script("""
        return {
            url: window.location.href,
            title: document.title,
            totalLinks: document.querySelectorAll('a').length,
            appLinks: document.querySelectorAll('a[href*="/app/"]').length,
            shareLinks: document.querySelectorAll('a[href*="/share/"]').length
        };
    """)
    
    print("📊 基本信息:")
    print(f"  URL: {basic_info['url']}")
    print(f"  標題: {basic_info['title']}")
    print(f"  總連結數: {basic_info['totalLinks']}")
    print(f"  App 連結: {basic_info['appLinks']}")
    print(f"  Share 連結: {basic_info['shareLinks']}")
    
    # 診斷 2: 查找中文數字
    chinese_check = driver.execute_script("""
        const numbers = ['一', '二', '三', '四', '五'];
        const found = {};
        
        numbers.forEach(num => {
            const elements = Array.from(document.querySelectorAll('*')).filter(el => 
                el.innerText && el.innerText.includes(num)
            );
            found[num] = elements.length;
        });
        
        return found;
    """)
    
    print("\n🔢 中文數字檢測:")
    for num, count in chinese_check.items():
        print(f"  '{num}': 找到 {count} 個元素")
    
    # 診斷 3: 查找所有連結
    all_links = driver.execute_script("""
        const links = [];
        document.querySelectorAll('a').forEach(link => {
            if (link.href && (link.href.includes('/app/') || link.href.includes('/share/'))) {
                links.push({
                    href: link.href,
                    text: link.innerText.substring(0, 50),
                    visible: link.offsetParent !== null
                });
            }
        });
        return links;
    """)
    
    print(f"\n🔗 找到 {len(all_links)} 個相關連結:")
    for i, link in enumerate(all_links[:10]):
        print(f"  {i+1}. {link['text']} - 可見: {link['visible']}")
        print(f"      {link['href'][:80]}")
    
    if len(all_links) > 10:
        print(f"  ... 還有 {len(all_links) - 10} 個連結")
    
    # 診斷 4: 查找左側元素
    left_elements = driver.execute_script("""
        const leftElements = [];
        const elements = document.querySelectorAll('*');
        
        elements.forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.x < 400 && rect.width > 100 && rect.height > 200) {
                const links = el.querySelectorAll('a');
                if (links.length > 0) {
                    leftElements.push({
                        tag: el.tagName,
                        class: el.className,
                        x: Math.round(rect.x),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        linkCount: links.length,
                        hasScroll: el.scrollHeight > el.clientHeight
                    });
                }
            }
        });
        
        return leftElements.slice(0, 10);
    """)
    
    print(f"\n📍 左側元素（前10個）:")
    for i, el in enumerate(left_elements):
        print(f"  {i+1}. {el['tag']}.{el['class'][:30]}")
        print(f"      位置: x={el['x']}, 大小: {el['width']}x{el['height']}")
        print(f"      連結: {el['linkCount']}, 可滾動: {el['hasScroll']}")
    
    # 診斷 5: 截圖
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_name = f'manus_debug_{timestamp}.png'
    driver.save_screenshot(screenshot_name)
    print(f"\n📸 已保存截圖: {screenshot_name}")
    
    # 診斷 6: 嘗試不同的選擇器
    print("\n🔍 嘗試各種選擇器:")
    selectors = [
        'a[href*="/app/"]',
        'a[href*="/share/"]',
        '[class*="conversation"]',
        '[class*="task"]',
        '[class*="item"]',
        '[class*="list"]',
        'aside',
        'nav',
        '[role="navigation"]',
        '[class*="sidebar"]'
    ]
    
    for selector in selectors:
        count = driver.execute_script(f"""
            return document.querySelectorAll('{selector}').length;
        """)
        if count > 0:
            print(f"  '{selector}': {count} 個")
    
    # 保存完整的診斷報告
    with open(f'manus_debug_report_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write("Manus 診斷報告\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"時間: {datetime.now()}\n")
        f.write(f"URL: {basic_info['url']}\n")
        f.write(f"找到的連結數: {len(all_links)}\n\n")
        f.write("所有連結:\n")
        for link in all_links:
            f.write(f"- {link['text']}: {link['href']}\n")
    
    print(f"\n📄 完整報告已保存: manus_debug_report_{timestamp}.txt")
    
    # 讓用戶檢查
    print("\n💡 請檢查：")
    print("1. 截圖中是否能看到左側任務列表？")
    print("2. 上面的連結中是否包含您的任務？")
    print("3. 如果沒有，可能需要特殊操作才能顯示任務列表")
    
except Exception as e:
    print(f"\n❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    input("\n按 Enter 關閉...")
    driver.quit()