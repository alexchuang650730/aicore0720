#!/usr/bin/env python3
"""
MemoryRAG 數據提取器
直接從 MemoryRAG 系統提取對話數據用於訓練
"""

import json
import sqlite3
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import re


class MemoryRAGDataExtractor:
    """從 MemoryRAG 提取訓練數據"""
    
    def __init__(self, memoryrag_db_path: str = "./core/memoryrag/memory.db"):
        self.db_path = Path(memoryrag_db_path)
        self.output_dir = Path("./data/memoryrag_training")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_all_conversations(self) -> Dict[str, Any]:
        """提取所有對話數據"""
        print("📥 從 MemoryRAG 提取對話數據...")
        
        if not self.db_path.exists():
            print(f"❌ 找不到 MemoryRAG 數據庫: {self.db_path}")
            return {}
            
        # 連接數據庫
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 查詢所有對話記錄
            cursor.execute("""
                SELECT conversation_id, user_input, assistant_response, 
                       timestamp, context, metadata
                FROM conversations
                ORDER BY timestamp DESC
            """)
            
            conversations = []
            for row in cursor.fetchall():
                conv = {
                    'conversation_id': row[0],
                    'user_input': row[1],
                    'assistant_response': row[2],
                    'timestamp': row[3],
                    'context': json.loads(row[4]) if row[4] else {},
                    'metadata': json.loads(row[5]) if row[5] else {}
                }
                conversations.append(conv)
                
            print(f"✅ 提取了 {len(conversations)} 條對話記錄")
            
            # 處理數據
            processed_data = self._process_conversations(conversations)
            
            # 保存結果
            self._save_training_data(processed_data)
            
            return processed_data
            
        except Exception as e:
            print(f"❌ 提取失敗: {e}")
            return {}
        finally:
            conn.close()
            
    def extract_recent_conversations(self, days: int = 7) -> Dict[str, Any]:
        """提取最近幾天的對話"""
        print(f"📥 提取最近 {days} 天的對話...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 查詢最近的對話
            cursor.execute("""
                SELECT conversation_id, user_input, assistant_response, 
                       timestamp, context, metadata
                FROM conversations
                WHERE timestamp > datetime('now', '-{} days')
                ORDER BY timestamp DESC
            """.format(days))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'conversation_id': row[0],
                    'user_input': row[1],
                    'assistant_response': row[2],
                    'timestamp': row[3],
                    'context': json.loads(row[4]) if row[4] else {},
                    'metadata': json.loads(row[5]) if row[5] else {}
                })
                
            return self._process_conversations(conversations)
            
        finally:
            conn.close()
            
    def extract_by_pattern(self, pattern: str) -> Dict[str, Any]:
        """根據模式提取特定對話"""
        print(f"📥 提取包含 '{pattern}' 的對話...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 查詢匹配模式的對話
            cursor.execute("""
                SELECT conversation_id, user_input, assistant_response, 
                       timestamp, context, metadata
                FROM conversations
                WHERE user_input LIKE ? OR assistant_response LIKE ?
                ORDER BY timestamp DESC
            """, (f'%{pattern}%', f'%{pattern}%'))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'conversation_id': row[0],
                    'user_input': row[1],
                    'assistant_response': row[2],
                    'timestamp': row[3],
                    'context': json.loads(row[4]) if row[4] else {},
                    'metadata': json.loads(row[5]) if row[5] else {}
                })
                
            return self._process_conversations(conversations)
            
        finally:
            conn.close()
            
    def _process_conversations(self, conversations: List[Dict]) -> Dict[str, Any]:
        """處理對話數據"""
        print("🔄 處理對話數據...")
        
        training_pairs = []
        code_examples = []
        optimization_patterns = []
        
        for conv in conversations:
            # 檢查是否為編程相關
            if self._is_programming_related(conv):
                # 提取訓練對
                pair = self._create_training_pair(conv)
                training_pairs.append(pair)
                
                # 提取代碼示例
                if '```' in conv['assistant_response']:
                    code_examples.extend(self._extract_code_blocks(conv))
                    
                # 提取優化模式
                if 'optimization' in conv.get('metadata', {}).get('type', ''):
                    optimization_patterns.append(self._extract_optimization_pattern(conv))
                    
        # 統計分析
        stats = self._analyze_statistics(training_pairs)
        
        return {
            'total_conversations': len(conversations),
            'training_pairs': training_pairs,
            'code_examples': code_examples,
            'optimization_patterns': optimization_patterns,
            'statistics': stats,
            'extracted_at': datetime.now().isoformat()
        }
        
    def _is_programming_related(self, conv: Dict) -> bool:
        """判斷是否為編程相關對話"""
        keywords = [
            'code', '代碼', 'function', '函數', 'class', '類',
            'error', '錯誤', 'bug', 'implement', '實現',
            'mcp', 'api', 'claude', 'python', 'javascript'
        ]
        
        text = (conv['user_input'] + ' ' + conv['assistant_response']).lower()
        return any(keyword in text for keyword in keywords)
        
    def _create_training_pair(self, conv: Dict) -> Dict[str, Any]:
        """創建訓練對"""
        return {
            'id': conv['conversation_id'],
            'input': conv['user_input'],
            'output': conv['assistant_response'],
            'timestamp': conv['timestamp'],
            'type': self._classify_conversation_type(conv),
            'quality_score': self._calculate_quality_score(conv),
            'k2_optimized': self._create_k2_optimized_version(conv),
            'deepswe_format': self._create_deepswe_format(conv)
        }
        
    def _classify_conversation_type(self, conv: Dict) -> str:
        """分類對話類型"""
        user_input = conv['user_input'].lower()
        
        if any(word in user_input for word in ['實現', 'implement', '創建', 'create']):
            return 'implementation'
        elif any(word in user_input for word in ['錯誤', 'error', 'bug', '修復']):
            return 'debugging'
        elif any(word in user_input for word in ['優化', 'optimize', '改進']):
            return 'optimization'
        elif any(word in user_input for word in ['解釋', 'explain', '分析']):
            return 'explanation'
        else:
            return 'general'
            
    def _calculate_quality_score(self, conv: Dict) -> float:
        """計算質量分數"""
        score = 0.5
        
        # 回答長度
        response_length = len(conv['assistant_response'])
        if 200 < response_length < 2000:
            score += 0.2
            
        # 包含代碼
        if '```' in conv['assistant_response']:
            score += 0.2
            
        # 有結構化內容
        if any(marker in conv['assistant_response'] for marker in ['1.', '2.', '步驟']):
            score += 0.1
            
        return min(score, 1.0)
        
    def _create_k2_optimized_version(self, conv: Dict) -> str:
        """創建 K2 優化版本"""
        context = conv.get('context', {})
        
        return f"""<context>
項目：PowerAutomation
技術棧：{context.get('tech_stack', 'Python, TypeScript, React')}
任務類型：{self._classify_conversation_type(conv)}
</context>

<user_request>
{conv['user_input']}
</user_request>

請提供詳細的解決方案。"""
        
    def _create_deepswe_format(self, conv: Dict) -> Dict[str, str]:
        """創建 DeepSWE 格式"""
        # 提取思考過程
        thinking = self._extract_thinking_from_response(conv['assistant_response'])
        
        return {
            'prompt': conv['user_input'],
            'thinking': thinking,
            'response': conv['assistant_response']
        }
        
    def _extract_thinking_from_response(self, response: str) -> str:
        """從回答中提取思考過程"""
        patterns = [
            r'(讓我.*?[。\n])',
            r'(首先.*?[。\n])',
            r'(這個.*?需要.*?[。\n])'
        ]
        
        thinking_parts = []
        for pattern in patterns:
            matches = re.findall(pattern, response)
            thinking_parts.extend(matches)
            
        return ' '.join(thinking_parts) if thinking_parts else "分析問題並生成解決方案。"
        
    def _extract_code_blocks(self, conv: Dict) -> List[Dict[str, str]]:
        """提取代碼塊"""
        code_blocks = []
        pattern = r'```(\w*)\n(.*?)\n```'
        
        matches = re.finditer(pattern, conv['assistant_response'], re.DOTALL)
        for match in matches:
            language = match.group(1) or 'text'
            code = match.group(2)
            
            code_blocks.append({
                'language': language,
                'code': code,
                'context': conv['user_input'][:100] + '...',
                'conversation_id': conv['conversation_id']
            })
            
        return code_blocks
        
    def _extract_optimization_pattern(self, conv: Dict) -> Dict[str, Any]:
        """提取優化模式"""
        return {
            'original_request': conv['user_input'],
            'optimization_approach': conv['assistant_response'][:500],
            'key_improvements': self._identify_improvements(conv['assistant_response']),
            'metrics': conv.get('metadata', {}).get('metrics', {})
        }
        
    def _identify_improvements(self, response: str) -> List[str]:
        """識別改進點"""
        improvements = []
        
        improvement_patterns = [
            r'改進了(.*?)[。\n]',
            r'優化了(.*?)[。\n]',
            r'提升了(.*?)[。\n]',
            r'reduced(.*?)[.\n]',
            r'improved(.*?)[.\n]'
        ]
        
        for pattern in improvement_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            improvements.extend(matches)
            
        return improvements
        
    def _analyze_statistics(self, training_pairs: List[Dict]) -> Dict[str, Any]:
        """統計分析"""
        if not training_pairs:
            return {}
            
        stats = {
            'total_pairs': len(training_pairs),
            'by_type': {},
            'average_quality': sum(p['quality_score'] for p in training_pairs) / len(training_pairs),
            'with_code': len([p for p in training_pairs if '```' in p['output']])
        }
        
        # 按類型統計
        for pair in training_pairs:
            pair_type = pair['type']
            stats['by_type'][pair_type] = stats['by_type'].get(pair_type, 0) + 1
            
        return stats
        
    def _save_training_data(self, data: Dict[str, Any]):
        """保存訓練數據"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存完整數據
        full_data_file = self.output_dir / f"memoryrag_training_data_{timestamp}.json"
        with open(full_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # 保存訓練對（JSONL 格式）
        if data.get('training_pairs'):
            training_file = self.output_dir / f"training_pairs_{timestamp}.jsonl"
            with open(training_file, 'w', encoding='utf-8') as f:
                for pair in data['training_pairs']:
                    f.write(json.dumps({
                        'input': pair['input'],
                        'output': pair['output'],
                        'metadata': {
                            'type': pair['type'],
                            'quality': pair['quality_score']
                        }
                    }, ensure_ascii=False) + '\n')
                    
        # 保存 K2 優化數據
        if data.get('training_pairs'):
            k2_file = self.output_dir / f"k2_optimized_{timestamp}.jsonl"
            with open(k2_file, 'w', encoding='utf-8') as f:
                for pair in data['training_pairs']:
                    f.write(json.dumps({
                        'prompt': pair['k2_optimized'],
                        'completion': pair['output']
                    }, ensure_ascii=False) + '\n')
                    
        print(f"\n✅ 數據已保存:")
        print(f"   - 完整數據: {full_data_file}")
        print(f"   - 訓練對: {training_file if data.get('training_pairs') else 'None'}")
        print(f"   - K2 優化: {k2_file if data.get('training_pairs') else 'None'}")
        print(f"   - 總訓練對: {data.get('statistics', {}).get('total_pairs', 0)}")


def main():
    """主函數"""
    extractor = MemoryRAGDataExtractor()
    
    # 提取所有數據
    print("🚀 開始提取 MemoryRAG 數據...")
    data = extractor.extract_all_conversations()
    
    if data:
        print(f"\n📊 提取結果:")
        print(f"   - 總對話數: {data.get('total_conversations', 0)}")
        print(f"   - 訓練對: {len(data.get('training_pairs', []))}")
        print(f"   - 代碼示例: {len(data.get('code_examples', []))}")
        print(f"   - 優化模式: {len(data.get('optimization_patterns', []))}")
        
        stats = data.get('statistics', {})
        if stats:
            print(f"\n📈 統計信息:")
            print(f"   - 平均質量分數: {stats.get('average_quality', 0):.2f}")
            print(f"   - 包含代碼: {stats.get('with_code', 0)}")
            print(f"   - 類型分布: {stats.get('by_type', {})}")
    else:
        print("❌ 未能提取到數據")
        
    # 也可以提取特定模式的數據
    print("\n🔍 提取 MCP 相關對話...")
    mcp_data = extractor.extract_by_pattern('mcp')
    if mcp_data:
        print(f"   - 找到 {len(mcp_data.get('training_pairs', []))} 個 MCP 相關對話")


if __name__ == "__main__":
    main()