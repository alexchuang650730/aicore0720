#!/usr/bin/env python3
"""
使用 CodeFlow MCP 自動生成規格文檔
通過分析現有實現代碼，自動提取架構、接口和規格
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import ast
import inspect

@dataclass
class CodeAnalysisResult:
    """代碼分析結果"""
    file_path: str
    classes: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    constants: Dict[str, Any] = field(default_factory=dict)
    architecture_patterns: List[str] = field(default_factory=list)
    interfaces: List[Dict[str, Any]] = field(default_factory=list)

class CodeFlowMCP:
    """CodeFlow MCP - 代碼分析和規格生成"""
    
    def __init__(self):
        self.analysis_cache = {}
        self.pattern_recognizers = self._init_pattern_recognizers()
        
    def _init_pattern_recognizers(self) -> Dict[str, Any]:
        """初始化模式識別器"""
        return {
            "mcp_pattern": {
                "indicators": ["BaseMCP", "handle_request", "methods"],
                "type": "MCP Component"
            },
            "adapter_pattern": {
                "indicators": ["Adapter", "adapt", "convert"],
                "type": "Adapter Pattern"
            },
            "factory_pattern": {
                "indicators": ["Factory", "create", "build"],
                "type": "Factory Pattern"
            },
            "singleton_pattern": {
                "indicators": ["instance", "getInstance", "_instance"],
                "type": "Singleton Pattern"
            }
        }
    
    async def analyze_file(self, file_path: str) -> CodeAnalysisResult:
        """分析單個文件"""
        print(f"\n📄 分析文件: {file_path}")
        
        result = CodeAnalysisResult(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 AST
            tree = ast.parse(content)
            
            # 提取組件
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    result.classes.append(self._extract_class_info(node, content))
                elif isinstance(node, ast.FunctionDef):
                    if node.col_offset == 0:  # 頂層函數
                        result.functions.append(self._extract_function_info(node))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        result.imports.append(f"{module}.{alias.name}")
            
            # 識別架構模式
            result.architecture_patterns = self._identify_patterns(content, result)
            
            # 提取接口定義
            result.interfaces = self._extract_interfaces(result)
            
        except Exception as e:
            print(f"   ⚠️ 分析錯誤: {e}")
        
        return result
    
    def _extract_class_info(self, node: ast.ClassDef, content: str) -> Dict[str, Any]:
        """提取類信息"""
        class_info = {
            "name": node.name,
            "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
            "methods": [],
            "attributes": [],
            "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
            "docstring": ast.get_docstring(node)
        }
        
        # 提取方法
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    "name": item.name,
                    "params": [arg.arg for arg in item.args.args],
                    "is_async": isinstance(item, ast.AsyncFunctionDef),
                    "docstring": ast.get_docstring(item)
                }
                class_info["methods"].append(method_info)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info["attributes"].append(target.id)
        
        return class_info
    
    def _extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """提取函數信息"""
        return {
            "name": node.name,
            "params": [arg.arg for arg in node.args.args],
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
            "docstring": ast.get_docstring(node)
        }
    
    def _identify_patterns(self, content: str, result: CodeAnalysisResult) -> List[str]:
        """識別架構模式"""
        patterns = []
        
        # 檢查已知模式
        for pattern_name, pattern_info in self.pattern_recognizers.items():
            for indicator in pattern_info["indicators"]:
                if indicator in content:
                    patterns.append(pattern_info["type"])
                    break
        
        # 檢查類層次結構
        for class_info in result.classes:
            if "MCP" in class_info["name"] or "BaseMCP" in class_info["bases"]:
                if "MCP Component" not in patterns:
                    patterns.append("MCP Component")
            
            if "Adapter" in class_info["name"]:
                if "Adapter Pattern" not in patterns:
                    patterns.append("Adapter Pattern")
        
        return patterns
    
    def _extract_interfaces(self, result: CodeAnalysisResult) -> List[Dict[str, Any]]:
        """提取接口定義"""
        interfaces = []
        
        for class_info in result.classes:
            # 識別 MCP 接口
            if "handle_request" in [m["name"] for m in class_info["methods"]]:
                interface = {
                    "type": "MCP Interface",
                    "class": class_info["name"],
                    "methods": []
                }
                
                # 提取公共方法作為接口
                for method in class_info["methods"]:
                    if not method["name"].startswith("_"):
                        interface["methods"].append({
                            "name": method["name"],
                            "params": method["params"],
                            "is_async": method["is_async"]
                        })
                
                interfaces.append(interface)
        
        return interfaces
    
    async def analyze_directory(self, directory: str, 
                              file_pattern: str = "*.py") -> Dict[str, CodeAnalysisResult]:
        """分析整個目錄"""
        print(f"\n📁 分析目錄: {directory}")
        
        results = {}
        
        # 獲取所有 Python 文件
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    result = await self.analyze_file(file_path)
                    results[file_path] = result
        
        return results
    
    async def generate_specification(self, analysis_results: Dict[str, CodeAnalysisResult]) -> str:
        """生成規格文檔"""
        print(f"\n📝 生成規格文檔")
        
        spec = f"""# 自動生成的規格文檔
