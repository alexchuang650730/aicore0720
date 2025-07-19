#!/usr/bin/env python3
"""
Manus Selenium 數據收集器
專門針對 Manus.im 的結構優化
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManusSeleniumCollector:
    """Manus 專用 Selenium 收集器"""
    
    def __init__(self, browser_type: str = "chrome", headless: bool = False):
        self.browser_type = browser_type
        self.headless = headless
        self.driver = None
        self.output_dir = Path(f"./data/manus_{browser_type}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_chrome(self):
        """設置 Chrome"""
        options = ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
            
        # 防檢測設置
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 用戶數據目錄，保持登錄狀態
        options.add_argument(f'--user-data-dir={Path.home()}/Library/Application Support/Google/Chrome')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("✅ Chrome 已啟動")
        except Exception as e:
            logger.error(f"Chrome 啟動失敗: {e}")
            logger.info("嘗試使用新的用戶數據目錄...")
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=options)
            
    def collect_replay(self, replay_url: str) -> Optional[Dict[str, Any]]:
        """收集單個 replay"""
        try:
            logger.info(f"📥 收集: {replay_url}")
            
            # 訪問頁面
            self.driver.get(replay_url)
            
            # 等待頁面加載
            wait = WebDriverWait(self.driver, 20)
            
            # 等待消息容器加載
            # Manus 可能使用不同的類名，嘗試多個選擇器
            message_selectors = [
                "div[class*='message']",
                "div[class*='chat']",
                "div[class*='conversation']",
                ".message-container",
                ".chat-message",
                "[data-testid='message']"
            ]
            
            messages_found = False
            for selector in message_selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    messages_found = True
                    logger.info(f"找到消息容器: {selector}")
                    break
                except TimeoutException:
                    continue
                    
            if not messages_found:
                logger.warning("未找到消息容器，嘗試等待動態加載...")
                time.sleep(5)
                
            # 滾動到底部確保加載所有消息
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 提取數據
            conversation_data = self._extract_conversation_data()
            
            if conversation_data and conversation_data['messages']:
                # 保存數據
                self._save_conversation(replay_url, conversation_data)
                return conversation_data
            else:
                logger.warning(f"未能提取到有效數據: {replay_url}")
                # 保存頁面源碼供調試
                self._save_debug_info(replay_url)
                return None
                
        except Exception as e:
            logger.error(f"收集失敗 {replay_url}: {e}")
            self._save_debug_info(replay_url)
            return None
            
    def _extract_conversation_data(self) -> Dict[str, Any]:
        """提取對話數據"""
        messages = []
        
        # 方法1：通過 JavaScript 獲取數據
        try:
            js_data = self.driver.execute_script("""
                // 嘗試從全局變量獲取數據
                if (window.conversationData) return window.conversationData;
                if (window.__APP_DATA__) return window.__APP_DATA__;
                if (window.__INITIAL_STATE__) return window.__INITIAL_STATE__;
                
                // 嘗試從 React 獲取
                const root = document.querySelector('#root, #app, [data-reactroot]');
                if (root && root._reactRootContainer) {
                    // React 17+
                    const fiber = root._reactRootContainer._internalRoot.current;
                    let node = fiber;
                    while (node) {
                        if (node.memoizedProps && node.memoizedProps.messages) {
                            return {messages: node.memoizedProps.messages};
                        }
                        node = node.child || node.sibling;
                    }
                }
                
                // 嘗試從 Vue 獲取
                if (window.Vue || window.app) {
                    const app = window.app || document.querySelector('#app').__vue__;
                    if (app && app.$data) {
                        return app.$data;
                    }
                }
                
                return null;
            """)
            
            if js_data:
                logger.info("✅ 通過 JavaScript 獲取到數據")
                return self._process_js_data(js_data)
        except Exception as e:
            logger.debug(f"JavaScript 提取失敗: {e}")
            
        # 方法2：解析 DOM
        logger.info("嘗試從 DOM 提取數據...")
        
        # 嘗試多種消息選擇器
        message_selectors = [
            ("div[class*='message']", "role", "content"),
            ("div[class*='chat-message']", "sender", "text"),
            (".message-wrapper", ".message-role", ".message-content"),
            ("[data-message-id]", "[data-role]", "[data-content]")
        ]
        
        for container_sel, role_sel, content_sel in message_selectors:
            try:
                message_elements = self.driver.find_elements(By.CSS_SELECTOR, container_sel)
                if message_elements:
                    logger.info(f"找到 {len(message_elements)} 個消息元素")
                    
                    for element in message_elements:
                        try:
                            # 提取角色
                            role = self._extract_role(element, role_sel)
                            
                            # 提取內容
                            content = self._extract_content(element, content_sel)
                            
                            if content:
                                messages.append({
                                    'role': role,
                                    'content': content,
                                    'timestamp': datetime.now().isoformat()
                                })
                        except Exception as e:
                            logger.debug(f"處理消息元素失敗: {e}")
                            
                    if messages:
                        break
                        
            except Exception as e:
                logger.debug(f"選擇器 {container_sel} 失敗: {e}")
                
        # 創建訓練對
        training_pairs = self._create_training_pairs(messages)
        
        return {
            'messages': messages,
            'message_count': len(messages),
            'training_pairs': training_pairs,
            'extracted_at': datetime.now().isoformat(),
            'extraction_method': 'dom_parsing'
        }
        
    def _extract_role(self, element, role_selector) -> str:
        """提取消息角色"""
        try:
            # 嘗試通過選擇器找角色
            if role_selector.startswith('.') or role_selector.startswith('['):
                role_element = element.find_element(By.CSS_SELECTOR, role_selector)
                role_text = role_element.text.lower()
            else:
                role_text = element.get_attribute(role_selector) or ''
                
            # 判斷角色
            if any(word in role_text for word in ['user', '用戶', '我', 'human']):
                return 'user'
            elif any(word in role_text for word in ['assistant', 'ai', 'manus', 'bot']):
                return 'assistant'
            else:
                # 根據位置判斷（通常用戶在左/右交替）
                return 'user' if element.get_attribute('data-index') % 2 == 0 else 'assistant'
                
        except:
            # 默認根據樣式判斷
            classes = element.get_attribute('class') or ''
            if 'user' in classes or 'human' in classes:
                return 'user'
            return 'assistant'
            
    def _extract_content(self, element, content_selector) -> str:
        """提取消息內容"""
        try:
            if content_selector.startswith('.') or content_selector.startswith('['):
                content_element = element.find_element(By.CSS_SELECTOR, content_selector)
                return content_element.text
            else:
                return element.get_attribute(content_selector) or element.text
        except:
            return element.text
            
    def _process_js_data(self, js_data: Dict) -> Dict[str, Any]:
        """處理 JavaScript 獲取的數據"""
        messages = []
        
        # 處理不同的數據結構
        if 'messages' in js_data:
            raw_messages = js_data['messages']
        elif 'conversation' in js_data:
            raw_messages = js_data.get('conversation', {}).get('messages', [])
        else:
            raw_messages = []
            
        for msg in raw_messages:
            if isinstance(msg, dict):
                messages.append({
                    'role': msg.get('role', 'unknown'),
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp', datetime.now().isoformat())
                })
                
        training_pairs = self._create_training_pairs(messages)
        
        return {
            'messages': messages,
            'message_count': len(messages),
            'training_pairs': training_pairs,
            'extracted_at': datetime.now().isoformat(),
            'extraction_method': 'javascript'
        }
        
    def _create_training_pairs(self, messages: List[Dict]) -> List[Dict]:
        """創建訓練對"""
        pairs = []
        
        for i in range(len(messages) - 1):
            if messages[i]['role'] == 'user' and messages[i + 1]['role'] == 'assistant':
                pairs.append({
                    'input': messages[i]['content'],
                    'output': messages[i + 1]['content'],
                    'quality_score': self._calculate_quality_score(
                        messages[i]['content'],
                        messages[i + 1]['content']
                    )
                })
                
        return pairs
        
    def _calculate_quality_score(self, user_input: str, assistant_output: str) -> float:
        """計算質量分數"""
        score = 0.5
        
        # 長度合適
        if 20 < len(user_input) < 1000:
            score += 0.1
        if 50 < len(assistant_output) < 3000:
            score += 0.1
            
        # 包含代碼
        if '```' in assistant_output:
            score += 0.2
            
        # 有結構
        if any(marker in assistant_output for marker in ['1.', '2.', '步驟', '首先']):
            score += 0.1
            
        return min(score, 1.0)
        
    def _save_conversation(self, replay_url: str, data: Dict):
        """保存對話數據"""
        # 從 URL 提取 ID
        replay_id = replay_url.split('/')[-1].split('?')[0]
        
        # 保存完整數據
        output_file = self.output_dir / f"{replay_id}_{int(time.time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'replay_url': replay_url,
                'data': data
            }, f, ensure_ascii=False, indent=2)
            
        logger.info(f"💾 數據已保存: {output_file}")
        
    def _save_debug_info(self, replay_url: str):
        """保存調試信息"""
        debug_dir = self.output_dir / "debug"
        debug_dir.mkdir(exist_ok=True)
        
        replay_id = replay_url.split('/')[-1].split('?')[0]
        timestamp = int(time.time())
        
        # 保存頁面源碼
        with open(debug_dir / f"{replay_id}_{timestamp}.html", 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
            
        # 保存截圖
        self.driver.save_screenshot(str(debug_dir / f"{replay_id}_{timestamp}.png"))
        
        logger.info(f"調試信息已保存到: {debug_dir}")
        
    def collect_batch(self, replay_urls: List[str]) -> Dict[str, Any]:
        """批量收集"""
        # 設置瀏覽器
        if self.browser_type == "chrome":
            self.setup_chrome()
        else:
            logger.error(f"不支持的瀏覽器: {self.browser_type}")
            return {}
            
        results = {
            'successful': 0,
            'failed': 0,
            'data': []
        }
        
        try:
            for i, url in enumerate(replay_urls):
                logger.info(f"\n進度: {i+1}/{len(replay_urls)}")
                
                data = self.collect_replay(url)
                if data:
                    results['successful'] += 1
                    results['data'].append(data)
                else:
                    results['failed'] += 1
                    
                # 避免過快請求
                if i < len(replay_urls) - 1:
                    time.sleep(3)
                    
        finally:
            if self.driver:
                self.driver.quit()
                
        # 創建總結報告
        self._create_summary_report(results)
        
        return results
        
    def _create_summary_report(self, results: Dict):
        """創建總結報告"""
        report = {
            'collection_time': datetime.now().isoformat(),
            'total_urls': results['successful'] + results['failed'],
            'successful': results['successful'],
            'failed': results['failed'],
            'total_messages': sum(d['message_count'] for d in results['data']),
            'total_training_pairs': sum(len(d['training_pairs']) for d in results['data'])
        }
        
        report_file = self.output_dir / f"collection_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        logger.info(f"\n📊 收集報告已保存: {report_file}")
        logger.info(f"總計: {report['total_messages']} 條消息, {report['total_training_pairs']} 個訓練對")


def main():
    """測試函數"""
    # 測試 URL
    test_urls = [
        "https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1"
    ]
    
    collector = ManusSeleniumCollector(browser_type="chrome", headless=False)
    results = collector.collect_batch(test_urls)
    
    print(f"\n✅ 完成！成功: {results['successful']}, 失敗: {results['failed']}")


if __name__ == "__main__":
    main()