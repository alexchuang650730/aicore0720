#!/usr/bin/env python3
"""
Replay DOCX 內容提取器
從 /Users/alexchuang/Downloads/replay.docx 提取 414 個 Manus replay 鏈接
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReplayDocxExtractor:
    """Replay DOCX 提取器"""
    
    def __init__(self, docx_path: str = "/Users/alexchuang/Downloads/replay.docx"):
        self.docx_path = Path(docx_path)
        self.data_dir = Path(__file__).parent / "data/replay_links"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_docx(self) -> str:
        """從 DOCX 文件提取純文本"""
        try:
            logger.info(f"🔓 開始提取 DOCX 內容: {self.docx_path}")
            
            with zipfile.ZipFile(self.docx_path, 'r') as docx_zip:
                # 讀取主文檔
                document_xml = docx_zip.read('word/document.xml')
                
                # 解析 XML
                root = ET.fromstring(document_xml)
                
                # 提取所有文本節點
                text_parts = []
                
                # 遞歸提取文本
                def extract_text_recursive(element):
                    if element.text:
                        text_parts.append(element.text)
                    
                    for child in element:
                        extract_text_recursive(child)
                        if child.tail:
                            text_parts.append(child.tail)
                
                extract_text_recursive(root)
                
                full_text = ' '.join(text_parts)
                logger.info(f"✅ 成功提取文本，長度: {len(full_text)} 字符")
                
                return full_text
                
        except Exception as e:
            logger.error(f"❌ 提取 DOCX 失敗: {e}")
            return ""
    
    def find_replay_links(self, text: str) -> List[Dict]:
        """從文本中查找 Manus replay 鏈接"""
        logger.info("🔍 開始查找 Manus replay 鏈接...")
        
        found_links = []
        seen_share_ids = set()
        
        # 正則表達式模式
        patterns = [
            # 完整 URL
            r'https://manus\.im/share/([a-zA-Z0-9_-]+)\?replay=1',
            r'manus\.im/share/([a-zA-Z0-9_-]+)\?replay=1',
            
            # Share ID 模式
            r'share/([a-zA-Z0-9_-]{15,})',
            
            # 可能的 Share ID（獨立出現）
            r'\b([a-zA-Z0-9_-]{20,})\b',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for match in matches:
                share_id = match
                
                # 過濾明顯不是 Share ID 的內容
                if self._is_valid_share_id(share_id):
                    if share_id not in seen_share_ids:
                        seen_share_ids.add(share_id)
                        
                        replay_info = {
                            'share_id': share_id,
                            'url': f"https://manus.im/share/{share_id}?replay=1",
                            'extraction_time': datetime.now().isoformat(),
                            'status': 'pending'
                        }
                        
                        found_links.append(replay_info)
        
        logger.info(f"✅ 找到 {len(found_links)} 個不重複的 replay 鏈接")
        
        return found_links
    
    def _is_valid_share_id(self, share_id: str) -> bool:
        """驗證 Share ID 是否有效"""
        # 基本長度檢查
        if len(share_id) < 15 or len(share_id) > 50:
            return False
        
        # 不能全是數字
        if share_id.isdigit():
            return False
        
        # 不能包含空格
        if ' ' in share_id:
            return False
        
        # 必須包含字母和數字的組合
        has_letter = any(c.isalpha() for c in share_id)
        has_number = any(c.isdigit() for c in share_id)
        
        if not (has_letter and has_number):
            return False
        
        # 過濾一些明顯的非 Share ID 模式
        invalid_patterns = [
            'document', 'content', 'extract', 'analysis', 'replay',
            'manus', 'share', 'http', 'www', 'com', 'org'
        ]
        
        share_id_lower = share_id.lower()
        for invalid in invalid_patterns:
            if invalid in share_id_lower:
                return False
        
        return True
    
    def save_replay_data(self, replay_links: List[Dict]) -> Dict[str, str]:
        """保存 replay 數據"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 準備數據
        data_to_save = {
            'extraction_metadata': {
                'source_file': str(self.docx_path),
                'extraction_time': datetime.now().isoformat(),
                'total_replays': len(replay_links),
                'extractor_version': '1.0'
            },
            'replay_links': replay_links
        }
        
        # 保存為 JSON
        json_file = self.data_dir / f"replay_links_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        # 保存為純鏈接列表
        txt_file = self.data_dir / f"replay_urls_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            for replay in replay_links:
                f.write(replay['url'] + '\\n')
        
        # 保存統計信息
        stats_file = self.data_dir / f"extraction_stats_{timestamp}.md"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(f"""# Replay 提取統計報告

## 基本信息
- **提取時間**: {datetime.now().isoformat()}
- **源文件**: {self.docx_path}
- **提取的 replay 數量**: {len(replay_links)}

## 數據評估
- **預期數據量**: {len(replay_links)} 個 replay × 平均 2-3 小時 = {len(replay_links) * 2.5:.0f} 小時對話
- **估算訓練數據**: {len(replay_links) * 500:,} 條消息
- **估算 token 數**: {len(replay_links) * 25000:,} tokens

## 建議訓練策略
基於 {len(replay_links)} 個 replay 的數據量：

1. **如果 < 100 個**: 適合 K2 LoRA 微調
2. **如果 100-300 個**: 適合 K2 完整微調
3. **如果 > 300 個**: 可考慮 DeepSWE 部分微調

## 下一步行動
1. 使用 manus_complete_analyzer.py 批量下載這些 replay
2. 分析和分類對話內容
3. 生成訓練數據集
4. 執行模型訓練

## 文件輸出
- **JSON 數據**: `{json_file.name}`
- **URL 列表**: `{txt_file.name}`
- **統計報告**: `{stats_file.name}`
""")
        
        logger.info(f"💾 數據已保存:")
        logger.info(f"   JSON: {json_file}")
        logger.info(f"   URLs: {txt_file}")
        logger.info(f"   統計: {stats_file}")
        
        return {
            'json_file': str(json_file),
            'txt_file': str(txt_file),
            'stats_file': str(stats_file)
        }
    
    def generate_batch_download_script(self, replay_links: List[Dict]) -> str:
        """生成批量下載腳本"""
        script_content = f'''#!/usr/bin/env python3
"""
批量下載 Manus Replay 腳本
自動下載 {len(replay_links)} 個 replay 並分析內容
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.components.memoryrag_mcp.manus_complete_analyzer import ManusCompleteAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    print("❌ 無法導入 ManusCompleteAnalyzer")
    ANALYZER_AVAILABLE = False

async def download_replays():
    """批量下載 replay"""
    if not ANALYZER_AVAILABLE:
        print("請確保 ManusCompleteAnalyzer 可用")
        return
    
    # Replay 列表
    replays = {json.dumps(replay_links, indent=4)}
    
    # 創建輸出目錄
    output_dir = Path("data/downloaded_replays")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    analyzer = ManusCompleteAnalyzer()
    
    try:
        await analyzer.initialize_browser()
        
        success_count = 0
        total_messages = 0
        
        for i, replay in enumerate(replays, 1):
            print(f"\\n📥 處理 {{i}}/{len(replays)}: {{replay['share_id']}}")
            
            try:
                # 提取對話數據
                conversation_data = await analyzer.extract_conversation_from_web(replay['url'])
                
                if conversation_data and conversation_data.get('messages'):
                    # 分析對話
                    analysis_result = analyzer.analyze_conversation(conversation_data)
                    
                    # 保存原始數據
                    raw_file = output_dir / f"raw_{{replay['share_id']}}.json"
                    with open(raw_file, 'w', encoding='utf-8') as f:
                        json.dump(conversation_data, f, ensure_ascii=False, indent=2)
                    
                    # 保存分析結果
                    analysis_file = output_dir / f"analysis_{{replay['share_id']}}.json"
                    with open(analysis_file, 'w', encoding='utf-8') as f:
                        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
                    
                    message_count = len(conversation_data.get('messages', []))
                    total_messages += message_count
                    success_count += 1
                    
                    print(f"  ✅ 成功: {{message_count}} 條消息")
                
                else:
                    print(f"  ❌ 無法提取數據")
                
                # 避免請求過快
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"  ❌ 處理失敗: {{e}}")
                continue
        
        print(f"\\n📊 下載完成:")
        print(f"   成功: {{success_count}}/{len(replays)}")
        print(f"   總消息數: {{total_messages:,}}")
        print(f"   估算 tokens: {{total_messages * 50:,}}")
    
    finally:
        await analyzer.close_browser()

if __name__ == "__main__":
    asyncio.run(download_replays())
'''
        
        script_file = self.data_dir / "batch_download_replays.py"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 設置可執行權限
        script_file.chmod(0o755)
        
        logger.info(f"🔨 批量下載腳本已生成: {script_file}")
        
        return str(script_file)
    
    def extract_all(self) -> Dict:
        """執行完整提取流程"""
        logger.info("🚀 開始完整的 replay 提取流程...")
        
        # 檢查文件是否存在
        if not self.docx_path.exists():
            logger.error(f"❌ 文件不存在: {self.docx_path}")
            return {}
        
        # 提取文本
        text_content = self.extract_text_from_docx()
        if not text_content:
            logger.error("❌ 無法提取文本內容")
            return {}
        
        # 查找 replay 鏈接
        replay_links = self.find_replay_links(text_content)
        if not replay_links:
            logger.error("❌ 未找到任何 replay 鏈接")
            return {}
        
        # 保存數據
        saved_files = self.save_replay_data(replay_links)
        
        # 生成下載腳本
        script_file = self.generate_batch_download_script(replay_links)
        saved_files['script_file'] = script_file
        
        # 顯示結果
        print(f"\\n🎉 提取完成!")
        print(f"   找到 replay: {len(replay_links)} 個")
        print(f"   數據文件: {saved_files['json_file']}")
        print(f"   下載腳本: {saved_files['script_file']}")
        
        # 顯示前幾個示例
        print(f"\\n🔗 前 5 個 replay:")
        for i, replay in enumerate(replay_links[:5], 1):
            print(f"   {i}. {replay['share_id']}")
        
        if len(replay_links) > 5:
            print(f"   ... 還有 {len(replay_links) - 5} 個")
        
        return {
            'replay_count': len(replay_links),
            'replay_links': replay_links,
            'saved_files': saved_files
        }

def main():
    """主函數"""
    extractor = ReplayDocxExtractor()
    result = extractor.extract_all()
    
    if result:
        print(f"\\n💡 下一步建議:")
        print(f"   1. 執行下載腳本: python {result['saved_files']['script_file']}")
        print(f"   2. 等待下載完成（預計 {result['replay_count'] * 0.5:.0f} 分鐘）")
        print(f"   3. 檢查 data/downloaded_replays/ 目錄中的數據")
        print(f"   4. 運行 K2 訓練器處理這些數據")

if __name__ == "__main__":
    main()