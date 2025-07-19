#!/usr/bin/env python3
"""
Manus 左側邊欄專用滾動收集器
確保只滾動左側的任務列表，不是中間的對話區
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


class ManusLeftSidebarCollector:
    """專門滾動左側任務列表的收集器"""
    
    def __init__(self):
        self.driver = None
        self.output_dir = Path("./data/manus_left_sidebar")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collected_tasks = {}
        
    def setup_browser(self):
        """設置瀏覽器"""
        options = ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)
        logger.info("✅ 瀏覽器已啟動")
        
    def collect_all_tasks(self):
        """收集所有任務"""
        logger.info("🚀 開始收集 Manus 左側任務列表")
        
        self.setup_browser()
        
        try:
            # 登錄
            self.driver.get("https://manus.im/login")
            logger.info("\n請完成以下步驟：")
            logger.info("1. 登錄 Manus")
            logger.info("2. 進入任意對話頁面（確保左側任務列表可見）")
            logger.info("3. 如果左側列表被隱藏，請點擊菜單按鈕打開它")
            input("\n準備好後按 Enter...")
            
            # 分析頁面佈局
            self._analyze_layout()
            
            # 讓用戶手動指定左側邊欄
            logger.info("\n🎯 請幫助定位左側任務列表...")
            logger.info("請在瀏覽器中：")
            logger.info("1. 將鼠標移到左側任務列表上")
            logger.info("2. 點擊任意一個任務項（但不要離開當前頁面）")
            input("\n完成後按 Enter...")
            
            # 自動檢測左側邊欄
            sidebar = self._detect_left_sidebar()
            
            if sidebar:
                logger.info("✅ 成功定位左側任務列表")
                
                # 開始收集
                self._collect_with_left_sidebar_scroll()
                
                # 保存結果
                if self.collected_tasks:
                    self._save_all_results()
                else:
                    logger.error("未收集到任務")
            else:
                logger.error("無法定位左側任務列表")
                self._manual_collection_mode()
                
        except Exception as e:
            logger.error(f"錯誤: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            input("\n按 Enter 關閉...")
            self.driver.quit()
            
    def _analyze_layout(self):
        """分析頁面佈局"""
        layout = self.driver.execute_script("""
            // 分析頁面佈局
            const layout = {
                windowWidth: window.innerWidth,
                windowHeight: window.innerHeight,
                leftElements: [],
                centerElements: [],
                rightElements: []
            };
            
            // 查找所有可能的容器
            const containers = document.querySelectorAll('div, aside, nav, section');
            
            containers.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 50 && rect.height > 200) {
                    const info = {
                        tag: el.tagName,
                        class: el.className || 'no-class',
                        x: Math.round(rect.x),
                        y: Math.round(rect.y),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        hasScroll: el.scrollHeight > el.clientHeight,
                        linkCount: el.querySelectorAll('a[href*="/app/"]').length
                    };
                    
                    // 根據位置分類
                    if (rect.x < 400) {
                        layout.leftElements.push(info);
                    } else if (rect.x < window.innerWidth - 400) {
                        layout.centerElements.push(info);
                    } else {
                        layout.rightElements.push(info);
                    }
                }
            });
            
            // 排序（按連結數量）
            layout.leftElements.sort((a, b) => b.linkCount - a.linkCount);
            
            return layout;
        """)
        
        logger.info(f"\n📐 頁面佈局分析:")
        logger.info(f"窗口大小: {layout['windowWidth']}x{layout['windowHeight']}")
        logger.info(f"\n左側元素 ({len(layout['leftElements'])}):")
        for i, el in enumerate(layout['leftElements'][:3]):
            logger.info(f"  {i+1}. {el['tag']}.{el['class'][:30]} - 位置:({el['x']},{el['y']}) 連結:{el['linkCount']} 可滾動:{el['hasScroll']}")
            
    def _detect_left_sidebar(self):
        """檢測左側任務列表"""
        detect_script = """
            // 查找左側任務列表的特徵
            let bestCandidate = null;
            let maxScore = 0;
            
            // 遍歷所有元素
            const elements = document.querySelectorAll('*');
            
            for (const el of elements) {
                const rect = el.getBoundingClientRect();
                
                // 基本條件：在左側，有一定大小
                if (rect.x < 400 && rect.width > 150 && rect.width < 500 && rect.height > 300) {
                    let score = 0;
                    
                    // 評分標準
                    // 1. 包含多個 app 連結
                    const appLinks = el.querySelectorAll('a[href*="/app/"]');
                    score += appLinks.length * 10;
                    
                    // 2. 可滾動
                    if (el.scrollHeight > el.clientHeight) {
                        score += 20;
                    }
                    
                    // 3. 在左側邊緣
                    if (rect.x < 100) {
                        score += 10;
                    }
                    
                    // 4. 寬度合適（200-400）
                    if (rect.width > 200 && rect.width < 400) {
                        score += 15;
                    }
                    
                    // 5. 包含列表元素
                    const listItems = el.querySelectorAll('li, [class*="item"], [class*="conversation"]');
                    score += listItems.length * 2;
                    
                    if (score > maxScore) {
                        maxScore = score;
                        bestCandidate = el;
                    }
                }
            }
            
            if (bestCandidate) {
                // 標記找到的元素
                bestCandidate.style.outline = '3px solid #00ff00';
                bestCandidate.style.outlineOffset = '-3px';
                
                // 保存引用
                window.__manusSidebar = bestCandidate;
                
                const rect = bestCandidate.getBoundingClientRect();
                return {
                    found: true,
                    score: maxScore,
                    tag: bestCandidate.tagName,
                    class: bestCandidate.className,
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    scrollable: bestCandidate.scrollHeight > bestCandidate.clientHeight,
                    linkCount: bestCandidate.querySelectorAll('a[href*="/app/"]').length
                };
            }
            
            return { found: false };
        """
        
        result = self.driver.execute_script(detect_script)
        
        if result['found']:
            logger.info(f"\n✅ 找到左側任務列表:")
            logger.info(f"  標籤: {result['tag']}.{result['class']}")
            logger.info(f"  位置: ({result['x']}, {result['y']})")
            logger.info(f"  大小: {result['width']}x{result['height']}")
            logger.info(f"  連結數: {result['linkCount']}")
            logger.info(f"  可滾動: {result['scrollable']}")
            logger.info(f"  評分: {result['score']}")
            logger.info("\n✅ 已用綠色邊框標記左側任務列表")
            return True
        
        return False
        
    def _collect_with_left_sidebar_scroll(self):
        """滾動左側邊欄收集任務"""
        logger.info("\n📋 開始收集任務...")
        
        # 先滾動到頂部
        self.driver.execute_script("""
            if (window.__manusSidebar) {
                window.__manusSidebar.scrollTop = 0;
            }
        """)
        time.sleep(1)
        
        scroll_count = 0
        no_new_count = 0
        last_position = 0
        
        while no_new_count < 5:
            scroll_count += 1
            logger.info(f"\n--- 第 {scroll_count} 輪收集 ---")
            
            # 提取當前任務
            tasks = self.driver.execute_script("""
                if (!window.__manusSidebar) return {};
                
                const sidebar = window.__manusSidebar;
                const tasks = {};
                
                // 只從標記的側邊欄中提取
                const links = sidebar.querySelectorAll('a[href*="/app/"]');
                
                links.forEach((link, index) => {
                    const href = link.href;
                    const match = href.match(/\\/app\\/([^\\/\\?]+)/);
                    
                    if (match) {
                        const taskId = match[1];
                        
                        // 獲取任務文本
                        let container = link.closest('li, [class*="item"], div');
                        let taskText = container ? container.textContent : link.textContent;
                        taskText = taskText.trim().substring(0, 100);
                        
                        // 查找數字
                        const numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                                        '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                                        '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十'];
                        
                        let number = '';
                        for (const num of numbers) {
                            if (taskText.includes(num)) {
                                number = num;
                                break;
                            }
                        }
                        
                        tasks[taskId] = {
                            id: taskId,
                            title: taskText,
                            href: href,
                            number: number,
                            index: Object.keys(tasks).length
                        };
                    }
                });
                
                return tasks;
            """)
            
            # 更新收集的任務
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
                
            # 滾動左側邊欄
            scroll_info = self.driver.execute_script("""
                if (!window.__manusSidebar) return { error: 'No sidebar' };
                
                const sidebar = window.__manusSidebar;
                const before = sidebar.scrollTop;
                const scrollHeight = sidebar.scrollHeight;
                const clientHeight = sidebar.clientHeight;
                
                // 滾動一屏
                sidebar.scrollTop = before + clientHeight * 0.8;
                
                // 確保滾動生效
                const after = sidebar.scrollTop;
                const atBottom = (after + clientHeight) >= (scrollHeight - 10);
                
                return {
                    before: before,
                    after: after,
                    scrollHeight: scrollHeight,
                    clientHeight: clientHeight,
                    atBottom: atBottom,
                    scrolled: after > before
                };
            """)
            
            logger.info(f"滾動信息: 從 {scroll_info.get('before', 0)} 到 {scroll_info.get('after', 0)}")
            
            if scroll_info.get('atBottom'):
                logger.info("已到達底部")
                if no_new_count >= 2:
                    break
                    
            if not scroll_info.get('scrolled'):
                logger.warning("滾動可能失敗")
                
            # 等待加載
            time.sleep(2)
            
            # 保存進度
            if scroll_count % 5 == 0:
                self._save_progress()
                
        logger.info(f"\n✅ 收集完成，共 {len(self.collected_tasks)} 個任務")
        
    def _manual_collection_mode(self):
        """手動收集模式"""
        logger.info("\n切換到手動收集模式...")
        logger.info("請手動滾動左側任務列表")
        
        collected = 0
        while True:
            input("\n滾動後按 Enter 收集當前可見任務（輸入 'done' 完成）: ")
            
            if input().strip().lower() == 'done':
                break
                
            # 收集當前頁面所有任務
            tasks = self.driver.execute_script("""
                const tasks = {};
                document.querySelectorAll('a[href*="/app/"]').forEach((link, i) => {
                    const match = link.href.match(/\\/app\\/([^\\/\\?]+)/);
                    if (match) {
                        tasks[match[1]] = {
                            id: match[1],
                            title: link.textContent || `任務 ${i+1}`,
                            href: link.href
                        };
                    }
                });
                return tasks;
            """)
            
            new_count = 0
            for task_id, task_info in tasks.items():
                if task_id not in self.collected_tasks:
                    self.collected_tasks[task_id] = task_info
                    new_count += 1
                    
            logger.info(f"新增 {new_count} 個任務，總計 {len(self.collected_tasks)} 個")
            
    def _save_progress(self):
        """保存進度"""
        progress_file = self.output_dir / "progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'collected': len(self.collected_tasks),
                'timestamp': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
    def _save_all_results(self):
        """保存所有結果"""
        tasks = list(self.collected_tasks.values())
        
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
            f.write(f"# Manus 左側任務列表 - {len(tasks)} 個任務\n")
            f.write(f"# 收集時間: {datetime.now().isoformat()}\n")
            f.write("#" * 60 + "\n\n")
            
            for i, task in enumerate(tasks):
                number = task.get('number', '')
                title = task.get('title', f'任務 {i+1}')[:80]
                
                f.write(f"# {i+1}. {number} {title}\n")
                f.write(f"https://manus.im/share/{task['id']}?replay=1\n\n")
                
        logger.info(f"\n✅ 結果已保存:")
        logger.info(f"  任務數據: {tasks_file}")
        logger.info(f"  Replay URLs: {urls_file}")
        
        # 顯示統計
        logger.info(f"\n📊 統計:")
        logger.info(f"  總任務數: {len(tasks)}")
        logger.info(f"  帶數字標記: {len([t for t in tasks if t.get('number')])}")


def main():
    """主函數"""
    print("""
    🤖 Manus 左側邊欄專用收集器
    
    重要：這個工具會：
    1. 自動識別左側任務列表（綠色邊框標記）
    2. 只滾動左側列表，不會滾動中間對話區
    3. 持續收集直到所有任務
    
    請確保左側任務列表可見！
    """)
    
    collector = ManusLeftSidebarCollector()
    collector.collect_all_tasks()


if __name__ == "__main__":
    main()