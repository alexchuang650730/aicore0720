#!/usr/bin/env python3
"""
Manus 任務列表收集器
從 Manus 任務列表頁面提取所有任務和對話
"""

import json
import time
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManusTaskListCollector:
    """Manus 任務列表收集器"""
    
    def __init__(self):
        self.output_dir = Path("./data/manus_tasks")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.driver = None
        
    def setup_chrome(self):
        """連接到現有的 Chrome"""
        logger.info("連接到 Chrome...")
        
        options = ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("✅ 成功連接到 Chrome")
            return True
        except Exception as e:
            logger.error(f"連接失敗: {e}")
            logger.info("\n請確保：")
            logger.info('1. Chrome 以調試模式運行：')
            logger.info('   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222')
            logger.info('2. 已登錄 Manus')
            return False
            
    def extract_task_list(self, app_url: str):
        """從應用頁面提取任務列表"""
        logger.info(f"📋 提取任務列表: {app_url}")
        
        # 訪問應用頁面
        self.driver.get(app_url)
        
        # 等待任務列表加載
        wait = WebDriverWait(self.driver, 20)
        
        try:
            # 等待左側任務列表出現
            # Manus 的任務列表通常在左側邊欄
            logger.info("等待任務列表加載...")
            
            # 嘗試多種可能的選擇器
            task_selectors = [
                "div[class*='task-list']",
                "div[class*='sidebar'] div[class*='item']",
                "div[class*='conversation-list']",
                "div[class*='chat-list']",
                "[data-testid='task-item']",
                ".task-item",
                ".conversation-item"
            ]
            
            tasks = []
            for selector in task_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"找到 {len(elements)} 個任務使用選擇器: {selector}")
                        tasks = elements
                        break
                except:
                    continue
                    
            if not tasks:
                # 如果找不到，嘗試通過 JavaScript 獲取
                logger.info("嘗試通過 JavaScript 獲取任務列表...")
                tasks_data = self._extract_tasks_via_js()
                if tasks_data:
                    return tasks_data
                    
            # 提取任務信息
            task_list = []
            for i, task in enumerate(tasks):
                try:
                    task_info = {
                        'index': i,
                        'title': task.text.split('\n')[0] if task.text else f"任務 {i+1}",
                        'element': task
                    }
                    task_list.append(task_info)
                except Exception as e:
                    logger.debug(f"處理任務 {i} 失敗: {e}")
                    
            logger.info(f"✅ 找到 {len(task_list)} 個任務")
            return task_list
            
        except Exception as e:
            logger.error(f"提取任務列表失敗: {e}")
            # 保存截圖以供調試
            self.driver.save_screenshot(str(self.output_dir / "task_list_error.png"))
            return []
            
    def _extract_tasks_via_js(self):
        """通過 JavaScript 提取任務數據"""
        try:
            tasks_data = self.driver.execute_script("""
                // 嘗試從應用狀態獲取任務列表
                
                // 方法1：從 React 組件獲取
                const root = document.querySelector('#root, #app');
                if (root && root._reactRootContainer) {
                    // 遍歷查找任務數據
                    // ... React fiber 遍歷邏輯
                }
                
                // 方法2：從全局狀態獲取
                if (window.__APP_STATE__ && window.__APP_STATE__.tasks) {
                    return window.__APP_STATE__.tasks;
                }
                
                // 方法3：從 Redux 獲取
                if (window.__REDUX_STORE__) {
                    const state = window.__REDUX_STORE__.getState();
                    if (state.tasks || state.conversations) {
                        return state.tasks || state.conversations;
                    }
                }
                
                // 方法4：手動提取可見的任務
                const tasks = [];
                document.querySelectorAll('[class*="task"], [class*="conversation"]').forEach((el, i) => {
                    tasks.push({
                        index: i,
                        title: el.innerText.split('\\n')[0],
                        id: el.getAttribute('data-id') || i
                    });
                });
                
                return tasks.length > 0 ? tasks : null;
            """)
            
            if tasks_data:
                logger.info(f"✅ 通過 JavaScript 找到 {len(tasks_data)} 個任務")
                return tasks_data
                
        except Exception as e:
            logger.debug(f"JavaScript 提取失敗: {e}")
            
        return None
        
    def collect_all_tasks(self, app_url: str):
        """收集所有任務的對話數據"""
        if not self.setup_chrome():
            return
            
        # 提取任務列表
        tasks = self.extract_task_list(app_url)
        
        if not tasks:
            logger.warning("未找到任務")
            return
            
        # 收集每個任務的數據
        all_conversations = []
        
        for task in tasks:
            logger.info(f"\n處理任務 {task['index'] + 1}/{len(tasks)}: {task['title']}")
            
            try:
                # 點擊任務以查看對話
                if 'element' in task:
                    task['element'].click()
                    time.sleep(2)  # 等待對話加載
                    
                # 提取對話數據
                conversation = self._extract_conversation_data()
                
                if conversation:
                    conversation['task_title'] = task['title']
                    conversation['task_index'] = task['index']
                    all_conversations.append(conversation)
                    
                    # 保存單個任務數據
                    self._save_task_data(task['index'], conversation)
                    
            except Exception as e:
                logger.error(f"處理任務失敗: {e}")
                
            # 避免過快操作
            time.sleep(1)
            
        # 保存所有數據
        self._save_all_data(all_conversations)
        
        logger.info(f"\n✅ 收集完成！")
        logger.info(f"總任務數: {len(tasks)}")
        logger.info(f"成功收集: {len(all_conversations)}")
        
    def _extract_conversation_data(self):
        """提取當前對話數據"""
        try:
            # 等待消息加載
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='message']"))
            )
            
            # 提取消息
            messages = []
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
            
            for element in message_elements:
                try:
                    # 判斷角色
                    classes = element.get_attribute('class') or ''
                    role = 'user' if 'user' in classes else 'assistant'
                    
                    # 提取內容
                    content = element.text
                    
                    if content:
                        messages.append({
                            'role': role,
                            'content': content
                        })
                except:
                    continue
                    
            # 獲取分享連結
            share_url = self._get_share_url()
            
            return {
                'messages': messages,
                'message_count': len(messages),
                'share_url': share_url,
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"提取對話失敗: {e}")
            return None
            
    def _get_share_url(self):
        """獲取當前任務的分享連結"""
        try:
            # 查找分享按鈕
            share_button = self.driver.find_element(By.CSS_SELECTOR, "[class*='share'], [title*='分享']")
            share_button.click()
            time.sleep(1)
            
            # 獲取分享連結
            share_input = self.driver.find_element(By.CSS_SELECTOR, "input[value*='manus.im/share']")
            share_url = share_input.get_attribute('value')
            
            # 關閉分享對話框
            close_button = self.driver.find_element(By.CSS_SELECTOR, "[class*='close']")
            close_button.click()
            
            return share_url
            
        except:
            # 如果無法獲取分享連結，從當前 URL 推斷
            current_url = self.driver.current_url
            if '/app/' in current_url:
                task_id = current_url.split('/app/')[-1]
                return f"https://manus.im/share/{task_id}?replay=1"
                
        return None
        
    def _save_task_data(self, index: int, data: Dict):
        """保存單個任務數據"""
        filename = self.output_dir / f"task_{index:03d}_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def _save_all_data(self, conversations: List[Dict]):
        """保存所有數據"""
        # 完整數據
        all_data = {
            'total_tasks': len(conversations),
            'extraction_time': datetime.now().isoformat(),
            'conversations': conversations
        }
        
        filename = self.output_dir / f"all_tasks_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
            
        # 生成 replay URLs 列表
        replay_urls = []
        for conv in conversations:
            if conv.get('share_url'):
                replay_urls.append(conv['share_url'])
                
        urls_file = self.output_dir / "extracted_replay_urls.txt"
        with open(urls_file, 'w') as f:
            f.write("# 自動提取的 Manus replay URLs\n")
            for url in replay_urls:
                f.write(f"{url}\n")
                
        logger.info(f"\n💾 數據已保存:")
        logger.info(f"  完整數據: {filename}")
        logger.info(f"  Replay URLs: {urls_file}")
        
    def extract_from_sidebar_only(self):
        """僅從側邊欄提取任務信息（不點擊）"""
        logger.info("📋 快速提取任務列表（不載入對話）...")
        
        try:
            # 執行 JavaScript 提取所有任務信息
            tasks_info = self.driver.execute_script("""
                const tasks = [];
                
                // 查找所有可能的任務元素
                const selectors = [
                    '[class*="task"]',
                    '[class*="conversation"]',
                    '[class*="chat-item"]',
                    '.sidebar [class*="item"]'
                ];
                
                const foundElements = new Set();
                
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        if (!foundElements.has(el)) {
                            foundElements.add(el);
                            
                            // 提取任務信息
                            const title = el.innerText.split('\\n')[0];
                            const link = el.querySelector('a');
                            const href = link ? link.href : '';
                            
                            // 從 href 提取 ID
                            let taskId = '';
                            if (href.includes('/app/')) {
                                taskId = href.split('/app/')[1];
                            }
                            
                            tasks.push({
                                title: title,
                                taskId: taskId,
                                shareUrl: taskId ? `https://manus.im/share/${taskId}?replay=1` : '',
                                timestamp: el.querySelector('[class*="time"]')?.innerText || ''
                            });
                        }
                    });
                });
                
                return tasks;
            """)
            
            if tasks_info:
                logger.info(f"✅ 快速提取了 {len(tasks_info)} 個任務")
                
                # 保存任務列表
                self._save_task_list(tasks_info)
                
                return tasks_info
                
        except Exception as e:
            logger.error(f"快速提取失敗: {e}")
            
        return []
        
    def _save_task_list(self, tasks: List[Dict]):
        """保存任務列表"""
        filename = self.output_dir / f"task_list_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'total_tasks': len(tasks),
                'tasks': tasks,
                'extracted_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        # 生成 replay_urls.txt
        urls_file = self.output_dir / "all_replay_urls.txt"
        with open(urls_file, 'w') as f:
            f.write("# Manus 任務列表中的所有 replay URLs\n")
            f.write(f"# 提取時間: {datetime.now().isoformat()}\n")
            f.write(f"# 總數: {len(tasks)}\n\n")
            
            for task in tasks:
                if task.get('shareUrl'):
                    f.write(f"# {task['title']}\n")
                    f.write(f"{task['shareUrl']}\n\n")
                    
        logger.info(f"💾 任務列表已保存: {filename}")
        logger.info(f"📝 Replay URLs 已保存: {urls_file}")


def main():
    """主函數"""
    collector = ManusTaskListCollector()
    
    # 檢查 Chrome
    print("\n" + "="*60)
    print("Manus 任務列表收集器")
    print("="*60)
    print("\n請確保：")
    print('1. Chrome 以調試模式運行')
    print('2. 已登錄 Manus')
    print('3. 在 Manus 應用頁面（如 https://manus.im/app/xxx）')
    print("="*60)
    
    # 獲取應用 URL
    app_url = input("\n請輸入 Manus 應用 URL（或按 Enter 使用當前頁面）: ").strip()
    
    if not app_url:
        # 使用當前頁面
        if collector.setup_chrome():
            app_url = collector.driver.current_url
            print(f"使用當前頁面: {app_url}")
        else:
            return
            
    # 選擇收集模式
    print("\n選擇收集模式：")
    print("1. 快速模式（僅提取任務列表）")
    print("2. 完整模式（提取所有對話內容）")
    
    mode = input("\n選擇 (1/2) [默認: 1]: ").strip() or "1"
    
    if mode == "1":
        # 快速模式
        if not collector.driver and not collector.setup_chrome():
            return
        collector.extract_from_sidebar_only()
    else:
        # 完整模式
        collector.collect_all_tasks(app_url)
        
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()