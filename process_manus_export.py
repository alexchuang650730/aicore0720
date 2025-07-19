#!/usr/bin/env python3
"""
處理 Manus 批量導出的對話文件
將導出的 JSON/文本文件轉換為訓練數據
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime


class ManusExportProcessor:
    """處理 Manus 導出文件"""
    
    def __init__(self, export_dir: str = "./manus_export"):
        self.export_dir = Path(export_dir)
        self.output_dir = Path("./data/manus_processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def process_all_exports(self):
        """處理所有導出文件"""
        print("🚀 處理 Manus 導出文件...")
        
        if not self.export_dir.exists():
            print(f"\n請將 Manus 導出的文件放到: {self.export_dir}")
            print("\n步驟：")
            print("1. 在 Manus 中，點擊分享按鈕旁的批量下載")
            print("2. 下載所有對話文件")
            print("3. 解壓到 manus_export 目錄")
            return
            
        # 查找所有導出文件
        export_files = list(self.export_dir.glob("*.json")) + \
                      list(self.export_dir.glob("*.txt")) + \
                      list(self.export_dir.glob("*.md"))
        
        if not export_files:
            print(f"❌ 在 {self.export_dir} 中沒有找到導出文件")
            return
            
        print(f"✅ 找到 {len(export_files)} 個導出文件")
        
        all_conversations = []
        for file_path in export_files:
            print(f"\n處理: {file_path.name}")
            conversation = self._process_export_file(file_path)
            if conversation:
                all_conversations.append(conversation)
                
        # 創建訓練數據
        training_data = self._create_training_dataset(all_conversations)
        
        # 保存結果
        self._save_processed_data(training_data)
        
        print(f"\n✅ 處理完成！")
        print(f"總對話數: {len(all_conversations)}")
        print(f"訓練對數: {training_data['total_pairs']}")
        
    def _process_export_file(self, file_path: Path) -> Dict[str, Any]:
        """處理單個導出文件"""
        try:
            if file_path.suffix == '.json':
                return self._process_json_export(file_path)
            elif file_path.suffix in ['.txt', '.md']:
                return self._process_text_export(file_path)
        except Exception as e:
            print(f"❌ 處理失敗: {e}")
            return None
            
    def _process_json_export(self, file_path: Path) -> Dict[str, Any]:
        """處理 JSON 格式導出"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Manus 導出格式可能包含
        messages = []
        
        # 情況1: 直接的消息數組
        if isinstance(data, list):
            messages = data
        # 情況2: 包含 messages 字段
        elif 'messages' in data:
            messages = data['messages']
        # 情況3: 包含 conversation 字段
        elif 'conversation' in data:
            messages = data['conversation'].get('messages', [])
            
        # 處理消息
        processed_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                processed_messages.append({
                    'role': msg.get('role', 'unknown'),
                    'content': msg.get('content', msg.get('text', ''))
                })
            elif isinstance(msg, str):
                # 純文本格式，需要解析角色
                role = 'user' if len(processed_messages) % 2 == 0 else 'assistant'
                processed_messages.append({
                    'role': role,
                    'content': msg
                })
                
        return {
            'file_name': file_path.name,
            'messages': processed_messages,
            'metadata': data.get('metadata', {})
        }
        
    def _process_text_export(self, file_path: Path) -> Dict[str, Any]:
        """處理文本格式導出"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 解析對話格式
        messages = []
        
        # 模式1: User: / Assistant: 格式
        pattern1 = r'(User|Assistant|用戶|助手):\s*(.*?)(?=(?:User|Assistant|用戶|助手):|$)'
        matches = re.finditer(pattern1, content, re.DOTALL)
        
        for match in matches:
            role = 'user' if match.group(1) in ['User', '用戶'] else 'assistant'
            content_text = match.group(2).strip()
            if content_text:
                messages.append({
                    'role': role,
                    'content': content_text
                })
                
        # 如果沒有找到，嘗試其他格式
        if not messages:
            # 模式2: 按空行分割
            parts = content.split('\n\n')
            for i, part in enumerate(parts):
                if part.strip():
                    role = 'user' if i % 2 == 0 else 'assistant'
                    messages.append({
                        'role': role,
                        'content': part.strip()
                    })
                    
        return {
            'file_name': file_path.name,
            'messages': messages,
            'metadata': {}
        }
        
    def _create_training_dataset(self, conversations: List[Dict]) -> Dict[str, Any]:
        """創建訓練數據集"""
        all_pairs = []
        
        for conv in conversations:
            messages = conv.get('messages', [])
            
            # 創建訓練對
            for i in range(len(messages) - 1):
                if messages[i]['role'] == 'user' and messages[i + 1]['role'] == 'assistant':
                    pair = {
                        'input': messages[i]['content'],
                        'output': messages[i + 1]['content'],
                        'source': conv['file_name'],
                        'type': self._classify_conversation(messages[i]['content']),
                        'has_code': '```' in messages[i + 1]['content'],
                        'quality_score': self._calculate_quality(
                            messages[i]['content'],
                            messages[i + 1]['content']
                        )
                    }
                    all_pairs.append(pair)
                    
        # 過濾高質量對話
        high_quality_pairs = [p for p in all_pairs if p['quality_score'] > 0.6]
        
        return {
            'total_pairs': len(all_pairs),
            'high_quality_pairs': len(high_quality_pairs),
            'training_data': high_quality_pairs,
            'statistics': self._calculate_statistics(high_quality_pairs)
        }
        
    def _classify_conversation(self, user_input: str) -> str:
        """分類對話類型"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['實現', 'implement', '創建', 'create']):
            return 'implementation'
        elif any(word in user_lower for word in ['錯誤', 'error', 'bug', '修復']):
            return 'debugging'
        elif any(word in user_lower for word in ['優化', 'optimize', '改進']):
            return 'optimization'
        elif any(word in user_lower for word in ['解釋', 'explain', '分析']):
            return 'explanation'
        else:
            return 'general'
            
    def _calculate_quality(self, user_input: str, assistant_output: str) -> float:
        """計算質量分數"""
        score = 0.5
        
        # 輸入長度合適
        if 20 < len(user_input) < 500:
            score += 0.1
            
        # 輸出長度合適
        if 100 < len(assistant_output) < 3000:
            score += 0.1
            
        # 包含代碼
        if '```' in assistant_output:
            score += 0.2
            
        # 有結構
        if any(marker in assistant_output for marker in ['1.', '2.', '步驟']):
            score += 0.1
            
        return min(score, 1.0)
        
    def _calculate_statistics(self, pairs: List[Dict]) -> Dict[str, Any]:
        """計算統計信息"""
        stats = {
            'by_type': {},
            'with_code': len([p for p in pairs if p['has_code']]),
            'average_quality': sum(p['quality_score'] for p in pairs) / len(pairs) if pairs else 0
        }
        
        for pair in pairs:
            pair_type = pair['type']
            stats['by_type'][pair_type] = stats['by_type'].get(pair_type, 0) + 1
            
        return stats
        
    def _save_processed_data(self, training_data: Dict):
        """保存處理後的數據"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存完整報告
        report_file = self.output_dir / f"manus_export_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processing_time': datetime.now().isoformat(),
                'total_pairs': training_data['total_pairs'],
                'high_quality_pairs': training_data['high_quality_pairs'],
                'statistics': training_data['statistics']
            }, f, ensure_ascii=False, indent=2)
            
        # 保存訓練數據（JSONL 格式）
        training_file = self.output_dir / f"training_pairs_{timestamp}.jsonl"
        with open(training_file, 'w', encoding='utf-8') as f:
            for pair in training_data['training_data']:
                f.write(json.dumps({
                    'instruction': pair['input'],
                    'response': pair['output'],
                    'metadata': {
                        'type': pair['type'],
                        'has_code': pair['has_code'],
                        'quality': pair['quality_score']
                    }
                }, ensure_ascii=False) + '\n')
                
        # 保存 K2 優化格式
        k2_file = self.output_dir / f"k2_optimized_{timestamp}.jsonl"
        with open(k2_file, 'w', encoding='utf-8') as f:
            for pair in training_data['training_data']:
                k2_prompt = f"""<context>
任務類型: {pair['type']}
來源: Manus 對話
項目: PowerAutomation
</context>

<task>
{pair['input']}
</task>"""
                
                f.write(json.dumps({
                    'prompt': k2_prompt,
                    'completion': pair['output']
                }, ensure_ascii=False) + '\n')
                
        print(f"\n💾 數據已保存:")
        print(f"  報告: {report_file}")
        print(f"  訓練數據: {training_file}")
        print(f"  K2 格式: {k2_file}")


def main():
    """主函數"""
    print("""
🚀 Manus 批量導出處理器

使用步驟：
1. 在 Manus 中點擊分享按鈕旁的「批量下載」
2. 下載所有對話文件（通常是 ZIP 壓縮包）
3. 解壓到 ./manus_export 目錄
4. 運行此腳本

支持的格式：
- JSON 文件
- TXT 文件
- Markdown 文件
""")
    
    export_dir = input("\n導出文件目錄 [默認: ./manus_export]: ").strip() or "./manus_export"
    
    processor = ManusExportProcessor(export_dir)
    processor.process_all_exports()


if __name__ == "__main__":
    main()