#!/usr/bin/env python3
"""
Manus 深度診斷工具
徹底分析頁面結構，找出任務列表的實現方式
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime

print("🔬 Manus 深度診斷工具\n")

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
    print("2. 進入有左側任務列表的頁面")
    print("3. 確保能看到多個任務（一、二、三、四、五等）")
    print("4. 如果需要點擊展開，請展開所有任務")
    input("\n完成後按 Enter 開始深度診斷...")
    
    print("\n" + "="*70)
    print("開始深度診斷...")
    print("="*70 + "\n")
    
    # 診斷1: 檢查 iframe
    iframe_check = driver.execute_script("""
        const iframes = document.querySelectorAll('iframe');
        return {
            count: iframes.length,
            sources: Array.from(iframes).map(f => f.src)
        };
    """)
    
    print("1️⃣ IFRAME 檢查:")
    print(f"   找到 {iframe_check['count']} 個 iframe")
    if iframe_check['count'] > 0:
        print("   ⚠️ 檢測到 iframe，任務列表可能在 iframe 中！")
        for i, src in enumerate(iframe_check['sources']):
            print(f"   iframe {i+1}: {src}")
    
    # 診斷2: 查找包含中文數字的元素
    print("\n2️⃣ 中文數字元素分析:")
    number_elements = driver.execute_script("""
        const numbers = ['一', '二', '三', '四', '五'];
        const results = {};
        
        numbers.forEach(num => {
            const elements = Array.from(document.querySelectorAll('*')).filter(el => {
                const text = el.textContent || '';
                // 只包含這個數字，且文本不太長
                return text.includes(num) && text.length < 200 && el.children.length < 5;
            });
            
            results[num] = elements.map(el => {
                // 查找元素內的可點擊元素
                const clickables = el.querySelectorAll('a, button, [onclick], [role="button"], [class*="clickable"], [class*="item"]');
                const rect = el.getBoundingClientRect();
                
                return {
                    tag: el.tagName,
                    class: el.className,
                    text: el.textContent.substring(0, 100),
                    x: Math.round(rect.x),
                    y: Math.round(rect.y),
                    clickableCount: clickables.length,
                    hasOnClick: !!el.onclick,
                    role: el.getAttribute('role'),
                    cursor: window.getComputedStyle(el).cursor
                };
            }).slice(0, 3); // 每個數字最多3個結果
        });
        
        return results;
    """)
    
    for num, elements in number_elements.items():
        if elements:
            print(f"\n   '{num}' 找到 {len(elements)} 個元素:")
            for el in elements[:2]:
                print(f"      - {el['tag']}.{el['class'][:30]} at ({el['x']},{el['y']})")
                print(f"        文本: {el['text'][:50]}")
                print(f"        可點擊元素: {el['clickableCount']}, cursor: {el['cursor']}")
    
    # 診斷3: 查找左側的可點擊元素
    print("\n3️⃣ 左側可點擊元素分析:")
    left_clickables = driver.execute_script("""
        const clickables = [];
        const selectors = [
            '[onclick]',
            '[role="button"]',
            '[class*="item"][class*="click"]',
            '[class*="task"]',
            '[class*="conversation"]',
            '[style*="cursor: pointer"]',
            'div[class*="item"]:has(span)',
            'li:has(span)'
        ];
        
        selectors.forEach(selector => {
            try {
                document.querySelectorAll(selector).forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.x < 400 && rect.width > 50) {
                        const text = el.textContent || '';
                        clickables.push({
                            selector: selector,
                            tag: el.tagName,
                            class: el.className.substring(0, 100),
                            text: text.substring(0, 80),
                            x: Math.round(rect.x),
                            width: Math.round(rect.width),
                            hasNumber: /[一二三四五六七八九十]/.test(text)
                        });
                    }
                });
            } catch(e) {}
        });
        
        // 去重並排序
        const unique = {};
        clickables.forEach(c => {
            const key = c.tag + c.class + c.text;
            if (!unique[key] || c.hasNumber) {
                unique[key] = c;
            }
        });
        
        return Object.values(unique).slice(0, 20);
    """)
    
    if left_clickables:
        print(f"   找到 {len(left_clickables)} 個左側可點擊元素:")
        for i, el in enumerate(left_clickables[:10]):
            if el['hasNumber']:
                print(f"   ⭐ {el['tag']} - {el['text'][:50]}")
                print(f"      選擇器: {el['selector']}")
                print(f"      位置: x={el['x']}, 寬度={el['width']}")
    
    # 診斷4: 查找所有類型的連結
    print("\n4️⃣ 連結類型分析:")
    link_analysis = driver.execute_script("""
        const links = {
            standard: [],
            dataAttr: [],
            jsRoutes: []
        };
        
        // 標準連結
        document.querySelectorAll('a').forEach(a => {
            if (a.href) {
                links.standard.push({
                    href: a.href,
                    text: a.textContent.substring(0, 50)
                });
            }
        });
        
        // data 屬性
        document.querySelectorAll('[data-href], [data-url], [data-link], [data-route]').forEach(el => {
            links.dataAttr.push({
                tag: el.tagName,
                dataAttrs: Object.keys(el.dataset),
                text: el.textContent.substring(0, 50)
            });
        });
        
        // JavaScript 路由
        document.querySelectorAll('[onclick*="navigate"], [onclick*="route"], [onclick*="go"]').forEach(el => {
            links.jsRoutes.push({
                tag: el.tagName,
                onclick: el.onclick ? el.onclick.toString().substring(0, 100) : 'has onclick',
                text: el.textContent.substring(0, 50)
            });
        });
        
        return {
            standardCount: links.standard.length,
            dataAttrCount: links.dataAttr.length,
            jsRoutesCount: links.jsRoutes.length,
            samples: {
                standard: links.standard.slice(0, 3),
                dataAttr: links.dataAttr.slice(0, 3),
                jsRoutes: links.jsRoutes.slice(0, 3)
            }
        };
    """)
    
    print(f"   標準 <a> 連結: {link_analysis['standardCount']} 個")
    print(f"   Data 屬性連結: {link_analysis['dataAttrCount']} 個")
    print(f"   JavaScript 路由: {link_analysis['jsRoutesCount']} 個")
    
    # 診斷5: React/Vue/Angular 檢測
    print("\n5️⃣ 前端框架檢測:")
    framework_check = driver.execute_script("""
        return {
            react: !!(window.React || document.querySelector('[data-reactroot]') || window.__REACT_DEVTOOLS_GLOBAL_HOOK__),
            vue: !!(window.Vue || document.querySelector('[data-v-]') || window.__VUE__),
            angular: !!(window.ng || document.querySelector('[ng-version]')),
            jquery: !!window.jQuery,
            hasDataBinding: !!document.querySelector('[v-for], [ng-repeat], [*ngFor]')
        };
    """)
    
    for framework, detected in framework_check.items():
        if detected:
            print(f"   ✅ {framework} 檢測到")
    
    # 診斷6: 事件監聽器
    print("\n6️⃣ 事件監聽器分析:")
    event_check = driver.execute_script("""
        const leftElements = Array.from(document.querySelectorAll('*')).filter(el => {
            const rect = el.getBoundingClientRect();
            return rect.x < 400 && rect.width > 50 && rect.width < 400;
        });
        
        let hasClickListeners = 0;
        leftElements.forEach(el => {
            // 這個方法不完美，但可以給出提示
            if (el.onclick || el.getAttribute('onclick')) {
                hasClickListeners++;
            }
        });
        
        return {
            leftElementCount: leftElements.length,
            withClickHandlers: hasClickListeners
        };
    """)
    
    print(f"   左側元素總數: {event_check['leftElementCount']}")
    print(f"   有點擊處理的: {event_check['withClickHandlers']}")
    
    # 保存完整診斷報告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 截圖
    screenshot_file = f'manus_deep_diagnostic_{timestamp}.png'
    driver.save_screenshot(screenshot_file)
    print(f"\n📸 已保存截圖: {screenshot_file}")
    
    # HTML 源碼
    with open(f'manus_page_source_{timestamp}.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print(f"📄 已保存頁面源碼: manus_page_source_{timestamp}.html")
    
    print("\n" + "="*70)
    print("診斷完成！")
    print("="*70)
    
    print("\n💡 下一步建議：")
    print("1. 如果檢測到 iframe，需要切換到 iframe 內收集")
    print("2. 如果是 React/Vue 應用，可能需要觸發點擊事件")
    print("3. 檢查截圖和源碼，看任務列表的實現方式")
    print("4. 根據找到的選擇器，創建專門的收集器")
    
except Exception as e:
    print(f"\n❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    input("\n按 Enter 關閉...")
    driver.quit()