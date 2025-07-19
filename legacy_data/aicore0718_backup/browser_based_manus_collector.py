#!/usr/bin/env python3
"""
基於瀏覽器的 Manus 數據收集系統
使用持久化瀏覽器會話避免重複認證
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import aiofiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserBasedManusCollector:
    """使用持久化瀏覽器會話的 Manus 數據收集器"""
    
    def __init__(self, user_data_dir: str = "./browser_data", headless: bool = False):
        self.user_data_dir = Path(user_data_dir)
        self.user_data_dir.mkdir(exist_ok=True)
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.collected_data = []
        
    async def setup_browser(self):
        """設置持久化瀏覽器"""
        logger.info("設置瀏覽器...")
        
        playwright = await async_playwright().start()
        
        # 使用 Chromium 並保存用戶數據
        self.browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ],
            # 偽裝成正常瀏覽器
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN'
        )
        
        self.page = await self.browser.new_page()
        
        # 注入反檢測腳本
        await self.page.add_init_script("""
            // 隱藏 webdriver 屬性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 隱藏自動化特徵
            window.chrome = {
                runtime: {}
            };
            
            // 隱藏 Playwright 特徵
            delete window.__playwright;
            delete window.__pw_manual;
        """)
        
        logger.info("瀏覽器設置完成")
    
    async def check_auth_status(self) -> bool:
        """檢查認證狀態"""
        try:
            # 訪問 Manus 主頁檢查是否已登錄
            await self.page.goto('https://manus.im', wait_until='networkidle')
            
            # 檢查是否有用戶頭像或其他登錄標識
            user_avatar = await self.page.query_selector('[data-testid="user-avatar"]')
            if user_avatar:
                logger.info("✅ 已認證")
                return True
            
            # 檢查是否在登錄頁面
            login_button = await self.page.query_selector('button:has-text("登錄")')
            if login_button:
                logger.info("❌ 未認證，需要登錄")
                return False
                
            return False
            
        except Exception as e:
            logger.error(f"檢查認證狀態失敗: {e}")
            return False
    
    async def manual_login(self):
        """手動登錄流程"""
        logger.info("請手動完成登錄...")
        
        # 導航到登錄頁面
        await self.page.goto('https://manus.im/login', wait_until='networkidle')
        
        # 等待用戶手動登錄
        logger.info("請在瀏覽器中完成登錄，登錄成功後按 Enter 繼續...")
        
        if not self.headless:
            # 非無頭模式下，等待用戶輸入
            input("按 Enter 確認已完成登錄...")
        else:
            # 無頭模式下，等待登錄成功的標識
            try:
                await self.page.wait_for_selector('[data-testid="user-avatar"]', timeout=300000)  # 5分鐘超時
                logger.info("✅ 登錄成功")
            except:
                logger.error("登錄超時")
                raise
    
    async def extract_replay_data(self, replay_url: str) -> Optional[Dict[str, Any]]:
        """從 replay URL 提取數據"""
        try:
            logger.info(f"提取數據: {replay_url}")
            
            # 訪問 replay 頁面
            await self.page.goto(replay_url, wait_until='networkidle')
            
            # 等待內容加載
            await self.page.wait_for_selector('.message-content', timeout=10000)
            
            # 方法1：嘗試從頁面上下文獲取數據
            conversation_data = await self.page.evaluate("""
                () => {
                    // 嘗試從全局變量獲取
                    if (window.conversationData) {
                        return window.conversationData;
                    }
                    
                    // 嘗試從 React 組件獲取
                    const reactRoot = document.querySelector('#root')._reactRootContainer;
                    if (reactRoot && reactRoot._internalRoot) {
                        const fiber = reactRoot._internalRoot.current;
                        // 遍歷查找對話數據
                        // ... React fiber 遍歷邏輯
                    }
                    
                    // 嘗試從 Redux store 獲取
                    if (window.__REDUX_STORE__) {
                        const state = window.__REDUX_STORE__.getState();
                        return state.conversation || state.messages;
                    }
                    
                    return null;
                }
            """)
            
            # 方法2：如果上述方法失敗，直接解析 DOM
            if not conversation_data:
                conversation_data = await self._extract_from_dom()
            
            # 方法3：監聽網絡請求
            if not conversation_data:
                conversation_data = await self._extract_from_network()
            
            if conversation_data:
                # 添加元數據
                conversation_data['replay_url'] = replay_url
                conversation_data['extracted_at'] = datetime.now().isoformat()
                
                return conversation_data
            else:
                logger.warning(f"無法提取數據: {replay_url}")
                return None
                
        except Exception as e:
            logger.error(f"提取失敗 {replay_url}: {e}")
            return None
    
    async def _extract_from_dom(self) -> Optional[Dict[str, Any]]:
        """從 DOM 提取對話數據"""
        try:
            messages = []
            
            # 獲取所有消息元素
            message_elements = await self.page.query_selector_all('.message-container')
            
            for element in message_elements:
                # 提取角色
                role_element = await element.query_selector('.message-role')
                role = await role_element.inner_text() if role_element else 'unknown'
                
                # 提取內容
                content_element = await element.query_selector('.message-content')
                content = await content_element.inner_text() if content_element else ''
                
                # 提取代碼塊
                code_blocks = []
                code_elements = await element.query_selector_all('pre code')
                for code_element in code_elements:
                    code = await code_element.inner_text()
                    language = await code_element.get_attribute('class') or ''
                    code_blocks.append({
                        'language': language.replace('language-', ''),
                        'code': code
                    })
                
                messages.append({
                    'role': 'user' if 'user' in role.lower() else 'assistant',
                    'content': content,
                    'code_blocks': code_blocks
                })
            
            return {
                'messages': messages,
                'message_count': len(messages),
                'source': 'dom_extraction'
            }
            
        except Exception as e:
            logger.error(f"DOM 提取失敗: {e}")
            return None
    
    async def _extract_from_network(self) -> Optional[Dict[str, Any]]:
        """從網絡請求提取數據"""
        conversation_data = None
        
        async def handle_response(response):
            nonlocal conversation_data
            if 'api/conversation' in response.url or 'replay' in response.url:
                try:
                    data = await response.json()
                    if 'messages' in data or 'conversation' in data:
                        conversation_data = data
                except:
                    pass
        
        # 監聽網絡響應
        self.page.on('response', handle_response)
        
        # 重新加載頁面觸發 API 請求
        await self.page.reload(wait_until='networkidle')
        
        # 等待數據
        await asyncio.sleep(2)
        
        # 移除監聽器
        self.page.remove_listener('response', handle_response)
        
        return conversation_data
    
    async def collect_batch(self, replay_urls: List[str], save_progress: bool = True) -> Dict[str, Any]:
        """批量收集 replay 數據"""
        results = {
            'successful': 0,
            'failed': 0,
            'data': [],
            'errors': []
        }
        
        # 設置瀏覽器
        await self.setup_browser()
        
        # 檢查認證
        if not await self.check_auth_status():
            await self.manual_login()
        
        # 處理每個 URL
        for i, url in enumerate(replay_urls):
            logger.info(f"處理進度: {i+1}/{len(replay_urls)}")
            
            try:
                data = await self.extract_replay_data(url)
                
                if data:
                    results['data'].append(data)
                    results['successful'] += 1
                    
                    # 保存進度
                    if save_progress and (i + 1) % 10 == 0:
                        await self._save_progress(results, i + 1)
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'url': url,
                        'error': 'No data extracted'
                    })
                    
                # 避免過快請求
                await asyncio.sleep(2)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'url': url,
                    'error': str(e)
                })
                
                # 發生錯誤時保存當前進度
                if save_progress:
                    await self._save_progress(results, i + 1)
        
        # 關閉瀏覽器
        await self.close()
        
        return results
    
    async def _save_progress(self, results: Dict[str, Any], processed: int):
        """保存收集進度"""
        progress_file = Path("./data/collection_progress.json")
        progress_file.parent.mkdir(exist_ok=True)
        
        progress_data = {
            'processed': processed,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        async with aiofiles.open(progress_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(progress_data, ensure_ascii=False, indent=2))
        
        logger.info(f"進度已保存: {processed} 個已處理")
    
    async def resume_from_progress(self, replay_urls: List[str]) -> Dict[str, Any]:
        """從上次進度恢復"""
        progress_file = Path("./data/collection_progress.json")
        
        if progress_file.exists():
            async with aiofiles.open(progress_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                progress_data = json.loads(content)
            
            processed = progress_data['processed']
            results = progress_data['results']
            
            logger.info(f"從進度恢復: 已處理 {processed} 個")
            
            # 繼續處理剩餘的
            remaining_urls = replay_urls[processed:]
            new_results = await self.collect_batch(remaining_urls)
            
            # 合併結果
            results['successful'] += new_results['successful']
            results['failed'] += new_results['failed']
            results['data'].extend(new_results['data'])
            results['errors'].extend(new_results['errors'])
            
            return results
        else:
            # 沒有進度文件，從頭開始
            return await self.collect_batch(replay_urls)
    
    async def close(self):
        """關閉瀏覽器"""
        if self.browser:
            await self.browser.close()
            logger.info("瀏覽器已關閉")


class ManusDataProcessor:
    """Manus 數據處理器"""
    
    def __init__(self):
        self.output_dir = Path("./data/processed_manus")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_collected_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """處理收集的原始數據"""
        processed_conversations = []
        
        for conversation in raw_data:
            processed = self._process_conversation(conversation)
            if processed:
                processed_conversations.append(processed)
        
        # 創建訓練數據集
        training_pairs = self._create_training_pairs(processed_conversations)
        
        # 統計分析
        statistics = self._analyze_statistics(training_pairs)
        
        return {
            'conversations': processed_conversations,
            'training_pairs': training_pairs,
            'statistics': statistics
        }
    
    def _process_conversation(self, conversation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """處理單個對話"""
        messages = conversation.get('messages', [])
        
        if len(messages) < 2:
            return None
        
        # 提取有用信息
        processed_messages = []
        for msg in messages:
            processed_msg = {
                'role': msg['role'],
                'content': msg['content'],
                'has_code': '```' in msg['content'],
                'length': len(msg['content'])
            }
            
            # 提取代碼塊
            if processed_msg['has_code']:
                processed_msg['code_blocks'] = self._extract_code_blocks(msg['content'])
            
            processed_messages.append(processed_msg)
        
        return {
            'replay_url': conversation.get('replay_url'),
            'messages': processed_messages,
            'turn_count': len(messages) // 2,
            'total_length': sum(m['length'] for m in processed_messages)
        }
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """提取代碼塊"""
        import re
        
        code_blocks = []
        pattern = r'```(\w*)\n(.*?)\n```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2)
            
            code_blocks.append({
                'language': language,
                'code': code,
                'lines': len(code.split('\n'))
            })
        
        return code_blocks
    
    def _create_training_pairs(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """創建訓練對"""
        training_pairs = []
        
        for conv in conversations:
            messages = conv['messages']
            
            for i in range(0, len(messages) - 1, 2):
                if i + 1 < len(messages):
                    user_msg = messages[i]
                    assistant_msg = messages[i + 1]
                    
                    if user_msg['role'] == 'user' and assistant_msg['role'] == 'assistant':
                        pair = {
                            'input': user_msg['content'],
                            'output': assistant_msg['content'],
                            'has_code': assistant_msg['has_code'],
                            'quality_score': self._calculate_quality_score(user_msg, assistant_msg),
                            'source': conv['replay_url']
                        }
                        
                        training_pairs.append(pair)
        
        return training_pairs
    
    def _calculate_quality_score(self, user_msg: Dict[str, Any], assistant_msg: Dict[str, Any]) -> float:
        """計算訓練對質量分數"""
        score = 0.5
        
        # 長度合適
        if 20 < user_msg['length'] < 1000:
            score += 0.1
        if 100 < assistant_msg['length'] < 3000:
            score += 0.1
        
        # 包含代碼
        if assistant_msg['has_code']:
            score += 0.2
        
        # 代碼質量
        if 'code_blocks' in assistant_msg:
            for block in assistant_msg['code_blocks']:
                if block['lines'] > 5:
                    score += 0.1
                    break
        
        return min(score, 1.0)
    
    def _analyze_statistics(self, training_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """統計分析"""
        total_pairs = len(training_pairs)
        with_code = len([p for p in training_pairs if p['has_code']])
        high_quality = len([p for p in training_pairs if p['quality_score'] > 0.7])
        
        return {
            'total_pairs': total_pairs,
            'pairs_with_code': with_code,
            'high_quality_pairs': high_quality,
            'code_percentage': (with_code / total_pairs * 100) if total_pairs > 0 else 0,
            'quality_percentage': (high_quality / total_pairs * 100) if total_pairs > 0 else 0
        }
    
    def save_processed_data(self, processed_data: Dict[str, Any]):
        """保存處理後的數據"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存訓練對
        training_file = self.output_dir / f"training_pairs_{timestamp}.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data['training_pairs'], f, ensure_ascii=False, indent=2)
        
        # 保存統計
        stats_file = self.output_dir / f"statistics_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data['statistics'], f, ensure_ascii=False, indent=2)
        
        logger.info(f"數據已保存:")
        logger.info(f"  訓練數據: {training_file}")
        logger.info(f"  統計信息: {stats_file}")
        
        return {
            'training_file': str(training_file),
            'stats_file': str(stats_file)
        }


