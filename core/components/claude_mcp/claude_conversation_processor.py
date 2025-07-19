#!/usr/bin/env python3
"""
Claude 對話處理器
提取並分析我們的 Claude 對話作為訓練數據
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re

class ClaudeConversationProcessor:
    """處理 Claude 對話歷史"""
    
    def __init__(self):
        self.output_dir = Path("./data/claude_conversations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 定義任務類型
        self.task_types = {
            'code_generation': ['創建', '寫', 'create', 'write', 'implement'],
            'debugging': ['錯誤', '修復', 'error', 'fix', 'debug'],
            'analysis': ['分析', '檢查', 'analyze', 'check', 'review'],
            'automation': ['自動化', '腳本', 'automate', 'script'],
            'data_processing': ['數據', '處理', 'data', 'process', 'extract']
        }
        
    def extract_current_conversation(self) -> Dict:
        """提取當前對話"""
        # 這是一個示例結構，實際需要從 Claude 的對話歷史中提取
        conversation = {
            'id': 'current_session',
            'timestamp': datetime.now().isoformat(),
            'messages': [],
            'context': 'PowerAutomation Development & Manus Data Collection',
            'tasks_completed': []
        }
        
        # 記錄本次對話中完成的主要任務
        main_tasks = [
            {
                'type': 'data_collection',
                'description': 'Manus 任務收集',
                'tools_used': ['selenium', 'beautifulsoup', 'asyncio'],
                'outcome': 'collected_72_tasks'
            },
            {
                'type': 'tool_development',
                'description': '開發多個數據收集工具',
                'tools_used': ['python', 'selenium', 'chrome_driver'],
                'files_created': [
                    'manus_precise_sidebar_collector.py',
                    'manus_interactive_collector.py',
                    'manus_simple_scroll_collector.py',
                    'manus_advanced_analyzer.py'
                ]
            },
            {
                'type': 'pattern_analysis',
                'description': '工具使用模式分析',
                'focus': 'Manus tool usage patterns',
                'purpose': 'training_data_generation'
            }
        ]
        
        conversation['tasks_completed'] = main_tasks
        
        return conversation
        
    def analyze_tool_usage_in_conversation(self, conversation: Dict) -> Dict:
        """分析對話中的工具使用"""
        analysis = {
            'tools_mentioned': set(),
            'programming_languages': set(),
            'frameworks': set(),
            'task_patterns': [],
            'problem_solving_approaches': []
        }
        
        # 從任務中提取工具
        for task in conversation.get('tasks_completed', []):
            tools = task.get('tools_used', [])
            analysis['tools_mentioned'].update(tools)
            
            # 識別編程語言
            for tool in tools:
                if tool in ['python', 'javascript', 'typescript']:
                    analysis['programming_languages'].add(tool)
                elif tool in ['selenium', 'beautifulsoup', 'asyncio', 'aiohttp']:
                    analysis['frameworks'].add(tool)
                    
        # 識別問題解決模式
        problem_patterns = [
            {
                'problem': '自動識別側邊欄失敗',
                'approaches': [
                    '創建多個不同的收集器',
                    '從自動化到半自動化',
                    '最終採用手動方式'
                ],
                'lesson': '靈活調整策略，不固執於一種方法'
            },
            {
                'problem': '需要批量處理大量數據',
                'approaches': [
                    '異步下載',
                    '批次處理',
                    '進度保存'
                ],
                'lesson': '大規模數據處理需要考慮效率和容錯'
            }
        ]
        
        analysis['problem_solving_approaches'] = problem_patterns
        
        return analysis
        
    def create_training_examples(self, conversation: Dict, analysis: Dict) -> List[Dict]:
        """創建訓練樣本"""
        examples = []
        
        # 基於完成的任務創建樣本
        for task in conversation.get('tasks_completed', []):
            example = {
                'input': f"Task: {task['description']}",
                'approach': 'tool_based_solution',
                'tools': task.get('tools_used', []),
                'output_type': task['type'],
                'complexity': 'high' if len(task.get('tools_used', [])) > 2 else 'medium'
            }
            
            # 添加具體的代碼生成示例
            if 'files_created' in task:
                example['generated_files'] = task['files_created']
                example['pattern'] = 'iterative_development'
                
            examples.append(example)
            
        # 添加問題解決示例
        for pattern in analysis.get('problem_solving_approaches', []):
            example = {
                'input': f"Problem: {pattern['problem']}",
                'approach': 'adaptive_problem_solving',
                'strategies': pattern['approaches'],
                'learning': pattern['lesson'],
                'pattern': 'flexibility_and_adaptation'
            }
            examples.append(example)
            
        return examples
        
    def generate_insights(self, analysis: Dict) -> Dict:
        """生成洞察"""
        insights = {
            'key_patterns': [],
            'tool_preferences': [],
            'success_factors': [],
            'recommendations': []
        }
        
        # 關鍵模式
        insights['key_patterns'] = [
            '工具選擇基於任務類型',
            '從複雜到簡單的漸進式解決方案',
            '重視用戶反饋並快速調整'
        ]
        
        # 工具偏好
        tools = list(analysis['tools_mentioned'])
        insights['tool_preferences'] = {
            'primary_language': 'python',
            'automation': ['selenium', 'asyncio'],
            'data_processing': ['beautifulsoup', 'json'],
            'commonly_used': tools
        }
        
        # 成功因素
        insights['success_factors'] = [
            '快速原型開發',
            '多種方案並行',
            '根據實際情況調整策略',
            '清晰的錯誤處理和用戶提示'
        ]
        
        # 建議
        insights['recommendations'] = [
            '結合 Manus 的工具使用模式',
            '保持靈活的問題解決方法',
            '注重實用性而非完美性'
        ]
        
        return insights
        
    def save_conversation_data(self):
        """保存對話數據"""
        # 提取當前對話
        conversation = self.extract_current_conversation()
        
        # 分析工具使用
        analysis = self.analyze_tool_usage_in_conversation(conversation)
        
        # 創建訓練樣本
        training_examples = self.create_training_examples(conversation, analysis)
        
        # 生成洞察
        insights = self.generate_insights(analysis)
        
        # 保存所有數據
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存對話記錄
        conv_file = self.output_dir / f'conversation_{timestamp}.json'
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump({
                'conversation': conversation,
                'analysis': {k: list(v) if isinstance(v, set) else v for k, v in analysis.items()},
                'timestamp': timestamp
            }, f, ensure_ascii=False, indent=2)
            
        # 保存訓練樣本
        training_file = self.output_dir / f'training_examples_{timestamp}.jsonl'
        with open(training_file, 'w', encoding='utf-8') as f:
            for example in training_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
                
        # 保存洞察報告
        insights_file = self.output_dir / f'insights_{timestamp}.json'
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
            
        # 生成摘要報告
        report_file = self.output_dir / f'conversation_report_{timestamp}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Claude 對話分析報告\n\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 對話概覽\n\n")
            f.write(f"- 主題: {conversation['context']}\n")
            f.write(f"- 完成任務數: {len(conversation['tasks_completed'])}\n\n")
            
            f.write("## 使用的工具和技術\n\n")
            f.write("### 編程語言\n")
            for lang in analysis['programming_languages']:
                f.write(f"- {lang}\n")
                
            f.write("\n### 框架和庫\n")
            for framework in analysis['frameworks']:
                f.write(f"- {framework}\n")
                
            f.write("\n## 關鍵洞察\n\n")
            for pattern in insights['key_patterns']:
                f.write(f"- {pattern}\n")
                
            f.write("\n## 成功因素\n\n")
            for factor in insights['success_factors']:
                f.write(f"- {factor}\n")
                
            f.write("\n## 建議\n\n")
            for rec in insights['recommendations']:
                f.write(f"- {rec}\n")
                
        print(f"\n✅ Claude 對話數據已保存:")
        print(f"  對話記錄: {conv_file}")
        print(f"  訓練樣本: {training_file}")
        print(f"  洞察: {insights_file}")
        print(f"  報告: {report_file}")
        
        return {
            'conversation': conversation,
            'analysis': analysis,
            'training_examples': training_examples,
            'insights': insights
        }


def main():
    """主函數"""
    print("""
    🤖 Claude 對話處理器
    
    功能：
    1. 提取當前對話內容
    2. 分析工具使用模式
    3. 創建訓練樣本
    4. 生成洞察和建議
    """)
    
    processor = ClaudeConversationProcessor()
    results = processor.save_conversation_data()
    
    print(f"\n📊 處理結果:")
    print(f"  完成任務: {len(results['conversation']['tasks_completed'])}")
    print(f"  訓練樣本: {len(results['training_examples'])}")
    print(f"  識別工具: {len(results['analysis']['tools_mentioned'])}")


if __name__ == "__main__":
    main()