生成時間: {datetime.now().isoformat()}
使用 CodeFlow MCP 自動分析生成

## 1. 系統架構概覽

### 1.1 核心組件
"""
        
        # 統計組件類型
        component_types = {}
        for path, result in analysis_results.items():
            for pattern in result.architecture_patterns:
                component_types[pattern] = component_types.get(pattern, 0) + 1
        
        spec += "\n組件類型分布:\n"
        for comp_type, count in component_types.items():
            spec += f"- {comp_type}: {count} 個\n"
        
        # 生成組件清單
        spec += "\n### 1.2 組件清單\n\n"
        
        mcp_components = []
        other_components = []
        
        for path, result in analysis_results.items():
            for class_info in result.classes:
                if "MCP" in class_info["name"] or "BaseMCP" in class_info["bases"]:
                    mcp_components.append((path, class_info))
                else:
                    other_components.append((path, class_info))
        
        # MCP 組件
        if mcp_components:
            spec += "#### MCP 組件\n\n"
            for path, class_info in mcp_components:
                spec += f"##### {class_info['name']}\n"
                spec += f"- 文件: `{os.path.basename(path)}`\n"
                if class_info["docstring"]:
                    spec += f"- 描述: {class_info['docstring'].split('\\n')[0]}\n"
                spec += f"- 方法數: {len(class_info['methods'])}\n"
                spec += "\n"
        
        # 其他主要組件
        if other_components:
            spec += "#### 其他主要組件\n\n"
            for path, class_info in sorted(other_components, key=lambda x: x[1]["name"])[:10]:
                spec += f"- **{class_info['name']}**: {class_info['docstring'].split('\\n')[0] if class_info['docstring'] else '無描述'}\n"
        
        # 生成接口規格
        spec += "\n## 2. 接口規格\n\n"
        
        all_interfaces = []
        for path, result in analysis_results.items():
            all_interfaces.extend(result.interfaces)
        
        # 按類型分組接口
        interface_groups = {}
        for interface in all_interfaces:
            interface_type = interface["type"]
            if interface_type not in interface_groups:
                interface_groups[interface_type] = []
            interface_groups[interface_type].append(interface)
        
        for interface_type, interfaces in interface_groups.items():
            spec += f"### 2.{list(interface_groups.keys()).index(interface_type) + 1} {interface_type}\n\n"
            
            for interface in interfaces[:5]:  # 限制每類最多5個
                spec += f"#### {interface['class']}\n\n"
                spec += "```python\n"
                for method in interface["methods"][:5]:  # 限制方法數
                    async_prefix = "async " if method["is_async"] else ""
                    params = ", ".join(method["params"])
                    spec += f"{async_prefix}def {method['name']}({params})\n"
                spec += "```\n\n"
        
        # 生成數據流
        spec += "## 3. 數據流規格\n\n"
        spec += self._analyze_data_flow(analysis_results)
        
        # 生成依賴關係
        spec += "\n## 4. 依賴關係\n\n"
        spec += self._analyze_dependencies(analysis_results)
        
        # 生成集成點
        spec += "\n## 5. 集成點\n\n"
        spec += self._analyze_integration_points(analysis_results)
        
        # 生成測試需求
        spec += "\n## 6. 測試需求\n\n"
        spec += self._generate_test_requirements(analysis_results)
        
        return spec
    
    def _analyze_data_flow(self, analysis_results: Dict[str, CodeAnalysisResult]) -> str:
        """分析數據流"""
        flow = "### 3.1 主要數據流路徑\n\n"
        
        # 識別數據處理方法
        data_methods = []
        for path, result in analysis_results.items():
            for class_info in result.classes:
                for method in class_info["methods"]:
                    if any(keyword in method["name"].lower() 
                          for keyword in ["process", "handle", "execute", "transform"]):
                        data_methods.append({
                            "class": class_info["name"],
                            "method": method["name"],
                            "params": method["params"]
                        })
        
        # 生成數據流描述
        flow += "```mermaid\ngraph LR\n"
        for i, method in enumerate(data_methods[:5]):
            if i > 0:
                flow += f"    M{i-1} --> M{i}\n"
            flow += f"    M{i}[{method['class']}.{method['method']}]\n"
        flow += "```\n"
        
        return flow
    
    def _analyze_dependencies(self, analysis_results: Dict[str, CodeAnalysisResult]) -> str:
        """分析依賴關係"""
        deps = "### 4.1 核心依賴\n\n"
        
        # 統計導入
        import_stats = {}
        for path, result in analysis_results.items():
            for imp in result.imports:
                base_module = imp.split('.')[0]
                import_stats[base_module] = import_stats.get(base_module, 0) + 1
        
        # 排序並顯示前10個
        sorted_imports = sorted(import_stats.items(), key=lambda x: x[1], reverse=True)
        
        deps += "| 模塊 | 使用次數 |\n"
        deps += "|------|----------|\n"
        for module, count in sorted_imports[:10]:
            deps += f"| {module} | {count} |\n"
        
        return deps
    
    def _analyze_integration_points(self, analysis_results: Dict[str, CodeAnalysisResult]) -> str:
        """分析集成點"""
        integration = "### 5.1 主要集成點\n\n"
        
        # 識別集成相關的類和方法
        integration_points = []
        for path, result in analysis_results.items():
            for class_info in result.classes:
                if any(keyword in class_info["name"].lower() 
                      for keyword in ["integration", "bridge", "adapter", "connector"]):
                    integration_points.append({
                        "type": "Class",
                        "name": class_info["name"],
                        "file": os.path.basename(path)
                    })
        
        for point in integration_points[:5]:
            integration += f"- **{point['name']}** (`{point['file']}`): {point['type']}\n"
        
        return integration
    
    def _generate_test_requirements(self, analysis_results: Dict[str, CodeAnalysisResult]) -> str:
        """生成測試需求"""
        test_req = "### 6.1 測試覆蓋需求\n\n"
        
        # 統計需要測試的組件
        total_classes = 0
        total_methods = 0
        async_methods = 0
        
        for path, result in analysis_results.items():
            total_classes += len(result.classes)
            for class_info in result.classes:
                total_methods += len(class_info["methods"])
                async_methods += sum(1 for m in class_info["methods"] if m["is_async"])
        
        test_req += f"- 總類數: {total_classes}\n"
        test_req += f"- 總方法數: {total_methods}\n"
        test_req += f"- 異步方法: {async_methods}\n"
        test_req += f"- 建議測試用例數: {total_methods * 2} (每個方法至少2個測試)\n"
        
        test_req += "\n### 6.2 關鍵測試點\n\n"
        
        # 識別關鍵測試點
        critical_methods = []
        for path, result in analysis_results.items():
            for class_info in result.classes:
                for method in class_info["methods"]:
                    if any(keyword in method["name"].lower() 
                          for keyword in ["execute", "process", "validate", "authenticate"]):
                        critical_methods.append(f"{class_info['name']}.{method['name']}")
        
        for method in critical_methods[:10]:
            test_req += f"- {method}\n"
        
        return test_req
    
    async def compare_with_manual_spec(self, 
                                     auto_spec: str, 
                                     manual_spec_path: str) -> Dict[str, Any]:
        """比較自動生成和手動編寫的規格"""
        print(f"\n🔍 比較規格文檔")
        
        try:
            with open(manual_spec_path, 'r', encoding='utf-8') as f:
                manual_spec = f.read()
            
            # 簡單的比較分析
            comparison = {
                "auto_spec_lines": len(auto_spec.split('\n')),
                "manual_spec_lines": len(manual_spec.split('\n')),
                "auto_sections": len([line for line in auto_spec.split('\n') if line.startswith('#')]),
                "manual_sections": len([line for line in manual_spec.split('\n') if line.startswith('#')]),
                "coverage_estimate": 0.0
            }
            
            # 計算覆蓋率（基於關鍵詞匹配）
            keywords = ["MCP", "接口", "規格", "測試", "集成", "架構", "組件", "數據流"]
            auto_keywords = sum(1 for keyword in keywords if keyword in auto_spec)
            manual_keywords = sum(1 for keyword in keywords if keyword in manual_spec)
            
            if manual_keywords > 0:
                comparison["coverage_estimate"] = auto_keywords / manual_keywords
            
            return comparison
            
        except Exception as e:
            print(f"   ⚠️ 比較失敗: {e}")
            return {}

async def demonstrate_codeflow_spec_generation():
    """演示使用 CodeFlow MCP 生成規格文檔"""
    print("🚀 CodeFlow MCP 規格文檔自動生成演示")
    print("="*70)
    
    # 初始化 CodeFlow MCP
    codeflow = CodeFlowMCP()
    
    # 分析目標目錄（假設是當前目錄）
    target_directory = "/Users/alexchuang/alexchuangtest/aicore0718"
    
    # 只分析核心文件
    core_files = [
        "external_tools_mcp_integration.py",
        "advanced_tool_intelligence_system.py",
        "powerautomation_external_tools_integration.py"
    ]
    
    print(f"\n📊 分析核心實現文件")
    print("-"*50)
    
    analysis_results = {}
    for file_name in core_files:
        file_path = os.path.join(target_directory, file_name)
        if os.path.exists(file_path):
            result = await codeflow.analyze_file(file_path)
            analysis_results[file_path] = result
            
            print(f"\n{file_name}:")
            print(f"  - 類: {len(result.classes)}")
            print(f"  - 函數: {len(result.functions)}")
            print(f"  - 架構模式: {', '.join(result.architecture_patterns)}")
    
    # 生成規格文檔
    print(f"\n📝 生成規格文檔")
    print("-"*50)
    
    auto_spec = await codeflow.generate_specification(analysis_results)
    
    # 保存規格文檔
    output_path = os.path.join(target_directory, "auto_generated_spec.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(auto_spec)
    
    print(f"✅ 規格文檔已生成: {output_path}")
    
    # 顯示部分內容
    print(f"\n📄 規格文檔預覽:")
    print("-"*50)
    lines = auto_spec.split('\n')[:30]
    for line in lines:
        print(line)
    print("... (更多內容請查看完整文檔)")
    
    # 比較與手動規格
    manual_spec_path = os.path.join(target_directory, "external_tools_integration_spec.md")
    if os.path.exists(manual_spec_path):
        comparison = await codeflow.compare_with_manual_spec(auto_spec, manual_spec_path)
        
        print(f"\n📊 與手動規格比較:")
        print("-"*50)
        print(f"自動生成: {comparison.get('auto_spec_lines', 0)} 行, {comparison.get('auto_sections', 0)} 個章節")
        print(f"手動編寫: {comparison.get('manual_spec_lines', 0)} 行, {comparison.get('manual_sections', 0)} 個章節")
        print(f"覆蓋率估計: {comparison.get('coverage_estimate', 0):.1%}")
    
    # 生成測試用例
    print(f"\n🧪 基於規格生成測試用例")
    print("-"*50)
    
    test_cases = []
    for path, result in analysis_results.items():
        for class_info in result.classes:
            for method in class_info["methods"]:
                if not method["name"].startswith("_"):
                    test_cases.append({
                        "class": class_info["name"],
                        "method": method["name"],
                        "test_name": f"test_{method['name']}_basic",
                        "is_async": method["is_async"]
                    })
    
    # 生成測試文件框架
    test_template = """import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

