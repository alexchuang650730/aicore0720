#!/usr/bin/env python3
"""
Manus 手動滾動自動收集器
你手動滾動，腳本自動收集
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
from pathlib import Path
from datetime import datetime

print("🤖 Manus 手動滾動自動收集器\n")

# 設置輸出目錄
output_dir = Path("./data/manus_manual_scroll")
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
    
    print("步驟 1: 登錄並進入任務頁面")
    print("  - 登錄 Manus")
    print("  - 進入有左側任務列表的頁面")
    print("  - 確保能看到任務列表")
    input("\n準備好後按 Enter...")
    
    print("\n步驟 2: 滾動左側任務列表到最頂部")
    input("完成後按 Enter...")
    
    print("\n步驟 3: 開始收集")
    print("現在我會每隔2秒自動收集一次當前可見的任務")
    print("請你慢慢向下滾動左側任務列表")
    print("看到底部後，等待5秒讓我完成收集")
    print("\n按 Ctrl+C 停止收集\n")
    
    input("準備好開始滾動了嗎？按 Enter 開始自動收集...")
    
    print("\n🔄 開始自動收集（請開始滾動左側列表）...\n")
    
    round_count = 0
    last_count = 0
    no_new_rounds = 0
    
    try:
        while True:
            round_count += 1
            
            # 收集當前頁面上的所有任務
            current_tasks = driver.execute_script("""
                const tasks = {};
                const numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                               '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十',
                               '三十一', '三十二', '三十三', '三十四', '三十五', '三十六', '三十七', '三十八', '三十九', '四十',
                               '四十一', '四十二', '四十三', '四十四', '四十五', '四十六', '四十七', '四十八', '四十九', '五十'];
                
                // 收集所有任務連結
                const links = document.querySelectorAll('a[href*="/share/"], a[href*="/app/"]');
                
                links.forEach(link => {
                    const href = link.href;
                    let id = '';
                    
                    // 提取 ID
                    if (href.includes('/share/')) {
                        const match = href.match(/\\/share\\/([^\\/\\?]+)/);
                        if (match) id = match[1];
                    } else if (href.includes('/app/')) {
                        const match = href.match(/\\/app\\/([^\\/\\?]+)/);
                        if (match) id = match[1];
                    }
                    
                    if (id && !tasks[id]) {
                        // 獲取任務文本
                        let text = '';
                        let number = '';
                        
                        // 從連結開始向上查找
                        let element = link;
                        for (let depth = 0; depth < 5 && element; depth++) {
                            const content = element.textContent || '';
                            
                            // 查找中文數字
                            for (const num of numbers) {
                                if (content.includes(num)) {
                                    number = num;
                                    text = content;
                                    break;
                                }
                            }
                            
                            // 如果找到了數字就停止
                            if (number) break;
                            
                            // 保存最長的文本（但不要太長）
                            if (content.length > text.length && content.length < 300) {
                                text = content;
                            }
                            
                            element = element.parentElement;
                        }
                        
                        // 如果還沒有文本，使用連結文本
                        if (!text) {
                            text = link.textContent || link.innerText || '';
                        }
                        
                        tasks[id] = {
                            id: id,
                            text: text.trim().substring(0, 200),
                            number: number,
                            shareUrl: `https://manus.im/share/${id}?replay=1`,
                            href: href
                        };
                    }
                });
                
                return tasks;
            """)
            
            # 更新收集的任務
            new_count = 0
            for task_id, task_info in current_tasks.items():
                if task_id not in collected_tasks:
                    collected_tasks[task_id] = task_info
                    new_count += 1
            
            current_total = len(collected_tasks)
            
            # 顯示進度
            if round_count % 2 == 0 or new_count > 0:  # 每4秒或有新任務時顯示
                print(f"\r收集輪次: {round_count} | 新增: {new_count} | 總計: {current_total} 個任務", end='', flush=True)
            
            # 如果有新任務，顯示詳情
            if new_count > 0:
                print()  # 換行
                recent_tasks = list(current_tasks.values())[-min(3, new_count):]
                for task in recent_tasks:
                    if task['id'] in [t_id for t_id, t in current_tasks.items() if t_id not in list(collected_tasks.keys())[:-new_count]]:
                        number = task.get('number', '')
                        text = task.get('text', '').replace('\n', ' ')[:50]
                        print(f"  + {number} {text}")
                no_new_rounds = 0
            else:
                no_new_rounds += 1
            
            # 如果連續10輪沒有新任務，提示用戶
            if no_new_rounds == 10:
                print("\n\n💡 提示：已經10輪沒有新任務了")
                print("如果已經滾動到底部，可以按 Ctrl+C 結束收集")
                no_new_rounds = 0
            
            # 等待2秒
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n✋ 收集已停止")
    
    print(f"\n\n✅ 收集完成！共找到 {len(collected_tasks)} 個任務")
    
    # 保存結果
    if collected_tasks:
        # 轉換為列表並排序
        task_list = list(collected_tasks.values())
        
        # 中文數字排序
        chinese_order = {}
        numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                  '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十',
                  '三十一', '三十二', '三十三', '三十四', '三十五', '三十六', '三十七', '三十八', '三十九', '四十',
                  '四十一', '四十二', '四十三', '四十四', '四十五', '四十六', '四十七', '四十八', '四十九', '五十']
        
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
        numbered_tasks = [t for t in task_list if t.get('number')]
        print(f"\n📊 統計:")
        print(f"  總任務數: {len(task_list)}")
        print(f"  帶數字標記: {len(numbered_tasks)}")
        
        # 顯示數字分布
        if numbered_tasks:
            print(f"\n📋 數字分布:")
            number_counts = {}
            for task in numbered_tasks:
                num = task['number']
                number_counts[num] = number_counts.get(num, 0) + 1
            
            for num in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']:
                if num in number_counts:
                    print(f"  {num}: {number_counts[num]} 個")
        
        # 顯示前幾個任務
        print(f"\n📋 前10個任務:")
        for i, task in enumerate(task_list[:10]):
            number = task.get('number', '')
            text = task.get('text', '').replace('\n', ' ')[:60]
            print(f"  {i+1}. {number} - {text}")
        
        if len(task_list) > 10:
            print(f"\n  ... 還有 {len(task_list) - 10} 個任務")
            
            # 也顯示最後幾個
            print(f"\n📋 最後5個任務:")
            for i, task in enumerate(task_list[-5:], len(task_list) - 4):
                number = task.get('number', '')
                text = task.get('text', '').replace('\n', ' ')[:60]
                print(f"  {i}. {number} - {text}")
    
except Exception as e:
    print(f"\n❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    input("\n按 Enter 關閉瀏覽器...")
    driver.quit()

print("\n🎉 完成！")