#!/usr/bin/env python3
"""
Manus 側邊欄專注收集器
專門針對左側任務列表進行優化
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManusSidebarFocusedCollector:
    """專注於 Manus 左側任務列表的收集器"""
    
    def __init__(self):
        self.driver = None
        self.output_dir = Path("./data/manus_sidebar_focused")
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
        logger.info("✅ 瀏覽器已啟動")
        
    def collect_all_tasks(self):
        """收集所有任務"""
        logger.info("🚀 開始 Manus 側邊欄收集")
        
        self.setup_browser()
        
        try:
            # 步驟1: 登錄
            self.driver.get("https://manus.im/login")
            logger.info("\n請完成以下步驟：")
            logger.info("1. 登錄 Manus")
            logger.info("2. 點擊進入任意一個對話/任務")
            logger.info("3. 確保左側任務列表可見")
            input("\n準備好後按 Enter 繼續...")
            
            # 步驟2: 分析頁面結構
            self._analyze_page_structure()
            
            # 步驟3: 手動確認側邊欄
            logger.info("\n請看瀏覽器窗口...")
            logger.info("如果左側任務列表不可見，請點擊菜單按鈕打開它")
            input("確保左側任務列表可見後，按 Enter 繼續...")
            
            # 步驟4: 使用 JavaScript 直接定位側邊欄
            sidebar_info = self._locate_sidebar_with_js()
            
            if sidebar_info and sidebar_info['found']:
                logger.info(f"\n✅ 找到側邊欄: {sidebar_info['info']}")
                
                # 步驟5: 收集任務
                self._collect_tasks_from_sidebar()
                
                # 步驟6: 保存結果
                if self.collected_tasks:
                    self._save_results()
                else:
                    logger.error("未收集到任務，請檢查頁面")
                    self._save_debug_info()
            else:
                logger.error("無法定位側邊欄")
                self._save_debug_info()
                
        except Exception as e:
            logger.error(f"發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            self._save_debug_info()
            
        finally:
            input("\n按 Enter 關閉瀏覽器...")
            self.driver.quit()
            
    def _analyze_page_structure(self):
        """分析頁面結構"""
        logger.info("\n🔍 分析頁面結構...")
        
        analysis = self.driver.execute_script("""
            const analysis = {
                url: window.location.href,
                title: document.title,
                hasAside: !!document.querySelector('aside'),
                totalLinks: document.querySelectorAll('a').length,
                appLinks: document.querySelectorAll('a[href*="/app/"]').length,
                possibleSidebars: []
            };
            
            // 查找可能的側邊欄
            const candidates = document.querySelectorAll('aside, [class*="sidebar"], [class*="panel"], [class*="navigation"], nav');
            candidates.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    analysis.possibleSidebars.push({
                        tag: el.tagName,
                        class: el.className,
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        childLinks: el.querySelectorAll('a').length
                    });
                }
            });
            
            return analysis;
        """)
        
        logger.info(f"URL: {analysis['url']}")
        logger.info(f"總連結數: {analysis['totalLinks']}")
        logger.info(f"App 連結數: {analysis['appLinks']}")
        logger.info(f"可能的側邊欄: {len(analysis['possibleSidebars'])}")
        
        for i, sidebar in enumerate(analysis['possibleSidebars']):
            logger.info(f"  {i+1}. {sidebar['tag']}.{sidebar['class']} - 位置:({sidebar['x']},{sidebar['y']}) 大小:{sidebar['width']}x{sidebar['height']} 連結:{sidebar['childLinks']}")
            
    def _locate_sidebar_with_js(self):
        """使用 JavaScript 定位側邊欄"""
        locate_script = """
            // 查找左側的任務列表
            let sidebar = null;
            let info = '';
            
            // 方法1: 根據位置查找（左側，有一定寬度和高度）
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {
                const rect = el.getBoundingClientRect();
                // 檢查：在左側（x < 500），有足夠高度（> 300），有適當寬度（100-500）
                if (rect.x < 500 && rect.height > 300 && rect.width > 100 && rect.width < 500) {
                    // 檢查是否包含任務連結
                    const links = el.querySelectorAll('a[href*="/app/"]');
                    if (links.length > 0) {
                        sidebar = el;
                        info = `位置法: ${el.tagName}.${el.className} - ${links.length}個連結`;
                        break;
                    }
                }
            }
            
            // 方法2: 根據類名查找
            if (!sidebar) {
                const sidebarSelectors = [
                    'aside', '.sidebar', '[class*="sidebar"]', '[class*="side-bar"]',
                    '.conversation-list', '[class*="conversation"]', '.task-list',
                    '.left-panel', '[class*="left"]', 'nav'
                ];
                
                for (const selector of sidebarSelectors) {
                    const el = document.querySelector(selector);
                    if (el) {
                        const rect = el.getBoundingClientRect();
                        const links = el.querySelectorAll('a[href*="/app/"]');
                        if (rect.x < 500 && links.length > 0) {
                            sidebar = el;
                            info = `選擇器法: ${selector} - ${links.length}個連結`;
                            break;
                        }
                    }
                }
            }
            
            if (sidebar) {
                // 高亮顯示找到的側邊欄
                sidebar.style.border = '3px solid red';
                sidebar.style.boxShadow = '0 0 10px red';
                
                return {
                    found: true,
                    info: info,
                    rect: sidebar.getBoundingClientRect(),
                    linkCount: sidebar.querySelectorAll('a[href*="/app/"]').length
                };
            }
            
            return { found: false };
        """
        
        return self.driver.execute_script(locate_script)
        
    def _collect_tasks_from_sidebar(self):
        """從側邊欄收集任務"""
        logger.info("\n📋 開始收集任務...")
        
        # 首先滾動到頂部
        self.driver.execute_script("""
            // 找到紅框標記的側邊欄
            const sidebar = document.querySelector('[style*="border: 3px solid red"]');
            if (sidebar) {
                sidebar.scrollTop = 0;
            }
        """)
        time.sleep(1)
        
        scroll_count = 0
        no_new_count = 0
        
        while no_new_count < 5:
            scroll_count += 1
            logger.info(f"\n--- 第 {scroll_count} 輪收集 ---")
            
            # 提取當前可見的任務
            tasks = self.driver.execute_script("""
                const sidebar = document.querySelector('[style*="border: 3px solid red"]');
                if (!sidebar) return {};
                
                const tasks = {};
                
                // 查找所有任務連結
                const links = sidebar.querySelectorAll('a[href*="/app/"]');
                
                links.forEach((link, index) => {
                    const href = link.href;
                    const match = href.match(/\\/app\\/([^\\/\\?]+)/);
                    
                    if (match) {
                        const taskId = match[1];
                        
                        // 獲取任務文本（向上查找包含文本的父元素）
                        let taskText = '';
                        let element = link;
                        let depth = 0;
                        
                        while (element && depth < 5) {
                            const text = element.textContent || '';
                            if (text.trim() && text.length > taskText.length && text.length < 200) {
                                taskText = text.trim();
                            }
                            element = element.parentElement;
                            depth++;
                        }
                        
                        // 查找數字標記
                        const chineseNumbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                                               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                                               '二十一', '二十二', '二十三', '二十四', '二十五'];
                        
                        let number = '';
                        for (const num of chineseNumbers) {
                            if (taskText.includes(num)) {
                                number = num;
                                break;
                            }
                        }
                        
                        tasks[taskId] = {
                            id: taskId,
                            title: taskText.substring(0, 100),
                            href: href,
                            number: number,
                            index: index
                        };
                    }
                });
                
                return tasks;
            """)
            
            # 統計新任務
            new_count = 0
            for task_id, task_info in tasks.items():
                if task_id not in self.collected_tasks:
                    self.collected_tasks[task_id] = task_info
                    new_count += 1
                    
            logger.info(f"本輪新增: {new_count} 個任務")
            logger.info(f"總計: {len(self.collected_tasks)} 個任務")
            
            if new_count == 0:
                no_new_count += 1
            else:
                no_new_count = 0
                
            # 滾動側邊欄
            at_bottom = self.driver.execute_script("""
                const sidebar = document.querySelector('[style*="border: 3px solid red"]');
                if (!sidebar) return true;
                
                const before = sidebar.scrollTop;
                sidebar.scrollTop = sidebar.scrollHeight;
                const after = sidebar.scrollTop;
                
                // 如果滾動位置沒變，說明到底了
                return before === after;
            """)
            
            if at_bottom:
                logger.info("已到達底部")
                break
                
            # 等待加載
            time.sleep(2)
            
            # 每10輪保存一次
            if scroll_count % 10 == 0:
                self._save_progress()
                
        logger.info(f"\n✅ 收集完成，共 {len(self.collected_tasks)} 個任務")
        
    def _save_progress(self):
        """保存進度"""
        progress_file = self.output_dir / "progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'collected': len(self.collected_tasks),
                'tasks': list(self.collected_tasks.values()),
                'timestamp': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 已保存進度")
        
    def _save_results(self):
        """保存最終結果"""
        tasks = list(self.collected_tasks.values())
        tasks.sort(key=lambda x: x.get('index', 999999))
        
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
            f.write("#" * 60 + "\n\n")
            
            for i, task in enumerate(tasks):
                number = task.get('number', '')
                title = task.get('title', f'任務 {i+1}')[:80]
                
                f.write(f"# {i+1}. {number} {title}\n")
                f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
                
        # 統計報告
        stats = {
            '總任務數': len(tasks),
            '帶數字標記': len([t for t in tasks if t.get('number')]),
            '收集時間': datetime.now().isoformat()
        }
        
        stats_file = self.output_dir / "stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
            
        logger.info(f"\n✅ 結果已保存:")
        logger.info(f"  任務數據: {tasks_file}")
        logger.info(f"  Replay URLs: {urls_file}")
        logger.info(f"  統計: {stats_file}")
        
        # 顯示統計
        logger.info(f"\n📊 統計:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
            
        # 顯示樣本
        logger.info(f"\n📋 任務樣本:")
        for i, task in enumerate(tasks[:5]):
            logger.info(f"  {i+1}. {task.get('number', '')} {task.get('title', 'Unknown')[:60]}")
        if len(tasks) > 5:
            logger.info(f"  ... 還有 {len(tasks) - 5} 個任務")
            
    def _save_debug_info(self):
        """保存調試信息"""
        logger.info("\n💾 保存調試信息...")
        
        # 截圖
        screenshot_file = self.output_dir / f"debug_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.driver.save_screenshot(str(screenshot_file))
        
        # 頁面源碼
        source_file = self.output_dir / "page_source.html"
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
            
        logger.info(f"  截圖: {screenshot_file}")
        logger.info(f"  源碼: {source_file}")


def main():
    """主函數"""
    print("""
    🤖 Manus 側邊欄專注收集器
    
    這個工具會：
    1. 自動找到左側任務列表（會用紅框標記）
    2. 從頂部開始向下滾動
    3. 收集所有任務信息
    4. 生成完整的 replay URLs
    
    請按照提示操作...
    """)
    
    collector = ManusSidebarFocusedCollector()
    collector.collect_all_tasks()


if __name__ == "__main__":
    main()