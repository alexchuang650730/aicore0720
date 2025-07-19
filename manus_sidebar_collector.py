#!/usr/bin/env python3
"""
Manus 側邊欄專用收集器
針對左側任務列表的特定結構優化
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


class ManusSidebarCollector:
    """專門針對 Manus 側邊欄的收集器"""
    
    def __init__(self):
        self.driver = None
        self.output_dir = Path("./data/manus_sidebar_collection")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_browser(self):
        """設置瀏覽器"""
        options = ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def collect_from_sidebar(self):
        """從側邊欄收集所有任務"""
        logger.info("🚀 開始 Manus 側邊欄收集")
        
        self.setup_browser()
        
        try:
            # 訪問 Manus
            self.driver.get("https://manus.im/login")
            logger.info("請登錄 Manus...")
            input("登錄完成後，進入任意任務頁面，然後按 Enter...")
            
            # 確認在正確頁面
            current_url = self.driver.current_url
            logger.info(f"當前 URL: {current_url}")
            
            # 截圖保存
            self.driver.save_screenshot(str(self.output_dir / "initial_page.png"))
            
            # 等待頁面完全加載
            time.sleep(3)
            
            # 專門查找側邊欄
            logger.info("\n🔍 查找側邊欄...")
            sidebar_found = self._find_and_activate_sidebar()
            
            if not sidebar_found:
                logger.warning("未找到側邊欄，嘗試手動定位...")
                input("請確保側邊欄可見，然後按 Enter...")
            
            # 收集所有任務
            all_tasks = self._collect_all_sidebar_tasks()
            
            if all_tasks:
                logger.info(f"\n✅ 成功收集 {len(all_tasks)} 個任務")
                self._save_results(all_tasks)
                
                # 顯示結果
                logger.info("\n📋 任務列表:")
                for i, task in enumerate(all_tasks[:10]):
                    logger.info(f"  {i+1}. {task['title']}")
                if len(all_tasks) > 10:
                    logger.info(f"  ... 還有 {len(all_tasks) - 10} 個任務")
            else:
                logger.error("未能收集到任務")
                self._debug_page_structure()
                
        except Exception as e:
            logger.error(f"發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            input("\n按 Enter 關閉瀏覽器...")
            self.driver.quit()
            
    def _find_and_activate_sidebar(self):
        """查找並激活側邊欄"""
        # 嘗試多種方式找到側邊欄
        sidebar_selectors = [
            # 通用側邊欄選擇器
            "aside",
            ".sidebar",
            "[class*='sidebar']",
            "[class*='side-bar']",
            "[class*='side_bar']",
            ".left-panel",
            ".left-sidebar",
            "[class*='navigation']",
            "[class*='nav-panel']",
            # Manus 特定選擇器
            ".conversation-list",
            "[class*='conversation-list']",
            ".task-list",
            "[class*='task-list']",
            ".thread-list",
            "[class*='thread-list']",
            # 包含數字的容器
            "[class*='numbered']",
            ".numbered-list"
        ]
        
        for selector in sidebar_selectors:
            try:
                sidebar = self.driver.find_element(By.CSS_SELECTOR, selector)
                if sidebar.is_displayed():
                    logger.info(f"✅ 找到側邊欄: {selector}")
                    
                    # 獲取側邊欄信息
                    rect = sidebar.rect
                    logger.info(f"  位置: x={rect['x']}, y={rect['y']}")
                    logger.info(f"  大小: {rect['width']}x{rect['height']}")
                    
                    # 滾動到頂部
                    self.driver.execute_script("arguments[0].scrollTop = 0", sidebar)
                    return True
            except:
                continue
                
        # 如果沒找到，嘗試點擊菜單按鈕
        logger.info("嘗試點擊菜單按鈕...")
        menu_clicked = self._try_click_menu()
        
        if menu_clicked:
            time.sleep(2)
            # 再次查找側邊欄
            for selector in sidebar_selectors:
                try:
                    sidebar = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if sidebar.is_displayed():
                        logger.info(f"✅ 點擊菜單後找到側邊欄: {selector}")
                        return True
                except:
                    continue
                    
        return False
        
    def _try_click_menu(self):
        """嘗試點擊菜單按鈕"""
        menu_selectors = [
            "[aria-label*='menu']",
            "[class*='menu-button']",
            "[class*='hamburger']",
            "[class*='toggle']",
            "button[class*='menu']",
            "svg[class*='menu']",
            "[data-testid*='menu']",
            "button:has(svg)",
            "[role='button']:has(svg)"
        ]
        
        for selector in menu_selectors:
            try:
                menu = self.driver.find_element(By.CSS_SELECTOR, selector)
                if menu.is_displayed():
                    menu.click()
                    logger.info(f"✅ 點擊了菜單: {selector}")
                    return True
            except:
                continue
        return False
        
    def _collect_all_sidebar_tasks(self):
        """收集側邊欄中的所有任務"""
        logger.info("\n📋 開始收集任務...")
        
        # 使用 JavaScript 全面收集
        collect_script = """
        // 收集所有任務的綜合方法
        const tasks = new Map();
        let taskIndex = 0;
        
        // 方法1: 查找所有包含數字標記的元素
        const chineseNumbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十'];
        
        chineseNumbers.forEach(num => {
            const elements = document.querySelectorAll(`*:contains("${num}")`);
            elements.forEach(el => {
                // 查找最近的連結
                const link = el.closest('a') || el.querySelector('a');
                if (link && link.href && link.href.includes('/app/')) {
                    const match = link.href.match(/\/app\/([^\/\?]+)/);
                    if (match) {
                        tasks.set(match[1], {
                            id: match[1],
                            title: num + ' - ' + (el.textContent || '').trim().substring(0, 50),
                            href: link.href,
                            number: num,
                            index: taskIndex++
                        });
                    }
                }
            });
        });
        
        // 方法2: 查找側邊欄中的所有連結
        const sidebarSelectors = [
            'aside', '.sidebar', '[class*="sidebar"]', '.left-panel',
            '.conversation-list', '[class*="conversation"]', '.task-list'
        ];
        
        sidebarSelectors.forEach(selector => {
            const sidebar = document.querySelector(selector);
            if (sidebar) {
                // 收集所有子元素中的連結
                const links = sidebar.querySelectorAll('a[href*="/app/"]');
                links.forEach((link, idx) => {
                    const match = link.href.match(/\/app\/([^\/\?]+)/);
                    if (match) {
                        const taskId = match[1];
                        if (!tasks.has(taskId)) {
                            // 獲取包含此連結的容器文本
                            let container = link.parentElement;
                            let depth = 0;
                            let title = '';
                            
                            while (container && depth < 5) {
                                const text = container.textContent || '';
                                if (text.length > title.length && text.length < 200) {
                                    title = text;
                                }
                                container = container.parentElement;
                                depth++;
                            }
                            
                            tasks.set(taskId, {
                                id: taskId,
                                title: title.trim().substring(0, 100) || `任務 ${idx + 1}`,
                                href: link.href,
                                selector: selector,
                                index: taskIndex++
                            });
                        }
                    }
                });
            }
        });
        
        // 方法3: 查找所有可點擊的任務項
        const itemSelectors = [
            '[class*="item"]', '[class*="row"]', '[class*="entry"]',
            'li', 'div[onclick]', 'div[role="button"]'
        ];
        
        itemSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(item => {
                const link = item.querySelector('a[href*="/app/"]');
                if (link) {
                    const match = link.href.match(/\/app\/([^\/\?]+)/);
                    if (match) {
                        const taskId = match[1];
                        if (!tasks.has(taskId)) {
                            tasks.set(taskId, {
                                id: taskId,
                                title: (item.textContent || '').trim().substring(0, 100),
                                href: link.href,
                                index: taskIndex++
                            });
                        }
                    }
                }
            });
        });
        
        // 轉換為數組並排序
        const taskArray = Array.from(tasks.values());
        taskArray.sort((a, b) => a.index - b.index);
        
        return {
            tasks: taskArray,
            debug: {
                totalFound: taskArray.length,
                selectors: {
                    sidebarFound: !!document.querySelector(sidebarSelectors.join(',')),
                    totalLinks: document.querySelectorAll('a[href*="/app/"]').length,
                    visibleLinks: Array.from(document.querySelectorAll('a[href*="/app/"]'))
                        .filter(a => a.offsetParent !== null).length
                }
            }
        };
        """
        
        # 首次收集
        result = self.driver.execute_script(collect_script)
        initial_count = len(result['tasks'])
        logger.info(f"初次收集: {initial_count} 個任務")
        logger.info(f"調試信息: {result['debug']}")
        
        # 如果任務太少，嘗試滾動收集更多
        if initial_count < 10:
            logger.info("\n嘗試滾動加載更多任務...")
            all_tasks = self._scroll_and_collect(result['tasks'])
        else:
            all_tasks = result['tasks']
            
        return all_tasks
        
    def _scroll_and_collect(self, initial_tasks):
        """滾動並收集更多任務"""
        all_tasks = {task['id']: task for task in initial_tasks}
        
        # 查找可滾動的容器
        scrollable_script = """
        // 查找可滾動的容器
        const candidates = [
            document.querySelector('aside'),
            document.querySelector('.sidebar'),
            document.querySelector('[class*="sidebar"]'),
            document.querySelector('.conversation-list'),
            document.querySelector('[class*="scroll"]'),
            document.querySelector('[style*="overflow"]')
        ].filter(el => el !== null);
        
        // 找到實際可滾動的
        for (const el of candidates) {
            if (el.scrollHeight > el.clientHeight) {
                return {
                    found: true,
                    selector: el.tagName + '.' + el.className,
                    scrollHeight: el.scrollHeight,
                    clientHeight: el.clientHeight
                };
            }
        }
        return { found: false };
        """
        
        scrollable = self.driver.execute_script(scrollable_script)
        
        if scrollable['found']:
            logger.info(f"找到可滾動容器: {scrollable['selector']}")
            
            # 滾動收集
            for i in range(20):  # 最多滾動20次
                # 向下滾動
                self.driver.execute_script("""
                    const scrollables = document.querySelectorAll('aside, .sidebar, [class*="sidebar"], .conversation-list');
                    scrollables.forEach(el => {
                        if (el.scrollHeight > el.clientHeight) {
                            el.scrollTop = el.scrollHeight;
                        }
                    });
                    window.scrollTo(0, document.body.scrollHeight);
                """)
                
                time.sleep(1.5)  # 等待加載
                
                # 收集新任務
                result = self.driver.execute_script(collect_script)
                
                for task in result['tasks']:
                    all_tasks[task['id']] = task
                    
                new_count = len(all_tasks)
                logger.info(f"滾動 {i+1} 次後: {new_count} 個任務")
                
                # 如果沒有新任務，停止滾動
                if new_count == len(all_tasks) and i > 2:
                    break
                    
        return list(all_tasks.values())
        
    def _save_results(self, tasks):
        """保存結果"""
        # 保存完整任務列表
        tasks_file = self.output_dir / "all_sidebar_tasks.json"
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(tasks),
                'tasks': tasks,
                'collected_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        # 生成 replay URLs
        urls_file = self.output_dir / "sidebar_replay_urls.txt"
        with open(urls_file, 'w', encoding='utf-8') as f:
            f.write(f"# Manus 側邊欄任務 - {len(tasks)} 個\n")
            f.write(f"# 收集時間: {datetime.now().isoformat()}\n\n")
            
            for task in tasks:
                f.write(f"# {task.get('number', task['index']+1)}. {task['title']}\n")
                f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
                
        logger.info(f"\n💾 已保存:")
        logger.info(f"  任務列表: {tasks_file}")
        logger.info(f"  Replay URLs: {urls_file}")
        
    def _debug_page_structure(self):
        """調試頁面結構"""
        logger.info("\n🔍 調試頁面結構...")
        
        debug_script = """
        const debug = {
            url: window.location.href,
            title: document.title,
            hasAside: !!document.querySelector('aside'),
            hasSidebar: !!document.querySelector('.sidebar, [class*="sidebar"]'),
            totalLinks: document.querySelectorAll('a').length,
            appLinks: document.querySelectorAll('a[href*="/app/"]').length,
            visibleElements: []
        };
        
        // 收集可見的主要元素
        const mainElements = document.querySelectorAll('aside, nav, [class*="sidebar"], [class*="panel"], [class*="list"]');
        mainElements.forEach(el => {
            if (el.offsetParent !== null) {
                debug.visibleElements.push({
                    tag: el.tagName,
                    class: el.className,
                    id: el.id,
                    childLinks: el.querySelectorAll('a').length
                });
            }
        });
        
        return debug;
        """
        
        debug_info = self.driver.execute_script(debug_script)
        
        # 保存調試信息
        debug_file = self.output_dir / "debug_info.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(debug_info, f, ensure_ascii=False, indent=2)
            
        logger.info(f"調試信息已保存: {debug_file}")
        
        # 保存頁面源碼
        source_file = self.output_dir / "page_source.html"
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
            
        logger.info(f"頁面源碼已保存: {source_file}")


def main():
    """主函數"""
    collector = ManusSidebarCollector()
    collector.collect_from_sidebar()


if __name__ == "__main__":
    main()