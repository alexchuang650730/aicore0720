#!/usr/bin/env python3
"""
全自動 Manus 數據收集器
自動提取所有任務並收集數據
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoManusCollector:
    """全自動 Manus 收集器"""
    
    def __init__(self, browser_type="chrome"):
        self.browser_type = browser_type
        self.driver = None
        self.output_dir = Path(f"./data/manus_{browser_type}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_browser(self):
        """設置瀏覽器（使用現有配置文件避免重新登錄）"""
        if self.browser_type == "chrome":
            options = ChromeOptions()
            
            # 檢查是否有遠程調試端口在運行
            import requests
            try:
                response = requests.get('http://localhost:9222/json', timeout=1)
                if response.status_code == 200:
                    # 方案1: 連接到遠程調試端口
                    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                    self.driver = webdriver.Chrome(options=options)
                    logger.info("✅ 連接到現有 Chrome 實例")
                    return
            except:
                logger.info("未找到遠程調試端口，使用新的瀏覽器實例")
            
            # 方案2: 創建臨時配置文件（複製現有 cookies）
            import tempfile
            import shutil
            
            temp_dir = tempfile.mkdtemp()
            options.add_argument(f"--user-data-dir={temp_dir}")
            
            # 防檢測設置
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            
            self.driver = webdriver.Chrome(options=options)
        else:
            # Safari
            safari_options = SafariOptions()
            self.driver = webdriver.Safari(options=safari_options)
            
        logger.info(f"✅ {self.browser_type} 瀏覽器已啟動")
        
    def auto_collect_all(self, start_url):
        """全自動收集所有任務"""
        logger.info("🚀 開始全自動收集...")
        
        # 設置瀏覽器
        self.setup_browser()
        
        try:
            # 訪問起始頁面
            self.driver.get(start_url)
            time.sleep(3)
            
            # 檢查登錄狀態
            if not self._check_logged_in():
                logger.info("❌ 未自動檢測到登錄狀態")
                logger.info("請在打開的瀏覽器中登錄 Manus")
                logger.info("登錄成功後，按 Enter 繼續...")
                input()
                
                # 手動確認
                confirm = input("您是否已經成功登錄？(y/n) [默認: y]: ").strip().lower()
                if confirm == 'n':
                    logger.error("請先登錄再繼續")
                    return
                    
                logger.info("✅ 手動確認已登錄，繼續收集...")
                
            # 自動提取所有任務
            all_tasks = self._auto_extract_all_tasks()
            logger.info(f"✅ 找到 {len(all_tasks)} 個任務")
            
            # 保存任務列表
            self._save_task_list(all_tasks)
            
            # 收集每個任務的對話數據
            all_conversations = []
            for i, task in enumerate(all_tasks):
                logger.info(f"\n收集任務 {i+1}/{len(all_tasks)}: {task['title']}")
                
                conversation = self._collect_task_conversation(task['shareUrl'])
                if conversation:
                    conversation['task_info'] = task
                    all_conversations.append(conversation)
                    
                # 每10個任務保存一次進度
                if (i + 1) % 10 == 0:
                    self._save_progress(all_conversations, i + 1)
                    
                # 避免過快請求
                time.sleep(2)
                
            # 保存最終結果
            self._save_final_results(all_conversations)
            
            logger.info(f"\n✅ 自動收集完成！")
            logger.info(f"成功收集: {len(all_conversations)}/{len(all_tasks)} 個任務")
            
        finally:
            self.driver.quit()
            
    def _check_logged_in(self):
        """檢查是否已登錄"""
        try:
            # 等待頁面加載
            time.sleep(2)
            
            # 方法1: 檢查 URL 是否包含 /app/
            current_url = self.driver.current_url
            if '/app/' in current_url:
                logger.info("✅ 檢測到應用頁面，已登錄")
                return True
                
            # 方法2: 查找用戶相關元素
            user_selectors = [
                "[class*='user']",
                "[class*='avatar']", 
                "[class*='profile']",
                "[id*='user']",
                "img[src*='avatar']",
                ".user-info",
                ".sidebar"  # Manus 通常有側邊欄
            ]
            
            for selector in user_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"✅ 找到登錄標識: {selector}")
                    return True
                    
            # 方法3: 檢查是否有登錄按鈕（如果有說明未登錄）
            login_elements = self.driver.find_elements(By.XPATH, "//button[contains(text(), '登錄') or contains(text(), 'Login') or contains(text(), 'Sign')]")
            if login_elements:
                logger.info("❌ 找到登錄按鈕，未登錄")
                return False
                
            # 方法4: 執行 JavaScript 檢查
            try:
                is_logged = self.driver.execute_script("""
                    // 檢查常見的登錄狀態
                    if (window.localStorage.getItem('token')) return true;
                    if (window.localStorage.getItem('user')) return true;
                    if (document.cookie.includes('session')) return true;
                    if (document.querySelector('.conversation-list')) return true;
                    return false;
                """)
                if is_logged:
                    logger.info("✅ JavaScript 檢測到登錄狀態")
                    return True
            except:
                pass
                
            return False
        except Exception as e:
            logger.error(f"檢查登錄狀態時出錯: {e}")
            return False
            
    def _auto_extract_all_tasks(self):
        """自動提取所有任務（包含自動滾動）"""
        logger.info("📋 自動提取任務列表...")
        
        # 執行 JavaScript 自動滾動並收集
        extract_script = """
        return new Promise(async (resolve) => {
            const sidebar = document.querySelector('.sidebar, [class*="task-list"], [class*="conversation-list"]');
            if (!sidebar) {
                resolve([]);
                return;
            }
            
            const allTasks = new Map();
            let previousCount = 0;
            let scrollAttempts = 0;
            
            // 滾動到頂部
            sidebar.scrollTop = 0;
            await new Promise(r => setTimeout(r, 500));
            
            while (scrollAttempts < 50) {
                // 收集當前可見的任務
                const items = document.querySelectorAll('[class*="conversation"], [class*="task-item"], .sidebar-item');
                
                items.forEach(item => {
                    const link = item.querySelector('a[href*="/app/"]');
                    if (link) {
                        const href = link.href;
                        const match = href.match(/\\/app\\/([^\\/\\?]+)/);
                        if (match) {
                            const taskId = match[1];
                            const title = item.innerText.split('\\n')[0].trim();
                            const shareUrl = `https://manus.im/share/${taskId}?replay=1`;
                            
                            allTasks.set(taskId, {
                                title: title || `任務 ${allTasks.size + 1}`,
                                taskId: taskId,
                                shareUrl: shareUrl,
                                appUrl: href
                            });
                        }
                    }
                });
                
                // 滾動到底部
                sidebar.scrollTop = sidebar.scrollHeight;
                await new Promise(r => setTimeout(r, 1000));
                
                // 檢查是否有新任務
                if (allTasks.size === previousCount) {
                    scrollAttempts++;
                    if (scrollAttempts > 3) break;
                } else {
                    scrollAttempts = 0;
                    previousCount = allTasks.size;
                }
            }
            
            resolve(Array.from(allTasks.values()));
        });
        """
        
        # 執行腳本
        tasks = self.driver.execute_script(extract_script)
        
        return tasks
        
    def _collect_task_conversation(self, share_url):
        """收集單個任務的對話"""
        try:
            # 在新標籤頁打開
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # 訪問分享頁面
            self.driver.get(share_url)
            
            # 等待內容加載
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='message']")))
            time.sleep(2)
            
            # 提取對話數據
            conversation_data = self._extract_conversation()
            
            # 關閉標籤頁
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return conversation_data
            
        except Exception as e:
            logger.error(f"收集失敗: {e}")
            # 確保回到主標籤頁
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            return None
            
    def _extract_conversation(self):
        """提取對話數據"""
        # 使用 JavaScript 提取所有數據
        extract_script = """
        const messages = [];
        
        // 嘗試從頁面狀態獲取
        if (window.conversationData) {
            return window.conversationData;
        }
        
        // 從 DOM 提取
        document.querySelectorAll('[class*="message"]').forEach((el, i) => {
            const role = i % 2 === 0 ? 'user' : 'assistant';
            const content = el.innerText;
            
            if (content) {
                messages.push({
                    role: role,
                    content: content,
                    index: i
                });
            }
        });
        
        // 提取代碼塊
        const codeBlocks = [];
        document.querySelectorAll('pre code').forEach(el => {
            codeBlocks.push({
                language: el.className || 'text',
                code: el.innerText
            });
        });
        
        return {
            messages: messages,
            codeBlocks: codeBlocks,
            messageCount: messages.length,
            extractedAt: new Date().toISOString()
        };
        """
        
        data = self.driver.execute_script(extract_script)
        
        # 創建訓練對
        if data and data.get('messages'):
            data['trainingPairs'] = self._create_training_pairs(data['messages'])
            
        return data
        
    def _create_training_pairs(self, messages):
        """創建訓練對"""
        pairs = []
        
        for i in range(len(messages) - 1):
            if messages[i]['role'] == 'user' and messages[i + 1]['role'] == 'assistant':
                pairs.append({
                    'input': messages[i]['content'],
                    'output': messages[i + 1]['content'],
                    'index': i
                })
                
        return pairs
        
    def _save_task_list(self, tasks):
        """保存任務列表"""
        file_path = self.output_dir / "all_tasks.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'totalTasks': len(tasks),
                'tasks': tasks,
                'extractedAt': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        # 同時保存 replay_urls.txt
        urls_file = self.output_dir / "replay_urls.txt"
        with open(urls_file, 'w') as f:
            f.write(f"# 自動提取的 {len(tasks)} 個 Manus replay URLs\n")
            f.write(f"# 提取時間: {datetime.now().isoformat()}\n\n")
            
            for i, task in enumerate(tasks):
                f.write(f"# {i+1}. {task['title']}\n")
                f.write(f"{task['shareUrl']}\n\n")
                
        logger.info(f"💾 任務列表已保存: {file_path}")
        logger.info(f"📝 Replay URLs 已保存: {urls_file}")
        
    def _save_progress(self, conversations, processed):
        """保存進度"""
        progress_file = self.output_dir / "collection_progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processed': processed,
                'conversations': conversations,
                'timestamp': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
    def _save_final_results(self, conversations):
        """保存最終結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 完整數據
        full_data_file = self.output_dir / f"all_conversations_{timestamp}.json"
        with open(full_data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'totalConversations': len(conversations),
                'conversations': conversations,
                'collectionTime': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        # 訓練數據
        training_pairs = []
        for conv in conversations:
            if conv and 'trainingPairs' in conv:
                for pair in conv['trainingPairs']:
                    pair['source'] = conv.get('task_info', {}).get('title', 'unknown')
                    training_pairs.append(pair)
                    
        training_file = self.output_dir / f"training_pairs_{timestamp}.jsonl"
        with open(training_file, 'w', encoding='utf-8') as f:
            for pair in training_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')
                
        logger.info(f"\n💾 數據已保存:")
        logger.info(f"  完整數據: {full_data_file}")
        logger.info(f"  訓練數據: {training_file} ({len(training_pairs)} 對)")


def main():
    """主函數 - 完全自動化"""
    print("""
    🤖 Manus 全自動數據收集器
    
    功能：
    1. 自動提取所有任務（無需手動操作）
    2. 自動收集每個任務的對話
    3. 自動生成訓練數據
    
    要求：
    - 您已經在瀏覽器中登錄過 Manus
    - Chrome 或 Safari
    """)
    
    # 獲取起始 URL
    start_url = input("\n請輸入任意 Manus 頁面 URL [默認使用您提供的]: ").strip()
    if not start_url:
        start_url = "https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1"
        
    # 選擇瀏覽器
    browser = input("\n使用哪個瀏覽器？(chrome/safari) [默認: chrome]: ").strip().lower() or "chrome"
    
    # 開始自動收集
    collector = AutoManusCollector(browser_type=browser)
    collector.auto_collect_all(start_url)
    
    print("\n✅ 全自動收集完成！")
    print(f"數據已保存到: ./data/manus_{browser}/")


if __name__ == "__main__":
    main()