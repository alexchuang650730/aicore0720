#!/usr/bin/env python3
"""
Manus Complete Analyzer - 完整的 Manus 對話分析工具
支持登錄、數據提取、分析和訓練數據生成
"""

import asyncio
import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass, asdict

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ 請先安裝 Playwright: pip install playwright")
    print("然後安裝瀏覽器: playwright install chromium")

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None
    tools_used: Optional[List[str]] = None

@dataclass
class CodeBlock:
    language: str
    code: str
    purpose: Optional[str] = None

@dataclass
class ToolUsage:
    tool_name: str
    parameters: Optional[Dict] = None
    result: Optional[str] = None

@dataclass
class ManusConversation:
    url: str
    title: str
    messages: List[Message]
    code_blocks: List[CodeBlock]
    tools_used: List[ToolUsage]
    task_type: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    extracted_at: str = datetime.now().isoformat()

class ManusCompleteAnalyzer:
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        self.email = email
        self.password = password
        self.logged_in = False
        
        # 工具使用模式
        self.tool_patterns = {
            'file_operations': r'(create|write|read|edit|delete|modify)\s+(file|directory|folder)',
            'command_execution': r'(run|execute|exec)\s+(command|script|code)',
            'api_calls': r'(fetch|request|call|get|post|put|delete)\s+(api|endpoint|url)',
            'search': r'(search|find|grep|locate)\s+(for|in|pattern)',
            'git_operations': r'git\s+(clone|commit|push|pull|branch|checkout|merge)',
            'package_management': r'(npm|pip|yarn|cargo|gem)\s+(install|update|remove)',
            'docker': r'docker\s+(build|run|compose|exec|ps|logs)',
            'testing': r'(test|jest|pytest|mocha|jasmine)\s+',
            'database': r'(select|insert|update|delete|create table|alter|drop)',
            'ai_tools': r'(gpt|claude|llm|model|prompt|completion)'
        }
        
        # 編程語言檢測
        self.language_patterns = {
            'python': r'(def |class |import |from .* import|print\(|if __name__|\.py)',
            'javascript': r'(function |const |let |var |console\.log|require\(|\.js)',
            'typescript': r'(interface |type |enum |implements|\.ts)',
            'java': r'(public class|private |protected |static void|\.java)',
            'go': r'(func |package |import \"|var |\.go)',
            'rust': r'(fn |let mut|use |impl |\.rs)',
            'cpp': r'(#include|int main|void |class |namespace|\.cpp|\.h)',
            'csharp': r'(using |namespace |public class|static void|\.cs)',
            'ruby': r'(def |class |require |puts |\.rb)',
            'php': r'(<\?php|\$|function |echo |\.php)'
        }
    
    async def analyze_url(self, url: str, output_dir: str = "./manus_analysis") -> ManusConversation:
        """分析單個 Manus URL"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright 未安裝")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # 設為 False 以便查看過程
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            # 如果提供了登錄信息，先登錄
            if self.email and self.password and not self.logged_in:
                await self._login(context)
            
            # 分析 URL
            conversation = await self._analyze_single_url(context, url, output_path)
            
            await browser.close()
            
            # 保存結果
            self._save_conversation(conversation, output_path)
            
            return conversation
    
    async def analyze_batch(self, urls: List[str], output_dir: str = "./manus_analysis") -> List[ManusConversation]:
        """批量分析多個 URL"""
        results = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"分析 {i}/{len(urls)}: {url}")
            try:
                conversation = await self.analyze_url(url, output_dir)
                results.append(conversation)
            except Exception as e:
                logger.error(f"分析失敗: {str(e)}")
                results.append(ManusConversation(
                    url=url,
                    title="分析失敗",
                    messages=[],
                    code_blocks=[],
                    tools_used=[],
                    success=False,
                    error_message=str(e)
                ))
            
            # 避免請求過快
            if i < len(urls):
                await asyncio.sleep(3)
        
        # 生成批量分析報告
        self._generate_batch_report(results, Path(output_dir))
        
        return results
    
    async def _login(self, context):
        """登錄 Manus"""
        logger.info("🔐 正在登錄 Manus...")
        page = await context.new_page()
        
        try:
            await page.goto('https://manus.im/signin', wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # 填寫登錄表單
            await page.fill('input[type="email"]', self.email)
            await page.fill('input[type="password"]', self.password)
            
            # 點擊登錄
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(5000)
            
            # 檢查登錄狀態
            if 'signin' not in page.url:
                logger.info("✅ 登錄成功")
                self.logged_in = True
                
                # 保存 cookies
                cookies = await context.cookies()
                with open('manus_cookies.json', 'w') as f:
                    json.dump(cookies, f)
            else:
                logger.error("❌ 登錄失敗")
                
        finally:
            await page.close()
    
    async def _analyze_single_url(self, context, url: str, output_path: Path) -> ManusConversation:
        """分析單個 URL 的內容"""
        page = await context.new_page()
        
        try:
            logger.info(f"📄 正在訪問: {url}")
            await page.goto(url, wait_until='networkidle')
            await page.wait_for_timeout(5000)
            
            # 提取標題
            title = await page.title()
            
            # 截圖
            screenshot_path = output_path / f"screenshot_{self._get_id_from_url(url)}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"📸 已保存截圖: {screenshot_path}")
            
            # 提取對話內容
            messages = await self._extract_messages(page)
            
            # 提取代碼塊
            code_blocks = await self._extract_code_blocks(page)
            
            # 分析工具使用
            page_text = await page.text_content('body') or ''
            tools_used = self._analyze_tool_usage(page_text, messages)
            
            # 判斷任務類型
            task_type = self._classify_task_type(title, messages, code_blocks)
            
            # 保存 HTML
            html_path = output_path / f"html_{self._get_id_from_url(url)}.html"
            html_content = await page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return ManusConversation(
                url=url,
                title=title,
                messages=messages,
                code_blocks=code_blocks,
                tools_used=tools_used,
                task_type=task_type,
                success=True
            )
            
        except Exception as e:
            logger.error(f"分析出錯: {str(e)}")
            return ManusConversation(
                url=url,
                title="提取失敗",
                messages=[],
                code_blocks=[],
                tools_used=[],
                success=False,
                error_message=str(e)
            )
        finally:
            await page.close()
    
    async def _extract_messages(self, page) -> List[Message]:
        """提取對話消息"""
        messages = []
        
        # 嘗試多種選擇器
        selectors = [
            'div[class*="message"]',
            'div[class*="chat"]',
            'article',
            '.prose',
            'div[role="article"]',
            'div[class*="conversation"]'
        ]
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                logger.info(f"找到 {len(elements)} 個消息元素 (使用選擇器: {selector})")
                break
        
        # 提取消息內容
        for element in elements:
            text = await element.text_content()
            if text and len(text) > 10:
                # 嘗試判斷角色
                role = 'unknown'
                element_html = await element.inner_html()
                
                if any(indicator in element_html.lower() for indicator in ['user', 'human', 'question']):
                    role = 'user'
                elif any(indicator in element_html.lower() for indicator in ['assistant', 'ai', 'answer']):
                    role = 'assistant'
                
                # 檢查是否包含工具使用
                tools = []
                for tool_name, pattern in self.tool_patterns.items():
                    if re.search(pattern, text, re.IGNORECASE):
                        tools.append(tool_name)
                
                messages.append(Message(
                    role=role,
                    content=text.strip(),
                    tools_used=tools if tools else None
                ))
        
        return messages
    
    async def _extract_code_blocks(self, page) -> List[CodeBlock]:
        """提取代碼塊"""
        code_blocks = []
        
        # 查找代碼元素
        code_elements = await page.query_selector_all('pre, code, [class*="highlight"], [class*="code"]')
        
        for element in code_elements:
            code = await element.text_content()
            if code and len(code) > 30:
                # 嘗試檢測語言
                language = 'unknown'
                
                # 從 class 屬性獲取語言
                class_name = await element.get_attribute('class') or ''
                if 'language-' in class_name:
                    language = class_name.split('language-')[1].split()[0]
                
                # 如果沒有明確標記，嘗試從內容推斷
                if language == 'unknown':
                    for lang, pattern in self.language_patterns.items():
                        if re.search(pattern, code):
                            language = lang
                            break
                
                # 嘗試推斷代碼用途
                purpose = self._infer_code_purpose(code)
                
                code_blocks.append(CodeBlock(
                    language=language,
                    code=code.strip(),
                    purpose=purpose
                ))
        
        return code_blocks
    
    def _analyze_tool_usage(self, page_text: str, messages: List[Message]) -> List[ToolUsage]:
        """分析工具使用情況"""
        tools = []
        seen = set()
        
        # 從頁面文本中提取
        for tool_name, pattern in self.tool_patterns.items():
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                context = page_text[max(0, match.start()-50):min(len(page_text), match.end()+50)]
                if context not in seen:
                    seen.add(context)
                    tools.append(ToolUsage(
                        tool_name=tool_name,
                        parameters={'context': context.strip()}
                    ))
        
        # 從消息中提取
        for message in messages:
            if message.tools_used:
                for tool in message.tools_used:
                    if tool not in [t.tool_name for t in tools]:
                        tools.append(ToolUsage(tool_name=tool))
        
        return tools[:20]  # 限制數量
    
    def _classify_task_type(self, title: str, messages: List[Message], code_blocks: List[CodeBlock]) -> str:
        """分類任務類型"""
        all_text = title + ' '.join([m.content for m in messages])
        
        task_types = {
            'debugging': ['debug', 'error', 'fix', 'issue', 'problem', 'bug'],
            'implementation': ['implement', 'create', 'build', 'develop', 'add feature'],
            'refactoring': ['refactor', 'optimize', 'improve', 'clean', 'restructure'],
            'testing': ['test', 'unit test', 'integration', 'e2e', 'coverage'],
            'documentation': ['document', 'readme', 'docs', 'comment', 'explain'],
            'deployment': ['deploy', 'ci/cd', 'docker', 'kubernetes', 'aws'],
            'data_analysis': ['analyze', 'data', 'statistics', 'visualization', 'report'],
            'web_scraping': ['scrape', 'crawl', 'extract', 'parse html', 'beautiful soup'],
            'api_development': ['api', 'endpoint', 'rest', 'graphql', 'backend'],
            'frontend': ['react', 'vue', 'angular', 'css', 'ui', 'frontend']
        }
        
        # 計算每種類型的匹配分數
        scores = {}
        for task_type, keywords in task_types.items():
            score = sum(1 for keyword in keywords if keyword.lower() in all_text.lower())
            if score > 0:
                scores[task_type] = score
        
        # 返回得分最高的類型
        if scores:
            return max(scores, key=scores.get)
        
        return 'general'
    
    def _infer_code_purpose(self, code: str) -> str:
        """推斷代碼用途"""
        purposes = {
            'data_processing': ['pandas', 'numpy', 'csv', 'json.load', 'dataframe'],
            'web_scraping': ['requests', 'beautifulsoup', 'selenium', 'scrapy'],
            'api_server': ['flask', 'fastapi', 'express', 'app.get', 'app.post'],
            'testing': ['test_', 'assert', 'expect', 'describe', 'it('],
            'configuration': ['config', 'settings', 'env', 'constants'],
            'utility': ['utils', 'helpers', 'tools', 'common'],
            'main_logic': ['main(', '__main__', 'if __name__'],
            'class_definition': ['class ', '@dataclass', 'interface ', 'struct '],
            'database': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE'],
            'frontend_component': ['render', 'useState', 'component', '<div', 'jsx']
        }
        
        for purpose, keywords in purposes.items():
            if any(keyword in code for keyword in keywords):
                return purpose
        
        return 'general'
    
    def _get_id_from_url(self, url: str) -> str:
        """從 URL 提取 ID"""
        if '/share/' in url:
            return url.split('/share/')[1].split('?')[0]
        return url.replace('/', '_')[-20:]
    
    def _save_conversation(self, conversation: ManusConversation, output_path: Path):
        """保存對話數據"""
        # 保存 JSON
        json_path = output_path / f"conversation_{self._get_id_from_url(conversation.url)}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(conversation), f, ensure_ascii=False, indent=2)
        
        # 生成 Markdown 報告
        md_path = output_path / f"report_{self._get_id_from_url(conversation.url)}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {conversation.title}\n\n")
            f.write(f"**URL**: {conversation.url}\n")
            f.write(f"**分析時間**: {conversation.extracted_at}\n")
            f.write(f"**任務類型**: {conversation.task_type}\n\n")
            
            if not conversation.success:
                f.write(f"## ❌ 分析失敗\n\n{conversation.error_message}\n\n")
                return
            
            f.write(f"## 📊 統計\n\n")
            f.write(f"- 消息數量: {len(conversation.messages)}\n")
            f.write(f"- 代碼塊數量: {len(conversation.code_blocks)}\n")
            f.write(f"- 工具使用: {len(conversation.tools_used)}\n\n")
            
            if conversation.tools_used:
                f.write(f"## 🔧 工具使用\n\n")
                for tool in conversation.tools_used[:10]:
                    f.write(f"- **{tool.tool_name}**\n")
                    if tool.parameters:
                        f.write(f"  - 上下文: {tool.parameters.get('context', '')[:100]}...\n")
            
            if conversation.code_blocks:
                f.write(f"\n## 💻 代碼分析\n\n")
                languages = {}
                for block in conversation.code_blocks:
                    languages[block.language] = languages.get(block.language, 0) + 1
                
                f.write("### 語言分布\n\n")
                for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- {lang}: {count} 個代碼塊\n")
                
                f.write("\n### 代碼用途\n\n")
                purposes = {}
                for block in conversation.code_blocks:
                    if block.purpose:
                        purposes[block.purpose] = purposes.get(block.purpose, 0) + 1
                
                for purpose, count in sorted(purposes.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- {purpose}: {count} 個\n")
            
            if conversation.messages:
                f.write(f"\n## 💬 對話摘要\n\n")
                f.write(f"前 5 條消息:\n\n")
                for i, msg in enumerate(conversation.messages[:5], 1):
                    f.write(f"{i}. **{msg.role}**: {msg.content[:200]}...\n\n")
        
        logger.info(f"✅ 已保存分析結果: {json_path}")
        logger.info(f"📄 已生成報告: {md_path}")
    
    def _generate_batch_report(self, results: List[ManusConversation], output_path: Path):
        """生成批量分析報告"""
        report_path = output_path / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        success_count = sum(1 for r in results if r.success)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Manus 批量分析報告\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"## 📊 總體統計\n\n")
            f.write(f"- 總任務數: {len(results)}\n")
            f.write(f"- 成功: {success_count}\n")
            f.write(f"- 失敗: {len(results) - success_count}\n")
            f.write(f"- 成功率: {success_count/len(results)*100:.1f}%\n\n")
            
            # 任務類型分布
            task_types = {}
            for r in results:
                if r.success and r.task_type:
                    task_types[r.task_type] = task_types.get(r.task_type, 0) + 1
            
            if task_types:
                f.write(f"## 📈 任務類型分布\n\n")
                for task_type, count in sorted(task_types.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- {task_type}: {count} ({count/success_count*100:.1f}%)\n")
            
            # 工具使用統計
            all_tools = {}
            for r in results:
                if r.success:
                    for tool in r.tools_used:
                        all_tools[tool.tool_name] = all_tools.get(tool.tool_name, 0) + 1
            
            if all_tools:
                f.write(f"\n## 🔧 工具使用頻率\n\n")
                for tool, count in sorted(all_tools.items(), key=lambda x: x[1], reverse=True)[:10]:
                    f.write(f"- {tool}: {count} 次\n")
            
            # 編程語言統計
            all_languages = {}
            for r in results:
                if r.success:
                    for block in r.code_blocks:
                        all_languages[block.language] = all_languages.get(block.language, 0) + 1
            
            if all_languages:
                f.write(f"\n## 💻 編程語言分布\n\n")
                for lang, count in sorted(all_languages.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- {lang}: {count} 個代碼塊\n")
            
            # 詳細結果
            f.write(f"\n## 📋 詳細結果\n\n")
            for i, r in enumerate(results, 1):
                status = "✅" if r.success else "❌"
                f.write(f"{i}. {status} [{r.title}]({r.url})\n")
                if r.success:
                    f.write(f"   - 類型: {r.task_type}\n")
                    f.write(f"   - 消息: {len(r.messages)}\n")
                    f.write(f"   - 代碼: {len(r.code_blocks)}\n")
                    f.write(f"   - 工具: {len(r.tools_used)}\n")
                else:
                    f.write(f"   - 錯誤: {r.error_message}\n")
                f.write("\n")
        
        # 生成訓練數據
        training_data_path = output_path / f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(training_data_path, 'w', encoding='utf-8') as f:
            for r in results:
                if r.success and len(r.messages) > 0:
                    # 生成訓練樣本
                    for i in range(0, len(r.messages)-1, 2):
                        if i+1 < len(r.messages):
                            user_msg = r.messages[i]
                            assistant_msg = r.messages[i+1]
                            
                            training_sample = {
                                'instruction': user_msg.content[:500],
                                'response': assistant_msg.content[:1000],
                                'task_type': r.task_type,
                                'tools_used': [t.tool_name for t in r.tools_used][:5],
                                'has_code': len(r.code_blocks) > 0,
                                'languages': list(set(b.language for b in r.code_blocks))[:3]
                            }
                            
                            f.write(json.dumps(training_sample, ensure_ascii=False) + '\n')
        
        logger.info(f"✅ 批量報告已生成: {report_path}")
        logger.info(f"🎯 訓練數據已生成: {training_data_path}")

def main():
    parser = argparse.ArgumentParser(description='Manus Complete Analyzer - 完整的對話分析工具')
    parser.add_argument('--url', type=str, help='單個 Manus URL')
    parser.add_argument('--urls-file', type=str, help='包含多個 URL 的文件')
    parser.add_argument('--output-dir', type=str, default='./manus_analysis', help='輸出目錄')
    parser.add_argument('--email', type=str, help='Manus 登錄郵箱')
    parser.add_argument('--password', type=str, help='Manus 登錄密碼')
    
    args = parser.parse_args()
    
    # 檢查 Playwright
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright 未安裝，請執行:")
        print("pip install playwright")
        print("playwright install chromium")
        return
    
    # 創建分析器
    analyzer = ManusCompleteAnalyzer(
        email=args.email,
        password=args.password
    )
    
    # 執行分析
    if args.url:
        # 分析單個 URL
        print(f"🔍 分析單個 URL: {args.url}")
        asyncio.run(analyzer.analyze_url(args.url, args.output_dir))
        
    elif args.urls_file:
        # 批量分析
        with open(args.urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip().startswith('http')]
        
        print(f"📚 批量分析 {len(urls)} 個 URL")
        asyncio.run(analyzer.analyze_batch(urls, args.output_dir))
        
    else:
        # 交互模式
        print("🎯 Manus Complete Analyzer")
        print("=" * 50)
        
        # 使用已有的任務文件
        if Path('manus_tasks_manual.txt').exists():
            print("\n找到 manus_tasks_manual.txt 文件")
            use_file = input("是否使用此文件中的 URL? (y/n): ").lower() == 'y'
            
            if use_file:
                urls = []
                with open('manus_tasks_manual.txt', 'r') as f:
                    for line in f:
                        if line.strip().startswith('http'):
                            urls.append(line.strip())
                
                print(f"\n找到 {len(urls)} 個 URL")
                
                # 詢問分析數量
                num = input(f"要分析多少個? (1-{len(urls)}) [默認: 5]: ").strip()
                num = int(num) if num.isdigit() else 5
                num = min(num, len(urls))
                
                print(f"\n即將分析前 {num} 個 URL")
                asyncio.run(analyzer.analyze_batch(urls[:num], args.output_dir))
                return
        
        # 手動輸入
        url = input("\n請輸入 Manus URL: ").strip()
        if url:
            asyncio.run(analyzer.analyze_url(url, args.output_dir))
        else:
            print("未提供 URL")

if __name__ == "__main__":
    main()