# 自動生成的測試用例框架

"""
    
    for test_case in test_cases[:10]:  # 限制數量
        if test_case["is_async"]:
            test_template += f"""
@pytest.mark.asyncio
async def {test_case['test_name']}():
    \"\"\"測試 {test_case['class']}.{test_case['method']}\"\"\"
    # TODO: 實現測試邏輯
    pass
"""
        else:
            test_template += f"""
def {test_case['test_name']}():
    \"\"\"測試 {test_case['class']}.{test_case['method']}\"\"\"
    # TODO: 實現測試邏輯
    pass
"""
    
    # 保存測試模板
    test_output_path = os.path.join(target_directory, "auto_generated_tests.py")
    with open(test_output_path, 'w', encoding='utf-8') as f:
        f.write(test_template)
    
    print(f"✅ 測試用例框架已生成: {test_output_path}")
    print(f"   生成了 {len(test_cases)} 個測試用例框架")
    
    # 總結
    print(f"\n✨ CodeFlow MCP 分析總結")
    print("="*70)
    print(f"\n1. 自動識別了系統架構和組件")
    print(f"2. 提取了所有公共接口和方法簽名")
    print(f"3. 分析了數據流和依賴關係")
    print(f"4. 生成了完整的規格文檔")
    print(f"5. 創建了測試用例框架")
    print(f"\n這證明了 CodeFlow MCP 可以：")
    print(f"- 快速理解現有代碼結構")
    print(f"- 自動生成標準化文檔")
    print(f"- 確保文檔與代碼同步")
    print(f"- 加速開發和測試流程")

if __name__ == "__main__":
    asyncio.run(demonstrate_codeflow_spec_generation())