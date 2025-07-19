#!/usr/bin/env python3
"""
Manus 批量分析器
分析手動收集的 Manus 任務，提取工具使用模式
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from datetime import datetime
import re

class ManusBatchAnalyzer:
    def __init__(self):
        self.output_dir = Path("./data/manus_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_tasks(self, file_path="manus_tasks_manual.txt"):
        """載入任務列表"""
        tasks = []
        with open(file_path, 'r', encoding='utf-8') as f:
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
            
        print(f"✅ 載入了 {len(tasks)} 個任務")
        return tasks
        
    def download_task(self, task):
        """下載單個任務的內容"""
        try:
            print(f"  下載: {task['number']}")
            response = requests.get(task['url'], timeout=30)
            if response.status_code == 200:
                return response.text
            else:
                print(f"    ❌ 狀態碼: {response.status_code}")
                return None
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")
            return None
            
    def extract_conversation(self, html_content):
        """從 HTML 提取對話內容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找對話內容（這需要根據實際的 HTML 結構調整）
            conversation = {
                'messages': [],
                'tool_calls': [],
                'code_blocks': []
            }
            
            # 提取標題
            title_elem = soup.find('title')
            if title_elem:
                conversation['title'] = title_elem.text.strip()
                
            # 查找消息（需要根據實際結構調整選擇器）
            message_elements = soup.find_all(['div', 'section'], class_=re.compile('message|chat|conversation'))
            
            for elem in message_elements:
                text = elem.get_text(strip=True)
                if text:
                    # 簡單分類
                    role = 'assistant' if 'manus' in elem.get('class', []) else 'user'
                    conversation['messages'].append({
                        'role': role,
                        'content': text[:500]  # 限制長度
                    })
                    
            # 查找代碼塊
            code_elements = soup.find_all('code')
            for code in code_elements:
                conversation['code_blocks'].append(code.get_text(strip=True)[:200])
                
            return conversation
            
        except Exception as e:
            print(f"    ❌ 解析錯誤: {e}")
            return None
            
    def analyze_tool_patterns(self, conversations):
        """分析工具使用模式"""
        patterns = {
            'total_conversations': len(conversations),
            'tool_keywords': {},
            'code_languages': {},
            'message_counts': [],
            'common_patterns': []
        }
        
        # 工具相關關鍵詞
        tool_keywords = [
            'search', 'find', 'create', 'edit', 'delete', 'run', 'execute',
            'analyze', 'check', 'test', 'build', 'generate', 'fix',
            '搜索', '查找', '創建', '編輯', '刪除', '執行', '分析', '檢查'
        ]
        
        for conv in conversations:
            if not conv:
                continue
                
            # 統計消息數
            patterns['message_counts'].append(len(conv.get('messages', [])))
            
            # 分析工具關鍵詞
            all_text = ' '.join([msg.get('content', '') for msg in conv.get('messages', [])])
            for keyword in tool_keywords:
                if keyword in all_text.lower():
                    patterns['tool_keywords'][keyword] = patterns['tool_keywords'].get(keyword, 0) + 1
                    
            # 統計代碼語言（簡單推測）
            for code in conv.get('code_blocks', []):
                if 'import' in code or 'def ' in code:
                    patterns['code_languages']['python'] = patterns['code_languages'].get('python', 0) + 1
                elif 'function' in code or 'const ' in code:
                    patterns['code_languages']['javascript'] = patterns['code_languages'].get('javascript', 0) + 1
                    
        return patterns
        
    def run_batch_analysis(self):
        """執行批量分析"""
        print("\n🚀 開始批量分析 Manus 任務...")
        
        # 載入任務
        tasks = self.load_tasks()
        
        # 下載並分析
        conversations = []
        print("\n📥 下載任務內容...")
        
        for i, task in enumerate(tasks[:10]):  # 先處理前10個
            print(f"\n處理 {i+1}/{min(10, len(tasks))}: {task['number']}")
            
            # 下載
            html = self.download_task(task)
            if html:
                # 保存 HTML
                html_file = self.output_dir / f"task_{task['id']}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                    
                # 提取對話
                conv = self.extract_conversation(html)
                if conv:
                    conv['task_info'] = task
                    conversations.append(conv)
                    print(f"    ✅ 提取了 {len(conv.get('messages', []))} 條消息")
                    
            # 避免請求過快
            time.sleep(2)
            
        # 分析模式
        print("\n📊 分析工具使用模式...")
        analysis = self.analyze_tool_patterns(conversations)
        
        # 保存結果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存對話數據
        conv_file = self.output_dir / f'conversations_{timestamp}.json'
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
            
        # 保存分析結果
        analysis_file = self.output_dir / f'analysis_{timestamp}.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
            
        # 生成報告
        report_file = self.output_dir / f'report_{timestamp}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Manus 工具使用分析報告\n\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 概覽\n\n")
            f.write(f"- 分析任務數: {len(tasks)}\n")
            f.write(f"- 成功提取: {len(conversations)}\n")
            f.write(f"- 平均消息數: {sum(analysis['message_counts']) / len(analysis['message_counts']) if analysis['message_counts'] else 0:.1f}\n\n")
            
            f.write("## 工具關鍵詞頻率\n\n")
            for keyword, count in sorted(analysis['tool_keywords'].items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"- {keyword}: {count} 次\n")
                
            f.write("\n## 代碼語言分布\n\n")
            for lang, count in analysis['code_languages'].items():
                f.write(f"- {lang}: {count} 個代碼塊\n")
                
        print(f"\n✅ 分析完成！")
        print(f"  對話數據: {conv_file}")
        print(f"  分析結果: {analysis_file}")
        print(f"  報告: {report_file}")
        
        return analysis

def main():
    print("""
    🔧 Manus 批量分析器
    
    這個工具會：
    1. 讀取手動收集的任務列表
    2. 批量下載任務內容
    3. 提取對話和工具使用信息
    4. 分析工具使用模式
    5. 生成分析報告
    """)
    
    analyzer = ManusBatchAnalyzer()
    analyzer.run_batch_analysis()

if __name__ == "__main__":
    main()