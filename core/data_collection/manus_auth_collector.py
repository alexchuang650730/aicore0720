#!/usr/bin/env python3
"""
Manus 認證數據收集器
使用 Playwright 進行登錄和數據收集
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

class ManusAuthCollector:
    def __init__(self, email: str, password: str, headless: bool = False):
        self.email = email
        self.password = password
        self.headless = headless
        self.tasks_file = Path('manus_tasks_manual.txt')
        self.output_dir = Path('data/manus_auth_collection')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logged_in = False
        
    async def login(self, context):
        """登錄 Manus"""
        logger.info("🔐 開始登錄 Manus...")
        
        page = await context.new_page()
        
        try:
            # 訪問登錄頁面
            await page.goto('https://manus.im/signin', wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # 查找並填寫郵箱
            email_input = await page.wait_for_selector('input[type="email"], input[name="email"], input[placeholder*="email"]', timeout=10000)
            await email_input.fill(self.email)
            logger.info("✓ 已輸入郵箱")
            
            # 查找並填寫密碼
            password_input = await page.wait_for_selector('input[type="password"], input[name="password"]', timeout=5000)
            await password_input.fill(self.password)
            logger.info("✓ 已輸入密碼")
            
            # 點擊登錄按鈕
            login_button = await page.wait_for_selector('button[type="submit"], button:has-text("Sign in"), button:has-text("Log in")', timeout=5000)
            await login_button.click()
            logger.info("✓ 已點擊登錄")
            
            # 等待登錄完成
            await page.wait_for_timeout(5000)
            
            # 檢查是否登錄成功
            if await self._check_logged_in(page):
                logger.info("✅ 登錄成功！")
                self.logged_in = True
                
                # 保存 cookies
                cookies = await context.cookies()
                cookies_file = self.output_dir / 'cookies.json'
                with open(cookies_file, 'w') as f:
                    json.dump(cookies, f)
                logger.info(f"💾 已保存 cookies: {cookies_file}")
                
                return True
            else:
                logger.error("❌ 登錄失敗")
                # 截圖用於調試
                await page.screenshot(path=str(self.output_dir / 'login_failed.png'))
                return False
                
        except Exception as e:
            logger.error(f"登錄過程出錯: {str(e)}")
            await page.screenshot(path=str(self.output_dir / 'login_error.png'))
            return False
        finally:
            await page.close()
    
    async def _check_logged_in(self, page) -> bool:
        """檢查是否已登錄"""
        # 檢查是否還在登錄頁面
        if 'signin' in page.url or 'login' in page.url:
            return False
            
        # 檢查是否有用戶相關元素
        user_indicators = [
            'button:has-text("Sign out")',
            'button:has-text("Log out")',
            '[class*="user"]',
            '[class*="avatar"]',
            '[class*="profile"]'
        ]
        
        for indicator in user_indicators:
            if await page.locator(indicator).count() > 0:
                return True
                
        return False
    
    async def collect_with_auth(self):
        """帶認證的數據收集"""
        logger.info("🚀 啟動認證收集器...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            # 嘗試載入已保存的 cookies
            cookies_file = self.output_dir / 'cookies.json'
            if cookies_file.exists():
                logger.info("載入已保存的 cookies...")
                with open(cookies_file, 'r') as f:
                    cookies = json.load(f)
                    await context.add_cookies(cookies)
            
            # 登錄
            if not self.logged_in:
                login_success = await self.login(context)
                if not login_success:
                    logger.error("無法登錄，中止收集")
                    await browser.close()
                    return []
            
            # 載入任務列表
            tasks = self._load_tasks()
            logger.info(f"載入了 {len(tasks)} 個任務")
            
            results = []
            
            # 收集數據
            for i, task in enumerate(tasks, 1):
                logger.info(f"\n處理任務 {i}/{len(tasks)}: {task['url']}")
                
                try:
                    result = await self._collect_single_task(context, task)
                    results.append(result)
                    
                    # 保存進度
                    if i % 10 == 0:
                        await self._save_progress(results)
                    
                    # 測試前5個
                    if i >= 5:
                        logger.info("\n測試模式：只收集前5個任務")
                        break
                        
                except Exception as e:
                    logger.error(f"任務 {i} 失敗: {str(e)}")
                    results.append({
                        'task': task,
                        'success': False,
                        'error': str(e)
                    })
                
                # 避免請求過快
                await asyncio.sleep(3)
            
            await browser.close()
            
            # 保存最終結果
            await self._save_final_results(results)
            
            return results
    
    async def _collect_single_task(self, context, task: Dict) -> Dict:
        """收集單個任務的數據"""
        page = await context.new_page()
        
        try:
            # 訪問 replay URL
            logger.info(f"訪問: {task['url']}")
            await page.goto(task['url'], wait_until='networkidle')
            
            # 等待內容加載
            await page.wait_for_timeout(5000)
            
            # 再次檢查是否需要登錄
            if await self._check_login_required(page):
                logger.warning("此頁面需要登錄，但應該已經登錄了")
                return {
                    'task': task,
                    'success': False,
                    'error': 'Login required on task page'
                }
            
            # 提取對話內容
            conversation_data = await self._extract_conversation(page)
            
            # 截圖保存
            screenshot_path = self.output_dir / f"screenshot_{task['id']}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            # 保存渲染後的 HTML
            html_content = await page.content()
            html_path = self.output_dir / f"html_{task['id']}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✓ 成功提取: {conversation_data['title']}")
            
            return {
                'task': task,
                'success': True,
                'conversation': conversation_data,
                'screenshot': str(screenshot_path),
                'html': str(html_path)
            }
            
        except Exception as e:
            logger.error(f"提取失敗: {str(e)}")
            await page.screenshot(path=str(self.output_dir / f"error_{task['id']}.png"))
            return {
                'task': task,
                'success': False,
                'error': str(e)
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
        """提取對話內容 - 增強版"""
        conversation_data = {
            'title': '',
            'messages': [],
            'tools': [],
            'code_blocks': [],
            'task_description': '',
            'execution_steps': []
        }
        
        # 提取標題
        try:
            title = await page.title()
            conversation_data['title'] = title
        except:
            pass
        
        # 等待對話內容加載
        try:
            await page.wait_for_selector('[class*="message"], [class*="chat"], article, .prose', 
                                        timeout=10000, 
                                        state='visible')
        except:
            logger.warning("未找到對話內容選擇器")
        
        # 提取整個頁面文本用於分析
        page_text = await page.text_content('body') or ''
        
        # 提取消息 - 更廣泛的選擇器
        message_selectors = [
            'div[class*="message"]',
            'div[role="article"]',
            'div[class*="chat"]',
            '.prose',
            'div[class*="content"]',
            'div[class*="text"]',
            'p'
        ]
        
        all_messages = []
        for selector in message_selectors:
            try:
                messages = await page.locator(selector).all()
                for msg in messages[:50]:  # 限制數量避免太多
                    text = await msg.text_content()
                    if text and len(text) > 20 and text not in [m['content'] for m in all_messages]:
                        all_messages.append({
                            'content': text.strip(),
                            'selector': selector
                        })
            except:
                continue
        
        conversation_data['messages'] = all_messages[:30]  # 保留前30條獨特消息
        
        # 提取代碼塊
        code_selectors = ['pre', 'code', '[class*="code"]', '[class*="highlight"]']
        for selector in code_selectors:
            try:
                code_blocks = await page.locator(selector).all()
                for block in code_blocks[:20]:
                    code_text = await block.text_content()
                    if code_text and len(code_text) > 30:
                        # 嘗試獲取語言
                        lang = 'unknown'
                        try:
                            class_name = await block.get_attribute('class') or ''
                            if 'language-' in class_name:
                                lang = class_name.split('language-')[1].split()[0]
                        except:
                            pass
                        
                        conversation_data['code_blocks'].append({
                            'code': code_text.strip(),
                            'language': lang
                        })
            except:
                continue
        
        # 提取工具使用
        tool_keywords = [
            'tool:', 'function:', 'calling', 'executing',
            '執行', '調用', '工具', '函數',
            'npm', 'pip', 'git', 'docker', 'python'
        ]
        
        for keyword in tool_keywords:
            if keyword.lower() in page_text.lower():
                # 找出包含關鍵詞的上下文
                lines = page_text.split('\n')
                for line in lines:
                    if keyword.lower() in line.lower():
                        conversation_data['tools'].append({
                            'keyword': keyword,
                            'context': line.strip()[:200]
                        })
        
        # 去重工具列表
        unique_tools = []
        seen = set()
        for tool in conversation_data['tools']:
            if tool['context'] not in seen:
                seen.add(tool['context'])
                unique_tools.append(tool)
        conversation_data['tools'] = unique_tools[:10]
        
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
            'success_rate': f"{success_count/len(results)*100:.1f}%" if results else "0%",
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        # 保存完整報告
        report_file = self.output_dir / f'auth_collection_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成摘要
        summary_file = self.output_dir / 'auth_collection_summary.md'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Manus 認證收集報告\n\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## 統計\n\n")
            f.write(f"- 總任務數: {report['total_tasks']}\n")
            f.write(f"- 成功: {report['successful']}\n")
            f.write(f"- 失敗: {report['failed']}\n")
            f.write(f"- 成功率: {report['success_rate']}\n\n")
            
            f.write(f"## 成功提取的對話\n\n")
            for r in results:
                if r['success']:
                    conv = r['conversation']
                    f.write(f"### {r['task']['number']}. {conv['title']}\n")
                    f.write(f"- 消息數: {len(conv['messages'])}\n")
                    f.write(f"- 代碼塊: {len(conv['code_blocks'])}\n")
                    f.write(f"- 工具使用: {len(conv['tools'])}\n")
                    if conv['messages']:
                        f.write(f"- 首條消息: {conv['messages'][0]['content'][:100]}...\n")
                    f.write("\n")
        
        logger.info(f"\n✅ 收集完成！")
        logger.info(f"📊 成功率: {report['success_rate']}")
        logger.info(f"📄 報告已保存: {report_file}")
        logger.info(f"📝 摘要已保存: {summary_file}")

async def main():
    """主函數"""
    print("=" * 60)
    print("🎯 Manus 認證數據收集器")
    print("=" * 60)
    
    # 使用提供的憑證
    email = "chuang.hsiaoyen@gmail.com"
    password = "silentfleet#1234"
    
    # 創建收集器（測試時使用有頭模式）
    collector = ManusAuthCollector(email, password, headless=False)
    
    print(f"\n即將使用提供的憑證登錄並收集數據...")
    print("將先測試前 5 個任務\n")
    
    try:
        await collector.collect_with_auth()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷收集")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())