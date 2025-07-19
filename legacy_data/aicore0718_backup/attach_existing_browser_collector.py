#!/usr/bin/env python3
"""
連接到現有瀏覽器會話的 Manus 數據收集器
支持 Chrome 和 Safari，直接使用已登錄的會話
"""

import asyncio
import json
import subprocess
import platform
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttachBrowserCollector:
    """連接到現有瀏覽器會話收集數據"""
    
    def __init__(self, browser_type: str = "chrome"):
        self.browser_type = browser_type.lower()
        self.driver = None
        self.collected_data = []
        self.output_dir = Path(f"./data/manus_{browser_type}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_chrome_remote_debugging(self):
        """設置 Chrome 遠程調試"""
        logger.info("設置 Chrome 遠程調試...")
        
        # 檢查是否已經有 Chrome 在運行遠程調試
        try:
            # 嘗試連接到現有的調試端口
            import requests
            response = requests.get('http://localhost:9222/json', timeout=1)
            if response.status_code == 200:
                logger.info("✅ 檢測到 Chrome 已在運行遠程調試模式")
                return
        except:
            pass
        
        # 如果沒有運行，提示用戶手動啟動
        system = platform.system()
        
        if system == "Darwin":  # macOS
            chrome_cmd = '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222'
        elif system == "Windows":
            chrome_cmd = '"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222'
        else:  # Linux
            chrome_cmd = 'google-chrome --remote-debugging-port=9222'
        
        logger.info("\n" + "="*60)
        logger.info("請手動啟動 Chrome 遠程調試模式：")
        logger.info("\n1. 關閉所有 Chrome 窗口")
        logger.info("\n2. 在終端運行以下命令：")
        logger.info(f"\n   {chrome_cmd}")
        logger.info("\n3. Chrome 啟動後，登錄到 Manus")
        logger.info("\n4. 確認登錄成功後，回到這裡按 Enter 繼續...")
        logger.info("="*60 + "\n")
        
        input("按 Enter 確認已完成上述步驟...")
    
    def connect_to_chrome(self):
        """連接到運行中的 Chrome"""
        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ 成功連接到 Chrome")
            return True
        except Exception as e:
            logger.error(f"連接 Chrome 失敗: {e}")
            return False
    
    def connect_to_safari(self):
        """連接到 Safari"""
        # Safari 需要在開發者菜單中啟用"允許遠程自動化"
        logger.info("連接到 Safari...")
        logger.info("請確保已在 Safari 開發者菜單中啟用'允許遠程自動化'")
        
        try:
            # Safari 不支持連接現有會話，但會使用當前用戶的 Safari 數據
            safari_options = SafariOptions()
            self.driver = webdriver.Safari(options=safari_options)
            
            # 導航到 Manus 檢查登錄狀態
            self.driver.get("https://manus.im")
            time.sleep(2)
            
            logger.info("✅ Safari 已連接")
            return True
            
        except Exception as e:
            logger.error(f"連接 Safari 失敗: {e}")
            logger.info("請確保：")
            logger.info("1. 在 Safari 偏好設置 > 高級 中勾選'在菜單欄中顯示開發菜單'")
            logger.info("2. 在開發菜單中勾選'允許遠程自動化'")
            return False
    
    def check_manus_login(self) -> bool:
        """檢查 Manus 登錄狀態"""
        try:
            # 檢查是否有用戶頭像或其他登錄標識
            user_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='user'], [class*='avatar']")
            if user_elements:
                logger.info("✅ 已登錄 Manus")
                return True
            
            # 檢查是否在登錄頁面
            login_elements = self.driver.find_elements(By.XPATH, "//button[contains(text(), '登錄')]")
            if login_elements:
                logger.info("❌ 未登錄，請在瀏覽器中手動登錄")
                return False
                
            return True  # 假設已登錄
            
        except Exception as e:
            logger.warning(f"檢查登錄狀態時出錯: {e}")
            return True  # 假設已登錄
    
    def extract_replay_data(self, replay_url: str) -> Optional[Dict[str, Any]]:
        """從 replay URL 提取數據"""
        try:
            logger.info(f"提取: {replay_url}")
            
            # 打開新標籤頁
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # 訪問 replay
            self.driver.get(replay_url)
            
            # 等待頁面加載
            wait = WebDriverWait(self.driver, 20)
            
            # 等待消息加載
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='message']")))
            time.sleep(2)  # 額外等待確保動態內容加載
            
            # 提取數據
            conversation_data = self._extract_conversation_data()
            
            # 關閉標籤頁
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return conversation_data
            
        except Exception as e:
            logger.error(f"提取失敗 {replay_url}: {e}")
            # 確保切換回主標籤頁
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            return None
    
    def _extract_conversation_data(self) -> Dict[str, Any]:
        """從當前頁面提取對話數據"""
        # 方法1：嘗試通過 JavaScript 獲取數據
        try:
            js_data = self.driver.execute_script("""
                // 嘗試各種方式獲取數據
                if (window.conversationData) return window.conversationData;
                if (window.__INITIAL_STATE__) return window.__INITIAL_STATE__.conversation;
                if (window.__REDUX_STORE__) return window.__REDUX_STORE__.getState().conversation;
                
                // 嘗試從 React DevTools 獲取
                const reactRoot = document.querySelector('#root');
                if (reactRoot && reactRoot._reactRootContainer) {
                    // 遍歷 React Fiber 樹尋找數據
                    // 這需要更複雜的邏輯
                }
                
                return null;
            """)
            
            if js_data:
                return js_data
        except:
            pass
        
        # 方法2：解析 DOM
        messages = []
        
        # 查找所有消息容器
        message_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
        
        for element in message_elements:
            try:
                # 嘗試多種選擇器
                role = None
                content = None
                
                # 提取角色
                role_selectors = ["[class*='role']", "[class*='sender']", "[class*='author']"]
                for selector in role_selectors:
                    role_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    if role_elements:
                        role_text = role_elements[0].text.lower()
                        role = 'user' if any(word in role_text for word in ['user', '用戶', '我']) else 'assistant'
                        break
                
                # 提取內容
                content_selectors = ["[class*='content']", "[class*='text']", "[class*='body']"]
                for selector in content_selectors:
                    content_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    if content_elements:
                        content = content_elements[0].text
                        break
                
                if not content:
                    content = element.text
                
                # 提取代碼塊
                code_blocks = []
                code_elements = element.find_elements(By.CSS_SELECTOR, "pre code")
                for code_element in code_elements:
                    code_blocks.append({
                        'code': code_element.text,
                        'language': code_element.get_attribute('class') or 'text'
                    })
                
                if content:
                    messages.append({
                        'role': role or 'unknown',
                        'content': content,
                        'code_blocks': code_blocks,
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.debug(f"解析消息元素失敗: {e}")
                continue
        
        return {
            'messages': messages,
            'message_count': len(messages),
            'extracted_at': datetime.now().isoformat(),
            'source': 'dom_parsing'
        }
    
    def collect_replays(self, replay_urls: List[str]) -> Dict[str, Any]:
        """批量收集 replay 數據"""
        # 連接瀏覽器
        if self.browser_type == "chrome":
            self.setup_chrome_remote_debugging()
            if not self.connect_to_chrome():
                return {"error": "無法連接到 Chrome"}
        else:
            if not self.connect_to_safari():
                return {"error": "無法連接到 Safari"}
        
        # 檢查登錄
        if not self.check_manus_login():
            logger.info("請先在瀏覽器中登錄 Manus，然後按 Enter 繼續...")
            input()
        
        # 收集數據
        results = {
            'successful': 0,
            'failed': 0,
            'data': [],
            'errors': []
        }
        
        for i, url in enumerate(replay_urls):
            logger.info(f"進度: {i+1}/{len(replay_urls)}")
            
            data = self.extract_replay_data(url)
            
            if data:
                data['replay_url'] = url
                results['data'].append(data)
                results['successful'] += 1
                
                # 每10個保存一次
                if (i + 1) % 10 == 0:
                    self._save_progress(results, i + 1)
            else:
                results['failed'] += 1
                results['errors'].append(url)
            
            # 避免過快請求
            time.sleep(2)
        
        # 保存最終結果
        self._save_final_results(results)
        
        # 關閉瀏覽器連接
        if self.driver:
            if self.browser_type == "safari":
                self.driver.quit()  # Safari 需要退出
            # Chrome 保持運行，只是斷開連接
        
        return results
    
    def _save_progress(self, results: Dict[str, Any], processed: int):
        """保存進度"""
        progress_file = self.output_dir / "collection_progress.json"
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processed': processed,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"進度已保存: {processed} 個已處理")
    
    def _save_final_results(self, results: Dict[str, Any]):
        """保存最終結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存原始數據
        raw_file = self.output_dir / f"raw_data_{timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 創建訓練數據
        training_pairs = self._create_training_pairs(results['data'])
        
        # 保存訓練數據
        training_file = self.output_dir / f"training_pairs_{timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_pairs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n結果已保存:")
        logger.info(f"  原始數據: {raw_file}")
        logger.info(f"  訓練數據: {training_file}")
        logger.info(f"  成功: {results['successful']}")
        logger.info(f"  失敗: {results['failed']}")
        logger.info(f"  訓練對: {len(training_pairs)}")
    
    def _create_training_pairs(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """創建訓練對"""
        training_pairs = []
        
        for conv in conversations:
            messages = conv.get('messages', [])
            
            for i in range(len(messages) - 1):
                if (messages[i].get('role') == 'user' and 
                    messages[i + 1].get('role') == 'assistant'):
                    
                    user_content = messages[i]['content']
                    assistant_content = messages[i + 1]['content']
                    
                    # 基本質量檢查
                    if len(user_content) > 10 and len(assistant_content) > 50:
                        training_pairs.append({
                            'input': user_content,
                            'output': assistant_content,
                            'source': conv['replay_url'],
                            'has_code': any(cb for cb in messages[i + 1].get('code_blocks', [])),
                            'timestamp': conv['extracted_at']
                        })
        
        return training_pairs


# 簡單的使用腳本
def create_collection_script():
    """創建一個簡單的收集腳本"""
    script_content = '''#!/usr/bin/env python3
"""
Manus Replay 數據收集腳本
使用方法：
1. 確保 Chrome 或 Safari 已登錄 Manus
2. 在 replay_urls.txt 中添加要收集的 URLs
3. 運行此腳本
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_collection.attach_existing_browser_collector import AttachBrowserCollector

def main():
    # 讀取 URLs
    urls_file = "replay_urls.txt"
    if not os.path.exists(urls_file):
        with open(urls_file, 'w') as f:
            f.write("# 在下面添加 Manus replay URLs，每行一個\\n")
            f.write("# https://manus.im/share/xxx?replay=1\\n")
        print(f"請在 {urls_file} 中添加要收集的 URLs")
        return
    
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("沒有找到 URLs")
        return
    
    print(f"準備收集 {len(urls)} 個 replays")
    
    # 選擇瀏覽器
    browser = input("使用哪個瀏覽器？(chrome/safari) [默認: chrome]: ").strip().lower()
    if browser not in ['chrome', 'safari']:
        browser = 'chrome'
    
    # 創建收集器
    collector = AttachBrowserCollector(browser_type=browser)
    
    # 開始收集
    results = collector.collect_replays(urls)
    
    print(f"\\n收集完成！")
    print(f"成功: {results['successful']}")
    print(f"失敗: {results['failed']}")

if __name__ == "__main__":
    main()
'''
    
    script_file = Path("collect_manus_data.py")
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # 使腳本可執行
    import stat
    script_file.chmod(script_file.stat().st_mode | stat.S_IEXEC)
    
    logger.info(f"已創建收集腳本: {script_file}")
    logger.info("使用方法：python collect_manus_data.py")


# 運行示例
if __name__ == "__main__":
    # 創建簡單的收集腳本
    create_collection_script()
    
    print("\n使用說明：")
    print("1. 運行 'python collect_manus_data.py'")
    print("2. 選擇您已登錄的瀏覽器 (Chrome/Safari)")
    print("3. 腳本會自動收集數據")
    print("\n注意：")
    print("- Chrome: 腳本會啟動一個新的 Chrome 實例並連接")
    print("- Safari: 需要在開發者菜單啟用'允許遠程自動化'")