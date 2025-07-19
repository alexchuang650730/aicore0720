#!/usr/bin/env python3
"""
Manus 精確側邊欄收集器
基於實際界面結構，精確定位並滾動左側任務列表
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
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManusPreciseSidebarCollector:
    """精確定位並收集左側任務列表"""
    
    def __init__(self):
        self.driver = None
        self.output_dir = Path("./data/manus_precise_collection")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collected_tasks = {}
        
    def setup_browser(self):
        """設置瀏覽器"""
        options = ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)
        # 設置較大的窗口以確保側邊欄可見
        self.driver.set_window_size(1400, 900)
        logger.info("✅ 瀏覽器已啟動")
        
    def collect_all_tasks(self):
        """收集所有任務"""
        logger.info("🚀 開始精確收集 Manus 任務列表")
        
        self.setup_browser()
        
        try:
            # 登錄
            self.driver.get("https://manus.im/login")
            logger.info("\n請登錄並進入對話頁面...")
            logger.info("確保左側任務列表可見（有'五'、'四'、'三'等標記）")
            input("\n準備好後按 Enter...")
            
            # 截圖當前狀態
            self.driver.save_screenshot(str(self.output_dir / "initial.png"))
            
            # 精確定位左側任務列表
            sidebar_info = self._locate_task_sidebar()
            
            if sidebar_info['found']:
                logger.info(f"\n✅ 找到左側任務列表！")
                logger.info(f"  位置: ({sidebar_info['x']}, {sidebar_info['y']})")
                logger.info(f"  大小: {sidebar_info['width']}x{sidebar_info['height']}")
                logger.info(f"  初始任務數: {sidebar_info['taskCount']}")
                
                # 開始收集
                self._collect_all_tasks_with_scroll()
                
                # 保存結果
                if self.collected_tasks:
                    self._save_final_results()
                else:
                    logger.error("未收集到任務")
            else:
                logger.error("未找到左側任務列表")
                self._try_alternative_methods()
                
        except Exception as e:
            logger.error(f"錯誤: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            input("\n按 Enter 關閉...")
            self.driver.quit()
            
    def _locate_task_sidebar(self):
        """精確定位左側任務列表"""
        locate_script = """
        // 查找包含中文數字的任務列表
        const chineseNumbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                               '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十'];
        
        let taskSidebar = null;
        let maxTasks = 0;
        
        // 方法1: 查找包含最多中文數字的容器
        const allElements = document.querySelectorAll('*');
        
        for (const element of allElements) {
            const rect = element.getBoundingClientRect();
            
            // 必須在左側（x < 500），有合適的寬度（150-400）和高度（> 300）
            if (rect.x < 500 && rect.width > 150 && rect.width < 400 && rect.height > 300) {
                // 計算包含的中文數字任務
                let taskCount = 0;
                const text = element.innerText || '';
                
                for (const num of chineseNumbers) {
                    if (text.includes(num)) {
                        taskCount++;
                    }
                }
                
                // 同時檢查是否有 app 連結
                const appLinks = element.querySelectorAll('a[href*="/app/"]');
                
                if (taskCount > 0 && appLinks.length > 0 && taskCount > maxTasks) {
                    maxTasks = taskCount;
                    taskSidebar = element;
                }
            }
        }
        
        // 方法2: 如果方法1失敗，查找左側包含最多 app 連結的容器
        if (!taskSidebar) {
            let maxLinks = 0;
            
            for (const element of allElements) {
                const rect = element.getBoundingClientRect();
                
                if (rect.x < 400 && rect.width > 150 && rect.width < 400 && rect.height > 300) {
                    const links = element.querySelectorAll('a[href*="/app/"]');
                    
                    if (links.length > maxLinks) {
                        maxLinks = links.length;
                        taskSidebar = element;
                    }
                }
            }
        }
        
        if (taskSidebar) {
            // 標記找到的側邊欄
            taskSidebar.style.border = '3px solid #00ff00';
            taskSidebar.style.boxShadow = 'inset 0 0 10px rgba(0,255,0,0.3)';
            
            // 保存引用
            window.__manusTaskSidebar = taskSidebar;
            
            // 滾動到頂部
            taskSidebar.scrollTop = 0;
            
            const rect = taskSidebar.getBoundingClientRect();
            
            // 收集初始任務信息
            const tasks = [];
            taskSidebar.querySelectorAll('a[href*="/app/"]').forEach(link => {
                const container = link.closest('li, div[class*="item"], div[role="button"]');
                if (container) {
                    const text = container.innerText || link.innerText || '';
                    tasks.push(text.substring(0, 50));
                }
            });
            
            return {
                found: true,
                x: Math.round(rect.x),
                y: Math.round(rect.y),
                width: Math.round(rect.width),
                height: Math.round(rect.height),
                scrollable: taskSidebar.scrollHeight > taskSidebar.clientHeight,
                scrollHeight: taskSidebar.scrollHeight,
                clientHeight: taskSidebar.clientHeight,
                taskCount: tasks.length,
                sampleTasks: tasks.slice(0, 3)
            };
        }
        
        return { found: false };
        """
        
        return self.driver.execute_script(locate_script)
        
    def _collect_all_tasks_with_scroll(self):
        """滾動收集所有任務"""
        logger.info("\n📋 開始收集任務...")
        
        # 確保從頂部開始
        self.driver.execute_script("""
            if (window.__manusTaskSidebar) {
                window.__manusTaskSidebar.scrollTop = 0;
            }
        """)
        time.sleep(1)
        
        scroll_round = 0
        no_new_tasks_count = 0
        total_scroll_distance = 0
        
        while no_new_tasks_count < 5:
            scroll_round += 1
            logger.info(f"\n--- 第 {scroll_round} 輪收集 ---")
            
            # 提取當前可見的任務
            current_tasks = self._extract_visible_tasks()
            
            # 統計新任務
            new_tasks = 0
            for task_id, task_info in current_tasks.items():
                if task_id not in self.collected_tasks:
                    self.collected_tasks[task_id] = task_info
                    new_tasks += 1
                    logger.debug(f"  新任務: {task_info['number']} {task_info['title'][:30]}")
                    
            logger.info(f"本輪新增: {new_tasks} 個任務")
            logger.info(f"總計: {len(self.collected_tasks)} 個任務")
            
            # 顯示一些已收集的任務
            if new_tasks > 0:
                numbers = [t['number'] for t in self.collected_tasks.values() if t.get('number')]
                logger.info(f"已收集數字: {', '.join(numbers[-10:])}")
            
            if new_tasks == 0:
                no_new_tasks_count += 1
            else:
                no_new_tasks_count = 0
                
            # 滾動側邊欄
            scroll_result = self._scroll_sidebar()
            
            if scroll_result['atBottom']:
                logger.info("✅ 已到達底部")
                if no_new_tasks_count >= 2:
                    break
                    
            if not scroll_result['success']:
                logger.warning("滾動可能失敗，嘗試備用方法...")
                self._alternative_scroll()
                
            # 等待內容加載
            time.sleep(1.5)
            
            # 每5輪保存進度
            if scroll_round % 5 == 0:
                self._save_progress()
                
            # 安全檢查：如果滾動超過50輪還在繼續，可能有問題
            if scroll_round > 50:
                logger.warning("滾動輪次過多，停止收集")
                break
                
        logger.info(f"\n✅ 收集完成！總共 {len(self.collected_tasks)} 個任務")
        
    def _extract_visible_tasks(self):
        """提取當前可見的任務"""
        extract_script = """
        if (!window.__manusTaskSidebar) return {};
        
        const sidebar = window.__manusTaskSidebar;
        const tasks = {};
        
        // 中文數字列表
        const chineseNumbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                               '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十',
                               '三十一', '三十二', '三十三', '三十四', '三十五', '三十六', '三十七', '三十八', '三十九', '四十'];
        
        // 查找所有任務連結
        const links = sidebar.querySelectorAll('a[href*="/app/"]');
        
        links.forEach((link, index) => {
            const href = link.href;
            const match = href.match(/\\/app\\/([^\\/\\?]+)/);
            
            if (match) {
                const taskId = match[1];
                
                // 查找包含此連結的容器
                let container = link.closest('li, div[class*="item"], div[role="button"], div[class*="conversation"]');
                if (!container) container = link.parentElement;
                
                let taskText = '';
                let taskNumber = '';
                
                if (container) {
                    taskText = container.innerText || '';
                    
                    // 查找中文數字
                    for (const num of chineseNumbers) {
                        if (taskText.includes(num)) {
                            taskNumber = num;
                            break;
                        }
                    }
                } else {
                    taskText = link.innerText || link.textContent || '';
                }
                
                tasks[taskId] = {
                    id: taskId,
                    title: taskText.trim().substring(0, 100),
                    href: href,
                    number: taskNumber,
                    index: Object.keys(tasks).length
                };
            }
        });
        
        return tasks;
        """
        
        return self.driver.execute_script(extract_script)
        
    def _scroll_sidebar(self):
        """滾動側邊欄"""
        scroll_script = """
        if (!window.__manusTaskSidebar) return { success: false };
        
        const sidebar = window.__manusTaskSidebar;
        const beforeScroll = sidebar.scrollTop;
        const scrollHeight = sidebar.scrollHeight;
        const clientHeight = sidebar.clientHeight;
        
        // 計算滾動距離（80%的可視高度）
        const scrollDistance = clientHeight * 0.8;
        
        // 執行滾動
        sidebar.scrollTop = beforeScroll + scrollDistance;
        
        // 給一點時間讓滾動生效
        return new Promise(resolve => {
            setTimeout(() => {
                const afterScroll = sidebar.scrollTop;
                const actualScrolled = afterScroll - beforeScroll;
                const atBottom = (afterScroll + clientHeight) >= (scrollHeight - 10);
                
                resolve({
                    success: actualScrolled > 0,
                    beforeScroll: beforeScroll,
                    afterScroll: afterScroll,
                    scrollHeight: scrollHeight,
                    clientHeight: clientHeight,
                    actualScrolled: actualScrolled,
                    atBottom: atBottom
                });
            }, 100);
        });
        """
        
        return self.driver.execute_script(scroll_script)
        
    def _alternative_scroll(self):
        """備用滾動方法"""
        try:
            # 方法1: 點擊側邊欄並使用鍵盤
            self.driver.execute_script("""
                if (window.__manusTaskSidebar) {
                    window.__manusTaskSidebar.click();
                    window.__manusTaskSidebar.focus();
                }
            """)
            
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.PAGE_DOWN)
            actions.perform()
            
        except:
            pass
            
    def _save_progress(self):
        """保存進度"""
        progress_file = self.output_dir / "collection_progress.json"
        tasks = list(self.collected_tasks.values())
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'collected': len(tasks),
                'tasks': tasks[:50],  # 保存前50個作為樣本
                'numbers': [t['number'] for t in tasks if t.get('number')],
                'timestamp': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        logger.info(f"💾 已保存進度")
        
    def _save_final_results(self):
        """保存最終結果"""
        tasks = list(self.collected_tasks.values())
        
        # 按數字排序（如果有的話）
        def sort_key(task):
            number = task.get('number', '')
            if number:
                # 中文數字轉換為數字以便排序
                chinese_to_num = {
                    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
                    '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
                    '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
                    '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30
                }
                return chinese_to_num.get(number, 999)
            return 999
            
        tasks.sort(key=sort_key)
        
        # 保存完整數據
        all_tasks_file = self.output_dir / "all_tasks.json"
        with open(all_tasks_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(tasks),
                'tasks': tasks,
                'collected_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        # 生成 replay URLs
        urls_file = self.output_dir / "replay_urls.txt"
        with open(urls_file, 'w', encoding='utf-8') as f:
            f.write(f"# Manus 任務列表 - {len(tasks)} 個任務\n")
            f.write(f"# 收集時間: {datetime.now().isoformat()}\n")
            f.write("#" * 70 + "\n\n")
            
            for task in tasks:
                number = task.get('number', '')
                title = task.get('title', '').replace('\n', ' ')[:80]
                
                if number:
                    f.write(f"# {number}. {title}\n")
                else:
                    f.write(f"# {title}\n")
                f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
                
        # 生成統計報告
        stats_file = self.output_dir / "collection_stats.txt"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("Manus 任務收集統計報告\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"收集時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"總任務數: {len(tasks)}\n")
            
            # 統計帶數字的任務
            numbered_tasks = [t for t in tasks if t.get('number')]
            f.write(f"帶數字標記的任務: {len(numbered_tasks)}\n\n")
            
            if numbered_tasks:
                f.write("數字分布:\n")
                numbers = [t['number'] for t in numbered_tasks]
                for num in set(numbers):
                    count = numbers.count(num)
                    f.write(f"  {num}: {count} 個\n")
                    
        logger.info(f"\n✅ 所有結果已保存:")
        logger.info(f"  任務數據: {all_tasks_file}")
        logger.info(f"  Replay URLs: {urls_file}")
        logger.info(f"  統計報告: {stats_file}")
        
        # 顯示摘要
        logger.info(f"\n📊 收集摘要:")
        logger.info(f"  總任務數: {len(tasks)}")
        logger.info(f"  帶數字標記: {len(numbered_tasks)}")
        
        # 顯示前幾個任務
        logger.info(f"\n📋 任務示例:")
        for i, task in enumerate(tasks[:5]):
            number = task.get('number', '')
            title = task.get('title', '').replace('\n', ' ')[:50]
            logger.info(f"  {i+1}. {number} {title}")
            
    def _try_alternative_methods(self):
        """嘗試其他方法"""
        logger.info("\n嘗試備用收集方法...")
        
        # 直接收集頁面上所有任務
        all_tasks = self.driver.execute_script("""
            const tasks = {};
            const chineseNumbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                                   '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十'];
            
            document.querySelectorAll('a[href*="/app/"]').forEach(link => {
                const match = link.href.match(/\\/app\\/([^\\/\\?]+)/);
                if (match) {
                    const taskId = match[1];
                    let text = link.innerText || '';
                    let number = '';
                    
                    // 向上查找包含中文數字的文本
                    let parent = link.parentElement;
                    let depth = 0;
                    while (parent && depth < 5) {
                        const parentText = parent.innerText || '';
                        for (const num of chineseNumbers) {
                            if (parentText.includes(num)) {
                                text = parentText;
                                number = num;
                                break;
                            }
                        }
                        if (number) break;
                        parent = parent.parentElement;
                        depth++;
                    }
                    
                    tasks[taskId] = {
                        id: taskId,
                        title: text.substring(0, 100),
                        href: link.href,
                        number: number
                    };
                }
            });
            
            return tasks;
        """)
        
        for task_id, task_info in all_tasks.items():
            self.collected_tasks[task_id] = task_info
            
        if self.collected_tasks:
            logger.info(f"✅ 備用方法收集到 {len(self.collected_tasks)} 個任務")
            self._save_final_results()


def main():
    """主函數"""
    print("""
    🤖 Manus 精確側邊欄收集器
    
    特點：
    1. 精確識別左側任務列表（包含"五"、"四"、"三"等標記）
    2. 綠色邊框標記找到的側邊欄
    3. 只滾動左側任務列表，不影響中間對話區
    4. 自動收集所有任務並生成 replay URLs
    
    請確保左側任務列表可見！
    """)
    
    collector = ManusPreciseSidebarCollector()
    collector.collect_all_tasks()


if __name__ == "__main__":
    main()