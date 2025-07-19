#!/usr/bin/env python3
"""
MCP 合併分析工具
分析項目中所有 MCP 的功能重複情況並提供合併建議
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
from datetime import datetime

class MCPConsolidationAnalyzer:
    def __init__(self):
        self.mcp_info = {}
        self.duplicate_functions = {}
        self.consolidation_suggestions = []
        
    def analyze_project(self, project_root: str = "."):
        """分析整個項目的 MCP"""
        print("🔍 開始分析 MCP 功能重複情況...")
        
        # 查找所有 MCP 相關文件
        mcp_files = self._find_mcp_files(project_root)
        print(f"找到 {len(mcp_files)} 個 MCP 相關文件")
        
        # 分析每個 MCP
        for file_path in mcp_files:
            self._analyze_mcp_file(file_path)
        
        # 查找重複功能
        self._find_duplicates()
        
        # 生成合併建議
        self._generate_consolidation_suggestions()
        
        # 生成報告
        return self._generate_report()
    
    def _find_mcp_files(self, root: str) -> List[Path]:
        """查找所有 MCP 相關文件"""
        mcp_files = []
        patterns = [
            '*_mcp.py',
            '*_manager.py',
            '*_server.py',
            'mcp_*.py'
        ]
        
        for pattern in patterns:
            mcp_files.extend(Path(root).rglob(pattern))
        
        # 過濾掉 venv 和 __pycache__
        mcp_files = [f for f in mcp_files if 'venv' not in str(f) and '__pycache__' not in str(f)]
        
        return sorted(set(mcp_files))
    
    def _analyze_mcp_file(self, file_path: Path):
        """分析單個 MCP 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取 MCP 名稱
            mcp_name = self._extract_mcp_name(file_path, content)
            if not mcp_name:
                return
            
            # 提取功能信息
            tools = self._extract_tools(content)
            resources = self._extract_resources(content)
            description = self._extract_description(content)
            
            self.mcp_info[mcp_name] = {
                'file': str(file_path),
                'tools': tools,
                'resources': resources,
                'description': description,
                'category': self._categorize_mcp(mcp_name, tools, description)
            }
            
        except Exception as e:
            print(f"分析文件 {file_path} 時出錯: {e}")
    
    def _extract_mcp_name(self, file_path: Path, content: str) -> str:
        """提取 MCP 名稱"""
        # 從文件名提取
        file_name = file_path.stem
        
        # 嘗試從類名提取
        class_match = re.search(r'class\s+(\w+MCP|\w+Manager|\w+Server)', content)
        if class_match:
            return class_match.group(1)
        
        # 使用文件名
        if '_mcp' in file_name:
            return file_name.replace('_mcp', '').title() + 'MCP'
        elif '_manager' in file_name:
            return file_name.replace('_manager', '').title() + 'Manager'
        
        return file_name
    
    def _extract_tools(self, content: str) -> List[Dict]:
        """提取工具定義"""
        tools = []
        
        # 查找 @mcp.tool 裝飾器
        tool_pattern = r'@(?:mcp\.)?tool(?:\([^)]*\))?\s*(?:async\s+)?def\s+(\w+)'
        for match in re.finditer(tool_pattern, content):
            tool_name = match.group(1)
            
            # 嘗試提取描述
            desc_pattern = rf'def\s+{tool_name}.*?"""(.*?)"""'
            desc_match = re.search(desc_pattern, content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else ""
            
            tools.append({
                'name': tool_name,
                'description': description
            })
        
        # 查找工具字典定義
        tools_dict_pattern = r'tools\s*=\s*\{([^}]+)\}'
        tools_match = re.search(tools_dict_pattern, content, re.DOTALL)
        if tools_match:
            tools_content = tools_match.group(1)
            tool_names = re.findall(r'["\'](\w+)["\']', tools_content)
            for name in tool_names:
                if not any(t['name'] == name for t in tools):
                    tools.append({'name': name, 'description': ''})
        
        return tools
    
    def _extract_resources(self, content: str) -> List[str]:
        """提取資源定義"""
        resources = []
        
        # 查找 @mcp.resource 裝飾器
        resource_pattern = r'@(?:mcp\.)?resource\s*(?:\([^)]*\))?\s*(?:async\s+)?def\s+(\w+)'
        for match in re.finditer(resource_pattern, content):
            resources.append(match.group(1))
        
        return resources
    
    def _extract_description(self, content: str) -> str:
        """提取描述"""
        # 查找文件開頭的文檔字符串
        doc_match = re.match(r'(?:.*?)?"""(.*?)"""', content, re.DOTALL)
        if doc_match:
            return doc_match.group(1).strip().split('\n')[0]
        
        return ""
    
    def _categorize_mcp(self, name: str, tools: List[Dict], description: str) -> str:
        """分類 MCP"""
        name_lower = name.lower()
        desc_lower = description.lower()
        tool_names = [t['name'].lower() for t in tools]
        
        # 基於名稱和工具判斷類別
        if any(word in name_lower for word in ['command', 'cmd', 'exec']):
            return 'command_execution'
        elif any(word in name_lower for word in ['code', 'flow', 'spec']):
            return 'code_generation'
        elif any(word in name_lower for word in ['ui', 'ag', 'interface']):
            return 'ui_generation'
        elif any(word in name_lower for word in ['route', 'router', 'proxy']):
            return 'routing'
        elif any(word in name_lower for word in ['memory', 'rag', 'store']):
            return 'memory_storage'
        elif any(word in name_lower for word in ['test', 'debug']):
            return 'testing'
        elif any(word in name_lower for word in ['coordinate', 'manage']):
            return 'coordination'
        else:
            return 'other'
    
    def _find_duplicates(self):
        """查找重複功能"""
        # 按類別分組
        categories = {}
        for mcp_name, info in self.mcp_info.items():
            category = info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(mcp_name)
        
        # 查找每個類別中的重複
        for category, mcps in categories.items():
            if len(mcps) > 1:
                self.duplicate_functions[category] = mcps
        
        # 查找相同工具名的 MCP
        tool_map = {}
        for mcp_name, info in self.mcp_info.items():
            for tool in info['tools']:
                tool_name = tool['name']
                if tool_name not in tool_map:
                    tool_map[tool_name] = []
                tool_map[tool_name].append(mcp_name)
        
        # 記錄有相同工具的 MCP
        for tool_name, mcps in tool_map.items():
            if len(mcps) > 1:
                self.duplicate_functions[f'tool_{tool_name}'] = mcps
    
    def _generate_consolidation_suggestions(self):
        """生成合併建議"""
        # 基於類別的合併建議
        for category, mcps in self.duplicate_functions.items():
            if category.startswith('tool_'):
                continue
                
            if len(mcps) > 1:
                self.consolidation_suggestions.append({
                    'type': 'category_merge',
                    'category': category,
                    'mcps': mcps,
                    'suggestion': f"合併 {category} 類別的 {len(mcps)} 個 MCP",
                    'new_name': f"{category}_unified_mcp",
                    'benefit': '減少功能重複，提高維護性'
                })
        
        # 特定的合併建議
        specific_merges = [
            {
                'mcps': ['command_manager', 'command_mcp'],
                'new_name': 'unified_command_mcp',
                'reason': '命令執行功能重複'
            },
            {
                'mcps': ['codeflow_manager', 'codeflow_mcp', 'spec_generator'],
                'new_name': 'unified_codeflow_mcp',
                'reason': '代碼生成功能重複'
            },
            {
                'mcps': ['claude_router_mcp', 'smart_routing_mcp'],
                'new_name': 'unified_routing_mcp',
                'reason': '路由功能重複'
            }
        ]
        
        for merge in specific_merges:
            existing_mcps = [m for m in merge['mcps'] if any(m in name.lower() for name in self.mcp_info.keys())]
            if len(existing_mcps) > 1:
                self.consolidation_suggestions.append({
                    'type': 'specific_merge',
                    'mcps': existing_mcps,
                    'new_name': merge['new_name'],
                    'reason': merge['reason'],
                    'benefit': '統一功能接口，避免混淆'
                })
    
    def _generate_report(self) -> str:
        """生成分析報告"""
        report = []
        report.append("=" * 80)
        report.append("MCP 功能重複分析報告")
        report.append("=" * 80)
        report.append(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 概覽
        report.append("## 📊 概覽")
        report.append(f"- 總共發現 {len(self.mcp_info)} 個 MCP")
        report.append(f"- 發現 {len(self.duplicate_functions)} 組功能重複")
        report.append(f"- 提出 {len(self.consolidation_suggestions)} 個合併建議\n")
        
        # MCP 列表
        report.append("## 📋 MCP 列表")
        categories = {}
        for name, info in self.mcp_info.items():
            cat = info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((name, info))
        
        for cat, mcps in sorted(categories.items()):
            report.append(f"\n### {cat.replace('_', ' ').title()}")
            for name, info in mcps:
                report.append(f"- **{name}**")
                report.append(f"  - 文件: {info['file']}")
                report.append(f"  - 工具數: {len(info['tools'])}")
                if info['description']:
                    report.append(f"  - 描述: {info['description'][:80]}...")
        
        # 功能重複
        report.append("\n## 🔄 功能重複檢測")
        for category, mcps in self.duplicate_functions.items():
            if not category.startswith('tool_'):
                report.append(f"\n### {category.replace('_', ' ').title()}")
                report.append(f"發現 {len(mcps)} 個 MCP 有相似功能:")
                for mcp in mcps:
                    report.append(f"- {mcp}")
        
        # 合併建議
        report.append("\n## 💡 合併建議")
        for i, suggestion in enumerate(self.consolidation_suggestions, 1):
            report.append(f"\n### 建議 {i}: {suggestion.get('suggestion', suggestion.get('reason', ''))}")
            report.append(f"- 涉及 MCP: {', '.join(suggestion['mcps'])}")
            report.append(f"- 建議新名稱: {suggestion.get('new_name', 'N/A')}")
            report.append(f"- 預期收益: {suggestion.get('benefit', 'N/A')}")
        
        # 實施計劃
        report.append("\n## 🚀 實施計劃")
        report.append("\n### 第一階段：合併命令執行類 MCP")
        report.append("1. 合併所有命令執行相關的 MCP")
        report.append("2. 統一接口和錯誤處理")
        report.append("3. 更新所有依賴")
        
        report.append("\n### 第二階段：合併代碼生成類 MCP")
        report.append("1. 整合 codeflow 和 spec 生成功能")
        report.append("2. 建立統一的代碼生成管道")
        
        report.append("\n### 第三階段：合併路由類 MCP")
        report.append("1. 統一路由邏輯")
        report.append("2. 優化性能和錯誤處理")
        
        # 保存詳細數據
        data = {
            'mcp_info': self.mcp_info,
            'duplicates': self.duplicate_functions,
            'suggestions': self.consolidation_suggestions,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('mcp_consolidation_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        report.append(f"\n\n💾 詳細數據已保存到: mcp_consolidation_data.json")
        
        return "\n".join(report)

def main():
    """主函數"""
    analyzer = MCPConsolidationAnalyzer()
    report = analyzer.analyze_project()
    
    # 保存報告
    with open('mcp_consolidation_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print("\n✅ 分析完成！報告已保存到: mcp_consolidation_report.txt")

if __name__ == "__main__":
    main()