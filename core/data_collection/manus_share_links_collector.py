#!/usr/bin/env python3
"""
Manus Share 連結收集器
直接收集所有 share 連結，無論是否可見
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
from datetime import datetime
from pathlib import Path

print("🎯 Manus Share 連結收集器\n")

# 設置輸出目錄
output_dir = Path("./data/manus_share_links")
output_dir.mkdir(parents=True, exist_ok=True)

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
    print("2. 進入任務頁面")
    print("3. 如果左側任務列表是隱藏的，請點擊按鈕打開它")
    print("4. 滾動左側列表，確保加載了所有任務")
    input("\n完成後按 Enter...")
    
    print("\n🔍 開始收集...\n")
    
    # 方法1: 收集所有 share 連結（包括隱藏的）
    share_links = driver.execute_script("""
        const tasks = [];
        const seen = new Set();
        
        // 查找所有 share 連結
        document.querySelectorAll('a[href*="/share/"]').forEach((link, index) => {
            const href = link.href;
            const match = href.match(/\\/share\\/([^\\/\\?]+)/);
            
            if (match && !seen.has(match[1])) {
                seen.add(match[1]);
                
                // 獲取任務文本
                let text = link.innerText || link.textContent || '';
                
                // 向上查找包含中文數字的文本
                let element = link;
                let number = '';
                const numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                               '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十'];
                
                for (let i = 0; i < 5 && element; i++) {
                    const content = element.textContent || '';
                    for (const num of numbers) {
                        if (content.includes(num)) {
                            number = num;
                            text = content;
                            break;
                        }
                    }
                    if (number) break;
                    element = element.parentElement;
                }
                
                tasks.push({
                    id: match[1],
                    href: href,
                    text: text.substring(0, 200).trim(),
                    number: number,
                    visible: link.offsetParent !== null,
                    index: tasks.length
                });
            }
        });
        
        return tasks;
    """)
    
    print(f"✅ 找到 {len(share_links)} 個 share 連結\n")
    
    # 方法2: 查找包含中文數字的元素中的連結
    numbered_tasks = driver.execute_script("""
        const tasks = [];
        const numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                       '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                       '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十'];
        
        // 查找所有包含中文數字的元素
        numbers.forEach(num => {
            const elements = Array.from(document.querySelectorAll('*')).filter(el => {
                const text = el.textContent || '';
                return text.includes(num) && text.length < 500;
            });
            
            elements.forEach(el => {
                // 查找元素內的連結
                const links = el.querySelectorAll('a[href*="/share/"], a[href*="/app/"]');
                links.forEach(link => {
                    const href = link.href;
                    let id = '';
                    
                    if (href.includes('/share/')) {
                        const match = href.match(/\\/share\\/([^\\/\\?]+)/);
                        if (match) id = match[1];
                    } else if (href.includes('/app/')) {
                        const match = href.match(/\\/app\\/([^\\/\\?]+)/);
                        if (match) id = match[1];
                    }
                    
                    if (id) {
                        tasks.push({
                            id: id,
                            number: num,
                            text: el.textContent.substring(0, 200).trim(),
                            shareUrl: `https://manus.im/share/${id}?replay=1`,
                            originalHref: href
                        });
                    }
                });
            });
        });
        
        // 去重
        const unique = {};
        tasks.forEach(task => {
            if (!unique[task.id] || task.number) {
                unique[task.id] = task;
            }
        });
        
        return Object.values(unique);
    """)
    
    print(f"✅ 找到 {len(numbered_tasks)} 個帶數字標記的任務\n")
    
    # 合併結果
    all_tasks = {}
    
    # 先添加 share 連結
    for task in share_links:
        all_tasks[task['id']] = {
            'id': task['id'],
            'text': task['text'],
            'number': task['number'],
            'shareUrl': task['href'] if '?replay=1' in task['href'] else task['href'] + '?replay=1',
            'visible': task['visible']
        }
    
    # 添加帶數字的任務（優先使用帶數字的版本）
    for task in numbered_tasks:
        if task['id'] in all_tasks:
            # 如果已存在但沒有數字，更新數字
            if not all_tasks[task['id']].get('number') and task['number']:
                all_tasks[task['id']]['number'] = task['number']
                all_tasks[task['id']]['text'] = task['text']
        else:
            all_tasks[task['id']] = task
    
    # 轉換為列表並排序
    task_list = list(all_tasks.values())
    
    # 中文數字排序
    chinese_order = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
        '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
        '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
        '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30
    }
    
    def sort_key(task):
        num = task.get('number', '')
        return chinese_order.get(num, 999)
    
    task_list.sort(key=sort_key)
    
    # 保存結果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON 文件
    json_file = output_dir / f'manus_tasks_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(task_list),
            'tasks': task_list,
            'collected_at': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    # Replay URLs 文件
    urls_file = output_dir / f'replay_urls_{timestamp}.txt'
    with open(urls_file, 'w', encoding='utf-8') as f:
        f.write(f"# Manus 任務列表 - {len(task_list)} 個任務\n")
        f.write(f"# 收集時間: {datetime.now().isoformat()}\n")
        f.write("#" * 70 + "\n\n")
        
        for i, task in enumerate(task_list):
            number = task.get('number', '')
            text = task.get('text', '').replace('\n', ' ')[:80]
            
            if number:
                f.write(f"# {i+1}. {number} - {text}\n")
            else:
                f.write(f"# {i+1}. {text}\n")
            f.write(f"{task.get('shareUrl', '')}\n\n")
    
    print(f"💾 已保存:")
    print(f"  任務數據: {json_file}")
    print(f"  Replay URLs: {urls_file}")
    
    # 顯示統計
    print(f"\n📊 統計:")
    print(f"  總任務數: {len(task_list)}")
    print(f"  帶數字標記: {len([t for t in task_list if t.get('number')])}")
    print(f"  可見任務: {len([t for t in task_list if t.get('visible')])}")
    
    # 顯示任務樣本
    print(f"\n📋 任務樣本:")
    for i, task in enumerate(task_list[:10]):
        number = task.get('number', '')
        text = task.get('text', '').replace('\n', ' ')[:60]
        visible = '✓' if task.get('visible') else '✗'
        print(f"  {i+1}. [{visible}] {number} - {text}")
    
    if len(task_list) > 10:
        print(f"\n  ... 還有 {len(task_list) - 10} 個任務")
    
    # 檢查是否需要特殊操作
    if all(not t.get('visible') for t in task_list):
        print("\n⚠️ 注意：所有任務都是不可見的")
        print("可能需要：")
        print("1. 點擊側邊欄按鈕")
        print("2. 展開任務列表")
        print("3. 或者任務在其他頁面")
    
except Exception as e:
    print(f"\n❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    input("\n按 Enter 關閉...")
    driver.quit()