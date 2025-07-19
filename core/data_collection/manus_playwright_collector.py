#!/usr/bin/env python3
"""
Manus Playwright 數據收集器
基於 aicore0622 的成功經驗實現
"""

import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManusPlaywrightCollector:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.tasks_file = Path('manus_tasks_manual.txt')
        self.output_dir = Path('data/manus_playwright_collection')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def collect_tasks(self):
        """收集所有 Manus 任務"""
        logger.info("🚀 啟動 Playwright 收集器...")
        
        async with async_playwright() as p:
            # 使用 Chromium（基於 aicore0622 的選擇）
            browser = await p.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            # 載入任務列表
            tasks = self._load_tasks()
            logger.info(f"載入了 {len(tasks)} 個任務")
            
            results = []
            
            for i, task in enumerate(tasks, 1):
                logger.info(f"\n處理任務 {i}/{len(tasks)}: {task['url']}")
                
                try:
                    result = await self._collect_single_task(context, task)
                    results.append(result)
                    
                    # 保存進度
                    if i % 10 == 0:
                        await self._save_progress(results)
                        
                except Exception as e:
                    logger.error(f"任務 {i} 失敗: {str(e)}")
                    results.append({
                        'task': task,
                        'success': False,
                        'error': str(e)
                    })
                
                # 避免請求過快
                await asyncio.sleep(2)
            
            await browser.close()
            
            # 保存最終結果
            await self._save_final_results(results)
            
            return results
    
    async def _collect_single_task(self, context, task: Dict) -> Dict:
        """收集單個任務的數據"""
        page = await context.new_page()
        
        try:
            # 訪問 replay URL
            await page.goto(task['url'], wait_until='networkidle')
            
            # 等待內容加載（基於 aicore0622 的經驗）
            await page.wait_for_timeout(3000)
            
            # 檢查是否需要登錄
            if await self._check_login_required(page):
                logger.warning("需要登錄，跳過此任務")
                return {
                    'task': task,
                    'success': False,
                    'error': 'Login required'
                }
            
            # 提取對話內容
            conversation_data = await self._extract_conversation(page)
            
            # 截圖保存
            screenshot_path = self.output_dir / f"screenshot_{task['id']}.png"
            await page.screenshot(path=str(screenshot_path))
            
            # 保存 HTML
            html_content = await page.content()
            html_path = self.output_dir / f"html_{task['id']}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'task': task,
                'success': True,
                'conversation': conversation_data,
                'screenshot': str(screenshot_path),
                'html': str(html_path)
            }
            
        finally:
            await page.close()
    
    async def _check_login_required(self, page) -> bool:
        """檢查是否需要登錄"""
        login_indicators = [
            'button:has-text("Sign in")',
            'button:has-text("Log in")',
            'input[type="password"]',
            '.login-form',
            '#login'
        ]
        
        for indicator in login_indicators:
            if await page.locator(indicator).count() > 0:
                return True
        return False
    
    async def _extract_conversation(self, page) -> Dict:
        """提取對話內容"""
        conversation_data = {
            'title': '',
            'messages': [],
            'tools': [],
            'code_blocks': []
        }
        
        # 提取標題
        try:
            title = await page.title()
            conversation_data['title'] = title
        except:
            pass
        
        # 等待對話內容加載
        await page.wait_for_selector('div[class*="message"], div[class*="chat"], article', 
                                    timeout=10000, 
                                    state='visible')
        
        # 提取消息
        message_selectors = [
            'div[class*="message"]',
            'div[role="article"]',
            'div[class*="chat-message"]',
            '.prose'
        ]
        
        for selector in message_selectors:
            messages = await page.locator(selector).all()
            if messages:
                for msg in messages:
                    text = await msg.text_content()
                    if text and len(text) > 10:
                        conversation_data['messages'].append({
                            'content': text.strip(),
                            'selector': selector
                        })
                break
        
        # 提取代碼塊
        code_blocks = await page.locator('pre, code').all()
        for block in code_blocks:
            code_text = await block.text_content()
            if code_text and len(code_text) > 20:
                conversation_data['code_blocks'].append(code_text.strip())
        
        # 提取工具使用（基於常見模式）
        tool_patterns = [
            'tool:',
            'function:',
            'calling',
            'executing',
            '執行',
            '調用'
        ]
        
        page_text = await page.text_content('body')
        for pattern in tool_patterns:
            if pattern.lower() in page_text.lower():
                conversation_data['tools'].append(pattern)
        
        return conversation_data
    
    def _load_tasks(self) -> List[Dict]:
        """載入任務列表"""
        tasks = []
        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            current_task = None
            for line in f:
                line = line.strip()
                if line.startswith('# 任務'):
                    if current_task:
                        tasks.append(current_task)
                    task_num = line.split()[1]
                    current_task = {'number': task_num}
                elif line.startswith('http'):
                    if current_task:
                        current_task['url'] = line
                        # 提取 ID
                        current_task['id'] = line.split('/share/')[1].split('?')[0]
            
            if current_task and 'url' in current_task:
                tasks.append(current_task)
        
        return tasks
    
    async def _save_progress(self, results: List[Dict]):
        """保存進度"""
        progress_file = self.output_dir / f'progress_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 進度已保存: {progress_file}")
    
    async def _save_final_results(self, results: List[Dict]):
        """保存最終結果"""
        # 統計
        success_count = sum(1 for r in results if r['success'])
        
        # 生成報告
        report = {
            'total_tasks': len(results),
            'successful': success_count,
            'failed': len(results) - success_count,
            'success_rate': f"{success_count/len(results)*100:.1f}%",
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        # 保存完整報告
        report_file = self.output_dir / f'collection_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成摘要
        summary_file = self.output_dir / 'collection_summary.md'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Manus Playwright 收集報告\n\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## 統計\n\n")
            f.write(f"- 總任務數: {report['total_tasks']}\n")
            f.write(f"- 成功: {report['successful']}\n")
            f.write(f"- 失敗: {report['failed']}\n")
            f.write(f"- 成功率: {report['success_rate']}\n\n")
            
            f.write(f"## 成功提取的對話\n\n")
            for r in results:
                if r['success']:
                    f.write(f"### {r['task']['number']}. {r['conversation']['title']}\n")
                    f.write(f"- 消息數: {len(r['conversation']['messages'])}\n")
                    f.write(f"- 代碼塊: {len(r['conversation']['code_blocks'])}\n")
                    f.write(f"- 工具: {len(r['conversation']['tools'])}\n\n")
        
        logger.info(f"\n✅ 收集完成！")
        logger.info(f"📊 成功率: {report['success_rate']}")
        logger.info(f"📄 報告已保存: {report_file}")
        logger.info(f"📝 摘要已保存: {summary_file}")

async def main():
    """主函數"""
    print("=" * 60)
    print("🎯 Manus Playwright 數據收集器")
    print("基於 aicore0622 的成功經驗")
    print("=" * 60)
    
    # 檢查依賴
    try:
        import playwright
    except ImportError:
        print("\n❌ 請先安裝 Playwright:")
        print("pip3 install playwright")
        print("playwright install chromium")
        return
    
    # 選擇模式
    print("\n選擇運行模式:")
    print("1. 有頭模式（可見瀏覽器）")
    print("2. 無頭模式（後台運行）")
    
    choice = input("\n請選擇 (1/2) [默認: 1]: ").strip() or "1"
    headless = choice == "2"
    
    # 開始收集
    collector = ManusPlaywrightCollector(headless=headless)
    
    print(f"\n即將開始收集 {len(collector._load_tasks())} 個任務...")
    print("按 Ctrl+C 可隨時中斷\n")
    
    try:
        await collector.collect_tasks()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷收集")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())