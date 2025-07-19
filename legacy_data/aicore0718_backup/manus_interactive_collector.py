#!/usr/bin/env python3
"""
Manus 互動式收集器
通過用戶互動確保正確定位並收集左側任務列表
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManusInteractiveCollector:
    """互動式 Manus 任務收集器"""
    
    def __init__(self):
        self.driver = None
        self.output_dir = Path("./data/manus_interactive")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collected_tasks = {}
        
    def setup_browser(self):
        """設置瀏覽器"""
        options = ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1400, 900)
        logger.info("✅ 瀏覽器已啟動")
        
    def collect_with_user_help(self):
        """通過用戶幫助收集任務"""
        logger.info("🚀 開始互動式收集")
        
        self.setup_browser()
        
        try:
            # 步驟1: 登錄
            self.driver.get("https://manus.im/login")
            logger.info("\n步驟1: 請登錄 Manus")
            input("登錄完成後按 Enter...")
            
            # 步驟2: 進入任務頁面
            logger.info("\n步驟2: 請點擊進入任意一個對話/任務")
            logger.info("確保左側任務列表可見（應該有'五'、'四'、'三'等中文數字）")
            input("準備好後按 Enter...")
            
            # 步驟3: 手動標記側邊欄
            logger.info("\n步驟3: 請幫助我定位左側任務列表")
            logger.info("請在瀏覽器控制台執行以下步驟：")
            logger.info("1. 右鍵點擊左側任務列表區域")
            logger.info("2. 選擇'檢查'或'Inspect'")
            logger.info("3. 在開發者工具中，找到包含所有任務的容器元素")
            logger.info("4. 記下該元素的 class 名稱或其他特徵")
            
            sidebar_class = input("\n請輸入側邊欄的 class 名稱（或輸入 'skip' 跳過）: ").strip()
            
            if sidebar_class and sidebar_class != 'skip':
                # 嘗試使用用戶提供的 class
                success = self._try_user_selector(sidebar_class)
                if success:
                    logger.info("✅ 成功找到側邊欄！")
                else:
                    logger.info("未能使用該選擇器，切換到手動模式")
                    
            # 步驟4: 手動收集模式
            logger.info("\n步驟4: 開始手動收集任務")
            self._manual_collection()
            
            # 保存結果
            if self.collected_tasks:
                self._save_results()
            else:
                logger.error("未收集到任何任務")
                
        except Exception as e:
            logger.error(f"錯誤: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            input("\n按 Enter 關閉...")
            self.driver.quit()
            
    def _try_user_selector(self, selector):
        """嘗試用戶提供的選擇器"""
        try:
            # 嘗試作為 class 名
            if not selector.startswith('.'):
                selector = f'.{selector}'
                
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            # 標記元素
            self.driver.execute_script("""
                arguments[0].style.border = '3px solid lime';
                arguments[0].style.backgroundColor = 'rgba(0,255,0,0.1)';
                window.__manusSidebar = arguments[0];
            """, element)
            
            logger.info(f"✅ 找到元素: {selector}")
            
            # 自動收集
            confirm = input("這是正確的側邊欄嗎？(y/n): ").lower()
            if confirm == 'y':
                self._auto_collect_from_marked_sidebar()
                return True
                
        except Exception as e:
            logger.error(f"無法使用選擇器 {selector}: {e}")
            
        return False
        
    def _manual_collection(self):
        """手動收集模式"""
        logger.info("\n=== 手動收集模式 ===")
        logger.info("請手動操作：")
        logger.info("1. 滾動左側任務列表到頂部")
        logger.info("2. 我會定期收集當前可見的任務")
        logger.info("3. 請慢慢向下滾動左側列表")
        logger.info("4. 輸入 'done' 完成收集")
        
        input("\n準備好後按 Enter 開始...")
        
        round_count = 0
        while True:
            round_count += 1
            
            # 收集當前可見的任務
            tasks = self._collect_visible_tasks()
            new_count = 0
            
            for task_id, task_info in tasks.items():
                if task_id not in self.collected_tasks:
                    self.collected_tasks[task_id] = task_info
                    new_count += 1
                    
            logger.info(f"\n第 {round_count} 輪: 新增 {new_count} 個任務，總計 {len(self.collected_tasks)} 個")
            
            # 顯示最近收集的任務
            if new_count > 0:
                recent_tasks = list(tasks.values())[-5:]
                for task in recent_tasks:
                    logger.info(f"  - {task.get('number', '')} {task['title'][:40]}")
                    
            # 用戶輸入
            user_input = input("\n繼續滾動並按 Enter，或輸入 'done' 完成: ").strip().lower()
            if user_input == 'done':
                break
                
            time.sleep(0.5)  # 短暫等待
            
        logger.info(f"\n✅ 手動收集完成，共 {len(self.collected_tasks)} 個任務")
        
    def _auto_collect_from_marked_sidebar(self):
        """從標記的側邊欄自動收集"""
        logger.info("\n自動收集中...")
        
        # 滾動到頂部
        self.driver.execute_script("""
            if (window.__manusSidebar) {
                window.__manusSidebar.scrollTop = 0;
            }
        """)
        time.sleep(1)
        
        no_new_count = 0
        round_count = 0
        
        while no_new_count < 3:
            round_count += 1
            logger.info(f"\n第 {round_count} 輪收集...")
            
            # 收集任務
            tasks = self._collect_visible_tasks()
            new_count = 0
            
            for task_id, task_info in tasks.items():
                if task_id not in self.collected_tasks:
                    self.collected_tasks[task_id] = task_info
                    new_count += 1
                    
            logger.info(f"新增: {new_count}，總計: {len(self.collected_tasks)}")
            
            if new_count == 0:
                no_new_count += 1
            else:
                no_new_count = 0
                
            # 滾動
            at_bottom = self.driver.execute_script("""
                if (window.__manusSidebar) {
                    const sidebar = window.__manusSidebar;
                    const before = sidebar.scrollTop;
                    sidebar.scrollTop = sidebar.scrollHeight;
                    return sidebar.scrollTop === before;
                }
                return true;
            """)
            
            if at_bottom:
                logger.info("已到達底部")
                break
                
            time.sleep(2)
            
    def _collect_visible_tasks(self):
        """收集當前可見的任務"""
        script = """
        const tasks = {};
        const chineseNumbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                               '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十',
                               '三十一', '三十二', '三十三', '三十四', '三十五', '三十六', '三十七', '三十八', '三十九', '四十',
                               '四十一', '四十二', '四十三', '四十四', '四十五', '四十六', '四十七', '四十八', '四十九', '五十'];
        
        // 收集所有包含 /app/ 的連結
        document.querySelectorAll('a[href*="/app/"]').forEach((link, index) => {
            const href = link.href;
            const match = href.match(/\\/app\\/([^\\/\\?]+)/);
            
            if (match) {
                const taskId = match[1];
                
                // 查找任務文本和數字
                let taskText = '';
                let taskNumber = '';
                
                // 向上查找包含文本的元素
                let element = link;
                let depth = 0;
                
                while (element && depth < 5) {
                    const text = element.textContent || '';
                    
                    // 檢查是否包含中文數字
                    for (const num of chineseNumbers) {
                        if (text.includes(num)) {
                            taskNumber = num;
                            taskText = text.trim();
                            break;
                        }
                    }
                    
                    if (taskNumber) break;
                    
                    // 如果沒找到數字，至少保存文本
                    if (!taskText && text.trim()) {
                        taskText = text.trim();
                    }
                    
                    element = element.parentElement;
                    depth++;
                }
                
                // 如果還是沒有文本，使用連結本身的文本
                if (!taskText) {
                    taskText = link.textContent || link.innerText || `任務 ${index + 1}`;
                }
                
                tasks[taskId] = {
                    id: taskId,
                    title: taskText.substring(0, 200),
                    href: href,
                    number: taskNumber,
                    index: index
                };
            }
        });
        
        return tasks;
        """
        
        return self.driver.execute_script(script)
        
    def _save_results(self):
        """保存結果"""
        tasks = list(self.collected_tasks.values())
        
        # 排序（優先按數字，然後按索引）
        def sort_key(task):
            number = task.get('number', '')
            if number:
                # 簡單的中文數字排序
                numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                          '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']
                try:
                    return numbers.index(number)
                except ValueError:
                    return 999
            return 999 + task.get('index', 0)
            
        tasks.sort(key=sort_key)
        
        # 保存任務數據
        tasks_file = self.output_dir / "all_tasks.json"
        with open(tasks_file, 'w', encoding='utf-8') as f:
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
            
            for i, task in enumerate(tasks):
                number = task.get('number', '')
                title = task.get('title', '').replace('\n', ' ')[:80]
                
                if number:
                    f.write(f"# {i+1}. {number} - {title}\n")
                else:
                    f.write(f"# {i+1}. {title}\n")
                f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
                
        # 生成簡單統計
        stats_file = self.output_dir / "stats.txt"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(f"收集統計\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"總任務數: {len(tasks)}\n")
            f.write(f"帶數字標記: {len([t for t in tasks if t.get('number')])}\n")
            f.write(f"收集時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
        logger.info(f"\n✅ 結果已保存:")
        logger.info(f"  任務數據: {tasks_file}")
        logger.info(f"  Replay URLs: {urls_file}")
        logger.info(f"  統計: {stats_file}")
        
        # 顯示摘要
        logger.info(f"\n📊 收集摘要:")
        logger.info(f"  總任務數: {len(tasks)}")
        logger.info(f"  帶數字標記: {len([t for t in tasks if t.get('number')])}")
        
        # 創建批量下載腳本
        self._create_batch_download_script(tasks)
        
    def _create_batch_download_script(self, tasks):
        """創建批量下載腳本"""
        script_file = self.output_dir / "batch_download.sh"
        
        with open(script_file, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Manus 批量下載腳本\n")
            f.write(f"# 生成時間: {datetime.now().isoformat()}\n")
            f.write(f"# 任務總數: {len(tasks)}\n\n")
            
            f.write("mkdir -p manus_conversations\n\n")
            
            for i, task in enumerate(tasks[:10]):  # 示例：前10個
                number = task.get('number', f'{i+1}')
                safe_title = task.get('title', '').replace('/', '_')[:30]
                filename = f"manus_conversations/{number}_{safe_title}.html"
                url = f"https://manus.im/share/{task['id']}?replay=1"
                
                f.write(f"# {i+1}. {task.get('title', '')[:50]}\n")
                f.write(f"curl -o \"{filename}\" \"{url}\"\n")
                f.write("sleep 2\n\n")
                
        # 設置執行權限
        import os
        os.chmod(script_file, 0o755)
        
        logger.info(f"\n💡 批量下載腳本: {script_file}")
        logger.info("   運行: bash batch_download.sh")


def main():
    """主函數"""
    print("""
    🤝 Manus 互動式收集器
    
    這個工具通過用戶互動確保正確收集左側任務列表：
    
    1. 可以手動指定側邊欄的 class 名稱
    2. 支持手動滾動收集模式
    3. 實時顯示收集進度
    4. 生成完整的任務列表和下載腳本
    
    如果自動識別失敗，我們會一起手動完成！
    """)
    
    collector = ManusInteractiveCollector()
    collector.collect_with_user_help()


if __name__ == "__main__":
    main()