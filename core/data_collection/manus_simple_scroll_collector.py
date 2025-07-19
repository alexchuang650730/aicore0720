#!/usr/bin/env python3
"""
Manus 簡單滾動收集器
最簡單的方式：打開頁面，等待用戶滾動，然後一次性收集所有任務
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_manus_tasks():
    """簡單的 Manus 任務收集"""
    logger.info("🚀 Manus 簡單收集器")
    
    # 設置瀏覽器
    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1400, 900)
    
    output_dir = Path("./data/manus_simple")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 登錄
        driver.get("https://manus.im/login")
        logger.info("\n請完成以下操作：")
        logger.info("1. 登錄 Manus")
        logger.info("2. 進入任意對話頁面")
        logger.info("3. 確保左側任務列表可見")
        input("\n準備好後按 Enter...")
        
        logger.info("\n現在請手動操作：")
        logger.info("1. 將左側任務列表滾動到最頂部")
        logger.info("2. 慢慢向下滾動，直到看到所有任務")
        logger.info("3. 確保所有任務都加載出來了")
        logger.info("\n💡 提示：如果任務很多，可能需要滾動多次等待加載")
        
        input("\n完成所有滾動後，按 Enter 開始收集...")
        
        # 等待一下確保頁面穩定
        time.sleep(2)
        
        logger.info("\n🔍 開始收集任務...")
        
        # 收集所有任務
        tasks = driver.execute_script("""
            const tasks = {};
            const chineseNumbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                                   '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                                   '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十',
                                   '三十一', '三十二', '三十三', '三十四', '三十五', '三十六', '三十七', '三十八', '三十九', '四十',
                                   '四十一', '四十二', '四十三', '四十四', '四十五', '四十六', '四十七', '四十八', '四十九', '五十'];
            
            // 收集所有 /app/ 連結
            const links = document.querySelectorAll('a[href*="/app/"]');
            console.log(`找到 ${links.length} 個 app 連結`);
            
            links.forEach((link, index) => {
                const href = link.href;
                const match = href.match(/\\/app\\/([^\\/\\?]+)/);
                
                if (match) {
                    const taskId = match[1];
                    
                    // 獲取任務信息
                    let taskText = '';
                    let taskNumber = '';
                    
                    // 方法1: 從連結文本獲取
                    taskText = link.textContent || link.innerText || '';
                    
                    // 方法2: 從父元素獲取更完整的文本
                    let parent = link.parentElement;
                    let depth = 0;
                    while (parent && depth < 5) {
                        const parentText = parent.textContent || parent.innerText || '';
                        
                        // 檢查中文數字
                        for (const num of chineseNumbers) {
                            if (parentText.includes(num)) {
                                taskNumber = num;
                                taskText = parentText;
                                break;
                            }
                        }
                        
                        if (taskNumber) break;
                        
                        // 更長的文本可能更完整
                        if (parentText.length > taskText.length && parentText.length < 300) {
                            taskText = parentText;
                        }
                        
                        parent = parent.parentElement;
                        depth++;
                    }
                    
                    // 清理文本
                    taskText = taskText.replace(/\\s+/g, ' ').trim();
                    
                    tasks[taskId] = {
                        id: taskId,
                        title: taskText.substring(0, 200),
                        href: href,
                        number: taskNumber,
                        index: Object.keys(tasks).length
                    };
                }
            });
            
            // 返回結果和調試信息
            return {
                tasks: tasks,
                debug: {
                    totalLinks: links.length,
                    totalTasks: Object.keys(tasks).length,
                    sampleTitles: Object.values(tasks).slice(0, 5).map(t => t.title.substring(0, 50))
                }
            };
        """)
        
        logger.info(f"\n調試信息:")
        logger.info(f"  找到連結: {tasks['debug']['totalLinks']}")
        logger.info(f"  提取任務: {tasks['debug']['totalTasks']}")
        
        all_tasks = tasks['tasks']
        
        if not all_tasks:
            logger.error("未找到任何任務！")
            logger.info("\n可能的原因：")
            logger.info("1. 左側任務列表未完全加載")
            logger.info("2. 頁面結構不同")
            logger.info("3. 需要更多時間加載")
            
            # 保存頁面源碼用於調試
            with open(output_dir / "debug_page.html", 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info(f"\n已保存頁面源碼: {output_dir}/debug_page.html")
            
        else:
            logger.info(f"\n✅ 成功收集 {len(all_tasks)} 個任務！")
            
            # 轉換為列表並排序
            task_list = list(all_tasks.values())
            
            # 按中文數字排序
            chinese_num_order = {
                '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
                '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
                '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
                '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
                '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34, '三十五': 35,
                '三十六': 36, '三十七': 37, '三十八': 38, '三十九': 39, '四十': 40,
                '四十一': 41, '四十二': 42, '四十三': 43, '四十四': 44, '四十五': 45,
                '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50
            }
            
            def sort_key(task):
                num = task.get('number', '')
                return chinese_num_order.get(num, 999)
            
            task_list.sort(key=sort_key)
            
            # 保存結果
            # 1. JSON 格式
            tasks_file = output_dir / f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total': len(task_list),
                    'tasks': task_list,
                    'collected_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
                
            # 2. Replay URLs
            urls_file = output_dir / f"replay_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(urls_file, 'w', encoding='utf-8') as f:
                f.write(f"# Manus 任務列表 - {len(task_list)} 個任務\n")
                f.write(f"# 收集時間: {datetime.now().isoformat()}\n")
                f.write("#" * 70 + "\n\n")
                
                for i, task in enumerate(task_list):
                    number = task.get('number', '')
                    title = task.get('title', '').replace('\n', ' ')[:80]
                    
                    f.write(f"# {i+1}. {number} - {title}\n")
                    f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
                    
            logger.info(f"\n💾 已保存:")
            logger.info(f"  任務數據: {tasks_file}")
            logger.info(f"  Replay URLs: {urls_file}")
            
            # 顯示統計
            numbered_tasks = [t for t in task_list if t.get('number')]
            logger.info(f"\n📊 統計:")
            logger.info(f"  總任務數: {len(task_list)}")
            logger.info(f"  帶數字標記: {len(numbered_tasks)}")
            
            # 顯示前幾個任務
            logger.info(f"\n📋 任務示例:")
            for i, task in enumerate(task_list[:10]):
                number = task.get('number', '')
                title = task.get('title', '').replace('\n', ' ')[:50]
                logger.info(f"  {i+1}. {number} - {title}")
                
            if len(task_list) > 10:
                logger.info(f"  ... 還有 {len(task_list) - 10} 個任務")
                
    except Exception as e:
        logger.error(f"發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        input("\n按 Enter 關閉瀏覽器...")
        driver.quit()


if __name__ == "__main__":
    print("""
    🌟 Manus 簡單滾動收集器
    
    最簡單的收集方式：
    1. 手動滾動左側任務列表
    2. 確保所有任務都加載出來
    3. 一次性收集所有可見任務
    
    無需複雜操作，只要滾動完成即可！
    """)
    
    collect_manus_tasks()