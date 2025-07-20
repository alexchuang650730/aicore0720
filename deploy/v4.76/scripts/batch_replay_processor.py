#!/usr/bin/env python3
"""
批量 Replay 處理器
使用 manus_complete_analyzer.py 批量處理 414 個 Manus replay
並將數據整理到 data/ 目錄
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging
import shutil
import zipfile
import xml.etree.ElementTree as ET
import re

# 添加 manus_complete_analyzer.py 的路徑
sys.path.insert(0, '/Users/alexchuang/Downloads')

try:
    from manus_complete_analyzer import ManusCompleteAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError as e:
    logging.error(f"無法導入 ManusCompleteAnalyzer: {e}")
    ANALYZER_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchReplayProcessor:
    """批量 Replay 處理器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.replay_data_dir = self.data_dir / "replay_analysis"
        self.training_data_dir = self.data_dir / "training_data"
        
        # 創建目錄
        self.replay_data_dir.mkdir(parents=True, exist_ok=True)
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 統計
        self.stats = {
            'total_replays': 0,
            'processed_replays': 0,
            'failed_replays': 0,
            'total_messages': 0,
            'category_counts': {'thinking': 0, 'observation': 0, 'action': 0}
        }
    
    def extract_replay_links_from_docx(self, docx_path: str = "/Users/alexchuang/Downloads/replay.docx") -> List[str]:
        """從 DOCX 文件中提取 replay 鏈接"""
        try:
            logger.info(f"🔓 從 DOCX 提取 replay 鏈接: {docx_path}")
            
            docx_file = Path(docx_path)
            if not docx_file.exists():
                logger.error(f"DOCX 文件不存在: {docx_path}")
                return []
            
            # 提取 DOCX 文本內容
            with zipfile.ZipFile(docx_file, 'r') as docx_zip:
                document_xml = docx_zip.read('word/document.xml')
                root = ET.fromstring(document_xml)
                
                # 提取所有文本
                text_parts = []
                def extract_text_recursive(element):
                    if element.text:
                        text_parts.append(element.text)
                    for child in element:
                        extract_text_recursive(child)
                        if child.tail:
                            text_parts.append(child.tail)
                
                extract_text_recursive(root)
                full_text = ' '.join(text_parts)
            
            # 使用正則表達式查找 Share ID
            replay_links = []
            seen_share_ids = set()
            
            # 多種模式匹配
            patterns = [
                r'https://manus\.im/share/([a-zA-Z0-9_-]+)\?replay=1',
                r'manus\.im/share/([a-zA-Z0-9_-]+)',
                r'share/([a-zA-Z0-9_-]{15,})',
                r'\b([a-zA-Z0-9_-]{20,})\b'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    share_id = match
                    if self._is_valid_share_id(share_id) and share_id not in seen_share_ids:
                        seen_share_ids.add(share_id)
                        url = f"https://manus.im/share/{share_id}?replay=1"
                        replay_links.append(url)
            
            logger.info(f"✅ 從DOCX成功提取 {len(replay_links)} 個 replay 鏈接")
            
            return replay_links
            
        except Exception as e:
            logger.error(f"❌ 提取 DOCX 失敗: {e}")
            return []
    
    def extract_manual_links(self, manual_file: str = "/Users/alexchuang/alexchuangtest/aicore0720/manus_tasks_manual.txt") -> List[str]:
        """從手動收集文件中提取 replay 鏈接"""
        try:
            logger.info(f"📝 從手動收集文件提取鏈接: {manual_file}")
            
            manual_file_path = Path(manual_file)
            if not manual_file_path.exists():
                logger.warning(f"手動收集文件不存在: {manual_file}")
                return []
            
            replay_links = []
            with open(manual_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('https://manus.im/share/') and '?replay=1' in line:
                        replay_links.append(line)
            
            logger.info(f"✅ 從手動收集文件提取 {len(replay_links)} 個 replay 鏈接")
            return replay_links
            
        except Exception as e:
            logger.error(f"❌ 提取手動收集鏈接失敗: {e}")
            return []
    
    def get_all_replay_links(self) -> List[str]:
        """獲取所有 replay 鏈接（DOCX + 手動收集）"""
        # 從 DOCX 提取
        docx_links = self.extract_replay_links_from_docx()
        
        # 從手動收集文件提取
        manual_links = self.extract_manual_links()
        
        # 合併並去重
        all_links = []
        seen_urls = set()
        
        for links, source in [(docx_links, "DOCX"), (manual_links, "手動收集")]:
            for link in links:
                if link not in seen_urls:
                    all_links.append(link)
                    seen_urls.add(link)
        
        logger.info(f"🎯 總計: {len(all_links)} 個唯一 replay 鏈接")
        logger.info(f"   DOCX: {len(docx_links)} 個")
        logger.info(f"   手動收集: {len(manual_links)} 個")
        logger.info(f"   去重後: {len(all_links)} 個")
        
        # 保存合併後的鏈接列表
        links_file = self.data_dir / f"all_replay_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(links_file, 'w', encoding='utf-8') as f:
            for link in all_links:
                f.write(link + '\\n')
        
        logger.info(f"💾 所有鏈接列表已保存: {links_file}")
        
        return all_links
    
    def _is_valid_share_id(self, share_id: str) -> bool:
        """驗證 Share ID"""
        if len(share_id) < 15 or len(share_id) > 50:
            return False
        if share_id.isdigit():
            return False
        if ' ' in share_id:
            return False
        
        has_letter = any(c.isalpha() for c in share_id)
        has_number = any(c.isdigit() for c in share_id)
        if not (has_letter and has_number):
            return False
        
        # 過濾明顯的非 Share ID
        invalid_keywords = ['document', 'content', 'manus', 'share', 'http', 'replay']
        share_id_lower = share_id.lower()
        for keyword in invalid_keywords:
            if keyword in share_id_lower:
                return False
        
        return True
    
    async def process_single_replay(self, url: str, analyzer: ManusCompleteAnalyzer) -> Dict[str, Any]:
        """處理單個 replay"""
        try:
            share_id = self._extract_share_id_from_url(url)
            logger.info(f"📥 處理 replay: {share_id}")
            
            # 檢查是否已經處理過
            raw_file = self.replay_data_dir / f"raw_{share_id}.json"
            analysis_file = self.replay_data_dir / f"analysis_{share_id}.json"
            
            if raw_file.exists() and analysis_file.exists():
                logger.info(f"⏭️ 跳過已處理的 replay: {share_id}")
                return None
            
            # 提取對話數據 - 使用修正的方法
            conversation_data = await self.extract_conversation_correctly(url, analyzer)
            
            if not conversation_data or not conversation_data.get('messages'):
                logger.warning(f"⚠️ 無法提取數據: {share_id}")
                return None
            
            # 分析對話
            analysis_result = analyzer.analyze_conversation(conversation_data)
            
            # 保存原始數據
            with open(raw_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            # 保存分析結果
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            
            # 更新統計
            message_count = len(conversation_data.get('messages', []))
            self.stats['total_messages'] += message_count
            self.stats['processed_replays'] += 1
            
            # 統計類別
            if 'statistics' in analysis_result:
                stats = analysis_result['statistics']
                self.stats['category_counts']['thinking'] += stats.get('thinking_count', 0)
                self.stats['category_counts']['observation'] += stats.get('observation_count', 0)
                self.stats['category_counts']['action'] += stats.get('action_count', 0)
            
            logger.info(f"✅ 完成 {share_id}: {message_count} 條消息")
            
            return {
                'share_id': share_id,
                'url': url,
                'message_count': message_count,
                'processing_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 處理 replay 失敗 {url}: {e}")
            self.stats['failed_replays'] += 1
            return None
    
    def _extract_share_id_from_url(self, url: str) -> str:
        """從 URL 提取 Share ID"""
        match = re.search(r'share/([a-zA-Z0-9_-]+)', url)
        return match.group(1) if match else 'unknown'
    
    async def extract_conversation_correctly(self, url: str, analyzer) -> Dict[str, Any]:
        """正確提取對話數據，針對 .prose 元素和動態加載"""
        try:
            logger.info(f"🔍 正確提取對話數據: {url}")
            
            # 訪問頁面
            await analyzer.page.goto(url, wait_until='networkidle')
            
            # 等待初始加載
            await asyncio.sleep(8)
            
            # 獲取頁面標題
            title = await analyzer.page.title()
            
            conversation_data = {
                'url': url,
                'title': title,
                'extraction_timestamp': datetime.now().isoformat(),
                'messages': [],
                'files': [],
                'file_count': 0
            }
            
            # 執行多次下拉滾動來加載完整對話內容
            logger.info("📜 開始滾動加載完整對話...")
            previous_count = 0
            stable_count = 0
            
            for scroll_attempt in range(10):  # 最多滾動10次
                # 滾動到頁面底部
                await analyzer.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(3)
                
                # 檢查當前 .prose 元素數量
                prose_elements = await analyzer.page.query_selector_all('.prose')
                current_count = len(prose_elements)
                
                logger.info(f"   滾動 {scroll_attempt + 1}: 找到 {current_count} 個 .prose 元素")
                
                # 如果數量沒有增加，說明已經加載完成
                if current_count == previous_count:
                    stable_count += 1
                    if stable_count >= 2:  # 連續2次沒有變化才停止
                        logger.info("✅ 對話內容已完全加載")
                        break
                else:
                    stable_count = 0
                    previous_count = current_count
                
                # 再次等待內容加載
                await asyncio.sleep(5)
            
            # 最終處理所有 .prose 元素
            final_prose_elements = await analyzer.page.query_selector_all('.prose')
            logger.info(f"🎯 最終找到 {len(final_prose_elements)} 個 .prose 元素")
            
            # 處理所有消息元素
            if len(final_prose_elements) >= 3:  # 至少要有3個才算正常對話
                for i, element in enumerate(final_prose_elements):
                    try:
                        content = await element.text_content()
                        if content and content.strip() and len(content.strip()) > 10:
                            
                            # 檢查父元素來確定消息類型
                            parent_class = await element.evaluate('el => el.parentElement?.className || ""')
                            
                            # 根據內容和位置進行分類
                            msg_type = self._classify_message_type(content, i, parent_class)
                            category = self._classify_message_category(content, msg_type)
                            
                            message = {
                                'index': len(conversation_data['messages']),
                                'type': msg_type,
                                'category': category,
                                'content': content.strip(),
                                'timestamp': datetime.now().isoformat(),
                                'extraction_method': 'prose_element_with_scroll',
                                'parent_class': parent_class,
                                'confidence': self._calculate_confidence(content, category)
                            }
                            
                            conversation_data['messages'].append(message)
                            
                    except Exception as e:
                        logger.warning(f"處理 .prose 元素 {i} 時出錯: {e}")
                        continue
            
            # 提取任務相關文件
            await self._extract_task_files(analyzer.page, conversation_data)
            
            logger.info(f"✅ 成功提取 {len(conversation_data['messages'])} 條消息和 {conversation_data['file_count']} 個文件")
            return conversation_data
            
        except Exception as e:
            logger.error(f"❌ 正確提取對話失敗: {e}")
            return {}
    
    def _classify_message_type(self, content: str, index: int, parent_class: str) -> str:
        """根據內容和位置分類消息類型"""
        content_lower = content.lower()
        
        # 系統消息
        if any(keyword in content for keyword in ['正在從任務', '已成功從原任務', '繼承上下文', '任務將在轉移完成後繼續']):
            return 'system_message'
        
        # 用戶消息 (通常較短且是指令性的)
        if len(content) < 100 and any(keyword in content for keyword in ['好的', '請', '幫我', '我需要', '開始']):
            return 'user_message'
        
        # AI回應 (通常較長且包含詳細說明)
        if len(content) > 100:
            return 'ai_response'
        
        # 默認根據位置判斷
        return 'ai_response' if index % 2 == 1 else 'user_message'
    
    def _classify_message_category(self, content: str, msg_type: str) -> str:
        """將消息分類為 thinking/observation/action"""
        content_lower = content.lower()
        
        # Action 類別 - 明確的動作指令
        action_keywords = [
            '開始', '執行', '運行', '創建', '修改', '更新', '部署', '推送', 
            '安裝', '配置', '連接', '調用', '應用', '實現', '構建',
            'git', 'ssh', 'deploy', 'push', 'pull', 'commit'
        ]
        
        if any(keyword in content for keyword in action_keywords):
            return 'action'
        
        # Observation 類別 - 觀察結果、狀態報告
        observation_keywords = [
            '成功', '完成', '失敗', '錯誤', '已', '結果', '狀態', '發現',
            '檢查', '確認', '驗證', '顯示', '返回', '輸出'
        ]
        
        if any(keyword in content for keyword in observation_keywords):
            return 'observation'
        
        # Thinking 類別 - 分析、計劃、理解
        thinking_keywords = [
            '理解', '分析', '認為', '需要', '明白', '根據', '基於', '考慮',
            '思考', '評估', '判斷', '計劃', '設計', '策略'
        ]
        
        if any(keyword in content for keyword in thinking_keywords):
            return 'thinking'
        
        # 默認分類
        if msg_type == 'system_message':
            return 'observation'
        elif msg_type == 'user_message':
            return 'action'
        else:
            return 'thinking'
    
    def _calculate_confidence(self, content: str, category: str) -> float:
        """計算分類置信度"""
        # 基於內容長度和關鍵詞匹配計算置信度
        base_confidence = 0.6
        
        # 根據內容長度調整
        if len(content) > 200:
            base_confidence += 0.1
        elif len(content) < 50:
            base_confidence -= 0.1
        
        # 根據關鍵詞匹配調整
        content_lower = content.lower()
        category_keywords = {
            'action': ['開始', '執行', '運行', '創建', 'git', 'deploy'],
            'observation': ['成功', '完成', '失敗', '已', '結果'],
            'thinking': ['理解', '分析', '需要', '明白', '計劃']
        }
        
        if category in category_keywords:
            matches = sum(1 for keyword in category_keywords[category] if keyword in content)
            base_confidence += matches * 0.05
        
        return min(max(base_confidence, 0.3), 0.95)
    
    async def _extract_task_files(self, page, conversation_data: Dict[str, Any]):
        """提取任務相關的文件信息"""
        try:
            logger.info("📂 開始提取任務文件...")
            
            # 尋找文件相關的選擇器
            file_selectors = [
                '[data-testid*="file"]',
                '.file-item',
                '.attachment',
                'a[href*="/files/"]',
                'div[class*="file"]',
                'span[class*="file"]',
                '.document',
                '.code-file'
            ]
            
            files_found = []
            
            for selector in file_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        logger.info(f"   選擇器 {selector}: 找到 {len(elements)} 個文件元素")
                        
                        for elem in elements:
                            try:
                                # 獲取文件信息
                                text = await elem.text_content()
                                href = await elem.get_attribute('href')
                                class_name = await elem.get_attribute('class')
                                
                                if text and text.strip():
                                    file_info = {
                                        'name': text.strip(),
                                        'selector': selector,
                                        'href': href,
                                        'class': class_name,
                                        'type': self._classify_file_type(text.strip())
                                    }
                                    files_found.append(file_info)
                                    
                            except Exception as e:
                                logger.warning(f"處理文件元素時出錯: {e}")
                                continue
                                
                except Exception as e:
                    logger.warning(f"選擇器 {selector} 查找失敗: {e}")
                    continue
            
            # 去重並整理文件列表
            unique_files = []
            seen_names = set()
            
            for file_info in files_found:
                name = file_info['name']
                if name not in seen_names and len(name) > 2:  # 過濾太短的文件名
                    unique_files.append(file_info)
                    seen_names.add(name)
            
            conversation_data['files'] = unique_files
            conversation_data['file_count'] = len(unique_files)
            
            if unique_files:
                logger.info(f"📁 找到 {len(unique_files)} 個唯一文件:")
                for i, file_info in enumerate(unique_files[:10]):  # 只顯示前10個
                    logger.info(f"   {i+1}. {file_info['name']} ({file_info['type']})")
                if len(unique_files) > 10:
                    logger.info(f"   ... 還有 {len(unique_files) - 10} 個文件")
            else:
                logger.info("📁 未找到文件信息")
                
        except Exception as e:
            logger.error(f"❌ 提取文件信息失敗: {e}")
            conversation_data['files'] = []
            conversation_data['file_count'] = 0
    
    def _classify_file_type(self, filename: str) -> str:
        """根據文件名分類文件類型"""
        filename_lower = filename.lower()
        
        # 代碼文件
        code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.json', '.xml', '.yaml', '.yml']
        if any(ext in filename_lower for ext in code_extensions):
            return 'code'
        
        # 配置文件
        config_files = ['config', 'package.json', 'requirements.txt', 'dockerfile', 'makefile', '.env']
        if any(config in filename_lower for config in config_files):
            return 'config'
        
        # 文檔文件
        doc_extensions = ['.md', '.txt', '.doc', '.pdf', '.readme']
        if any(ext in filename_lower for ext in doc_extensions):
            return 'document'
        
        # 圖片文件
        img_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']
        if any(ext in filename_lower for ext in img_extensions):
            return 'image'
        
        return 'other'
    
    async def process_all_replays(self, replay_links: List[str]):
        """批量處理所有 replay"""
        if not ANALYZER_AVAILABLE:
            logger.error("❌ ManusCompleteAnalyzer 不可用")
            return
        
        self.stats['total_replays'] = len(replay_links)
        logger.info(f"🚀 開始批量處理 {len(replay_links)} 個 replay")
        
        analyzer = ManusCompleteAnalyzer()
        
        try:
            await analyzer.initialize_browser()
            
            processed_results = []
            
            for i, url in enumerate(replay_links, 1):
                logger.info(f"\\n📊 進度: {i}/{len(replay_links)}")
                
                result = await self.process_single_replay(url, analyzer)
                if result:
                    processed_results.append(result)
                
                # 避免請求過快
                await asyncio.sleep(2)
                
                # 每處理 10 個就保存一次統計
                if i % 10 == 0:
                    await self._save_progress_stats(i, processed_results)
            
            # 最終統計
            await self._save_final_stats(processed_results)
            
        finally:
            await analyzer.close_browser()
    
    async def _save_progress_stats(self, current_index: int, processed_results: List[Dict]):
        """保存進度統計"""
        progress_stats = {
            'timestamp': datetime.now().isoformat(),
            'current_progress': current_index,
            'total_replays': self.stats['total_replays'],
            'processed_replays': self.stats['processed_replays'],
            'failed_replays': self.stats['failed_replays'],
            'success_rate': (self.stats['processed_replays'] / current_index * 100) if current_index > 0 else 0,
            'processed_results': processed_results[-10:]  # 只保存最近 10 個結果
        }
        
        progress_file = self.data_dir / f"processing_progress_{datetime.now().strftime('%Y%m%d')}.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_stats, f, ensure_ascii=False, indent=2)
    
    async def _save_final_stats(self, processed_results: List[Dict]):
        """保存最終統計"""
        final_stats = {
            'processing_completed': datetime.now().isoformat(),
            'total_replays': self.stats['total_replays'],
            'processed_replays': self.stats['processed_replays'],
            'failed_replays': self.stats['failed_replays'],
            'success_rate': (self.stats['processed_replays'] / self.stats['total_replays'] * 100) if self.stats['total_replays'] > 0 else 0,
            'total_messages': self.stats['total_messages'],
            'average_messages_per_replay': self.stats['total_messages'] / max(self.stats['processed_replays'], 1),
            'category_distribution': self.stats['category_counts'],
            'estimated_training_tokens': self.stats['total_messages'] * 50,
            'processed_results': processed_results
        }
        
        # 保存 JSON 統計
        stats_file = self.data_dir / f"final_processing_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, ensure_ascii=False, indent=2)
        
        # 生成 Markdown 報告
        report_file = self.data_dir / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(final_stats))
        
        logger.info(f"📊 最終統計已保存:")
        logger.info(f"   JSON: {stats_file}")
        logger.info(f"   報告: {report_file}")
        
        # 顯示摘要
        print(f"\\n🎉 批量處理完成!")
        print(f"   成功處理: {self.stats['processed_replays']}/{self.stats['total_replays']} ({final_stats['success_rate']:.1f}%)")
        print(f"   總消息數: {self.stats['total_messages']:,}")
        print(f"   估算 tokens: {final_stats['estimated_training_tokens']:,}")
        print(f"   思考消息: {self.stats['category_counts']['thinking']:,}")
        print(f"   觀察消息: {self.stats['category_counts']['observation']:,}")
        print(f"   動作消息: {self.stats['category_counts']['action']:,}")
    
    def _generate_markdown_report(self, stats: Dict) -> str:
        """生成 Markdown 報告"""
        return f"""# Manus Replay 批量處理報告

## 處理摘要

- **處理時間**: {stats['processing_completed']}
- **總 replay 數**: {stats['total_replays']}
- **成功處理**: {stats['processed_replays']}
- **失敗數量**: {stats['failed_replays']}
- **成功率**: {stats['success_rate']:.1f}%

## 數據統計

- **總消息數**: {stats['total_messages']:,}
- **平均每個 replay**: {stats['average_messages_per_replay']:.1f} 條消息
- **估算 tokens**: {stats['estimated_training_tokens']:,}

## 類別分布

- **🧠 思考 (Thinking)**: {stats['category_distribution']['thinking']:,} 條 ({stats['category_distribution']['thinking']/max(stats['total_messages'], 1)*100:.1f}%)
- **👁️ 觀察 (Observation)**: {stats['category_distribution']['observation']:,} 條 ({stats['category_distribution']['observation']/max(stats['total_messages'], 1)*100:.1f}%)
- **🎯 動作 (Action)**: {stats['category_distribution']['action']:,} 條 ({stats['category_distribution']['action']/max(stats['total_messages'], 1)*100:.1f}%)

## 訓練建議

基於收集到的 {stats['total_messages']:,} 條消息和 {stats['estimated_training_tokens']:,} tokens：

### 🎯 推薦策略: K2 完整微調
- **數據充足性**: ✅ 足夠進行完整微調
- **預期效果**: 🚀 顯著提升，接近 Claude 水平
- **實施複雜度**: 🟡 中等
- **預計時間**: 1-2 天

### 🤔 可選策略: DeepSWE 部分微調
- **數據適用性**: {('✅ 可行' if stats['total_messages'] > 10000 else '⚠️ 數據偏少')}
- **預期效果**: 🎯 SOTA 代碼生成能力
- **實施複雜度**: 🔴 較高
- **預計時間**: 3-5 天

## 下一步行動

1. **立即執行**: 啟動 K2 訓練系統
2. **數據整合**: 將分析結果轉換為訓練格式
3. **質量檢查**: 抽檢部分數據確保分類準確性
4. **訓練配置**: 設置訓練參數並開始微調

## 文件輸出

- 原始數據: `data/replay_analysis/raw_*.json`
- 分析結果: `data/replay_analysis/analysis_*.json`
- 訓練數據: 待生成至 `data/training_data/`
"""
    
    def generate_training_data(self):
        """生成訓練數據"""
        logger.info("🔄 開始生成訓練數據...")
        
        training_samples = []
        
        # 遍歷所有分析結果
        for analysis_file in self.replay_data_dir.glob("analysis_*.json"):
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                
                # 提取訓練樣本
                if 'categories' in analysis_data:
                    for category, messages in analysis_data['categories'].items():
                        for msg in messages:
                            sample = {
                                'instruction': '分析並執行任務',
                                'input': msg.get('content', '')[:300],  # 限制長度
                                'output': self._generate_output(msg.get('content', ''), category),
                                'category': category,
                                'confidence': msg.get('confidence', 0.6),
                                'source': 'manus_replay_batch',
                                'source_file': str(analysis_file),
                                'metadata': {
                                    'timestamp': datetime.now().isoformat(),
                                    'share_id': analysis_file.stem.replace('analysis_', ''),
                                    'extraction_method': msg.get('extraction_method', 'unknown')
                                }
                            }
                            
                            if len(sample['input'].strip()) > 10:  # 過濾太短的內容
                                training_samples.append(sample)
                
            except Exception as e:
                logger.error(f"處理分析文件失敗 {analysis_file}: {e}")
        
        # 保存訓練數據
        if training_samples:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            training_file = self.training_data_dir / f"manus_training_samples_{timestamp}.jsonl"
            
            with open(training_file, 'w', encoding='utf-8') as f:
                for sample in training_samples:
                    f.write(json.dumps(sample, ensure_ascii=False) + '\\n')
            
            logger.info(f"💾 訓練數據已生成: {training_file}")
            logger.info(f"   樣本數量: {len(training_samples):,}")
            
            return str(training_file)
        
        return None
    
    def _generate_output(self, content: str, category: str) -> str:
        """生成訓練輸出"""
        if category == 'action':
            return f"執行操作: {content[:200]}"
        elif category == 'observation':
            return f"觀察結果: {content[:200]}"
        else:  # thinking
            return f"分析思考: {content[:200]}"

async def main():
    """主函數"""
    processor = BatchReplayProcessor()
    
    print("🚀 Manus Replay 批量處理器")
    print("=" * 50)
    
    # 1. 獲取所有 replay 鏈接（DOCX + 手動收集）
    print("📄 步驟 1: 獲取所有 replay 鏈接...")
    replay_links = processor.get_all_replay_links()
    
    if not replay_links:
        print("❌ 未找到任何 replay 鏈接")
        return
    
    print(f"✅ 總計找到 {len(replay_links)} 個 replay 鏈接")
    
    # 2. 批量處理 replay
    print("\\n📥 步驟 2: 批量處理 replay...")
    await processor.process_all_replays(replay_links)
    
    # 3. 生成訓練數據
    print("\\n🔄 步驟 3: 生成訓練數據...")
    training_file = processor.generate_training_data()
    
    if training_file:
        print(f"✅ 訓練數據已生成: {training_file}")
    
    print("\\n🎉 所有處理完成！")
    print("\\n💡 下一步建議:")
    print("1. 檢查 data/replay_analysis/ 中的分析結果")
    print("2. 使用生成的訓練數據進行 K2 微調")
    print("3. 測試微調後的模型效果")

if __name__ == "__main__":
    asyncio.run(main())