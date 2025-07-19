#!/usr/bin/env python3
"""
Manus 滾動容器收集器
專門處理需要滾動才能看到所有任務的情況
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
from pathlib import Path
from datetime import datetime

print("📜 Manus 滾動容器收集器\n")

# 設置輸出目錄
output_dir = Path("./data/manus_scroll_collection")
output_dir.mkdir(parents=True, exist_ok=True)

# 啟動瀏覽器
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)
driver.maximize_window()

collected_tasks = {}

try:
    # 訪問 Manus
    driver.get("https://manus.im/login")
    
    print("請完成以下操作：")
    print("1. 登錄 Manus")
    print("2. 進入任務頁面（確保左側任務列表可見）")
    print("3. 將左側任務列表滾動到最頂部")
    input("\n準備好後按 Enter...")
    
    print("\n🔍 開始收集任務...\n")
    
    # 第一步：找到可滾動的容器
    print("正在查找可滾動容器...")
    
    scrollable_info = driver.execute_script("""
        // 查找所有可能的滾動容器
        const candidates = [];
        const elements = document.querySelectorAll('*');
        
        elements.forEach(el => {
            const rect = el.getBoundingClientRect();
            // 檢查：在左側、有溢出內容、包含連結
            if (rect.x < 400 && rect.width > 100 && rect.width < 500 && 
                el.scrollHeight > el.clientHeight && 
                el.querySelectorAll('a').length > 0) {
                
                candidates.push({
                    tag: el.tagName,
                    class: el.className,
                    id: el.id,
                    x: rect.x,
                    width: rect.width,
                    height: rect.height,
                    scrollHeight: el.scrollHeight,
                    clientHeight: el.clientHeight,
                    linkCount: el.querySelectorAll('a[href*="/share/"], a[href*="/app/"]').length
                });
            }
        });
        
        // 找最可能的（連結最多的）
        candidates.sort((a, b) => b.linkCount - a.linkCount);
        
        if (candidates.length > 0) {
            // 標記找到的容器
            const selector = candidates[0].id ? `#${candidates[0].id}` : 
                           candidates[0].class ? `.${candidates[0].class.split(' ')[0]}` : 
                           candidates[0].tag;
            
            const container = document.querySelector(selector);
            if (container) {
                container.style.border = '3px solid lime';
                window.__scrollContainer = container;
                return {
                    found: true,
                    info: candidates[0],
                    selector: selector
                };
            }
        }
        
        return { found: false };
    """)
    
    if not scrollable_info['found']:
        print("❌ 未找到可滾動容器")
        print("\n嘗試手動標記...")
        print("請在瀏覽器控制台執行：")
        print("1. 右鍵點擊左側任務列表")
        print("2. 選擇'檢查'")
        print("3. 在控制台輸入: window.__scrollContainer = $0")
        input("\n完成後按 Enter...")
    else:
        print(f"✅ 找到滾動容器: {scrollable_info['info']}")
        print(f"   大小: {scrollable_info['info']['width']}x{scrollable_info['info']['height']}")
        print(f"   可滾動高度: {scrollable_info['info']['scrollHeight']}")
        print(f"   包含連結: {scrollable_info['info']['linkCount']}")
    
    # 第二步：滾動收集
    print("\n開始滾動收集...")
    
    scroll_round = 0
    no_new_count = 0
    last_position = 0
    
    while no_new_count < 5:  # 連續5次沒有新任務就停止
        scroll_round += 1
        print(f"\n第 {scroll_round} 輪收集...")
        
        # 收集當前可見的任務
        current_tasks = driver.execute_script("""
            const tasks = {};
            const numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                           '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                           '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十',
                           '三十一', '三十二', '三十三', '三十四', '三十五', '三十六', '三十七', '三十八', '三十九', '四十'];
            
            // 收集所有連結
            document.querySelectorAll('a[href*="/share/"], a[href*="/app/"]').forEach(link => {
                let id = '';
                const href = link.href;
                
                if (href.includes('/share/')) {
                    const match = href.match(/\\/share\\/([^\\/\\?]+)/);
                    if (match) id = match[1];
                } else if (href.includes('/app/')) {
                    const match = href.match(/\\/app\\/([^\\/\\?]+)/);
                    if (match) id = match[1];
                }
                
                if (id) {
                    // 查找包含的文本和數字
                    let text = link.textContent || '';
                    let number = '';
                    
                    // 向上查找包含中文數字的元素
                    let el = link;
                    for (let i = 0; i < 5 && el; i++) {
                        const content = el.textContent || '';
                        for (const num of numbers) {
                            if (content.includes(num)) {
                                number = num;
                                text = content;
                                break;
                            }
                        }
                        if (number) break;
                        el = el.parentElement;
                    }
                    
                    tasks[id] = {
                        id: id,
                        text: text.substring(0, 200).trim(),
                        number: number,
                        shareUrl: `https://manus.im/share/${id}?replay=1`,
                        visible: link.offsetParent !== null
                    };
                }
            });
            
            return tasks;
        """)
        
        # 統計新任務
        new_count = 0
        for task_id, task_info in current_tasks.items():
            if task_id not in collected_tasks:
                collected_tasks[task_id] = task_info
                new_count += 1
        
        print(f"  新增: {new_count} 個任務")
        print(f"  總計: {len(collected_tasks)} 個任務")
        
        if new_count == 0:
            no_new_count += 1
        else:
            no_new_count = 0
            # 顯示最新收集的任務
            recent = list(current_tasks.values())[-3:]
            for task in recent:
                if task['number']:
                    print(f"    - {task['number']} {task['text'][:40]}")
        
        # 滾動容器
        scroll_result = driver.execute_script("""
            if (!window.__scrollContainer) {
                // 如果沒有標記容器，嘗試滾動所有可能的容器
                const containers = document.querySelectorAll('div[style*="overflow"], aside, nav, [class*="sidebar"], [class*="list"]');
                let scrolled = false;
                
                containers.forEach(container => {
                    if (container.scrollHeight > container.clientHeight) {
                        const before = container.scrollTop;
                        container.scrollTop = container.scrollTop + container.clientHeight * 0.8;
                        if (container.scrollTop > before) scrolled = true;
                    }
                });
                
                // 也滾動主窗口
                window.scrollBy(0, 300);
                
                return { scrolled: scrolled, method: 'auto' };
            } else {
                // 使用標記的容器
                const container = window.__scrollContainer;
                const before = container.scrollTop;
                const scrollHeight = container.scrollHeight;
                const clientHeight = container.clientHeight;
                
                // 滾動80%的可視高度
                container.scrollTop = before + clientHeight * 0.8;
                
                const after = container.scrollTop;
                const atBottom = (after + clientHeight) >= (scrollHeight - 10);
                
                return {
                    scrolled: after > before,
                    before: before,
                    after: after,
                    atBottom: atBottom,
                    method: 'marked'
                };
            }
        """)
        
        print(f"  滾動: {scroll_result.get('method', 'unknown')} 方法")
        
        if scroll_result.get('atBottom'):
            print("  ✅ 已到達底部")
            if no_new_count >= 2:
                break
        
        # 等待加載
        time.sleep(1.5)
        
        # 安全限制
        if scroll_round > 50:
            print("\n⚠️ 已滾動50次，停止收集")
            break
    
    print(f"\n✅ 收集完成！共找到 {len(collected_tasks)} 個任務")
    
    # 保存結果
    if collected_tasks:
        # 轉換為列表並排序
        task_list = list(collected_tasks.values())
        
        # 中文數字排序
        chinese_order = {}
        numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                  '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十',
                  '三十一', '三十二', '三十三', '三十四', '三十五', '三十六', '三十七', '三十八', '三十九', '四十']
        
        for i, num in enumerate(numbers):
            chinese_order[num] = i + 1
        
        def sort_key(task):
            return chinese_order.get(task.get('number', ''), 999)
        
        task_list.sort(key=sort_key)
        
        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON 文件
        json_file = output_dir / f'tasks_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(task_list),
                'tasks': task_list,
                'collected_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # Replay URLs
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
                f.write(f"{task['shareUrl']}\n\n")
        
        print(f"\n💾 已保存:")
        print(f"  任務數據: {json_file}")
        print(f"  Replay URLs: {urls_file}")
        
        # 顯示統計
        print(f"\n📊 統計:")
        print(f"  總任務數: {len(task_list)}")
        print(f"  帶數字標記: {len([t for t in task_list if t.get('number')])}")
        
        # 顯示樣本
        print(f"\n📋 任務樣本:")
        for i, task in enumerate(task_list[:10]):
            number = task.get('number', '')
            text = task.get('text', '').replace('\n', ' ')[:50]
            print(f"  {i+1}. {number} - {text}")
        
        if len(task_list) > 10:
            print(f"\n  ... 還有 {len(task_list) - 10} 個任務")
    
except Exception as e:
    print(f"\n❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    input("\n按 Enter 關閉...")
    driver.quit()