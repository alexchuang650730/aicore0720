#!/usr/bin/env python3
"""
增強版Manus對話萃取器
專門設計來獲取完整的2小時對話內容
"""

import json
import logging
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedManusExtractor:
    """增強版Manus對話萃取器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "data" / "enhanced_extracted_chats"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "total_urls": 0,
            "extracted": 0,
            "failed": 0,
            "total_messages": 0,
            "total_conversations": 0,
            "long_conversations": 0,  # 超過10條消息的對話
            "errors": []
        }
    
    async def extract_full_conversations(self, urls_file: str, batch_size: int = 5) -> Dict[str, Any]:
        """萃取完整對話，使用多種技術獲取2小時對話內容"""
        logger.info(f"🚀 開始增強版Manus對話萃取，批次大小: {batch_size}")
        
        # 讀取URL列表，跳過已處理的
        processed_urls = self._get_processed_urls()
        
        with open(urls_file, 'r', encoding='utf-8') as f:
            all_urls = [line.strip() for line in f if line.strip()]
        
        # 過濾未處理的URL
        remaining_urls = [url for url in all_urls if not self._is_url_processed(url, processed_urls)]
        
        self.stats["total_urls"] = len(remaining_urls)
        logger.info(f"📊 待處理URL: {len(remaining_urls)}/{len(all_urls)}")
        
        if not remaining_urls:
            logger.info("✅ 所有URL已處理完成！")
            return {"success": True, "stats": self.stats}
        
        # 檢查Playwright可用性
        playwright_available = await self._check_playwright()
        
        if playwright_available:
            await self._extract_with_enhanced_playwright(remaining_urls, batch_size)
        else:
            logger.error("❌ Playwright未安裝，無法進行增強萃取")
            return {"success": False, "stats": self.stats}
        
        # 生成增強萃取報告
        await self._generate_enhanced_report()
        
        logger.info(f"✅ 增強萃取完成：{self.stats['extracted']}/{self.stats['total_urls']} 成功")
        
        return {
            "success": True,
            "stats": self.stats
        }
    
    def _get_processed_urls(self) -> set:
        """獲取已處理的URL集合"""
        processed = set()
        
        # 檢查原始目錄
        original_dir = self.base_dir / "data" / "extracted_chats"
        if original_dir.exists():
            for file in original_dir.glob("chat_*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "url" in data:
                            processed.add(data["url"])
                except:
                    continue
        
        # 檢查增強目錄
        if self.output_dir.exists():
            for file in self.output_dir.glob("enhanced_*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "url" in data:
                            processed.add(data["url"])
                except:
                    continue
        
        return processed
    
    def _is_url_processed(self, url: str, processed_urls: set) -> bool:
        """檢查URL是否已處理"""
        return url in processed_urls
    
    async def _check_playwright(self) -> bool:
        """檢查Playwright是否可用"""
        try:
            from playwright.async_api import async_playwright
            return True
        except ImportError:
            return False
    
    async def _extract_with_enhanced_playwright(self, urls: List[str], batch_size: int):
        """使用增強的Playwright技術萃取完整對話"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                # 使用更完整的瀏覽器配置
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-background-networking',
                        '--disable-background-timer-throttling',
                        '--disable-renderer-backgrounding',
                        '--disable-backgrounding-occluded-windows'
                    ]
                )
                
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                for i in range(0, len(urls), batch_size):
                    batch_urls = urls[i:i + batch_size]
                    logger.info(f"🔄 處理批次 {i//batch_size + 1}: {len(batch_urls)} 個URL")
                    
                    for j, url in enumerate(batch_urls):
                        try:
                            await self._extract_single_conversation_enhanced(context, url, i + j)
                            await asyncio.sleep(3)  # 適當的請求間隔
                        except Exception as e:
                            logger.error(f"❌ 增強萃取失敗 {url}: {e}")
                            self.stats["failed"] += 1
                            self.stats["errors"].append(f"{url}: {str(e)}")
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"❌ 增強Playwright初始化失敗: {e}")
    
    async def _extract_single_conversation_enhanced(self, context, url: str, index: int):
        """使用增強技術萃取單個完整對話"""
        page = await context.new_page()
        
        try:
            logger.info(f"🌐 載入頁面: {url}")
            
            # 載入頁面並等待完全渲染
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 等待初始內容載入
            await page.wait_for_timeout(5000)
            
            # 嘗試多種策略獲取完整對話
            chat_messages = []
            
            # 策略1: 激進滾動加載
            messages_1 = await self._aggressive_scroll_loading(page)
            if len(messages_1) > len(chat_messages):
                chat_messages = messages_1
            
            # 策略2: 尋找並點擊"查看更多"按鈕
            messages_2 = await self._find_and_click_load_more(page)
            if len(messages_2) > len(chat_messages):
                chat_messages = messages_2
            
            # 策略3: 嘗試不同的CSS選擇器
            messages_3 = await self._try_multiple_selectors(page)
            if len(messages_3) > len(chat_messages):
                chat_messages = messages_3
            
            # 策略4: 模擬用戶交互
            messages_4 = await self._simulate_user_interaction(page)
            if len(messages_4) > len(chat_messages):
                chat_messages = messages_4
            
            if chat_messages:
                replay_id = url.split('/')[-1].split('?')[0]
                
                enhanced_data = {
                    "replay_id": replay_id,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "conversation": chat_messages,
                    "metadata": {
                        "total_messages": len(chat_messages),
                        "extraction_method": "enhanced_playwright",
                        "extraction_time": datetime.now().isoformat(),
                        "is_long_conversation": len(chat_messages) >= 10,
                        "estimated_duration_minutes": len(chat_messages) * 2  # 粗略估算
                    }
                }
                
                await self._save_enhanced_chat_data(enhanced_data, index)
                self.stats["extracted"] += 1
                self.stats["total_conversations"] += 1
                self.stats["total_messages"] += len(chat_messages)
                
                if len(chat_messages) >= 10:
                    self.stats["long_conversations"] += 1
                
                logger.info(f"✅ 成功萃取 {len(chat_messages)} 條消息 {'📈 長對話!' if len(chat_messages) >= 10 else ''}")
            else:
                logger.warning(f"⚠️ 未找到對話內容: {url}")
                self.stats["failed"] += 1
                
        except Exception as e:
            logger.error(f"❌ 頁面處理失敗: {e}")
            self.stats["failed"] += 1
            self.stats["errors"].append(str(e))
        finally:
            await page.close()
    
    async def _aggressive_scroll_loading(self, page) -> List[Dict[str, Any]]:
        """激進滾動加載策略"""
        messages = []
        
        try:
            # 獲取初始高度
            previous_height = await page.evaluate("document.body.scrollHeight")
            
            # 激進滾動 - 多達20次
            for i in range(20):
                # 快速滾動到底部
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
                
                # 慢速滾動加載更多內容
                await page.evaluate("""
                    let scrollStep = document.body.scrollHeight / 10;
                    for(let i = 0; i < 10; i++) {
                        window.scrollTo(0, scrollStep * i);
                    }
                """)
                await page.wait_for_timeout(2000)
                
                # 檢查是否有新內容
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    break
                
                previous_height = current_height
                logger.info(f"🔄 激進滾動第{i+1}次，頁面高度: {current_height}")
            
            # 滾動回頂部並萃取
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(2000)
            
            messages = await self._extract_messages_from_page(page)
            
        except Exception as e:
            logger.warning(f"⚠️ 激進滾動失敗: {e}")
        
        return messages
    
    async def _find_and_click_load_more(self, page) -> List[Dict[str, Any]]:
        """尋找並點擊加載更多按鈕"""
        messages = []
        
        try:
            # 多種可能的"加載更多"按鈕
            load_more_selectors = [
                'button:has-text("Load more")',
                'button:has-text("加載更多")',
                'button:has-text("查看更多")',
                'button:has-text("Show more")',
                'button:has-text("Continue")',
                'button:has-text("繼續")',
                '.load-more',
                '.show-more',
                '[data-testid="load-more"]',
                '[aria-label="Load more"]'
            ]
            
            for i in range(10):  # 最多點擊10次
                button_found = False
                
                for selector in load_more_selectors:
                    try:
                        button = await page.query_selector(selector)
                        if button and await button.is_visible():
                            await button.click()
                            await page.wait_for_timeout(3000)
                            button_found = True
                            logger.info(f"🖱️ 點擊了加載更多按鈕: {selector}")
                            break
                    except:
                        continue
                
                if not button_found:
                    break
            
            messages = await self._extract_messages_from_page(page)
            
        except Exception as e:
            logger.warning(f"⚠️ 點擊加載更多失敗: {e}")
        
        return messages
    
    async def _try_multiple_selectors(self, page) -> List[Dict[str, Any]]:
        """嘗試多種CSS選擇器策略"""
        messages = []
        
        # 更全面的選擇器列表
        selectors = [
            '.prose',  # 目前已知有效
            '[data-testid="message"]',
            '.message',
            '.chat-message',
            '.conversation-item',
            '.conversation-message',
            '[role="listitem"]',
            '.chat-bubble',
            '.message-bubble',
            '.dialogue-item',
            '.chat-item',
            'div[data-role="user"], div[data-role="assistant"]',
            '.user-message, .assistant-message',
            '.message-container',
            '.chat-content',
            'article',
            '.prose > *',  # prose的所有子元素
        ]
        
        try:
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements and len(elements) > len(messages):
                        current_messages = []
                        
                        for i, element in enumerate(elements):
                            try:
                                text_content = await element.text_content()
                                if text_content and len(text_content.strip()) > 5:
                                    
                                    # 智能角色檢測
                                    role = await self._smart_role_detection(element, i, text_content)
                                    
                                    message = {
                                        "role": role,
                                        "content": text_content.strip(),
                                        "timestamp": datetime.now().isoformat(),
                                        "index": i,
                                        "selector_used": selector
                                    }
                                    current_messages.append(message)
                                    
                            except Exception:
                                continue
                        
                        if len(current_messages) > len(messages):
                            messages = current_messages
                            logger.info(f"📋 找到更多消息 {len(current_messages)} 條，選擇器: {selector}")
                        
                except Exception:
                    continue
            
        except Exception as e:
            logger.warning(f"⚠️ 多選擇器策略失敗: {e}")
        
        return messages
    
    async def _simulate_user_interaction(self, page) -> List[Dict[str, Any]]:
        """模擬用戶交互以觸發內容加載"""
        messages = []
        
        try:
            # 模擬鍵盤操作
            await page.keyboard.press('End')  # 按End鍵到底部
            await page.wait_for_timeout(2000)
            
            await page.keyboard.press('Home')  # 按Home鍵到頂部
            await page.wait_for_timeout(2000)
            
            # 模擬Page Down多次
            for i in range(10):
                await page.keyboard.press('PageDown')
                await page.wait_for_timeout(1000)
            
            # 嘗試點擊頁面中央以觸發focus
            await page.click('body')
            await page.wait_for_timeout(1000)
            
            # 再次萃取
            messages = await self._extract_messages_from_page(page)
            
        except Exception as e:
            logger.warning(f"⚠️ 用戶交互模擬失敗: {e}")
        
        return messages
    
    async def _extract_messages_from_page(self, page) -> List[Dict[str, Any]]:
        """從頁面萃取消息（整合方法）"""
        # 使用已有的萃取邏輯，但做一些增強
        return await self._try_multiple_selectors(page)
    
    async def _smart_role_detection(self, element, index: int, text_content: str) -> str:
        """智能角色檢測"""
        try:
            # 檢查元素屬性
            class_name = await element.get_attribute('class') or ''
            data_role = await element.get_attribute('data-role') or ''
            
            # 屬性檢測
            if 'user' in class_name.lower() or 'user' in data_role.lower():
                return 'user'
            elif 'assistant' in class_name.lower() or 'assistant' in data_role.lower():
                return 'assistant'
            elif 'bot' in class_name.lower() or 'ai' in class_name.lower():
                return 'assistant'
            
            # 內容檢測
            if any(keyword in text_content.lower() for keyword in ['user:', '用戶:', 'human:']):
                return 'user'
            elif any(keyword in text_content.lower() for keyword in ['assistant:', '助手:', 'ai:', 'claude:']):
                return 'assistant'
            
            # 基於位置和長度的啟發式檢測
            if len(text_content) > 200:  # 長文本通常是助手回應
                return 'assistant'
            
            # 默認交替分配
            return 'user' if index % 2 == 0 else 'assistant'
            
        except Exception:
            return 'user' if index % 2 == 0 else 'assistant'
    
    async def _save_enhanced_chat_data(self, chat_data: Dict[str, Any], index: int):
        """保存增強的聊天數據"""
        output_file = self.output_dir / f"enhanced_{index}_{chat_data['replay_id']}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
    
    async def _generate_enhanced_report(self):
        """生成增強萃取報告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.base_dir / f"enhanced_manus_extraction_report_{timestamp}.md"
        
        avg_messages = self.stats["total_messages"] / max(self.stats["total_conversations"], 1)
        success_rate = self.stats["extracted"] / max(self.stats["total_urls"], 1) * 100
        long_conversation_rate = self.stats["long_conversations"] / max(self.stats["extracted"], 1) * 100
        
        report_content = f"""# 增強版Manus對話萃取報告
