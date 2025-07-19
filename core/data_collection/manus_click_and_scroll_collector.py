#!/usr/bin/env python3
"""
Manus 點擊側邊欄並滾動收集器
點擊左邊欄的每個項目並持續向下滾動收集所有任務
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManusClickScrollCollector:
    """點擊側邊欄並滾動收集所有任務"""
    
    def __init__(self):
        self.driver = None
        self.output_dir = Path("./data/manus_complete_collection")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collected_tasks = {}
        
    def setup_browser(self):
        """設置瀏覽器"""
        options = ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def collect_all_tasks(self):
        """收集所有任務 - 點擊側邊欄並滾動"""
        logger.info("🚀 開始 Manus 完整收集（點擊+滾動）")
        
        self.setup_browser()
        
        try:
            # 訪問 Manus
            self.driver.get("https://manus.im/login")
            logger.info("請登錄 Manus...")
            input("登錄完成後，進入任意任務頁面，確保左側邊欄可見，然後按 Enter...")
            
            # 截圖
            self.driver.save_screenshot(str(self.output_dir / "initial_state.png"))
            
            # 等待頁面穩定
            time.sleep(3)
            
            # 步驟1: 定位側邊欄
            sidebar = self._locate_sidebar()
            if not sidebar:
                logger.error("未找到側邊欄")
                input("請手動點擊打開側邊欄，然後按 Enter...")
                sidebar = self._locate_sidebar()
                
            if sidebar:
                logger.info("✅ 找到側邊欄，開始收集...")
                
                # 步驟2: 滾動到頂部
                self._scroll_to_top(sidebar)
                
                # 步驟3: 收集所有任務（點擊+滾動）
                self._collect_with_clicking_and_scrolling(sidebar)
                
                # 步驟4: 保存結果
                if self.collected_tasks:
                    self._save_all_results()
                else:
                    logger.error("未收集到任何任務")
            else:
                logger.error("無法定位側邊欄")
                
        except Exception as e:
            logger.error(f"發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            input("\n收集完成，按 Enter 關閉瀏覽器...")
            self.driver.quit()
            
    def _locate_sidebar(self):
        """定位側邊欄元素"""
        # 嘗試多種選擇器
        sidebar_selectors = [
            "aside",
            ".sidebar",
            "[class*='sidebar']",
            ".left-panel",
            "[class*='left-panel']",
            ".conversation-list",
            "[class*='conversation-list']",
            ".task-list",
            "[class*='task-list']",
            "[class*='navigation']",
            "[role='navigation']",
            # 更通用的選擇器
            "div[class*='left']",
            "div[class*='side']",
            # 根據位置查找
            "div[style*='position: fixed']",
            "div[style*='overflow']"
        ]
        
        for selector in sidebar_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # 檢查是否在左側且可見
                    if element.is_displayed():
                        rect = element.rect
                        # 檢查是否在左側（x坐標較小）且有一定高度
                        if rect['x'] < 400 and rect['height'] > 200:
                            logger.info(f"✅ 找到側邊欄: {selector}")
                            logger.info(f"  位置: x={rect['x']}, y={rect['y']}")
                            logger.info(f"  大小: {rect['width']}x{rect['height']}")
                            return element
            except:
                continue
                
        return None
        
    def _scroll_to_top(self, sidebar):
        """滾動側邊欄到頂部"""
        try:
            self.driver.execute_script("arguments[0].scrollTop = 0", sidebar)
            time.sleep(1)
            logger.info("✅ 已滾動到頂部")
        except:
            logger.warning("無法滾動側邊欄")
            
    def _collect_with_clicking_and_scrolling(self, sidebar):
        """點擊側邊欄項目並滾動收集"""
        logger.info("\n開始收集任務...")
        
        scroll_count = 0
        no_new_tasks_count = 0
        max_no_new_tasks = 5  # 連續5次沒有新任務就停止
        
        while no_new_tasks_count < max_no_new_tasks:
            scroll_count += 1
            logger.info(f"\n--- 第 {scroll_count} 輪收集 ---")
            
            # 獲取當前可見的任務
            current_tasks = self._extract_visible_tasks(sidebar)
            
            # 統計新任務
            new_tasks = 0
            for task_id, task_info in current_tasks.items():
                if task_id not in self.collected_tasks:
                    self.collected_tasks[task_id] = task_info
                    new_tasks += 1
                    
            logger.info(f"本輪新增: {new_tasks} 個任務")
            logger.info(f"總計: {len(self.collected_tasks)} 個任務")
            
            if new_tasks == 0:
                no_new_tasks_count += 1
            else:
                no_new_tasks_count = 0
                
            # 嘗試點擊側邊欄中的項目（可能觸發加載更多）
            self._try_click_sidebar_items(sidebar)
            
            # 滾動側邊欄
            self._scroll_sidebar(sidebar)
            
            # 等待加載
            time.sleep(2)
            
            # 每10輪保存一次進度
            if scroll_count % 10 == 0:
                self._save_progress()
                
        logger.info(f"\n✅ 收集完成，共 {len(self.collected_tasks)} 個任務")
        
    def _extract_visible_tasks(self, sidebar):
        """提取當前可見的任務"""
        tasks = {}
        
        # JavaScript 提取腳本
        extract_script = """
        const tasks = {};
        const sidebar = arguments[0];
        
        // 查找側邊欄中的所有連結
        const links = sidebar.querySelectorAll('a[href*="/app/"]');
        
        links.forEach((link, index) => {
            const href = link.href;
            const match = href.match(/\/app\/([^\/\?]+)/);
            
            if (match) {
                const taskId = match[1];
                
                // 獲取任務文本
                let taskText = link.textContent || '';
                
                // 如果連結本身沒有文本，查找父元素
                if (!taskText.trim()) {
                    let parent = link.parentElement;
                    let depth = 0;
                    while (parent && depth < 3) {
                        const text = parent.textContent;
                        if (text && text.trim()) {
                            taskText = text;
                            break;
                        }
                        parent = parent.parentElement;
                        depth++;
                    }
                }
                
                // 查找可能的數字標記
                let numberMark = '';
                const chineseNumbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                                       '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十'];
                
                for (const num of chineseNumbers) {
                    if (taskText.includes(num)) {
                        numberMark = num;
                        break;
                    }
                }
                
                tasks[taskId] = {
                    id: taskId,
                    title: taskText.trim().substring(0, 100),
                    href: href,
                    number: numberMark,
                    index: index,
                    visible: link.offsetParent !== null
                };
            }
        });
        
        // 也查找可點擊的 div 元素
        const clickableItems = sidebar.querySelectorAll('[onclick], [role="button"], [class*="item"]');
        clickableItems.forEach((item, index) => {
            const link = item.querySelector('a[href*="/app/"]');
            if (link) {
                const href = link.href;
                const match = href.match(/\/app\/([^\/\?]+)/);
                if (match && !tasks[match[1]]) {
                    tasks[match[1]] = {
                        id: match[1],
                        title: item.textContent.trim().substring(0, 100),
                        href: href,
                        index: index + 1000,
                        fromClickable: true
                    };
                }
            }
        });
        
        return tasks;
        """
        
        try:
            tasks = self.driver.execute_script(extract_script, sidebar)
            return tasks
        except Exception as e:
            logger.error(f"提取任務失敗: {e}")
            return {}
            
    def _try_click_sidebar_items(self, sidebar):
        """嘗試點擊側邊欄項目（可能觸發加載）"""
        try:
            # 查找可點擊的元素
            clickable_script = """
            const sidebar = arguments[0];
            const clickables = [];
            
            // 查找「查看更多」類型的按鈕
            const moreButtons = sidebar.querySelectorAll(
                'button:contains("更多"), button:contains("more"), ' +
                '[class*="load"], [class*="more"], [class*="expand"]'
            );
            
            moreButtons.forEach(btn => {
                if (btn.offsetParent !== null) {
                    clickables.push({
                        type: 'more_button',
                        text: btn.textContent
                    });
                    btn.click();
                }
            });
            
            return clickables.length;
            """
            
            clicked = self.driver.execute_script(clickable_script, sidebar)
            if clicked > 0:
                logger.info(f"✅ 點擊了 {clicked} 個加載按鈕")
                time.sleep(1)
        except:
            pass
            
    def _scroll_sidebar(self, sidebar):
        """滾動側邊欄"""
        try:
            # 方法1: 直接滾動側邊欄
            self.driver.execute_script("""
                const sidebar = arguments[0];
                const currentScroll = sidebar.scrollTop;
                const scrollHeight = sidebar.scrollHeight;
                const clientHeight = sidebar.clientHeight;
                
                // 滾動一個屏幕的高度
                sidebar.scrollTop = currentScroll + clientHeight * 0.8;
                
                // 如果已經到底部，返回 true
                return sidebar.scrollTop + clientHeight >= scrollHeight - 10;
            """, sidebar)
            
            # 方法2: 使用 ActionChains 在側邊欄內滾動
            actions = ActionChains(self.driver)
            actions.move_to_element(sidebar)
            actions.click()
            actions.send_keys_to_element(sidebar, " ")  # 空格鍵滾動
            actions.perform()
            
        except Exception as e:
            logger.warning(f"滾動失敗: {e}")
            
    def _save_progress(self):
        """保存進度"""
        progress_file = self.output_dir / "collection_progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'collected': len(self.collected_tasks),
                'tasks': list(self.collected_tasks.values()),
                'timestamp': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 已保存進度: {len(self.collected_tasks)} 個任務")
        
    def _save_all_results(self):
        """保存所有結果"""
        tasks = list(self.collected_tasks.values())
        
        # 按索引排序
        tasks.sort(key=lambda x: x.get('index', 999999))
        
        # 保存完整數據
        all_tasks_file = self.output_dir / "all_manus_tasks.json"
        with open(all_tasks_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(tasks),
                'tasks': tasks,
                'collected_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        # 生成 replay URLs
        urls_file = self.output_dir / "all_replay_urls.txt"
        with open(urls_file, 'w', encoding='utf-8') as f:
            f.write(f"# Manus 完整任務列表 - {len(tasks)} 個任務\n")
            f.write(f"# 收集時間: {datetime.now().isoformat()}\n")
            f.write("#" * 50 + "\n\n")
            
            for i, task in enumerate(tasks):
                number = task.get('number', '')
                title = task.get('title', f'任務 {i+1}')
                
                f.write(f"# {i+1}. {number} {title}\n")
                f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
                
        # 生成統計報告
        stats_file = self.output_dir / "collection_stats.txt"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(f"Manus 數據收集統計\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"總任務數: {len(tasks)}\n")
            f.write(f"收集時間: {datetime.now().isoformat()}\n\n")
            
            # 按數字分組統計
            numbered_tasks = [t for t in tasks if t.get('number')]
            f.write(f"帶數字標記的任務: {len(numbered_tasks)}\n")
            
            # 顯示前後任務樣本
            f.write("\n前10個任務:\n")
            for i, task in enumerate(tasks[:10]):
                f.write(f"  {i+1}. {task.get('title', 'Unknown')[:60]}\n")
                
            if len(tasks) > 10:
                f.write(f"\n... 中間省略 {len(tasks) - 20} 個任務 ...\n")
                f.write("\n後10個任務:\n")
                for i, task in enumerate(tasks[-10:], len(tasks) - 9):
                    f.write(f"  {i}. {task.get('title', 'Unknown')[:60]}\n")
                    
        logger.info(f"\n✅ 所有結果已保存:")
        logger.info(f"  任務數據: {all_tasks_file}")
        logger.info(f"  Replay URLs: {urls_file}")
        logger.info(f"  統計報告: {stats_file}")
        
        # 顯示摘要
        logger.info(f"\n📊 收集摘要:")
        logger.info(f"  總任務數: {len(tasks)}")
        logger.info(f"  帶數字標記: {len(numbered_tasks)}")
        
        # 創建下一步操作腳本
        self._create_next_step_script(tasks)
        
    def _create_next_step_script(self, tasks):
        """創建批量收集對話的腳本"""
        batch_script = self.output_dir / "batch_collect_conversations.py"
        
        script_content = f'''#!/usr/bin/env python3
"""
批量收集 Manus 對話內容
基於已收集的任務列表
"""

import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# 讀取任務列表
tasks_file = Path("{all_tasks_file.name}")
with open(tasks_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    tasks = data['tasks']

print(f"準備收集 {{len(tasks)}} 個任務的對話內容")

# 設置瀏覽器
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)

# 收集對話
conversations = []
for i, task in enumerate(tasks[:10]):  # 先收集前10個作為示例
    print(f"\\n收集 {{i+1}}/10: {{task['title'][:50]}}")
    
    url = f"https://manus.im/share/{{task['id']}}?replay=1"
    driver.get(url)
    time.sleep(3)
    
    # TODO: 提取對話內容
    
driver.quit()
print("\\n✅ 批量收集完成")
'''
        
        with open(batch_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
            
        logger.info(f"\n💡 下一步: 運行 {batch_script.name} 批量收集對話內容")


def main():
    """主函數"""
    print("""
    🤖 Manus 完整收集器（點擊+滾動）
    
    功能：
    1. 自動定位左側邊欄
    2. 點擊側邊欄項目
    3. 持續向下滾動直到收集完所有任務
    4. 生成完整的任務列表和 replay URLs
    
    準備：
    1. 登錄 Manus
    2. 確保左側邊欄可見
    3. 準備好後開始收集
    """)
    
    collector = ManusClickScrollCollector()
    collector.collect_all_tasks()


if __name__ == "__main__":
    main()