#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版 Manus 對話分解分析系統
基於參考代碼，集成網頁抓取和對話分析功能，將對話分解為思考、觀察、動作三個類別
"""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import argparse
from pathlib import Path

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ 請先安裝 Playwright: pip install playwright")
    print("然後安裝瀏覽器: playwright install chromium")

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ManusEnhancedAnalyzer:
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """初始化增強分析器"""
        self.email = email
        self.password = password
        self.browser = None
        self.page = None
        self.logged_in = False
        
        # 🧠 思考模式關鍵詞（中英文）
        self.thinking_patterns = [
            # 中文
            r'我.*理解', r'我.*分析', r'我.*認為', r'我.*發現', r'我.*需要',
            r'讓我.*', r'現在.*', r'根據.*', r'基於.*', r'考慮.*',
            r'思考.*', r'分析.*', r'評估.*', r'判斷.*', r'明白.*', r'理解.*',
            r'看起來.*', r'似乎.*', r'應該.*', r'可能.*', r'建議.*',
            # English
            r"I understand", r"I'll analyze", r"I think", r"Let me",
            r"Based on", r"According to", r"Considering", r"It seems",
            r"I need to", r"I should", r"Looking at", r"Analyzing"
        ]
        
        # 👁️ 觀察模式關鍵詞
        self.observation_patterns = [
            # 中文
            r'檢查.*', r'查看.*', r'觀察.*', r'發現.*', r'確認.*', r'驗證.*',
            r'測試結果', r'輸出.*', r'返回.*', r'顯示.*', r'狀態.*', r'結果.*',
            r'響應.*', r'錯誤.*', r'成功.*', r'失敗.*', r'完成.*', r'收到.*',
            # English
            r'Checking', r'Found', r'Result', r'Output', r'Status',
            r'Success', r'Failed', r'Error', r'Completed', r'Verified',
            r'Response', r'Returned', r'Showing', r'Detected'
        ]
        
        # 🎯 動作模式關鍵詞
        self.action_patterns = [
            # 中文
            r'執行.*', r'運行.*', r'啟動.*', r'停止.*', r'創建.*', r'修改.*',
            r'刪除.*', r'配置.*', r'安裝.*', r'部署.*', r'連接.*', r'發送.*',
            r'調用.*', r'使用.*', r'應用.*', r'實現.*', r'構建.*', r'編寫.*',
            # English
            r'Executing', r'Running', r'Creating', r'Modifying', r'Deleting',
            r'Installing', r'Deploying', r'Connecting', r'Sending', r'Calling',
            r'Building', r'Writing', r'Implementing', r'Configuring'
        ]
        
        # 命令行模式
        self.command_patterns = [
            r'^\$', r'^>', r'^#', r'^ubuntu@', r'^root@',
            r'^npm ', r'^pip ', r'^git ', r'^docker ', r'^python ',
            r'^node ', r'^cargo ', r'^rustc ', r'^go '
        ]
    
    async def initialize_browser(self):
        """初始化瀏覽器"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # 設為 False 方便調試
                args=['--disable-blink-features=AutomationControlled']
            )
            self.page = await self.browser.new_page()
            logger.info("瀏覽器初始化成功")
            
            # 如果有登錄憑證，嘗試登錄
            if self.email and self.password:
                await self._login()
                
        except Exception as e:
            logger.error(f"瀏覽器初始化失敗: {e}")
            raise
    
    async def _login(self):
        """登錄 Manus"""
        logger.info("🔐 正在嘗試登錄 Manus...")
        
        try:
            await self.page.goto('https://manus.im/signin', wait_until='networkidle')
            await self.page.wait_for_timeout(2000)
            
            # 填寫登錄表單
            await self.page.fill('input[type="email"]', self.email)
            await self.page.fill('input[type="password"]', self.password)
            
            # 點擊登錄
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_timeout(5000)
            
            # 檢查登錄狀態
            if 'signin' not in self.page.url:
                logger.info("✅ 登錄成功")
                self.logged_in = True
                
                # 保存 cookies
                cookies = await self.page.context.cookies()
                with open('manus_cookies.json', 'w') as f:
                    json.dump(cookies, f)
            else:
                logger.warning("❌ 登錄失敗，繼續以訪客模式運行")
                
        except Exception as e:
            logger.error(f"登錄過程出錯: {e}")
    
    async def extract_conversation_from_web(self, url: str) -> Dict[str, Any]:
        """從網頁提取對話數據"""
        try:
            logger.info(f"正在訪問 Manus 頁面: {url}")
            await self.page.goto(url, wait_until='networkidle')
            
            # 等待頁面加載和 replay 開始
            await asyncio.sleep(5)
            
            # 檢查是否需要登錄
            if await self._check_login_required():
                logger.warning("此頁面需要登錄才能查看")
                if not self.logged_in:
                    return {}
            
            # 提取頁面標題
            title = await self.page.title()
            
            conversation_data = {
                'url': url,
                'title': title,
                'extraction_timestamp': datetime.now().isoformat(),
                'messages': []
            }
            
            # 嘗試多種方式提取對話內容
            await self._extract_messages_by_selectors(conversation_data)
            
            if not conversation_data['messages']:
                await self._extract_messages_by_text(conversation_data)
            
            # 截圖保存
            screenshot_path = f"manus_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"📸 已保存截圖: {screenshot_path}")
            
            logger.info(f"成功提取 {len(conversation_data['messages'])} 條消息")
            return conversation_data
            
        except Exception as e:
            logger.error(f"網頁提取失敗: {e}")
            return {}
    
    async def _check_login_required(self) -> bool:
        """檢查是否需要登錄"""
        login_indicators = [
            'button:has-text("Sign in")',
            'button:has-text("Log in")',
            'input[type="password"]',
            '.login-form'
        ]
        
        for indicator in login_indicators:
            if await self.page.locator(indicator).count() > 0:
                return True
        return False
    
    async def _extract_messages_by_selectors(self, conversation_data: Dict[str, Any]):
        """通過 CSS 選擇器提取消息"""
        selectors = [
            # Manus 特定選擇器
            '.message-content',
            '.chat-message',
            '.conversation-item',
            '[data-testid*="message"]',
            '.manus-response',
            '.terminal-output',
            '.command-execution',
            # 通用選擇器
            'div[class*="message"]',
            'div[class*="chat"]',
            'article',
            '.prose',
            'div[role="article"]',
            'div[class*="conversation"]',
            'p',
            'pre',
            'code'
        ]
        
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    logger.info(f"使用選擇器 {selector} 找到 {len(elements)} 個元素")
                    
                    for i, element in enumerate(elements):
                        content = await element.text_content()
                        if content and content.strip() and len(content.strip()) > 10:
                            # 避免重複
                            if any(msg['content'] == content.strip() for msg in conversation_data['messages']):
                                continue
                                
                            msg_type = await self._determine_web_message_type(element, content)
                            
                            message = {
                                'index': len(conversation_data['messages']),
                                'type': msg_type,
                                'content': content.strip(),
                                'timestamp': datetime.now().isoformat(),
                                'extraction_method': f'selector_{selector}'
                            }
                            
                            conversation_data['messages'].append(message)
                    
                    if len(conversation_data['messages']) > 10:  # 找到足夠的消息就停止
                        break
                        
            except Exception as e:
                logger.warning(f"選擇器 {selector} 提取失敗: {e}")
                continue
    
    async def _extract_messages_by_text(self, conversation_data: Dict[str, Any]):
        """通過頁面文本提取消息"""
        try:
            page_text = await self.page.text_content('body')
            if not page_text:
                return
            
            # 分割文本並過濾
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            
            # 合併相關行和過濾無用內容
            processed_lines = self._process_text_lines(lines)
            
            for i, line in enumerate(processed_lines):
                if len(line) > 15 and not any(msg['content'] == line for msg in conversation_data['messages']):
                    msg_type = self._classify_text_content(line)
                    
                    message = {
                        'index': len(conversation_data['messages']),
                        'type': msg_type,
                        'content': line,
                        'timestamp': datetime.now().isoformat(),
                        'extraction_method': 'page_text'
                    }
                    
                    conversation_data['messages'].append(message)
            
            logger.info(f"通過文本提取了 {len(processed_lines)} 條消息")
            
        except Exception as e:
            logger.error(f"文本提取失敗: {e}")
    
    def _process_text_lines(self, lines: List[str]) -> List[str]:
        """處理文本行，合併相關內容"""
        processed = []
        current_block = ""
        
        for line in lines:
            # 跳過導航和 UI 元素
            skip_patterns = [
                'log in', 'sign in', 'skip to results', 'try it yourself',
                'manus is replaying', 'inherited from original',
                'continue the task', 'loading', 'please wait'
            ]
            
            if any(skip in line.lower() for skip in skip_patterns):
                continue
            
            # 檢查是否是新的消息塊開始
            if self._is_message_start(line):
                if current_block:
                    processed.append(current_block.strip())
                current_block = line
            else:
                # 繼續當前塊
                if current_block:
                    current_block += " " + line
                else:
                    current_block = line
        
        # 添加最後一個塊
        if current_block:
            processed.append(current_block.strip())
        
        return processed
    
    def _is_message_start(self, line: str) -> bool:
        """判斷是否是消息開始"""
        start_indicators = [
            # 中文
            '好的', '我', '讓我', '現在', '根據', '檢查', '執行',
            '理解', '分析', '需要', '開始', '首先', '接下來',
            # English
            'I understand', "I'll", "Let me", 'Now', 'Based on',
            'Checking', 'Executing', 'Running', 'Creating',
            # 技術指標
            'Manus is working', 'Executing command', 'ubuntu@',
            '$', '>', '#', 'root@'
        ]
        
        return any(line.startswith(indicator) for indicator in start_indicators)
    
    async def _determine_web_message_type(self, element, content: str) -> str:
        """確定網頁消息類型"""
        try:
            class_name = await element.get_attribute('class') or ""
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            
            # 基於標籤類型
            if tag_name in ['pre', 'code']:
                return 'code_block'
            
            # 基於 class 名稱
            if 'terminal' in class_name or 'command' in class_name:
                return 'command_execution'
            elif 'output' in class_name or 'result' in class_name:
                return 'terminal_output'
            elif 'status' in class_name:
                return 'status'
            elif 'error' in class_name:
                return 'error_message'
            
            return self._classify_text_content(content)
            
        except Exception:
            return self._classify_text_content(content)
    
    def _classify_text_content(self, content: str) -> str:
        """基於內容分類文本"""
        content_lower = content.lower()
        
        # 命令執行
        if any(re.match(pattern, content) for pattern in self.command_patterns):
            return 'command_execution'
        
        # 代碼塊
        if (content.count('{') > 2 or content.count('def ') > 0 or 
            content.count('function') > 0 or content.count('class ') > 0):
            return 'code_block'
        
        # 終端輸出
        if any(pattern in content for pattern in ['✅', '✓', '❌', '✗', 'Error:', 'Success:', 'Failed:']):
            return 'terminal_output'
        
        # 錯誤消息
        if any(pattern in content_lower for pattern in ['error', 'exception', 'failed', 'failure']):
            return 'error_message'
        
        # 狀態消息
        if any(pattern in content_lower for pattern in [
            'manus is working', 'thinking', 'processing', 'manus is replaying',
            'loading', 'waiting', 'initializing'
        ]):
            return 'status'
        
        # API 響應
        if content.startswith('{') and content.endswith('}'):
            return 'api_response'
        
        # 默認為文本內容
        return 'text_content'
    
    def classify_message_category(self, message: Dict[str, Any]) -> str:
        """將消息分類為思考、觀察、動作"""
        content = message.get('content', '')
        content_lower = content.lower()
        msg_type = message.get('type', '')
        
        # 基於消息類型的直接映射
        type_mapping = {
            'command_execution': 'action',
            'code_block': 'action',
            'terminal_output': 'observation',
            'status': 'observation',
            'api_response': 'observation',
            'error_message': 'observation'
        }
        
        if msg_type in type_mapping:
            return type_mapping[msg_type]
        
        # 基於內容模式分析
        thinking_score = sum(1 for pattern in self.thinking_patterns if re.search(pattern, content_lower))
        observation_score = sum(1 for pattern in self.observation_patterns if re.search(pattern, content_lower))
        action_score = sum(1 for pattern in self.action_patterns if re.search(pattern, content_lower))
        
        # 特殊情況處理
        # 如果包含問號，更可能是思考
        if '?' in content or '？' in content:
            thinking_score += 2
        
        # 如果包含命令行符號，更可能是動作
        if any(re.match(pattern, content) for pattern in self.command_patterns):
            action_score += 3
        
        # 返回得分最高的類別
        scores = {
            'thinking': thinking_score,
            'observation': observation_score,
            'action': action_score
        }
        
        max_category = max(scores, key=scores.get)
        
        # 如果所有得分都為0，根據消息類型默認分類
        if scores[max_category] == 0:
            if msg_type in ['manus_message', 'text_content']:
                # 檢查是否是用戶消息
                if any(indicator in content_lower for indicator in ['please', '請', 'help', '幫助', 'can you', '能否']):
                    return 'thinking'  # 用戶請求通常歸類為思考
                return 'thinking'
            else:
                return 'observation'
        
        return max_category
    
    def analyze_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析完整對話"""
        if not conversation_data or not conversation_data.get('messages'):
            return {}
        
        analysis_result = {
            'metadata': {
                'url': conversation_data.get('url', ''),
                'title': conversation_data.get('title', ''),
                'total_messages': len(conversation_data['messages']),
                'extraction_timestamp': conversation_data.get('extraction_timestamp', ''),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'categories': {
                'thinking': [],
                'observation': [],
                'action': []
            },
            'statistics': {
                'thinking_count': 0,
                'observation_count': 0,
                'action_count': 0,
                'category_distribution': {}
            },
            'patterns': {
                'workflow_steps': [],
                'tools_used': [],
                'languages_detected': []
            }
        }
        
        # 分析每條消息
        for message in conversation_data['messages']:
            category = self.classify_message_category(message)
            
            classified_message = {
                **message,
                'category': category,
                'confidence': self._calculate_classification_confidence(message, category)
            }
            
            analysis_result['categories'][category].append(classified_message)
            analysis_result['statistics'][f'{category}_count'] += 1
            
            # 提取模式
            self._extract_patterns(message, analysis_result['patterns'])
        
        # 計算分布
        total = sum(analysis_result['statistics'][f'{cat}_count'] for cat in ['thinking', 'observation', 'action'])
        if total > 0:
            for cat in ['thinking', 'observation', 'action']:
                count = analysis_result['statistics'][f'{cat}_count']
                analysis_result['statistics']['category_distribution'][cat] = {
                    'count': count,
                    'percentage': round(count / total * 100, 1)
                }
        
        return analysis_result
    
    def _calculate_classification_confidence(self, message: Dict[str, Any], category: str) -> float:
        """計算分類置信度"""
        content = message.get('content', '').lower()
        msg_type = message.get('type', '')
        
        # 基於消息類型的基礎置信度
        type_confidence_map = {
            'thinking': {
                'manus_message': 0.8,
                'text_content': 0.6
            },
            'observation': {
                'terminal_output': 0.9,
                'status': 0.8,
                'api_response': 0.9,
                'error_message': 0.9
            },
            'action': {
                'command_execution': 0.95,
                'code_block': 0.9,
                'api_call': 0.9
            }
        }
        
        base_confidence = type_confidence_map.get(category, {}).get(msg_type, 0.5)
        
        # 基於關鍵詞匹配的置信度
        if category == 'thinking':
            patterns = self.thinking_patterns
        elif category == 'observation':
            patterns = self.observation_patterns
        else:
            patterns = self.action_patterns
        
        pattern_matches = sum(1 for pattern in patterns if re.search(pattern, content))
        pattern_confidence = min(pattern_matches * 0.15, 1.0)
        
        # 綜合置信度
        final_confidence = (base_confidence * 0.7) + (pattern_confidence * 0.3)
        return round(final_confidence, 2)
    
    def _extract_patterns(self, message: Dict[str, Any], patterns: Dict[str, List]):
        """提取模式信息"""
        content = message.get('content', '')
        
        # 提取工具使用
        tool_patterns = {
            'git': r'git\s+\w+',
            'npm': r'npm\s+\w+',
            'pip': r'pip\s+\w+',
            'docker': r'docker\s+\w+',
            'python': r'python\s+\S+',
            'node': r'node\s+\S+',
            'curl': r'curl\s+',
            'wget': r'wget\s+',
            'ssh': r'ssh\s+',
            'scp': r'scp\s+'
        }
        
        for tool, pattern in tool_patterns.items():
            if re.search(pattern, content):
                if tool not in patterns['tools_used']:
                    patterns['tools_used'].append(tool)
        
        # 提取編程語言
        if message.get('type') == 'code_block':
            lang_indicators = {
                'python': ['def ', 'import ', 'print(', '__init__'],
                'javascript': ['function ', 'const ', 'let ', 'console.log'],
                'typescript': ['interface ', 'type ', ': string', ': number'],
                'java': ['public class', 'private ', 'static void'],
                'go': ['func ', 'package ', 'import "'],
                'rust': ['fn ', 'let mut', 'impl '],
                'cpp': ['#include', 'int main', 'std::'],
                'bash': ['#!/bin/bash', 'echo ', 'if [', 'for i in']
            }
            
            for lang, indicators in lang_indicators.items():
                if any(indicator in content for indicator in indicators):
                    if lang not in patterns['languages_detected']:
                        patterns['languages_detected'].append(lang)
    
    def generate_detailed_report(self, analysis_result: Dict[str, Any]) -> str:
        """生成詳細分析報告"""
        if not analysis_result:
            return "無法生成報告：分析結果為空"
        
        report = []
        report.append("=" * 80)
        report.append("🎯 Manus 對話分解分析詳細報告")
        report.append("=" * 80)
        report.append("")
        
        # 元數據
        metadata = analysis_result['metadata']
        report.append("📋 基本信息:")
        report.append(f"  標題: {metadata['title']}")
        report.append(f"  URL: {metadata['url']}")
        report.append(f"  總消息數: {metadata['total_messages']}")
        report.append(f"  提取時間: {metadata['extraction_timestamp']}")
        report.append(f"  分析時間: {metadata['analysis_timestamp']}")
        report.append("")
        
        # 統計信息
        stats = analysis_result['statistics']
        dist = stats.get('category_distribution', {})
        
        report.append("📊 分類統計:")
        for cat_name, cat_data in [
            ('思考 (Thinking)', 'thinking'),
            ('觀察 (Observation)', 'observation'),
            ('動作 (Action)', 'action')
        ]:
            if cat_data in dist:
                info = dist[cat_data]
                icon = {'thinking': '🧠', 'observation': '👁️', 'action': '🎯'}.get(cat_data, '📝')
                report.append(f"  {icon} {cat_name}: {info['count']} 條 ({info['percentage']}%)")
        report.append("")
        
        # 模式分析
        patterns = analysis_result.get('patterns', {})
        if patterns.get('tools_used'):
            report.append("🔧 檢測到的工具:")
            for tool in patterns['tools_used']:
                report.append(f"  - {tool}")
            report.append("")
        
        if patterns.get('languages_detected'):
            report.append("💻 檢測到的編程語言:")
            for lang in patterns['languages_detected']:
                report.append(f"  - {lang}")
            report.append("")
        
        # 詳細分類結果
        categories = analysis_result['categories']
        category_info = {
            'thinking': ('🧠', '思考', '包含分析、理解、規劃等認知過程'),
            'observation': ('👁️', '觀察', '包含檢查結果、狀態確認、輸出查看等'),
            'action': ('🎯', '動作', '包含執行命令、創建文件、調用API等')
        }
        
        for category_key, messages in categories.items():
            if not messages:
                continue
            
            icon, name, desc = category_info.get(category_key, ('📝', category_key, ''))
            
            report.append(f"{icon} 【{name.upper()}】類別詳情 ({len(messages)} 條):")
            report.append(f"   {desc}")
            report.append("-" * 60)
            
            # 顯示前5條最有代表性的消息
            sorted_messages = sorted(messages, key=lambda x: x['confidence'], reverse=True)
            for i, msg in enumerate(sorted_messages[:5], 1):
                report.append(f"\n{i}. 消息 #{msg['index']+1}")
                report.append(f"   類型: {msg['type']}")
                report.append(f"   置信度: {msg['confidence']} {'⭐' * int(msg['confidence'] * 5)}")
                report.append(f"   提取方法: {msg.get('extraction_method', 'unknown')}")
                
                # 內容預覽
                content = msg['content']
                if len(content) > 200:
                    content = content[:200] + "..."
                
                # 格式化內容顯示
                if msg['type'] in ['command_execution', 'code_block']:
                    report.append(f"   💻 內容:")
                    report.append(f"      ```")
                    report.append(f"      {content}")
                    report.append(f"      ```")
                else:
                    report.append(f"   📝 內容: {content}")
            
            if len(messages) > 5:
                report.append(f"\n   ... 還有 {len(messages) - 5} 條消息")
            
            report.append("")
        
        # 分析總結
        report.append("📈 分析總結:")
        total = metadata['total_messages']
        if total > 0:
            thinking_pct = dist.get('thinking', {}).get('percentage', 0)
            observation_pct = dist.get('observation', {}).get('percentage', 0)
            action_pct = dist.get('action', {}).get('percentage', 0)
            
            if thinking_pct > 50:
                report.append("  - 對話以思考和分析為主，表明這是一個規劃密集型任務")
            elif action_pct > 50:
                report.append("  - 對話以執行動作為主，表明這是一個實施密集型任務")
            elif observation_pct > 50:
                report.append("  - 對話以觀察和驗證為主，表明這是一個調試或測試型任務")
            else:
                report.append("  - 對話在思考、觀察和動作之間平衡，表明這是一個完整的開發流程")
        
        report.append("")
        report.append("=" * 80)
        report.append("分析完成 ✨")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    async def close_browser(self):
        """關閉瀏覽器"""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("瀏覽器已關閉")
        except Exception as e:
            logger.error(f"關閉瀏覽器失敗: {e}")

async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='Manus 增強對話分解分析工具')
    parser.add_argument('--url', help='Manus 對話 URL')
    parser.add_argument('--urls-file', help='包含多個 URL 的文件')
    parser.add_argument('--output-dir', default='.', help='輸出目錄')
    parser.add_argument('--email', help='Manus 登錄郵箱')
    parser.add_argument('--password', help='Manus 登錄密碼')
    
    args = parser.parse_args()
    
    # 確保輸出目錄存在
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 如果提供了憑證，使用它們
    if args.email and args.password:
        analyzer = ManusEnhancedAnalyzer(email=args.email, password=args.password)
    else:
        analyzer = ManusEnhancedAnalyzer()
    
    try:
        # 初始化瀏覽器
        await analyzer.initialize_browser()
        
        urls_to_process = []
        
        # 確定要處理的 URL
        if args.url:
            urls_to_process = [args.url]
        elif args.urls_file:
            with open(args.urls_file, 'r') as f:
                urls_to_process = [line.strip() for line in f if line.strip().startswith('http')]
        else:
            # 交互模式
            if Path('manus_tasks_manual.txt').exists():
                print("\n找到 manus_tasks_manual.txt 文件")
                use_file = input("是否使用此文件中的 URL? (y/n): ").lower() == 'y'
                
                if use_file:
                    with open('manus_tasks_manual.txt', 'r') as f:
                        for line in f:
                            if line.strip().startswith('http'):
                                urls_to_process.append(line.strip())
                    
                    print(f"\n找到 {len(urls_to_process)} 個 URL")
                    num = input(f"要分析多少個? (1-{len(urls_to_process)}) [默認: 1]: ").strip()
                    num = int(num) if num.isdigit() else 1
                    urls_to_process = urls_to_process[:num]
                else:
                    url = input("\n請輸入 Manus URL: ").strip()
                    if url:
                        urls_to_process = [url]
            else:
                # 使用默認測試 URL
                default_url = "https://manus.im/share/ztTmni7YtTEOjriw0ECPcb?replay=1"
                print(f"\n使用默認測試 URL: {default_url}")
                urls_to_process = [default_url]
        
        # 處理每個 URL
        for i, url in enumerate(urls_to_process, 1):
            print(f"\n處理 {i}/{len(urls_to_process)}: {url}")
            
            # 提取對話數據
            logger.info("開始提取和分析 Manus 對話...")
            conversation_data = await analyzer.extract_conversation_from_web(url)
            
            if not conversation_data or not conversation_data.get('messages'):
                logger.error("未能提取到對話數據")
                continue
            
            # 分析對話
            analysis_result = analyzer.analyze_conversation(conversation_data)
            
            # 生成時間戳
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 保存原始數據
            raw_data_file = output_path / f"manus_raw_data_{timestamp}.json"
            with open(raw_data_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            # 保存分析結果
            analysis_file = output_path / f"manus_analysis_{timestamp}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            
            # 生成並保存報告
            report = analyzer.generate_detailed_report(analysis_result)
            report_file = output_path / f"manus_report_{timestamp}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # 顯示報告
            print(report)
            
            logger.info(f"分析完成！文件已保存:")
            logger.info(f"  原始數據: {raw_data_file}")
            logger.info(f"  分析結果: {analysis_file}")
            logger.info(f"  詳細報告: {report_file}")
            
            # 如果有多個 URL，稍作延遲
            if i < len(urls_to_process):
                await asyncio.sleep(3)
    
    finally:
        await analyzer.close_browser()

if __name__ == "__main__":
    if not PLAYWRIGHT_AVAILABLE:
        print("\n請先安裝 Playwright:")
        print("pip install playwright")
        print("playwright install chromium")
    else:
        asyncio.run(main())