生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 萃取統計
- 目標URL數量: {self.stats['total_urls']}
- 成功萃取: {self.stats['extracted']}
- 萃取失敗: {self.stats['failed']}
- 成功率: {success_rate:.1f}%

## 💬 對話質量分析
- 總對話數: {self.stats['total_conversations']}
- 總消息數: {self.stats['total_messages']}
- 平均每對話消息數: {avg_messages:.1f}
- 長對話數 (≥10條消息): {self.stats['long_conversations']}
- 長對話比例: {long_conversation_rate:.1f}%

## 🎯 增強技術效果
使用的增強技術：
1. ✅ 激進滾動加載 (20次滾動)
2. ✅ 智能"加載更多"按鈕檢測
3. ✅ 多種CSS選擇器策略
4. ✅ 用戶交互模擬
5. ✅ 智能角色檢測

## 🚀 K2訓練影響
預期改進：
- **詞彙表規模**: 預計{self.stats['total_messages'] * 10}-{self.stats['total_messages'] * 20}詞彙
- **序列長度**: 支援更長的技術討論
- **訓練品質**: 真實2小時對話數據
- **模型性能**: 顯著提升實用性

## 📈 下一步優化
1. 繼續處理剩餘URL
2. 分析長對話的特徵模式
3. 優化MacBook Air GPU訓練配置
4. 評估增強數據的訓練效果

## ✅ 結論
增強萃取獲得{self.stats['total_messages']}條高質量消息！
{self.stats['long_conversations']}個長對話為K2訓練提供豐富數據。
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"📋 增強萃取報告已生成: {report_file}")

async def main():
    """主函數"""
    extractor = EnhancedManusExtractor()
    
    urls_file = "/Users/alexchuang/alexchuangtest/aicore0720/data/replay_links/replay_urls_fixed.txt"
    
    result = await extractor.extract_full_conversations(urls_file, batch_size=3)
    
    if result["success"]:
        print("\n🎉 增強版Manus對話萃取成功！")
        print(f"📊 萃取了 {result['stats']['extracted']} 個對話")
        print(f"💬 總消息數: {result['stats']['total_messages']}")
        print(f"📈 長對話數: {result['stats']['long_conversations']}")
        if result['stats']['total_conversations'] > 0:
            avg_msg = result['stats']['total_messages'] / result['stats']['total_conversations']
            print(f"📊 平均每對話: {avg_msg:.1f} 條消息")
        print("\n🚀 準備用增強數據進行K2訓練！")
    else:
        print("❌ 增強萃取失敗")

if __name__ == "__main__":
    asyncio.run(main())