#!/usr/bin/env python3
"""
最直接的 Manus 收集方法
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime

print("🚀 開始收集 Manus 任務\n")

# 啟動瀏覽器
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)
driver.maximize_window()

try:
    # 訪問 Manus
    driver.get("https://manus.im/login")
    
    print("請在瀏覽器中：")
    print("1. 登錄 Manus")
    print("2. 進入對話頁面（有左側任務列表）")
    print("3. 把左側任務列表從頭滾到尾")
    print("4. 確保看到了所有任務（五、四、三、二、一等）")
    input("\n全部完成後按 Enter...")
    
    # 直接執行 JavaScript 收集
    result = driver.execute_script("""
        // 找出所有任務
        const all_tasks = [];
        
        // 查找所有包含 /app/ 的連結
        document.querySelectorAll('a[href*="/app/"]').forEach(link => {
            const match = link.href.match(/\\/app\\/([^\\/\\?]+)/);
            if (match) {
                // 向上找包含中文數字的文本
                let text = link.innerText;
                let el = link;
                for (let i = 0; i < 5; i++) {
                    el = el.parentElement;
                    if (!el) break;
                    const t = el.innerText;
                    if (t && (t.includes('一') || t.includes('二') || t.includes('三') || 
                             t.includes('四') || t.includes('五') || t.includes('六') ||
                             t.includes('七') || t.includes('八') || t.includes('九') || 
                             t.includes('十'))) {
                        text = t;
                        break;
                    }
                }
                
                all_tasks.push({
                    id: match[1],
                    text: text.substring(0, 100),
                    url: 'https://manus.im/share/' + match[1] + '?replay=1'
                });
            }
        });
        
        return all_tasks;
    """)
    
    print(f"\n✅ 找到 {len(result)} 個任務\n")
    
    if result:
        # 保存結果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存 JSON
        with open(f'manus_tasks_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        # 保存 URLs
        with open(f'manus_urls_{timestamp}.txt', 'w', encoding='utf-8') as f:
            for i, task in enumerate(result):
                f.write(f"# {i+1}. {task['text']}\n")
                f.write(f"{task['url']}\n\n")
                
        print(f"已保存:")
        print(f"- manus_tasks_{timestamp}.json")
        print(f"- manus_urls_{timestamp}.txt")
        
        # 顯示前幾個
        print("\n前10個任務:")
        for i, task in enumerate(result[:10]):
            print(f"{i+1}. {task['text'][:60]}")
            
        if len(result) > 10:
            print(f"\n... 還有 {len(result) - 10} 個任務")
    else:
        print("❌ 沒找到任務")
        print("\n可能原因：")
        print("1. 左側列表沒有完全加載")
        print("2. 需要點擊展開某些部分")
        print("3. 頁面結構不同")
        
except Exception as e:
    print(f"\n錯誤: {e}")
    
finally:
    input("\n按 Enter 關閉...")
    driver.quit()