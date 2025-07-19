#!/usr/bin/env python3
"""
Claude 對話數據收集器
收集和處理 PowerAutomation 開發過程中的 Claude 對話
"""

import json
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import hashlib


class ClaudeConversationCollector:
    """Claude 對話數據收集和處理器"""
    
    def __init__(self, output_dir: str = "./data/claude_conversations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_conversations = []
        
    def process_current_conversation(self, conversation_text: str) -> Dict[str, Any]:
        """處理當前對話文本"""
        # 解析對話
        messages = self._parse_conversation(conversation_text)
        
        # 提取有價值的編程相關對話
        programming_pairs = self._extract_programming_pairs(messages)
        
        # 分析對話模式
        patterns = self._analyze_conversation_patterns(messages)
        
        # 創建訓練數據
        training_data = self._create_training_data(programming_pairs)
        
        # 保存處理結果
        result = {
            'conversation_id': self._generate_conversation_id(),
            'timestamp': datetime.now().isoformat(),
            'total_messages': len(messages),
            'programming_pairs': len(programming_pairs),
            'patterns': patterns,
            'training_data': training_data,
            'quality_metrics': self._calculate_quality_metrics(programming_pairs)
        }
        
        # 保存數據
        self._save_conversation_data(result)
        
        return result
        
    def _parse_conversation(self, text: str) -> List[Dict[str, str]]:
        """解析對話文本"""
        messages = []
        
        # 假設對話格式為標準的用戶/助手交替
        # 可以根據實際格式調整
        lines = text.split('\n')
        current_role = None
        current_content = []
        
        for line in lines:
            if line.startswith('Human:') or line.startswith('用戶:'):
                if current_content:
                    messages.append({
                        'role': current_role,
                        'content': '\n'.join(current_content).strip()
                    })
                current_role = 'user'
                current_content = [line.replace('Human:', '').replace('用戶:', '').strip()]
            elif line.startswith('Assistant:') or line.startswith('助手:'):
                if current_content:
                    messages.append({
                        'role': current_role,
                        'content': '\n'.join(current_content).strip()
                    })
                current_role = 'assistant'
                current_content = [line.replace('Assistant:', '').replace('助手:', '').strip()]
            else:
                current_content.append(line)
                
        # 添加最後一條消息
        if current_content:
            messages.append({
                'role': current_role,
                'content': '\n'.join(current_content).strip()
            })
            
        return messages
        
    def _extract_programming_pairs(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """提取編程相關的對話對"""
        pairs = []
        
        for i in range(len(messages) - 1):
            if messages[i]['role'] == 'user' and messages[i + 1]['role'] == 'assistant':
                user_msg = messages[i]['content']
                assistant_msg = messages[i + 1]['content']
                
                # 檢查是否為編程相關
                if self._is_programming_related(user_msg, assistant_msg):
                    pair = {
                        'input': user_msg,
                        'output': assistant_msg,
                        'type': self._classify_programming_task(user_msg, assistant_msg),
                        'has_code': '```' in assistant_msg,
                        'technologies': self._extract_technologies(user_msg + ' ' + assistant_msg),
                        'complexity': self._assess_complexity(assistant_msg)
                    }
                    pairs.append(pair)
                    
        return pairs
        
    def _is_programming_related(self, user_msg: str, assistant_msg: str) -> bool:
        """判斷是否為編程相關對話"""
        programming_keywords = [
            # 中文
            '代碼', '實現', '函數', '類', '方法', '錯誤', '調試', '優化',
            '部署', '測試', '數據', '架構', '設計', '文件', '目錄',
            # 英文
            'code', 'implement', 'function', 'class', 'method', 'error', 
            'debug', 'optimize', 'deploy', 'test', 'data', 'architecture',
            # 技術相關
            'python', 'javascript', 'typescript', 'react', 'vue', 'node',
            'api', 'database', 'mcp', 'claude', 'ai', 'llm'
        ]
        
        combined_text = (user_msg + ' ' + assistant_msg).lower()
        
        # 檢查關鍵詞
        has_keywords = any(keyword in combined_text for keyword in programming_keywords)
        
        # 檢查代碼塊
        has_code = '```' in assistant_msg
        
        # 檢查文件路徑
        has_file_path = bool(re.search(r'[./\\][\w/\\.-]+\.\w+', combined_text))
        
        return has_keywords or has_code or has_file_path
        
    def _classify_programming_task(self, user_msg: str, assistant_msg: str) -> str:
        """分類編程任務類型"""
        user_lower = user_msg.lower()
        
        task_patterns = {
            'implementation': ['實現', '創建', '生成', 'implement', 'create', 'generate'],
            'debugging': ['錯誤', '修復', 'bug', 'error', 'fix', 'debug'],
            'optimization': ['優化', '改進', '性能', 'optimize', 'improve', 'performance'],
            'architecture': ['架構', '設計', '結構', 'architecture', 'design', 'structure'],
            'integration': ['集成', '整合', '連接', 'integrate', 'connect', 'combine'],
            'testing': ['測試', '驗證', 'test', 'verify', 'validate'],
            'deployment': ['部署', '上線', '發布', 'deploy', 'release', 'publish'],
            'documentation': ['文檔', '說明', '註釋', 'document', 'explain', 'comment']
        }
        
        for task_type, keywords in task_patterns.items():
            if any(keyword in user_lower for keyword in keywords):
                return task_type
                
        return 'general'
        
    def _extract_technologies(self, text: str) -> List[str]:
        """提取涉及的技術棧"""
        technologies = []
        
        tech_patterns = {
            'python': r'\bpython\b',
            'javascript': r'\b(javascript|js)\b',
            'typescript': r'\b(typescript|ts)\b',
            'react': r'\breact\b',
            'vue': r'\bvue\b',
            'node': r'\bnode(js)?\b',
            'mcp': r'\bmcp\b',
            'claude': r'\bclaude\b',
            'docker': r'\bdocker\b',
            'kubernetes': r'\b(kubernetes|k8s)\b',
            'aws': r'\b(aws|amazon)\b',
            'git': r'\bgit\b'
        }
        
        text_lower = text.lower()
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, text_lower):
                technologies.append(tech)
                
        return technologies
        
    def _assess_complexity(self, assistant_msg: str) -> str:
        """評估回答的複雜度"""
        # 基於多個因素評估
        lines = assistant_msg.split('\n')
        code_blocks = assistant_msg.count('```')
        
        # 計算特徵
        line_count = len(lines)
        has_multiple_steps = bool(re.search(r'(\d+\.|\d+\))', assistant_msg))
        has_code = code_blocks > 0
        code_lines = sum(1 for line in lines if line.strip().startswith(('def ', 'class ', 'function ', 'const ')))
        
        # 評分
        score = 0
        if line_count > 50:
            score += 3
        elif line_count > 20:
            score += 2
        else:
            score += 1
            
        if code_blocks >= 3:
            score += 3
        elif code_blocks >= 1:
            score += 2
            
        if has_multiple_steps:
            score += 1
            
        if code_lines > 10:
            score += 2
        elif code_lines > 5:
            score += 1
            
        # 分類
        if score >= 7:
            return 'high'
        elif score >= 4:
            return 'medium'
        else:
            return 'low'
            
    def _analyze_conversation_patterns(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """分析對話模式"""
        patterns = {
            'total_turns': len(messages) // 2,
            'user_message_lengths': [],
            'assistant_message_lengths': [],
            'task_progression': [],
            'topics': []
        }
        
        for msg in messages:
            if msg['role'] == 'user':
                patterns['user_message_lengths'].append(len(msg['content']))
            else:
                patterns['assistant_message_lengths'].append(len(msg['content']))
                
        # 識別任務進展
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages):
                user_msg = messages[i]['content']
                task_type = self._classify_programming_task(user_msg, '')
                patterns['task_progression'].append(task_type)
                
        return patterns
        
    def _create_training_data(self, pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """創建訓練數據"""
        training_data = []
        
        for pair in pairs:
            # 基礎訓練格式
            base_format = {
                'instruction': pair['input'],
                'response': pair['output'],
                'metadata': {
                    'type': pair['type'],
                    'has_code': pair['has_code'],
                    'technologies': pair['technologies'],
                    'complexity': pair['complexity']
                }
            }
            
            # K2 優化格式
            k2_format = {
                'original_prompt': pair['input'],
                'optimized_prompt': self._create_k2_optimized_prompt(pair),
                'expected_output': pair['output']
            }
            
            # DeepSWE 格式
            deepswe_format = {
                'prompt': self._create_deepswe_prompt(pair),
                'completion': pair['output'],
                'thinking': self._extract_thinking_process(pair['output'])
            }
            
            training_data.append({
                'base': base_format,
                'k2_optimized': k2_format,
                'deepswe': deepswe_format
            })
            
        return training_data
        
    def _create_k2_optimized_prompt(self, pair: Dict[str, Any]) -> str:
        """創建 K2 優化的提示"""
        task_type = pair['type']
        original_prompt = pair['input']
        
        # 根據任務類型優化
        optimizations = {
            'implementation': f"""
<task_context>
任務類型：代碼實現
技術棧：{', '.join(pair['technologies'])}
複雜度：{pair['complexity']}
</task_context>

<requirements>
{original_prompt}
</requirements>

請提供完整的實現，包括：
1. 核心功能代碼
2. 錯誤處理
3. 必要的註釋
4. 使用示例
""",
            'debugging': f"""
<error_context>
需要修復的問題：
{original_prompt}
</error_context>

請分析問題原因並提供修復方案，包括：
1. 問題診斷
2. 修復代碼
3. 測試驗證
4. 預防建議
""",
            'optimization': f"""
<optimization_request>
{original_prompt}
</optimization_request>

請提供優化方案，考慮：
1. 性能改進
2. 代碼質量
3. 可維護性
4. 最佳實踐
"""
        }
        
        return optimizations.get(task_type, f"<request>{original_prompt}</request>")
        
    def _create_deepswe_prompt(self, pair: Dict[str, Any]) -> str:
        """創建 DeepSWE 格式的提示"""
        return f"""<thinking>
任務分析：{pair['type']}
涉及技術：{', '.join(pair['technologies'])}
複雜度評估：{pair['complexity']}
</thinking>

用戶需求：
{pair['input']}

請提供解決方案。"""
        
    def _extract_thinking_process(self, output: str) -> str:
        """提取思考過程"""
        thinking_patterns = [
            r'(讓我.*?[。\n])',
            r'(首先.*?[。\n])',
            r'(我將.*?[。\n])',
            r'(這個.*?需要.*?[。\n])',
            r'(分析.*?[。\n])'
        ]
        
        thinking_parts = []
        for pattern in thinking_patterns:
            matches = re.findall(pattern, output)
            thinking_parts.extend(matches)
            
        return ' '.join(thinking_parts) if thinking_parts else "分析問題並設計解決方案。"
        
    def _calculate_quality_metrics(self, pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """計算質量指標"""
        if not pairs:
            return {'total': 0}
            
        metrics = {
            'total': len(pairs),
            'with_code': len([p for p in pairs if p['has_code']]),
            'by_type': {},
            'by_complexity': {},
            'average_technologies': sum(len(p['technologies']) for p in pairs) / len(pairs)
        }
        
        # 按類型統計
        for pair in pairs:
            task_type = pair['type']
            metrics['by_type'][task_type] = metrics['by_type'].get(task_type, 0) + 1
            
            complexity = pair['complexity']
            metrics['by_complexity'][complexity] = metrics['by_complexity'].get(complexity, 0) + 1
            
        return metrics
        
    def _generate_conversation_id(self) -> str:
        """生成對話 ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
        
    def _save_conversation_data(self, data: Dict[str, Any]):
        """保存對話數據"""
        # 保存原始數據
        conversation_id = data['conversation_id']
        output_file = self.output_dir / f"conversation_{conversation_id}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # 保存訓練數據
        if data['training_data']:
            training_file = self.output_dir / f"training_{conversation_id}.jsonl"
            with open(training_file, 'w', encoding='utf-8') as f:
                for item in data['training_data']:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    
        print(f"✅ 對話數據已保存:")
        print(f"   - 原始數據: {output_file}")
        print(f"   - 訓練數據: {training_file}")
        print(f"   - 編程對話對: {data['programming_pairs']}")
        print(f"   - 質量指標: {data['quality_metrics']}")
        
    def export_current_session_guide(self):
        """導出當前會話的提取指南"""
        guide = """# Claude 對話數據提取指南

## 如何導出當前對話

### 方法一：從 Claude 界面導出

1. 在 Claude 界面右上角找到「...」菜單
2. 選擇「導出對話」或「Export conversation」
3. 保存為文本或 JSON 格式

### 方法二：手動複製

1. 選擇整個對話內容
2. 複製到文本文件
3. 保存為 `conversation.txt`

### 方法三：使用瀏覽器開發者工具

在 Console 中運行：

```javascript
// 提取所有消息
const messages = [];
document.querySelectorAll('.message-content').forEach((el, i) => {
    const role = i % 2 === 0 ? 'user' : 'assistant';
    messages.push({
        role: role,
        content: el.innerText
    });
});

// 下載為文件
const dataStr = JSON.stringify(messages, null, 2);
const dataBlob = new Blob([dataStr], {type: 'application/json'});
const link = document.createElement('a');
link.href = URL.createObjectURL(dataBlob);
link.download = 'claude_conversation.json';
link.click();
```

## 處理導出的數據

```python
from core.data_collection.claude_conversation_collector import ClaudeConversationCollector

# 創建收集器
collector = ClaudeConversationCollector()

# 讀取對話文件
with open('conversation.txt', 'r', encoding='utf-8') as f:
    conversation_text = f.read()

# 處理對話
result = collector.process_current_conversation(conversation_text)

print(f"提取了 {result['programming_pairs']} 個編程相關對話對")
```

## 數據價值

我們的 PowerAutomation 開發對話包含：
- MCP 集成經驗
- K2 優化模式
- 架構設計決策
- 問題解決方案
- 代碼實現示例

這些都是訓練 K2 優化器的寶貴數據！
"""
        
        guide_file = self.output_dir / "extraction_guide.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
            
        print(f"\n📝 提取指南已保存到: {guide_file}")


def main():
    """示例用法"""
    collector = ClaudeConversationCollector()
    
    # 導出提取指南
    collector.export_current_session_guide()
    
    # 如果有對話文件，可以處理
    conversation_file = Path("conversation.txt")
    if conversation_file.exists():
        with open(conversation_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        result = collector.process_current_conversation(text)
        print(f"\n✅ 處理完成！")
        print(f"總消息數: {result['total_messages']}")
        print(f"編程對話對: {result['programming_pairs']}")
        print(f"質量指標: {result['quality_metrics']}")
    else:
        print(f"\n請先導出對話到 {conversation_file}")


if __name__ == "__main__":
    main()