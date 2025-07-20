#!/usr/bin/env python3
"""
DOCX Replay 提取器
從 replay.docx 文件中提取 414 個 Manus replay 鏈接
"""

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Set
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocxReplayExtractor:
    """DOCX Replay 提取器"""
    
    def __init__(self, docx_path: str):
        self.docx_path = Path(docx_path)
        self.replay_links = []
        self.unique_share_ids = set()
        
    def extract_replays(self) -> List[Dict]:
        """提取所有 replay 鏈接"""
        try:
            logger.info(f"📄 開始解析 DOCX 文件: {self.docx_path}")
            
            # 提取文本內容
            text_content = self._extract_text_from_docx()
            
            # 查找 Manus replay 鏈接
            replay_links = self._find_replay_links(text_content)
            
            # 去重並結構化
            structured_replays = self._structure_replays(replay_links)
            
            logger.info(f"✅ 成功提取 {len(structured_replays)} 個不重複的 replay")
            
            return structured_replays
            
        except Exception as e:
            logger.error(f"❌ 提取失敗: {e}")
            return []
    
    def _extract_text_from_docx(self) -> str:
        """從 DOCX 文件提取文本內容"""
        try:
            with zipfile.ZipFile(self.docx_path, 'r') as docx_zip:
                # 讀取主要文檔內容
                document_xml = docx_zip.read('word/document.xml')
                
                # 解析 XML
                root = ET.fromstring(document_xml)
                
                # 提取所有文本
                text_elements = []
                
                # 遞歸提取文本
                def extract_text_recursive(element):
                    if element.text:
                        text_elements.append(element.text)
                    for child in element:
                        extract_text_recursive(child)
                
                extract_text_recursive(root)
                
                return '\n'.join(text_elements)
                
        except Exception as e:
            logger.error(f"提取 DOCX 文本失敗: {e}")
            return ""
    
    def _find_replay_links(self, text: str) -> List[str]:
        """查找所有 Manus replay 鏈接"""
        # Manus replay 鏈接的正則表達式
        patterns = [
            r'https://manus\.im/share/[a-zA-Z0-9]+\?replay=1',
            r'manus\.im/share/[a-zA-Z0-9]+\?replay=1',
            r'share/[a-zA-Z0-9]+\?replay=1',
            r'[a-zA-Z0-9]{20,}(?=\s*replay)',  # Share ID 模式
        ]
        
        found_links = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_links.extend(matches)
        
        # 也查找 Share ID 並構建完整鏈接
        share_id_pattern = r'\b[a-zA-Z0-9]{15,30}\b'
        potential_share_ids = re.findall(share_id_pattern, text)
        
        for share_id in potential_share_ids:
            # 檢查是否看起來像 Share ID
            if len(share_id) >= 15 and not share_id.isdigit():
                full_link = f"https://manus.im/share/{share_id}?replay=1"
                found_links.append(full_link)
        
        return found_links
    
    def _structure_replays(self, raw_links: List[str]) -> List[Dict]:
        """結構化 replay 數據"""
        structured = []
        seen_share_ids = set()
        
        for link in raw_links:
            # 標準化鏈接
            if not link.startswith('http'):
                if link.startswith('manus.im'):
                    link = 'https://' + link
                elif link.startswith('share/'):
                    link = 'https://manus.im/' + link
                elif '?replay' not in link:
                    link = f"https://manus.im/share/{link}?replay=1"
            
            # 提取 Share ID
            share_id_match = re.search(r'share/([a-zA-Z0-9]+)', link)
            if not share_id_match:
                continue
                
            share_id = share_id_match.group(1)
            
            # 去重
            if share_id in seen_share_ids:
                continue
            
            seen_share_ids.add(share_id)
            
            # 構建結構化數據
            replay_data = {
                'share_id': share_id,
                'url': f"https://manus.im/share/{share_id}?replay=1",
                'extracted_time': datetime.now().isoformat(),
                'status': 'pending',  # pending, downloaded, analyzed
                'estimated_size': 'unknown',
                'conversation_count': 0,
                'metadata': {}
            }
            
            structured.append(replay_data)
        
        # 按 share_id 排序
        structured.sort(key=lambda x: x['share_id'])
        
        return structured
    
    def save_replay_list(self, replays: List[Dict], output_dir: str = None) -> str:
        """保存 replay 列表"""
        if output_dir is None:
            output_dir = Path(__file__).parent / "data/manus_replays"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"replay_list_{timestamp}.json"
        
        # 準備輸出數據
        output_data = {
            'extraction_time': datetime.now().isoformat(),
            'source_file': str(self.docx_path),
            'total_replays': len(replays),
            'unique_share_ids': len(set(r['share_id'] for r in replays)),
            'replays': replays
        }
        
        # 保存為 JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Replay 列表已保存: {output_file}")
        
        # 也保存為純鏈接列表（便於批量處理）
        links_file = output_dir / f"replay_urls_{timestamp}.txt"
        with open(links_file, 'w', encoding='utf-8') as f:
            for replay in replays:
                f.write(replay['url'] + '\n')
        
        logger.info(f"🔗 鏈接列表已保存: {links_file}")
        
        return str(output_file)
    
    def generate_batch_download_script(self, replays: List[Dict], output_dir: str = None) -> str:
        """生成批量下載腳本"""
        if output_dir is None:
            output_dir = Path(__file__).parent / "data/manus_replays"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        script_file = output_dir / "batch_download_replays.py"
        
        script_content = f'''#!/usr/bin/env python3
"""
批量下載 Manus Replay 腳本
自動下載和分析 {len(replays)} 個 Manus replay
"""

import asyncio
import json
from pathlib import Path
import sys

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.components.memoryrag_mcp.manus_complete_analyzer import ManusCompleteAnalyzer

async def download_all_replays():
    """下載所有 replay"""
    
    # Replay 列表
    replays = {json.dumps(replays, indent=4)}
    
    analyzer = ManusCompleteAnalyzer()
    
    try:
        await analyzer.initialize_browser()
        
        total = len(replays)
        for i, replay in enumerate(replays, 1):
            print(f"\\n📥 處理 {{i}}/{{total}}: {{replay['share_id']}}")
            
            try:
                # 提取對話數據
                conversation_data = await analyzer.extract_conversation_from_web(replay['url'])
                
                if conversation_data and conversation_data.get('messages'):
                    # 分析對話
                    analysis_result = analyzer.analyze_conversation(conversation_data)
                    
                    # 保存數據
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    # 原始數據
                    raw_file = f"raw_{{replay['share_id']}}_{{timestamp}}.json"
                    with open(raw_file, 'w', encoding='utf-8') as f:
                        json.dump(conversation_data, f, ensure_ascii=False, indent=2)
                    
                    # 分析結果
                    analysis_file = f"analysis_{{replay['share_id']}}_{{timestamp}}.json"
                    with open(analysis_file, 'w', encoding='utf-8') as f:
                        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
                    
                    print(f"  ✅ 完成: {{len(conversation_data.get('messages', []))}} 條消息")
                
                else:
                    print(f"  ❌ 無法提取數據")
                
                # 避免請求過快
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"  ❌ 處理失敗: {{e}}")
                continue
    
    finally:
        await analyzer.close_browser()

if __name__ == "__main__":
    asyncio.run(download_all_replays())
'''
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 使腳本可執行
        import stat
        script_file.chmod(script_file.stat().st_mode | stat.S_IEXEC)
        
        logger.info(f"🔨 批量下載腳本已生成: {script_file}")
        
        return str(script_file)

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DOCX Replay 提取器')
    parser.add_argument('--docx', default='/Users/alexchuang/Downloads/replay.docx', 
                       help='DOCX 文件路徑')
    parser.add_argument('--output', help='輸出目錄')
    parser.add_argument('--generate-script', action='store_true', 
                       help='生成批量下載腳本')
    
    args = parser.parse_args()
    
    # 檢查文件是否存在
    if not Path(args.docx).exists():
        logger.error(f"❌ 文件不存在: {args.docx}")
        return
    
    # 創建提取器
    extractor = DocxReplayExtractor(args.docx)
    
    # 提取 replay
    replays = extractor.extract_replays()
    
    if not replays:
        logger.error("❌ 未找到任何 replay 鏈接")
        return
    
    # 保存結果
    output_file = extractor.save_replay_list(replays, args.output)
    
    # 顯示統計
    print(f"\\n📊 提取統計:")
    print(f"   總 replay 數: {len(replays)}")
    print(f"   唯一 Share ID: {len(set(r['share_id'] for r in replays))}")
    print(f"   輸出文件: {output_file}")
    
    # 生成批量下載腳本
    if args.generate_script:
        script_file = extractor.generate_batch_download_script(replays, args.output)
        print(f"   下載腳本: {script_file}")
    
    # 顯示前幾個示例
    print(f"\\n🔗 前 5 個 replay:")
    for i, replay in enumerate(replays[:5], 1):
        print(f"   {i}. {replay['share_id']}: {replay['url']}")
    
    if len(replays) > 5:
        print(f"   ... 還有 {len(replays) - 5} 個")

if __name__ == "__main__":
    main()