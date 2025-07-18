#!/usr/bin/env python3
"""
分析 MCP 組件之間的依賴關係
生成依賴關係圖和優化建議
"""

import os
import re
import json
import ast
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import graphviz

class MCPDependencyAnalyzer:
    """MCP 依賴關係分析器"""
    
    def __init__(self, components_dir: str):
        self.components_dir = components_dir
        self.dependencies = defaultdict(set)
        self.mcp_info = {}
        self.import_patterns = [
            r'from\s+\.\.components\.(\w+)\s+import',
            r'from\s+core\.components\.(\w+)\s+import',
            r'import\s+.*\.components\.(\w+)',
            r'self\.mcp_manager\.get_component\(["\'](\w+)["\']\)',
            r'self\.components\[["\'](\w+)["\']\]'
        ]
        
    def analyze_all_dependencies(self) -> Dict[str, Any]:
        """分析所有 MCP 的依賴關係"""
        print("🔍 分析 MCP 依賴關係...")
        
        # 1. 掃描所有 MCP 文件
        mcp_files = self._scan_mcp_files()
        
        # 2. 分析每個文件的依賴
        for mcp_file in mcp_files:
            self._analyze_file_dependencies(mcp_file)
            
        # 3. 生成依賴統計
        dependency_stats = self._generate_dependency_stats()
        
        # 4. 識別循環依賴
        circular_deps = self._find_circular_dependencies()
        
        # 5. 生成依賴層級
        dependency_layers = self._generate_dependency_layers()
        
        # 6. 生成優化建議
        optimization_suggestions = self._generate_optimization_suggestions()
        
        return {
            "mcp_count": len(self.mcp_info),
            "dependencies": dict(self.dependencies),
            "dependency_stats": dependency_stats,
            "circular_dependencies": circular_deps,
            "dependency_layers": dependency_layers,
            "optimization_suggestions": optimization_suggestions
        }
    
    def _scan_mcp_files(self) -> List[str]:
        """掃描所有 MCP 文件"""
        mcp_files = []
        
        if os.path.exists(self.components_dir):
            for file in os.listdir(self.components_dir):
                if file.endswith("_mcp.py") and not file.endswith("_backup.py"):
                    mcp_files.append(os.path.join(self.components_dir, file))
                    mcp_name = file.replace(".py", "")
                    self.mcp_info[mcp_name] = {
                        "file": file,
                        "path": os.path.join(self.components_dir, file),
                        "dependencies": set(),
                        "dependents": set()
                    }
                    
        print(f"✅ 發現 {len(mcp_files)} 個 MCP 組件")
        return mcp_files
    
    def _analyze_file_dependencies(self, file_path: str):
        """分析單個文件的依賴"""
        mcp_name = os.path.basename(file_path).replace(".py", "")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 使用正則表達式查找依賴
            for pattern in self.import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    dep_mcp = match if match.endswith("_mcp") else f"{match}_mcp"
                    if dep_mcp != mcp_name and dep_mcp in self.mcp_info:
                        self.dependencies[mcp_name].add(dep_mcp)
                        self.mcp_info[mcp_name]["dependencies"].add(dep_mcp)
                        self.mcp_info[dep_mcp]["dependents"].add(mcp_name)
                        
        except Exception as e:
            print(f"⚠️ 分析 {file_path} 時出錯: {str(e)}")
    
    def _generate_dependency_stats(self) -> Dict[str, Any]:
        """生成依賴統計"""
        stats = {
            "most_depended_on": [],
            "most_dependencies": [],
            "isolated_components": [],
            "dependency_depth": {}
        }
        
        # 統計被依賴次數
        depended_counts = [(mcp, len(info["dependents"])) 
                          for mcp, info in self.mcp_info.items()]
        depended_counts.sort(key=lambda x: x[1], reverse=True)
        stats["most_depended_on"] = depended_counts[:5]
        
        # 統計依賴數量
        dependency_counts = [(mcp, len(info["dependencies"])) 
                            for mcp, info in self.mcp_info.items()]
        dependency_counts.sort(key=lambda x: x[1], reverse=True)
        stats["most_dependencies"] = dependency_counts[:5]
        
        # 找出孤立組件
        stats["isolated_components"] = [
            mcp for mcp, info in self.mcp_info.items()
            if len(info["dependencies"]) == 0 and len(info["dependents"]) == 0
        ]
        
        return stats
    
    def _find_circular_dependencies(self) -> List[List[str]]:
        """查找循環依賴"""
        circular_deps = []
        visited = set()
        
        def dfs(node: str, path: List[str], in_stack: Set[str]):
            if node in in_stack:
                # 找到循環
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                circular_deps.append(cycle)
                return
                
            if node in visited:
                return
                
            visited.add(node)
            in_stack.add(node)
            
            for dep in self.dependencies.get(node, []):
                dfs(dep, path + [node], in_stack)
                
            in_stack.remove(node)
        
        for mcp in self.mcp_info:
            if mcp not in visited:
                dfs(mcp, [], set())
                
        return circular_deps
    
    def _generate_dependency_layers(self) -> List[List[str]]:
        """生成依賴層級（拓撲排序）"""
        # 計算每個節點的入度
        in_degree = {mcp: len(info["dependencies"]) 
                    for mcp, info in self.mcp_info.items()}
        
        # 使用 Kahn's 算法進行拓撲排序
        layers = []
        queue = [mcp for mcp, degree in in_degree.items() if degree == 0]
        
        while queue:
            current_layer = []
            next_queue = []
            
            for mcp in queue:
                current_layer.append(mcp)
                
                # 更新依賴它的節點的入度
                for dependent in self.mcp_info[mcp]["dependents"]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_queue.append(dependent)
                        
            layers.append(current_layer)
            queue = next_queue
            
        return layers
    
    def _generate_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """生成優化建議"""
        suggestions = []
        
        # 1. 建議解耦高依賴組件
        for mcp, count in self._generate_dependency_stats()["most_dependencies"]:
            if count > 5:
                suggestions.append({
                    "type": "high_coupling",
                    "component": mcp,
                    "issue": f"{mcp} 依賴了 {count} 個其他組件",
                    "suggestion": "考慮引入接口或事件系統來降低耦合度"
                })
        
        # 2. 建議提取公共依賴
        for mcp, count in self._generate_dependency_stats()["most_depended_on"]:
            if count > 5:
                suggestions.append({
                    "type": "common_dependency",
                    "component": mcp,
                    "issue": f"{mcp} 被 {count} 個組件依賴",
                    "suggestion": "確保這是一個穩定的核心組件，避免頻繁修改"
                })
        
        # 3. 建議處理循環依賴
        for cycle in self._find_circular_dependencies():
            suggestions.append({
                "type": "circular_dependency",
                "components": cycle,
                "issue": f"發現循環依賴: {' -> '.join(cycle)}",
                "suggestion": "引入中介者模式或事件總線來打破循環"
            })
        
        # 4. 建議處理孤立組件
        for mcp in self._generate_dependency_stats()["isolated_components"]:
            suggestions.append({
                "type": "isolated_component",
                "component": mcp,
                "issue": f"{mcp} 沒有任何依賴關係",
                "suggestion": "考慮是否可以移除或整合到其他組件"
            })
            
        return suggestions
    
    def generate_dependency_graph(self, output_file: str = "mcp_dependencies"):
        """生成依賴關係圖"""
        print("\n📊 生成依賴關係圖...")
        
        # 創建有向圖
        dot = graphviz.Digraph(comment='MCP Dependencies')
        dot.attr(rankdir='TB')
        
        # 定義節點樣式
        node_styles = {
            "P0": {"color": "red", "style": "filled", "fillcolor": "lightpink"},
            "P1": {"color": "orange", "style": "filled", "fillcolor": "lightyellow"},
            "P2": {"color": "green", "style": "filled", "fillcolor": "lightgreen"},
            "P3": {"color": "gray", "style": "filled", "fillcolor": "lightgray"}
        }
        
        # 根據優先級分類 MCP
        priority_map = self._get_mcp_priority_map()
        
        # 添加節點
        for mcp in self.mcp_info:
            priority = priority_map.get(mcp, "P3")
            style = node_styles.get(priority, node_styles["P3"])
            
            # 添加依賴統計信息
            deps_count = len(self.mcp_info[mcp]["dependencies"])
            dependents_count = len(self.mcp_info[mcp]["dependents"])
            label = f"{mcp}\n↓{deps_count} ↑{dependents_count}"
            
            dot.node(mcp, label=label, **style)
        
        # 添加邊
        for mcp, deps in self.dependencies.items():
            for dep in deps:
                dot.edge(mcp, dep)
        
        # 生成圖形
        try:
            dot.render(output_file, format='png', cleanup=True)
            print(f"✅ 依賴關係圖已生成: {output_file}.png")
        except Exception as e:
            print(f"⚠️ 生成圖形時出錯: {str(e)}")
            print("   請確保已安裝 graphviz: pip install graphviz")
    
    def _get_mcp_priority_map(self) -> Dict[str, str]:
        """獲取 MCP 優先級映射"""
        return {
            # P0 - 核心必需
            "memoryos_mcp": "P0",
            "enhanced_command_mcp": "P0",
            "mcp_coordinator_mcp": "P0",
            "claude_router_mcp": "P0",
            "local_adapter_mcp": "P0",
            "command_mcp": "P0",
            "smartui_mcp": "P0",
            "ag_ui_mcp": "P0",
            
            # P1 - 工作流必需
            "codeflow_mcp": "P1",
            "test_mcp": "P1",
            "zen_mcp": "P1",
            "xmasters_mcp": "P1",
            "stagewise_mcp": "P1",
            
            # P2 - 支撐功能
            "monitoring_mcp": "P2",
            "config_mcp": "P2",
            "security_mcp": "P2",
            "collaboration_mcp": "P2",
            "operations_mcp": "P2",
            
            # P3 - 可選（其他都是 P3）
        }
    
    def generate_report(self, analysis_results: Dict[str, Any]) -> str:
        """生成分析報告"""
        report = f"""
# MCP 依賴關係分析報告

## 📊 總體統計
- MCP 組件總數: {analysis_results['mcp_count']}
- 總依賴關係數: {sum(len(deps) for deps in analysis_results['dependencies'].values())}
- 循環依賴數: {len(analysis_results['circular_dependencies'])}
- 孤立組件數: {len(analysis_results['dependency_stats']['isolated_components'])}

## 🔝 最受依賴的組件
{self._format_top_list(analysis_results['dependency_stats']['most_depended_on'])}

## 📦 依賴最多的組件
{self._format_top_list(analysis_results['dependency_stats']['most_dependencies'])}

## ⚠️ 循環依賴
{self._format_circular_deps(analysis_results['circular_dependencies'])}

## 📊 依賴層級
{self._format_dependency_layers(analysis_results['dependency_layers'])}

## 💡 優化建議
{self._format_suggestions(analysis_results['optimization_suggestions'])}

## 🎯 行動計劃
1. **立即修復**
   - 解決所有循環依賴問題
   - 評估並處理孤立組件

2. **短期優化**
   - 降低高耦合組件的依賴數
   - 穩定核心被依賴組件的接口

3. **長期改進**
   - 引入依賴注入框架
   - 實現事件驅動架構
   - 建立組件接口規範
"""
        return report
    
    def _format_top_list(self, items: List[Tuple[str, int]]) -> str:
        """格式化排行榜"""
        if not items:
            return "無"
        return "\n".join([f"{i+1}. {mcp}: {count} 個" 
                         for i, (mcp, count) in enumerate(items)])
    
    def _format_circular_deps(self, circular_deps: List[List[str]]) -> str:
        """格式化循環依賴"""
        if not circular_deps:
            return "✅ 未發現循環依賴"
        return "\n".join([f"- {' → '.join(cycle)}" for cycle in circular_deps])
    
    def _format_dependency_layers(self, layers: List[List[str]]) -> str:
        """格式化依賴層級"""
        formatted = []
        for i, layer in enumerate(layers):
            formatted.append(f"### Layer {i} (基礎層)")
            formatted.extend([f"- {mcp}" for mcp in layer])
            formatted.append("")
        return "\n".join(formatted)
    
    def _format_suggestions(self, suggestions: List[Dict[str, Any]]) -> str:
        """格式化優化建議"""
        formatted = []
        for i, suggestion in enumerate(suggestions, 1):
            formatted.append(f"{i}. **{suggestion['type'].replace('_', ' ').title()}**")
            formatted.append(f"   - 問題: {suggestion['issue']}")
            formatted.append(f"   - 建議: {suggestion['suggestion']}")
            formatted.append("")
        return "\n".join(formatted)

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="分析 MCP 組件依賴關係")
    parser.add_argument("--components-dir", type=str, 
                       default="core/components",
                       help="MCP 組件目錄")
    parser.add_argument("--output-graph", action="store_true",
                       help="生成依賴關係圖")
    parser.add_argument("--output-report", type=str,
                       default="mcp_dependency_report.md",
                       help="輸出報告文件名")
    
    args = parser.parse_args()
    
    # 創建分析器
    analyzer = MCPDependencyAnalyzer(args.components_dir)
    
    # 執行分析
    results = analyzer.analyze_all_dependencies()
    
    # 生成報告
    report = analyzer.generate_report(results)
    print(report)
    
    # 保存報告
    with open(args.output_report, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ 報告已保存到: {args.output_report}")
    
    # 生成依賴關係圖
    if args.output_graph:
        analyzer.generate_dependency_graph()
    
    # 保存詳細分析結果
    with open("mcp_dependency_analysis.json", 'w', encoding='utf-8') as f:
        # 轉換 set 為 list 以便 JSON 序列化
        json_safe_results = {
            "mcp_count": results["mcp_count"],
            "dependencies": {k: list(v) for k, v in results["dependencies"].items()},
            "dependency_stats": results["dependency_stats"],
            "circular_dependencies": results["circular_dependencies"],
            "dependency_layers": results["dependency_layers"],
            "optimization_suggestions": results["optimization_suggestions"]
        }
        json.dump(json_safe_results, f, indent=2, ensure_ascii=False)
    print("✅ 詳細分析結果已保存到: mcp_dependency_analysis.json")

if __name__ == "__main__":
    main()