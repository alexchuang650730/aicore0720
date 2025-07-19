#!/usr/bin/env python3
"""
Manus HTML 解析器
專門用於從 Manus replay HTML 中提取對話內容
"""

from bs4 import BeautifulSoup
import json
import re
from pathlib import Path

class ManusHTMLParser:
    def __init__(self):
        self.patterns = {
            'tool_call': re.compile(r'(使用|調用|執行|運行|呼叫|call|use|execute|run)\s*(工具|tool|function|api)', re.I),
            'code_block': re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL),
            'command': re.compile(r'(npm|yarn|pip|python|node|git|docker|bash|sh)\s+[\w\-]+'),
            'file_operation': re.compile(r'(創建|修改|編輯|刪除|讀取|寫入|create|modify|edit|delete|read|write)\s*(文件|檔案|file)'),
        }
    
    def parse_replay_html(self, html_path):
        """解析 Manus replay HTML"""
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # 嘗試多種方式提取內容
        content = self._extract_content(soup)
        
        # 分析內容
        result = {
            'title': self._extract_title(soup),
            'messages': [],
            'tools_detected': [],
            'code_blocks': [],
            'commands': [],
            'file_operations': []
        }
        
        if content:
            # 提取工具使用
            if self.patterns['tool_call'].search(content):
                result['tools_detected'].append('tool_usage_detected')
            
            # 提取代碼塊
            code_blocks = self.patterns['code_block'].findall(content)
            for lang, code in code_blocks:
                result['code_blocks'].append({
                    'language': lang or 'unknown',
                    'code': code.strip()
                })
            
            # 提取命令
            commands = self.patterns['command'].findall(content)
            result['commands'] = list(set(commands))
            
            # 提取文件操作
            if self.patterns['file_operation'].search(content):
                result['file_operations'].append('file_operation_detected')
        
        return result
    
    def _extract_content(self, soup):
        """嘗試多種方式提取內容"""
        # 方法1: 查找所有文本節點
        all_text = soup.get_text(separator='\n', strip=True)
        
        # 方法2: 查找特定的內容區域
        content_areas = []
        
        # 查找可能包含對話的元素
        for selector in [
            'div[class*="message"]',
            'div[class*="chat"]',
            'div[class*="conversation"]',
            'div[role]',
            'article',
            'section[class*="content"]',
            '.prose',
            '[data-message]'
        ]:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(separator='\n', strip=True)
                if len(text) > 50:  # 過濾太短的內容
                    content_areas.append(text)
        
        # 合併所有找到的內容
        if content_areas:
            return '\n\n'.join(content_areas)
        
        # 如果沒找到特定區域，返回全部文本
        return all_text
    
    def _extract_title(self, soup):
        """提取標題"""
        # 嘗試多種方式
        title_elem = soup.find('title')
        if title_elem:
            return title_elem.text.strip()
        
        h1_elem = soup.find('h1')
        if h1_elem:
            return h1_elem.text.strip()
        
        return "Unknown Task"

def test_parser():
    """測試解析器"""
    parser = ManusHTMLParser()
    
    # 測試前幾個 HTML 文件
    html_dir = Path('./data/manus_advanced_analysis')
    html_files = list(html_dir.glob('sample_*.html'))[:5]
    
    print("測試 Manus HTML 解析器\n")
    
    for i, html_file in enumerate(html_files, 1):
        print(f"解析文件 {i}: {html_file.name}")
        result = parser.parse_replay_html(html_file)
        
        print(f"  標題: {result['title']}")
        print(f"  檢測到工具: {len(result['tools_detected'])}")
        print(f"  代碼塊: {len(result['code_blocks'])}")
        print(f"  命令: {len(result['commands'])}")
        print(f"  文件操作: {len(result['file_operations'])}")
        
        if result['code_blocks']:
            print(f"  代碼語言: {[cb['language'] for cb in result['code_blocks']]}")
        
        print()

if __name__ == "__main__":
    test_parser()