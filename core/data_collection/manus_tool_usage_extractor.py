#!/usr/bin/env python3
"""
Manus 工具使用模式提取器
專門學習 Manus 的工具調用模式和任務執行策略
"""

import json
from pathlib import Path
from datetime import datetime
import re
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManusToolUsageExtractor:
    """從 Manus 對話中提取工具使用模式"""
    
    def __init__(self):
        self.output_dir = Path("./data/manus_tool_patterns")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 常見的工具調用模式
        self.tool_patterns = {
            'file_operations': [
                r'創建.*文件', r'編輯.*文件', r'刪除.*文件', r'重命名.*文件',
                r'create.*file', r'edit.*file', r'delete.*file', r'rename.*file'
            ],
            'code_execution': [
                r'執行.*代碼', r'運行.*腳本', r'測試.*功能', r'調試.*程序',
                r'run.*code', r'execute.*script', r'test.*function', r'debug.*program'
            ],
            'search_operations': [
                r'搜索.*', r'查找.*', r'定位.*', r'檢索.*',
                r'search.*', r'find.*', r'locate.*', r'retrieve.*'
            ],
            'analysis_operations': [
                r'分析.*', r'評估.*', r'檢查.*', r'診斷.*',
                r'analyze.*', r'evaluate.*', r'check.*', r'diagnose.*'
            ],
            'automation_tasks': [
                r'自動化.*', r'批量.*', r'生成.*', r'構建.*',
                r'automate.*', r'batch.*', r'generate.*', r'build.*'
            ]
        }
        
    def extract_tool_patterns_from_conversations(self, conversations_file: str):
        """從對話文件中提取工具使用模式"""
        logger.info(f"開始提取工具使用模式: {conversations_file}")
        
        # 讀取對話數據
        with open(conversations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        conversations = data.get('conversations', [])
        logger.info(f"找到 {len(conversations)} 個對話")
        
        # 提取工具使用模式
        tool_usage_patterns = []
        
        for conv in conversations:
            if not conv or 'messages' not in conv:
                continue
                
            # 分析每個對話
            pattern = self._analyze_conversation(conv)
            if pattern:
                tool_usage_patterns.append(pattern)
                
        # 統計和分析
        analysis = self._analyze_patterns(tool_usage_patterns)
        
        # 保存結果
        self._save_analysis(tool_usage_patterns, analysis)
        
        return analysis
        
    def _analyze_conversation(self, conversation: Dict) -> Dict:
        """分析單個對話的工具使用模式"""
        messages = conversation.get('messages', [])
        task_info = conversation.get('task_info', {})
        
        pattern = {
            'task_id': task_info.get('id', 'unknown'),
            'task_title': task_info.get('title', ''),
            'tool_sequences': [],
            'user_intents': [],
            'execution_steps': [],
            'code_blocks': [],
            'file_operations': [],
            'success_indicators': []
        }
        
        # 分析消息序列
        for i, msg in enumerate(messages):
            role = msg.get('role', '')
            content = msg.get('content', '')
            
            if role == 'user':
                # 提取用戶意圖
                intent = self._extract_user_intent(content)
                if intent:
                    pattern['user_intents'].append({
                        'index': i,
                        'intent': intent,
                        'original': content[:100]
                    })
                    
            elif role == 'assistant':
                # 提取助手的工具使用
                tools_used = self._extract_tool_usage(content)
                if tools_used:
                    pattern['tool_sequences'].extend(tools_used)
                    
                # 提取代碼塊
                code_blocks = self._extract_code_blocks(content)
                pattern['code_blocks'].extend(code_blocks)
                
                # 提取執行步驟
                steps = self._extract_execution_steps(content)
                pattern['execution_steps'].extend(steps)
                
        return pattern if pattern['tool_sequences'] else None
        
    def _extract_user_intent(self, content: str) -> str:
        """提取用戶意圖"""
        content_lower = content.lower()
        
        # 常見意圖模式
        intent_keywords = {
            'create': ['創建', '新建', 'create', 'new', 'make'],
            'modify': ['修改', '編輯', '更新', 'modify', 'edit', 'update'],
            'fix': ['修復', '解決', '處理', 'fix', 'solve', 'handle'],
            'analyze': ['分析', '檢查', '診斷', 'analyze', 'check', 'diagnose'],
            'automate': ['自動化', '批量', 'automate', 'batch'],
            'search': ['搜索', '查找', '找到', 'search', 'find', 'locate'],
            'test': ['測試', '驗證', 'test', 'verify', 'validate'],
            'optimize': ['優化', '改進', 'optimize', 'improve']
        }
        
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return intent
                    
        return 'general'
        
    def _extract_tool_usage(self, content: str) -> List[Dict]:
        """提取工具使用信息"""
        tools = []
        
        # 檢查各種工具模式
        for tool_type, patterns in self.tool_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    tools.append({
                        'type': tool_type,
                        'action': match.group(),
                        'position': match.start()
                    })
                    
        # 檢查特定工具標記
        if '```' in content:
            tools.append({'type': 'code_execution', 'action': 'code_block'})
            
        if any(marker in content for marker in ['[執行]', '[運行]', '[Execute]', '[Run]']):
            tools.append({'type': 'command_execution', 'action': 'command'})
            
        return tools
        
    def _extract_code_blocks(self, content: str) -> List[Dict]:
        """提取代碼塊"""
        code_blocks = []
        
        # 匹配 ``` 代碼塊
        pattern = r'```(\w*)\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            
            code_blocks.append({
                'language': language,
                'code': code[:500],  # 只保存前500字符
                'purpose': self._infer_code_purpose(code)
            })
            
        return code_blocks
        
    def _extract_execution_steps(self, content: str) -> List[str]:
        """提取執行步驟"""
        steps = []
        
        # 查找步驟標記
        step_patterns = [
            r'步驟\s*(\d+)[：:](.+)',
            r'Step\s*(\d+)[：:](.+)',
            r'(\d+)\.\s*(.+)',
            r'第(\d+)步[：:](.+)'
        ]
        
        for pattern in step_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                step_text = match.group(2).strip()
                if len(step_text) > 10:  # 過濾太短的
                    steps.append(step_text[:200])
                    
        return steps
        
    def _infer_code_purpose(self, code: str) -> str:
        """推斷代碼用途"""
        code_lower = code.lower()
        
        if 'import' in code_lower or 'from' in code_lower:
            return 'import_setup'
        elif 'def ' in code_lower or 'function' in code_lower:
            return 'function_definition'
        elif 'class ' in code_lower:
            return 'class_definition'
        elif 'for ' in code_lower or 'while ' in code_lower:
            return 'loop_operation'
        elif 'if ' in code_lower:
            return 'conditional_logic'
        elif 'open(' in code_lower or 'read' in code_lower or 'write' in code_lower:
            return 'file_operation'
        elif 'request' in code_lower or 'api' in code_lower:
            return 'api_call'
        else:
            return 'general_code'
            
    def _analyze_patterns(self, patterns: List[Dict]) -> Dict:
        """分析工具使用模式"""
        analysis = {
            'total_conversations': len(patterns),
            'tool_usage_stats': {},
            'common_sequences': [],
            'intent_distribution': {},
            'code_language_distribution': {},
            'execution_patterns': []
        }
        
        # 統計工具使用
        tool_counts = {}
        intent_counts = {}
        language_counts = {}
        
        for pattern in patterns:
            # 統計工具類型
            for tool in pattern['tool_sequences']:
                tool_type = tool['type']
                tool_counts[tool_type] = tool_counts.get(tool_type, 0) + 1
                
            # 統計用戶意圖
            for intent_info in pattern['user_intents']:
                intent = intent_info['intent']
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
                
            # 統計代碼語言
            for code_block in pattern['code_blocks']:
                lang = code_block['language']
                language_counts[lang] = language_counts.get(lang, 0) + 1
                
        analysis['tool_usage_stats'] = tool_counts
        analysis['intent_distribution'] = intent_counts
        analysis['code_language_distribution'] = language_counts
        
        # 找出常見的工具序列
        analysis['common_sequences'] = self._find_common_sequences(patterns)
        
        return analysis
        
    def _find_common_sequences(self, patterns: List[Dict]) -> List[Dict]:
        """找出常見的工具使用序列"""
        sequences = []
        
        # 提取所有工具序列
        for pattern in patterns:
            if len(pattern['tool_sequences']) >= 2:
                # 創建工具類型序列
                seq = [tool['type'] for tool in pattern['tool_sequences']]
                sequences.append({
                    'sequence': seq,
                    'intent': pattern['user_intents'][0]['intent'] if pattern['user_intents'] else 'unknown'
                })
                
        # 統計序列頻率（簡化版）
        seq_counts = {}
        for seq_info in sequences:
            seq_str = ' -> '.join(seq_info['sequence'][:3])  # 只看前3個
            if seq_str not in seq_counts:
                seq_counts[seq_str] = {'count': 0, 'intents': []}
            seq_counts[seq_str]['count'] += 1
            seq_counts[seq_str]['intents'].append(seq_info['intent'])
            
        # 返回最常見的序列
        common_sequences = []
        for seq, info in sorted(seq_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
            common_sequences.append({
                'sequence': seq,
                'count': info['count'],
                'common_intent': max(set(info['intents']), key=info['intents'].count)
            })
            
        return common_sequences
        
    def _save_analysis(self, patterns: List[Dict], analysis: Dict):
        """保存分析結果"""
        # 保存詳細模式
        patterns_file = self.output_dir / f"tool_patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump({
                'patterns': patterns[:100],  # 保存前100個作為示例
                'analysis': analysis,
                'extracted_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        # 生成工具使用報告
        report_file = self.output_dir / f"tool_usage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Manus 工具使用模式分析報告\n\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 概覽\n\n")
            f.write(f"- 分析對話數: {analysis['total_conversations']}\n")
            f.write(f"- 識別的工具類型: {len(analysis['tool_usage_stats'])}\n\n")
            
            f.write("## 工具使用統計\n\n")
            for tool_type, count in sorted(analysis['tool_usage_stats'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{tool_type}**: {count} 次\n")
                
            f.write("\n## 用戶意圖分布\n\n")
            for intent, count in sorted(analysis['intent_distribution'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{intent}**: {count} 次\n")
                
            f.write("\n## 常見工具使用序列\n\n")
            for seq_info in analysis['common_sequences']:
                f.write(f"- `{seq_info['sequence']}` (出現 {seq_info['count']} 次，常見意圖: {seq_info['common_intent']})\n")
                
            f.write("\n## 代碼語言分布\n\n")
            for lang, count in sorted(analysis['code_language_distribution'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{lang}**: {count} 個代碼塊\n")
                
        # 生成訓練數據（專注於工具使用）
        training_file = self.output_dir / f"tool_training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(training_file, 'w', encoding='utf-8') as f:
            for pattern in patterns[:500]:  # 使用前500個
                if pattern['user_intents'] and pattern['tool_sequences']:
                    # 創建訓練樣本
                    training_sample = {
                        'input': pattern['user_intents'][0]['original'],
                        'intent': pattern['user_intents'][0]['intent'],
                        'tools_used': [tool['type'] for tool in pattern['tool_sequences']],
                        'has_code': len(pattern['code_blocks']) > 0,
                        'steps_count': len(pattern['execution_steps'])
                    }
                    f.write(json.dumps(training_sample, ensure_ascii=False) + '\n')
                    
        logger.info(f"\n✅ 分析完成！")
        logger.info(f"  模式文件: {patterns_file}")
        logger.info(f"  分析報告: {report_file}")
        logger.info(f"  訓練數據: {training_file}")
        
        # 顯示關鍵發現
        logger.info(f"\n🔍 關鍵發現:")
        logger.info(f"  最常用工具: {max(analysis['tool_usage_stats'].items(), key=lambda x: x[1])[0]}")
        logger.info(f"  最常見意圖: {max(analysis['intent_distribution'].items(), key=lambda x: x[1])[0]}")
        if analysis['common_sequences']:
            logger.info(f"  最常見序列: {analysis['common_sequences'][0]['sequence']}")


def create_tool_learning_dataset(patterns_file: str, output_file: str):
    """創建專門的工具學習數據集"""
    logger.info("創建工具學習數據集...")
    
    with open(patterns_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    patterns = data['patterns']
    training_data = []
    
    for pattern in patterns:
        if not pattern['tool_sequences']:
            continue
            
        # 構建上下文和工具調用序列
        context = {
            'user_request': pattern['user_intents'][0]['original'] if pattern['user_intents'] else '',
            'tool_sequence': [],
            'execution_steps': pattern['execution_steps']
        }
        
        # 整理工具調用序列
        for tool in pattern['tool_sequences']:
            context['tool_sequence'].append({
                'tool': tool['type'],
                'action': tool['action']
            })
            
        # 添加代碼示例
        if pattern['code_blocks']:
            context['code_examples'] = pattern['code_blocks'][:3]  # 最多3個
            
        training_data.append(context)
        
    # 保存訓練數據
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'dataset': 'manus_tool_usage',
            'version': '1.0',
            'samples': training_data,
            'total': len(training_data),
            'created_at': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
        
    logger.info(f"✅ 創建了 {len(training_data)} 個工具學習樣本")
    

def main():
    """主函數"""
    print("""
    🔧 Manus 工具使用模式提取器
    
    這個工具會：
    1. 分析 Manus 對話中的工具使用模式
    2. 提取常見的工具調用序列
    3. 統計用戶意圖和工具類型的對應關係
    4. 生成專門的工具使用訓練數據
    
    特別關注：
    - 工具調用的順序和組合
    - 不同任務類型的工具選擇策略
    - 執行步驟的組織方式
    """)
    
    # 使用之前收集的對話數據
    conversations_file = input("\n請輸入 Manus 對話數據文件路徑: ").strip()
    
    if not conversations_file:
        # 使用默認路徑
        conversations_file = "./data/manus_complete_collection/all_conversations.json"
        
    if not Path(conversations_file).exists():
        print(f"❌ 文件不存在: {conversations_file}")
        print("請先運行 manus_precise_sidebar_collector.py 收集對話數據")
        return
        
    extractor = ManusToolUsageExtractor()
    analysis = extractor.extract_tool_patterns_from_conversations(conversations_file)
    
    # 創建專門的訓練數據集
    if input("\n是否創建工具學習數據集？(y/n): ").lower() == 'y':
        patterns_file = list(Path("./data/manus_tool_patterns").glob("tool_patterns_*.json"))[-1]
        output_file = "./data/manus_tool_patterns/tool_learning_dataset.json"
        create_tool_learning_dataset(str(patterns_file), output_file)
        print(f"\n✅ 工具學習數據集已保存: {output_file}")


if __name__ == "__main__":
    main()