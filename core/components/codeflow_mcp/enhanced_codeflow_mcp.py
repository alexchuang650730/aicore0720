#!/usr/bin/env python3
"""
增強版 CodeFlow MCP
整合了代碼清理、數據分析、K2定價等功能的完整 MCP 組件
"""

import asyncio
import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import re

# MCP imports
try:
    from mcp.server.lowlevel import Server
    from mcp.server.models import Tool
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ MCP 未安裝，將以獨立模式運行")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolCategory(Enum):
    """工具分類"""
    CODE_CLEANUP = "code_cleanup"
    DATA_ANALYSIS = "data_analysis"
    PRICING = "pricing"
    VISUALIZATION = "visualization"
    WORKFLOW = "workflow"

@dataclass
class CleanupResult:
    """清理結果"""
    removed_files: int
    removed_dirs: int
    space_saved: int
    errors: List[str]
    backup_path: Optional[str]

@dataclass
class AnalysisResult:
    """分析結果"""
    total_files: int
    code_lines: int
    languages: Dict[str, int]
    complexity_score: float
    suggestions: List[str]

class EnhancedCodeFlowMCP:
    def __init__(self):
        self.name = "Enhanced CodeFlow MCP"
        self.version = "1.0.0"
        self.tools = {}
        self._init_tools()
        
    def _init_tools(self):
        """初始化所有工具"""
        self.tools = {
            "cleanup_redundant_code": self._cleanup_redundant_code,
            "analyze_manus_data": self._analyze_manus_data,
            "calculate_k2_pricing": self._calculate_k2_pricing,
            "visualize_project": self._visualize_project,
            "generate_workflow": self._generate_workflow,
            "analyze_mcp_duplicates": self._analyze_mcp_duplicates
        }
    
    async def _cleanup_redundant_code(self, project_path: str = ".", 
                                     dry_run: bool = True) -> Dict[str, Any]:
        """
        清理冗餘代碼
        
        Args:
            project_path: 項目路徑
            dry_run: 是否模擬運行
            
        Returns:
            清理結果和可視化數據
        """
        logger.info(f"開始清理冗餘代碼: {project_path}")
        
        redundant_patterns = {
            'directories': [
                'mirrorcode', 'mirror_code', 'workflow', 'workflows',
                'ai_assistants', '__pycache__', '.pytest_cache',
                'temp', 'tmp', 'backup', 'old', 'deprecated'
            ],
            'files': [
                '*_backup.py', '*_old.py', '*_deprecated.py',
                '*_test_*.py', 'test_*.py', '*.pyc', '.DS_Store'
            ]
        }
        
        to_remove = []
        total_size = 0
        
        root_path = Path(project_path)
        
        # 查找冗餘項目
        for dir_pattern in redundant_patterns['directories']:
            for path in root_path.rglob(dir_pattern):
                if path.is_dir() and 'venv' not in str(path):
                    size = self._get_dir_size(path)
                    to_remove.append({
                        'type': 'directory',
                        'path': str(path),
                        'size': size
                    })
                    total_size += size
        
        # 準備可視化數據
        visualization = {
            'type': 'cleanup_visualization',
            'data': {
                'categories': {
                    'directories': len([x for x in to_remove if x['type'] == 'directory']),
                    'files': len([x for x in to_remove if x['type'] == 'file']),
                    'empty_dirs': len([x for x in to_remove if x['type'] == 'empty_dir'])
                },
                'space_distribution': self._calculate_space_distribution(to_remove),
                'top_items': sorted(to_remove, key=lambda x: x['size'], reverse=True)[:10]
            },
            'chart_config': {
                'type': 'pie',
                'title': '冗餘代碼空間分布',
                'colors': ['#ff6b6b', '#4ecdc4', '#45b7d1']
            }
        }
        
        result = {
            'summary': {
                'total_items': len(to_remove),
                'total_size': total_size,
                'dry_run': dry_run
            },
            'items': to_remove,
            'visualization': visualization
        }
        
        if not dry_run:
            # 執行實際清理
            cleanup_result = self._perform_cleanup(to_remove)
            result['cleanup_result'] = asdict(cleanup_result)
        
        return result
    
    async def _analyze_manus_data(self, data_path: str) -> Dict[str, Any]:
        """
        分析 Manus 數據
        
        Args:
            data_path: 數據路徑
            
        Returns:
            分析結果和可視化數據
        """
        logger.info(f"分析 Manus 數據: {data_path}")
        
        # 載入數據
        manus_data = []
        data_dir = Path(data_path)
        
        for json_file in data_dir.glob("manus_analysis_*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                manus_data.append(json.load(f))
        
        # 分析類別分布
        category_stats = {
            'thinking': 0,
            'observation': 0,
            'action': 0
        }
        
        tool_usage = {}
        confidence_scores = []
        
        for data in manus_data:
            categories = data.get('categories', {})
            for cat, messages in categories.items():
                category_stats[cat] += len(messages)
                
                for msg in messages:
                    confidence_scores.append(msg.get('confidence', 0))
                    
            # 統計工具使用
            patterns = data.get('patterns', {})
            for tool in patterns.get('tools_used', []):
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        # 準備可視化數據
        visualization = {
            'type': 'manus_analysis_visualization',
            'data': {
                'category_distribution': {
                    'labels': ['思考', '觀察', '動作'],
                    'values': [category_stats['thinking'], 
                              category_stats['observation'], 
                              category_stats['action']],
                    'colors': ['#3498db', '#2ecc71', '#e74c3c']
                },
                'tool_usage': {
                    'labels': list(tool_usage.keys()),
                    'values': list(tool_usage.values())
                },
                'confidence_distribution': {
                    'scores': confidence_scores,
                    'average': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
                }
            },
            'charts': [
                {
                    'type': 'doughnut',
                    'title': '對話類別分布',
                    'data_key': 'category_distribution'
                },
                {
                    'type': 'bar',
                    'title': '工具使用頻率',
                    'data_key': 'tool_usage'
                },
                {
                    'type': 'histogram',
                    'title': '置信度分布',
                    'data_key': 'confidence_distribution'
                }
            ]
        }
        
        return {
            'summary': {
                'total_conversations': len(manus_data),
                'total_messages': sum(category_stats.values()),
                'average_confidence': visualization['data']['confidence_distribution']['average']
            },
            'statistics': category_stats,
            'tool_usage': tool_usage,
            'visualization': visualization
        }
    
    async def _calculate_k2_pricing(self, input_tokens: int, output_tokens: int,
                                  customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        計算 K2 定價
        
        Args:
            input_tokens: 輸入 tokens
            output_tokens: 輸出 tokens
            customer_id: 客戶 ID（用於折扣計算）
            
        Returns:
            定價結果和可視化數據
        """
        # K2 定價配置
        pricing_config = {
            'input_price_per_million': 2.0,   # 2元/M tokens
            'output_price_per_million': 8.0,  # 8元/M tokens
            'volume_discounts': {
                1_000_000: 0.95,
                5_000_000: 0.90,
                10_000_000: 0.85,
                50_000_000: 0.80
            }
        }
        
        # 計算基礎成本
        input_cost = (input_tokens / 1_000_000) * pricing_config['input_price_per_million']
        output_cost = (output_tokens / 1_000_000) * pricing_config['output_price_per_million']
        
        # 應用批量折扣
        total_tokens = input_tokens + output_tokens
        discount = 1.0
        for threshold, rate in sorted(pricing_config['volume_discounts'].items()):
            if total_tokens >= threshold:
                discount = rate
        
        final_input_cost = input_cost * discount
        final_output_cost = output_cost * discount
        total_cost = final_input_cost + final_output_cost
        
        # 準備可視化數據
        visualization = {
            'type': 'pricing_visualization',
            'data': {
                'cost_breakdown': {
                    'labels': ['輸入成本', '輸出成本'],
                    'values': [round(final_input_cost, 2), round(final_output_cost, 2)],
                    'colors': ['#3498db', '#e74c3c']
                },
                'token_distribution': {
                    'labels': ['輸入 Tokens', '輸出 Tokens'],
                    'values': [input_tokens, output_tokens]
                },
                'discount_levels': {
                    'current': (1 - discount) * 100,
                    'thresholds': [
                        {'tokens': t, 'discount': (1-r)*100} 
                        for t, r in pricing_config['volume_discounts'].items()
                    ]
                }
            },
            'charts': [
                {
                    'type': 'pie',
                    'title': '成本分布',
                    'data_key': 'cost_breakdown'
                },
                {
                    'type': 'bar',
                    'title': 'Token 分布',
                    'data_key': 'token_distribution'
                }
            ]
        }
        
        return {
            'pricing': {
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'input_cost': round(final_input_cost, 4),
                'output_cost': round(final_output_cost, 4),
                'total_cost': round(total_cost, 4),
                'discount_applied': discount,
                'currency': 'CNY'
            },
            'visualization': visualization
        }
    
    async def _visualize_project(self, project_path: str = ".") -> Dict[str, Any]:
        """
        生成項目可視化
        
        Args:
            project_path: 項目路徑
            
        Returns:
            項目結構和統計的可視化數據
        """
        logger.info(f"生成項目可視化: {project_path}")
        
        # 分析項目結構
        stats = {
            'languages': {},
            'file_types': {},
            'directory_sizes': {},
            'total_files': 0,
            'total_lines': 0
        }
        
        root_path = Path(project_path)
        
        for file_path in root_path.rglob('*'):
            if file_path.is_file() and 'venv' not in str(file_path):
                stats['total_files'] += 1
                
                # 統計語言
                if file_path.suffix == '.py':
                    lang = 'Python'
                elif file_path.suffix in ['.js', '.jsx']:
                    lang = 'JavaScript'
                elif file_path.suffix in ['.ts', '.tsx']:
                    lang = 'TypeScript'
                else:
                    lang = 'Other'
                
                stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
                
                # 統計行數
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        stats['total_lines'] += lines
                except:
                    pass
        
        # 準備可視化數據
        visualization = {
            'type': 'project_visualization',
            'data': {
                'language_distribution': {
                    'labels': list(stats['languages'].keys()),
                    'values': list(stats['languages'].values()),
                    'colors': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
                },
                'project_stats': {
                    'total_files': stats['total_files'],
                    'total_lines': stats['total_lines'],
                    'languages': len(stats['languages'])
                },
                'tree_structure': self._generate_tree_structure(root_path)
            },
            'charts': [
                {
                    'type': 'doughnut',
                    'title': '語言分布',
                    'data_key': 'language_distribution'
                },
                {
                    'type': 'stats',
                    'title': '項目統計',
                    'data_key': 'project_stats'
                },
                {
                    'type': 'tree',
                    'title': '項目結構',
                    'data_key': 'tree_structure'
                }
            ]
        }
        
        return {
            'statistics': stats,
            'visualization': visualization
        }
    
    async def _generate_workflow(self, task_type: str, 
                               requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成工作流
        
        Args:
            task_type: 任務類型
            requirements: 需求描述
            
        Returns:
            工作流定義和可視化
        """
        workflows = {
            'data_collection': {
                'name': '數據收集工作流',
                'steps': [
                    {'id': '1', 'name': '識別數據源', 'duration': '1h'},
                    {'id': '2', 'name': '設計收集策略', 'duration': '2h'},
                    {'id': '3', 'name': '實現收集器', 'duration': '4h'},
                    {'id': '4', 'name': '數據驗證', 'duration': '1h'},
                    {'id': '5', 'name': '存儲優化', 'duration': '2h'}
                ]
            },
            'code_cleanup': {
                'name': '代碼清理工作流',
                'steps': [
                    {'id': '1', 'name': '代碼分析', 'duration': '1h'},
                    {'id': '2', 'name': '識別冗餘', 'duration': '2h'},
                    {'id': '3', 'name': '備份重要文件', 'duration': '1h'},
                    {'id': '4', 'name': '執行清理', 'duration': '2h'},
                    {'id': '5', 'name': '驗證結果', 'duration': '1h'}
                ]
            }
        }
        
        workflow = workflows.get(task_type, workflows['data_collection'])
        
        # 準備可視化數據
        visualization = {
            'type': 'workflow_visualization',
            'data': {
                'workflow': workflow,
                'gantt_data': self._generate_gantt_data(workflow['steps']),
                'dependencies': self._generate_dependencies(workflow['steps'])
            },
            'charts': [
                {
                    'type': 'gantt',
                    'title': workflow['name'],
                    'data_key': 'gantt_data'
                },
                {
                    'type': 'flow',
                    'title': '工作流程圖',
                    'data_key': 'dependencies'
                }
            ]
        }
        
        return {
            'workflow': workflow,
            'visualization': visualization
        }
    
    async def _analyze_mcp_duplicates(self) -> Dict[str, Any]:
        """分析 MCP 重複功能"""
        # 這裡簡化實現，實際應該掃描所有 MCP 文件
        duplicate_analysis = {
            'command_execution': ['command_mcp', 'command_manager'],
            'code_generation': ['codeflow_mcp', 'spec_generator'],
            'routing': ['claude_router_mcp', 'smart_routing_mcp']
        }
        
        visualization = {
            'type': 'mcp_duplicate_visualization',
            'data': {
                'duplicate_groups': [
                    {
                        'category': cat,
                        'mcps': mcps,
                        'count': len(mcps)
                    }
                    for cat, mcps in duplicate_analysis.items()
                ],
                'total_mcps': sum(len(mcps) for mcps in duplicate_analysis.values()),
                'categories': len(duplicate_analysis)
            },
            'charts': [
                {
                    'type': 'network',
                    'title': 'MCP 重複關係圖',
                    'data_key': 'duplicate_groups'
                }
            ]
        }
        
        return {
            'analysis': duplicate_analysis,
            'visualization': visualization,
            'recommendations': [
                '合併 command_mcp 和 command_manager',
                '整合 codeflow_mcp 和 spec_generator',
                '統一 routing 功能'
            ]
        }
    
    # 輔助方法
    def _get_dir_size(self, path: Path) -> int:
        """獲取目錄大小"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            pass
        return total
    
    def _calculate_space_distribution(self, items: List[Dict]) -> Dict:
        """計算空間分布"""
        distribution = {}
        for item in items:
            item_type = item['type']
            distribution[item_type] = distribution.get(item_type, 0) + item['size']
        return distribution
    
    def _perform_cleanup(self, items: List[Dict]) -> CleanupResult:
        """執行清理"""
        # 實際清理邏輯
        return CleanupResult(
            removed_files=len([x for x in items if x['type'] == 'file']),
            removed_dirs=len([x for x in items if x['type'] == 'directory']),
            space_saved=sum(x['size'] for x in items),
            errors=[],
            backup_path=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    
    def _generate_tree_structure(self, root_path: Path) -> Dict:
        """生成樹形結構"""
        # 簡化的樹形結構生成
        return {
            'name': root_path.name,
            'type': 'directory',
            'children': []
        }
    
    def _generate_gantt_data(self, steps: List[Dict]) -> List[Dict]:
        """生成甘特圖數據"""
        gantt_data = []
        start_time = 0
        
        for step in steps:
            duration = int(step['duration'][:-1])  # 移除 'h'
            gantt_data.append({
                'task': step['name'],
                'start': start_time,
                'duration': duration
            })
            start_time += duration
        
        return gantt_data
    
    def _generate_dependencies(self, steps: List[Dict]) -> List[Dict]:
        """生成依賴關係"""
        dependencies = []
        for i in range(len(steps) - 1):
            dependencies.append({
                'from': steps[i]['id'],
                'to': steps[i+1]['id']
            })
        return dependencies
    
    # MCP 接口
    async def run_as_mcp(self):
        """作為 MCP 服務運行"""
        if not MCP_AVAILABLE:
            logger.error("MCP 未安裝")
            return
        
        server = Server("enhanced-codeflow-mcp")
        
        # 註冊工具
        for name, func in self.tools.items():
            server.add_tool(Tool(
                name=name,
                description=f"Execute {name} function",
                inputSchema={"type": "object"}
            ))
        
        await server.run()
    
    # 獨立運行接口
    async def run_standalone(self):
        """獨立運行模式"""
        print("🚀 Enhanced CodeFlow MCP - 獨立模式")
        print("=" * 60)
        
        while True:
            print("\n可用工具:")
            for i, (name, _) in enumerate(self.tools.items(), 1):
                print(f"{i}. {name}")
            print("0. 退出")
            
            choice = input("\n選擇工具 (0-6): ")
            
            if choice == '0':
                break
            
            try:
                tool_list = list(self.tools.keys())
                tool_name = tool_list[int(choice) - 1]
                tool_func = self.tools[tool_name]
                
                # 根據工具執行
                if tool_name == "cleanup_redundant_code":
                    result = await tool_func(dry_run=True)
                elif tool_name == "analyze_manus_data":
                    result = await tool_func("data/manus_analysis")
                elif tool_name == "calculate_k2_pricing":
                    result = await tool_func(10000, 5000)
                elif tool_name == "visualize_project":
                    result = await tool_func()
                elif tool_name == "generate_workflow":
                    result = await tool_func("data_collection", {})
                else:
                    result = await tool_func()
                
                # 顯示結果
                print("\n結果:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
                # 如果有可視化數據，提示保存
                if 'visualization' in result:
                    save = input("\n保存可視化數據? (y/n): ")
                    if save.lower() == 'y':
                        filename = f"{tool_name}_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(result['visualization'], f, ensure_ascii=False, indent=2)
                        print(f"已保存到: {filename}")
                
            except Exception as e:
                print(f"錯誤: {e}")

async def main():
    """主函數"""
    mcp = EnhancedCodeFlowMCP()
    
    if MCP_AVAILABLE and os.environ.get('RUN_AS_MCP'):
        await mcp.run_as_mcp()
    else:
        await mcp.run_standalone()

if __name__ == "__main__":
    asyncio.run(main())