async def main():
    """主函數"""
    # 從文件讀取 replay URLs
    replay_urls_file = Path("manus_replay_urls.txt")
    
    if not replay_urls_file.exists():
        # 創建示例文件
        with open(replay_urls_file, 'w') as f:
            f.write("https://manus.im/share/xHbeFo8tzQV51VeTErhskc?replay=1\n")
            f.write("# 在這裡添加更多 replay URLs，每行一個\n")
        
        logger.info(f"請在 {replay_urls_file} 中添加 replay URLs")
        return
    
    # 讀取 URLs
    with open(replay_urls_file, 'r') as f:
        replay_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    logger.info(f"準備收集 {len(replay_urls)} 個 replays")
    
    # 創建收集器
    collector = BrowserBasedManusCollector(headless=False)  # 設置為 False 以便手動登錄
    
    try:
        # 收集數據（支持斷點續傳）
        results = await collector.resume_from_progress(replay_urls)
        
        logger.info(f"\n收集完成:")
        logger.info(f"  成功: {results['successful']}")
        logger.info(f"  失敗: {results['failed']}")
        
        # 處理數據
        if results['data']:
            processor = ManusDataProcessor()
            processed = processor.process_collected_data(results['data'])
            
            # 保存處理結果
            saved_files = processor.save_processed_data(processed)
            
            logger.info(f"\n處理完成:")
            logger.info(f"  總訓練對: {processed['statistics']['total_pairs']}")
            logger.info(f"  包含代碼: {processed['statistics']['pairs_with_code']}")
            logger.info(f"  高質量對: {processed['statistics']['high_quality_pairs']}")
            
    except Exception as e:
        logger.error(f"收集過程出錯: {e}")
        raise
    finally:
        await collector.close()


if __name__ == "__main__":
    asyncio.run(main())