#!/usr/bin/env python3
"""
Manus 高級分析器
專門分析工具使用模式和任務執行策略
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManusAdvancedAnalyzer:
    """高級 Manus 分析器"""
    
    def __init__(self):
        self.output_dir = Path("./data/manus_advanced_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 工具模式定義
        self.tool_patterns = {
            'file_operations': {
                'keywords': ['create', 'edit', 'delete', 'write', 'read', 'file', '創建', '編輯', '刪除', '文件'],
                'patterns': [r'create.*file', r'edit.*file', r'寫入.*文件', r'讀取.*文件']
            },
            'code_execution': {
                'keywords': ['run', 'execute', 'test', 'debug', '運行', '執行', '測試', '調試'],
                'patterns': [r'run.*code', r'execute.*script', r'運行.*代碼', r'執行.*腳本']
            },
            'search_analysis': {
                'keywords': ['search', 'find', 'analyze', 'check', '搜索', '查找', '分析', '檢查'],
                'patterns': [r'search.*for', r'find.*in', r'分析.*數據', r'檢查.*結果']
            },
            'automation': {
                'keywords': ['automate', 'batch', 'generate', 'build', '自動化', '批量', '生成', '構建'],
                'patterns': [r'automate.*process', r'batch.*operation', r'自動.*生成', r'批量.*處理']
            },
            'api_integration': {
                'keywords': ['api', 'request', 'fetch', 'post', 'get', '接口', '請求', '獲取'],
                'patterns': [r'api.*call', r'fetch.*data', r'請求.*接口', r'調用.*API']
            }
        }
        
    async def fetch_task_content(self, session: aiohttp.ClientSession, task: Dict) -> Dict:
        """異步獲取任務內容"""
        try:
            async with session.get(task['url'], timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    return {
                        'task': task,
                        'html': html,
                        'success': True
                    }
                else:
                    return {
                        'task': task,
                        'error': f'Status {response.status}',
                        'success': False
                    }
        except Exception as e:
            return {
                'task': task,
                'error': str(e),
                'success': False
            }
            
    async def batch_download(self, tasks: List[Dict]) -> List[Dict]:
        """批量下載任務"""
        async with aiohttp.ClientSession() as session:
            download_tasks = [self.fetch_task_content(session, task) for task in tasks]
            results = await asyncio.gather(*download_tasks)
            return results
            
    def extract_advanced_patterns(self, html: str) -> Dict:
        """提取高級模式"""
        soup = BeautifulSoup(html, 'html.parser')
        
        patterns = {
            'title': '',
            'messages': [],
            'tool_sequences': [],
            'code_blocks': [],
            'execution_steps': [],
            'error_handling': [],
            'success_indicators': []
        }
        
        # 提取標題
        title_elem = soup.find('title')
        if title_elem:
            patterns['title'] = title_elem.text.strip()
            
        # 提取所有文本內容
        text_content = soup.get_text()
        
        # 分析工具使用序列
        for tool_type, config in self.tool_patterns.items():
            for keyword in config['keywords']:
                if keyword.lower() in text_content.lower():
                    patterns['tool_sequences'].append({
                        'type': tool_type,
                        'keyword': keyword,
                        'context': self._extract_context(text_content, keyword)
                    })
                    
        # 提取代碼塊
        code_elements = soup.find_all(['code', 'pre'])
        for code in code_elements:
            code_text = code.get_text(strip=True)
            if code_text:
                patterns['code_blocks'].append({
                    'content': code_text[:500],
                    'language': self._detect_language(code_text),
                    'purpose': self._infer_code_purpose(code_text)
                })
                
        # 提取執行步驟
        step_patterns = [
            r'步驟\s*(\d+)',
            r'Step\s*(\d+)',
            r'(\d+)\.\s*',
            r'第(\d+)步'
        ]
        
        for pattern in step_patterns:
            matches = re.finditer(pattern, text_content, re.MULTILINE)
            for match in matches:
                context = text_content[match.start():match.start()+200]
                patterns['execution_steps'].append(context.strip())
                
        # 識別錯誤處理
        error_keywords = ['error', 'exception', 'failed', '錯誤', '異常', '失敗']
        for keyword in error_keywords:
            if keyword in text_content.lower():
                patterns['error_handling'].append({
                    'keyword': keyword,
                    'context': self._extract_context(text_content, keyword)
                })
                
        # 識別成功標記
        success_keywords = ['success', 'completed', 'done', '成功', '完成', '已完成']
        for keyword in success_keywords:
            if keyword in text_content.lower():
                patterns['success_indicators'].append({
                    'keyword': keyword,
                    'context': self._extract_context(text_content, keyword)
                })
                
        return patterns
        
    def _extract_context(self, text: str, keyword: str, context_size: int = 100) -> str:
        """提取關鍵詞上下文"""
        idx = text.lower().find(keyword.lower())
        if idx >= 0:
            start = max(0, idx - context_size)
            end = min(len(text), idx + len(keyword) + context_size)
            return text[start:end].strip()
        return ""
        
    def _detect_language(self, code: str) -> str:
        """檢測編程語言"""
        if 'import' in code or 'def ' in code or 'class ' in code:
            return 'python'
        elif 'function' in code or 'const ' in code or 'var ' in code:
            return 'javascript'
        elif '#include' in code or 'int main' in code:
            return 'c/c++'
        elif 'public class' in code or 'private ' in code:
            return 'java'
        else:
            return 'unknown'
            
    def _infer_code_purpose(self, code: str) -> str:
        """推斷代碼用途"""
        code_lower = code.lower()
        
        if 'api' in code_lower or 'request' in code_lower:
            return 'api_integration'
        elif 'test' in code_lower:
            return 'testing'
        elif 'automat' in code_lower:
            return 'automation'
        elif 'analyz' in code_lower or 'analysis' in code_lower:
            return 'data_analysis'
        elif 'create' in code_lower or 'generate' in code_lower:
            return 'generation'
        else:
            return 'general'
            
    def analyze_tool_sequences(self, all_patterns: List[Dict]) -> Dict:
        """分析工具使用序列"""
        analysis = {
            'total_tasks': len(all_patterns),
            'tool_frequency': {},
            'tool_combinations': {},
            'common_sequences': [],
            'language_distribution': {},
            'code_purposes': {},
            'success_rate': 0,
            'error_patterns': []
        }
        
        # 統計工具頻率
        for pattern in all_patterns:
            for tool in pattern.get('tool_sequences', []):
                tool_type = tool['type']
                analysis['tool_frequency'][tool_type] = analysis['tool_frequency'].get(tool_type, 0) + 1
                
        # 分析工具組合
        for pattern in all_patterns:
            tools = [t['type'] for t in pattern.get('tool_sequences', [])]
            if len(tools) >= 2:
                for i in range(len(tools) - 1):
                    combo = f"{tools[i]} -> {tools[i+1]}"
                    analysis['tool_combinations'][combo] = analysis['tool_combinations'].get(combo, 0) + 1
                    
        # 統計語言分布
        for pattern in all_patterns:
            for code in pattern.get('code_blocks', []):
                lang = code['language']
                analysis['language_distribution'][lang] = analysis['language_distribution'].get(lang, 0) + 1
                
                purpose = code['purpose']
                analysis['code_purposes'][purpose] = analysis['code_purposes'].get(purpose, 0) + 1
                
        # 計算成功率
        success_count = sum(1 for p in all_patterns if p.get('success_indicators'))
        analysis['success_rate'] = success_count / len(all_patterns) if all_patterns else 0
        
        # 分析錯誤模式
        error_types = {}
        for pattern in all_patterns:
            for error in pattern.get('error_handling', []):
                error_types[error['keyword']] = error_types.get(error['keyword'], 0) + 1
                
        analysis['error_patterns'] = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        
        return analysis
        
    def generate_training_data(self, patterns: List[Dict]) -> List[Dict]:
        """生成訓練數據"""
        training_data = []
        
        for pattern in patterns:
            if pattern.get('tool_sequences'):
                # 創建工具使用訓練樣本
                sample = {
                    'task_description': pattern.get('title', ''),
                    'tools_used': [t['type'] for t in pattern['tool_sequences']],
                    'has_code': len(pattern.get('code_blocks', [])) > 0,
                    'code_languages': list(set(c['language'] for c in pattern.get('code_blocks', []))),
                    'step_count': len(pattern.get('execution_steps', [])),
                    'has_error_handling': len(pattern.get('error_handling', [])) > 0,
                    'success': len(pattern.get('success_indicators', [])) > 0
                }
                
                # 添加工具序列作為訓練目標
                if len(sample['tools_used']) >= 2:
                    sample['tool_sequence'] = ' -> '.join(sample['tools_used'])
                    
                training_data.append(sample)
                
        return training_data
        
    async def run_analysis(self):
        """運行完整分析"""
        logger.info("🚀 開始高級 Manus 分析...")
        
        # 載入任務
        tasks = self.load_tasks()
        logger.info(f"載入了 {len(tasks)} 個任務")
        
        # 批量下載（分批處理）
        batch_size = 20
        all_patterns = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            logger.info(f"\n處理批次 {i//batch_size + 1}/{(len(tasks)-1)//batch_size + 1}")
            
            # 下載
            results = await self.batch_download(batch)
            
            # 提取模式
            for result in results:
                if result['success']:
                    patterns = self.extract_advanced_patterns(result['html'])
                    patterns['task_info'] = result['task']
                    all_patterns.append(patterns)
                    
                    # 保存 HTML
                    html_file = self.output_dir / f"task_{result['task']['id']}.html"
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(result['html'])
                        
            # 避免過快請求
            await asyncio.sleep(2)
            
        logger.info(f"\n成功提取 {len(all_patterns)} 個任務的模式")
        
        # 分析工具序列
        analysis = self.analyze_tool_sequences(all_patterns)
        
        # 生成訓練數據
        training_data = self.generate_training_data(all_patterns)
        
        # 保存結果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存模式數據
        patterns_file = self.output_dir / f'patterns_{timestamp}.json'
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(all_patterns, f, ensure_ascii=False, indent=2)
            
        # 保存分析結果
        analysis_file = self.output_dir / f'analysis_{timestamp}.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
            
        # 保存訓練數據
        training_file = self.output_dir / f'training_data_{timestamp}.jsonl'
        with open(training_file, 'w', encoding='utf-8') as f:
            for sample in training_data:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
                
        # 生成報告
        self.generate_report(analysis, len(all_patterns), timestamp)
        
        logger.info(f"\n✅ 分析完成！")
        logger.info(f"  模式數據: {patterns_file}")
        logger.info(f"  分析結果: {analysis_file}")
        logger.info(f"  訓練數據: {training_file}")
        
        return analysis
        
    def load_tasks(self) -> List[Dict]:
        """載入任務列表"""
        tasks = []
        with open('manus_tasks_manual.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_task = None
        for line in lines:
            line = line.strip()
            if line.startswith("# 任務"):
                if current_task and current_task.get('url'):
                    tasks.append(current_task)
                current_task = {'number': line}
            elif line.startswith("https://"):
                if current_task:
                    current_task['url'] = line
                    current_task['id'] = line.split('/share/')[1].split('?')[0]
                    
        if current_task and current_task.get('url'):
            tasks.append(current_task)
            
        return tasks
        
    def generate_report(self, analysis: Dict, total_patterns: int, timestamp: str):
        """生成分析報告"""
        report_file = self.output_dir / f'report_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Manus 工具使用高級分析報告\n\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 概覽\n\n")
            f.write(f"- 分析任務數: {analysis['total_tasks']}\n")
            f.write(f"- 成功提取模式: {total_patterns}\n")
            f.write(f"- 平均成功率: {analysis['success_rate']:.1%}\n\n")
            
            f.write("## 工具使用頻率\n\n")
            for tool, count in sorted(analysis['tool_frequency'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{tool}**: {count} 次\n")
                
            f.write("\n## 常見工具組合\n\n")
            for combo, count in sorted(analysis['tool_combinations'].items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"- `{combo}`: {count} 次\n")
                
            f.write("\n## 編程語言分布\n\n")
            for lang, count in sorted(analysis['language_distribution'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{lang}**: {count} 個代碼塊\n")
                
            f.write("\n## 代碼用途分析\n\n")
            for purpose, count in sorted(analysis['code_purposes'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{purpose}**: {count} 次\n")
                
            f.write("\n## 錯誤處理模式\n\n")
            for error, count in analysis['error_patterns'][:5]:
                f.write(f"- {error}: {count} 次\n")
                
            f.write("\n## 關鍵發現\n\n")
            f.write("1. **最常用工具類型**：")
            if analysis['tool_frequency']:
                top_tool = max(analysis['tool_frequency'].items(), key=lambda x: x[1])
                f.write(f"{top_tool[0]} ({top_tool[1]} 次)\n")
                
            f.write("2. **最常見工具組合**：")
            if analysis['tool_combinations']:
                top_combo = max(analysis['tool_combinations'].items(), key=lambda x: x[1])
                f.write(f"{top_combo[0]} ({top_combo[1]} 次)\n")
                
            f.write("3. **主要編程語言**：")
            if analysis['language_distribution']:
                top_lang = max(analysis['language_distribution'].items(), key=lambda x: x[1])
                f.write(f"{top_lang[0]} ({top_lang[1]} 個代碼塊)\n")


async def main():
    """主函數"""
    print("""
    🔧 Manus 高級分析器
    
    功能：
    1. 批量異步下載任務內容
    2. 提取工具使用模式
    3. 分析工具組合和序列
    4. 生成訓練數據
    5. 創建詳細分析報告
    """)
    
    analyzer = ManusAdvancedAnalyzer()
    await analyzer.run_analysis()


if __name__ == "__main__":
    asyncio.run(main())