#!/usr/bin/env python3
"""
增強版 CodeFlow MCP 規格生成器
提供更深入的代碼分析和更完整的規格文檔生成
"""

import asyncio
import json
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import ast
import textwrap

@dataclass
class EnhancedCodeAnalysis:
    """增強的代碼分析結果"""
    file_path: str
    module_docstring: Optional[str] = None
    classes: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[Dict[str, str]] = field(default_factory=list)
    constants: Dict[str, Any] = field(default_factory=dict)
    architecture_patterns: List[str] = field(default_factory=list)
    interfaces: List[Dict[str, Any]] = field(default_factory=list)
    data_models: List[Dict[str, Any]] = field(default_factory=list)
    api_endpoints: List[Dict[str, Any]] = field(default_factory=list)
    test_coverage_hints: List[str] = field(default_factory=list)
    complexity_metrics: Dict[str, int] = field(default_factory=dict)

class EnhancedCodeFlowMCP:
    """增強版 CodeFlow MCP - 深度代碼分析和規格生成"""
    
    def __init__(self):
        self.analysis_cache = {}
        self.pattern_library = self._init_pattern_library()
        self.api_patterns = self._init_api_patterns()
        
    def _init_pattern_library(self) -> Dict[str, Any]:
        """初始化設計模式庫"""
        return {
            "mcp_component": {
                "indicators": ["BaseMCP", "handle_request", "register_handler"],
                "type": "MCP Component",
                "description": "Model Context Protocol 組件"
            },
            "adapter_pattern": {
                "indicators": ["Adapter", "adapt", "convert", "transform"],
                "type": "Adapter Pattern",
                "description": "適配器模式，用於接口轉換"
            },
            "factory_pattern": {
                "indicators": ["Factory", "create", "build", "make"],
                "type": "Factory Pattern",
                "description": "工廠模式，用於對象創建"
            },
            "singleton_pattern": {
                "indicators": ["_instance", "getInstance", "__new__"],
                "type": "Singleton Pattern",
                "description": "單例模式，確保唯一實例"
            },
            "observer_pattern": {
                "indicators": ["subscribe", "notify", "observer", "listener"],
                "type": "Observer Pattern",
                "description": "觀察者模式，用於事件處理"
            },
            "strategy_pattern": {
                "indicators": ["strategy", "algorithm", "policy"],
                "type": "Strategy Pattern",
                "description": "策略模式，用於算法選擇"
            }
        }
    
    def _init_api_patterns(self) -> List[Dict[str, Any]]:
        """初始化 API 模式識別"""
        return [
            {
                "pattern": r"async def (handle_request|execute|process)",
                "type": "async_api",
                "category": "異步 API"
            },
            {
                "pattern": r"@(app|router)\.(get|post|put|delete)",
                "type": "rest_api",
                "category": "REST API"
            },
            {
                "pattern": r"def handle_(\w+)_request",
                "type": "request_handler",
                "category": "請求處理器"
            }
        ]
    
    async def analyze_file_enhanced(self, file_path: str) -> EnhancedCodeAnalysis:
        """增強的文件分析"""
        print(f"\n🔍 深度分析文件: {os.path.basename(file_path)}")
        
        result = EnhancedCodeAnalysis(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 AST
            tree = ast.parse(content)
            
            # 提取模塊文檔字符串
            result.module_docstring = ast.get_docstring(tree)
            
            # 深度分析
            await self._deep_analyze_ast(tree, content, result)
            
            # 識別設計模式
            result.architecture_patterns = self._identify_patterns_enhanced(content, result)
            
            # 提取數據模型
            result.data_models = self._extract_data_models(result)
            
            # 識別 API 端點
            result.api_endpoints = self._identify_api_endpoints(content, result)
            
            # 生成測試覆蓋提示
            result.test_coverage_hints = self._generate_test_hints(result)
            
            # 計算複雜度指標
            result.complexity_metrics = self._calculate_complexity(result)
            
        except Exception as e:
            print(f"   ⚠️ 分析錯誤: {e}")
        
        return result
    
    async def _deep_analyze_ast(self, tree: ast.AST, content: str, 
                               result: EnhancedCodeAnalysis):
        """深度 AST 分析"""
        class DeepAnalyzer(ast.NodeVisitor):
            def __init__(self, parent_result):
                self.result = parent_result
                self.current_class = None
                
            def visit_ClassDef(self, node):
                class_info = {
                    "name": node.name,
                    "bases": [self._get_name(base) for base in node.bases],
                    "decorators": [self._get_name(d) for d in node.decorator_list],
                    "methods": [],
                    "attributes": [],
                    "properties": [],
                    "class_variables": [],
                    "docstring": ast.get_docstring(node),
                    "line_start": node.lineno,
                    "is_dataclass": any("dataclass" in self._get_name(d) 
                                       for d in node.decorator_list)
                }
                
                # 保存當前類上下文
                old_class = self.current_class
                self.current_class = class_info
                
                # 訪問類體
                self.generic_visit(node)
                
                self.result.classes.append(class_info)
                self.current_class = old_class
                
            def visit_FunctionDef(self, node):
                func_info = {
                    "name": node.name,
                    "params": self._extract_params(node),
                    "returns": self._get_return_annotation(node),
                    "decorators": [self._get_name(d) for d in node.decorator_list],
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "docstring": ast.get_docstring(node),
                    "line_start": node.lineno,
                    "complexity": self._calculate_cyclomatic_complexity(node)
                }
                
                if self.current_class:
                    # 這是類方法
                    func_info["is_property"] = any("property" in self._get_name(d) 
                                                  for d in node.decorator_list)
                    func_info["is_classmethod"] = any("classmethod" in self._get_name(d) 
                                                     for d in node.decorator_list)
                    func_info["is_staticmethod"] = any("staticmethod" in self._get_name(d) 
                                                       for d in node.decorator_list)
                    self.current_class["methods"].append(func_info)
                else:
                    # 這是模塊級函數
                    self.result.functions.append(func_info)
                    
            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)
                
            def visit_Import(self, node):
                for alias in node.names:
                    self.result.imports.append({
                        "module": alias.name,
                        "alias": alias.asname,
                        "type": "import"
                    })
                    
            def visit_ImportFrom(self, node):
                module = node.module or ''
                for alias in node.names:
                    self.result.imports.append({
                        "module": f"{module}.{alias.name}",
                        "alias": alias.asname,
                        "type": "from_import",
                        "level": node.level
                    })
                    
            def visit_Assign(self, node):
                if self.current_class:
                    # 類屬性
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.current_class["attributes"].append({
                                "name": target.id,
                                "line": node.lineno
                            })
                else:
                    # 模塊級常量
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            self.result.constants[target.id] = {
                                "line": node.lineno,
                                "value": self._get_value(node.value)
                            }
                            
            def _get_name(self, node):
                """安全獲取節點名稱"""
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return f"{self._get_name(node.value)}.{node.attr}"
                elif isinstance(node, ast.Call):
                    return self._get_name(node.func)
                else:
                    return str(node)
                    
            def _extract_params(self, node):
                """提取參數信息"""
                params = []
                for arg in node.args.args:
                    param = {
                        "name": arg.arg,
                        "annotation": self._get_annotation(arg.annotation)
                    }
                    params.append(param)
                return params
                
            def _get_annotation(self, node):
                """獲取類型註解"""
                if node is None:
                    return None
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Constant):
                    return str(node.value)
                else:
                    return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                    
            def _get_return_annotation(self, node):
                """獲取返回類型註解"""
                if node.returns:
                    return self._get_annotation(node.returns)
                return None
                
            def _get_value(self, node):
                """獲取節點值"""
                if isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.List):
                    return [self._get_value(elt) for elt in node.elts]
                elif isinstance(node, ast.Dict):
                    return {self._get_value(k): self._get_value(v) 
                           for k, v in zip(node.keys, node.values)}
                else:
                    return None
                    
            def _calculate_cyclomatic_complexity(self, node):
                """計算圈複雜度"""
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For)):
                        complexity += 1
                    elif isinstance(child, ast.ExceptHandler):
                        complexity += 1
                return complexity
        
        analyzer = DeepAnalyzer(result)
        analyzer.visit(tree)
    
    def _identify_patterns_enhanced(self, content: str, 
                                   result: EnhancedCodeAnalysis) -> List[str]:
        """增強的模式識別"""
        patterns = []
        
        # 檢查設計模式
        for pattern_name, pattern_info in self.pattern_library.items():
            for indicator in pattern_info["indicators"]:
                if indicator in content:
                    if pattern_info["type"] not in patterns:
                        patterns.append(pattern_info["type"])
                    break
        
        # 基於類結構識別模式
        for class_info in result.classes:
            # MCP 模式
            if "BaseMCP" in class_info["bases"] or "MCP" in class_info["name"]:
                if "MCP Component" not in patterns:
                    patterns.append("MCP Component")
                    
            # 數據類模式
            if class_info.get("is_dataclass"):
                if "Data Model" not in patterns:
                    patterns.append("Data Model")
                    
            # 單例模式
            if any(m["name"] == "__new__" for m in class_info["methods"]):
                if "Singleton Pattern" not in patterns:
                    patterns.append("Singleton Pattern")
        
        return patterns
    
    def _extract_data_models(self, result: EnhancedCodeAnalysis) -> List[Dict[str, Any]]:
        """提取數據模型"""
        data_models = []
        
        for class_info in result.classes:
            if class_info.get("is_dataclass") or "Model" in class_info["name"]:
                model = {
                    "name": class_info["name"],
                    "type": "dataclass" if class_info.get("is_dataclass") else "class",
                    "fields": [],
                    "docstring": class_info["docstring"]
                }
                
                # 提取字段
                for attr in class_info["attributes"]:
                    model["fields"].append({
                        "name": attr["name"],
                        "type": "Any"  # 需要更複雜的類型推斷
                    })
                
                data_models.append(model)
        
        return data_models
    
    def _identify_api_endpoints(self, content: str, 
                               result: EnhancedCodeAnalysis) -> List[Dict[str, Any]]:
        """識別 API 端點"""
        endpoints = []
        
        # 使用正則表達式識別 API 模式
        for pattern_info in self.api_patterns:
            pattern = pattern_info["pattern"]
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                endpoints.append({
                    "type": pattern_info["type"],
                    "category": pattern_info["category"],
                    "match": match.group(0),
                    "line": content[:match.start()].count('\n') + 1
                })
        
        # 從類方法中識別 API
        for class_info in result.classes:
            for method in class_info["methods"]:
                if any(keyword in method["name"].lower() 
                      for keyword in ["handle", "execute", "process", "request"]):
                    endpoints.append({
                        "type": "method_api",
                        "category": "方法 API",
                        "class": class_info["name"],
                        "method": method["name"],
                        "is_async": method["is_async"]
                    })
        
        return endpoints
    
    def _generate_test_hints(self, result: EnhancedCodeAnalysis) -> List[str]:
        """生成測試覆蓋提示"""
        hints = []
        
        # 類測試提示
        for class_info in result.classes:
            if class_info["methods"]:
                hints.append(f"為 {class_info['name']} 類創建測試，覆蓋 {len(class_info['methods'])} 個方法")
                
            # 異步方法需要特殊測試
            async_methods = [m for m in class_info["methods"] if m["is_async"]]
            if async_methods:
                hints.append(f"{class_info['name']} 有 {len(async_methods)} 個異步方法需要異步測試")
                
            # 複雜方法需要更多測試
            complex_methods = [m for m in class_info["methods"] 
                             if m.get("complexity", 0) > 5]
            if complex_methods:
                hints.append(f"{class_info['name']} 有 {len(complex_methods)} 個複雜方法需要重點測試")
        
        # API 測試提示
        if result.api_endpoints:
            hints.append(f"需要為 {len(result.api_endpoints)} 個 API 端點創建集成測試")
        
        return hints
    
    def _calculate_complexity(self, result: EnhancedCodeAnalysis) -> Dict[str, int]:
        """計算複雜度指標"""
        metrics = {
            "total_lines": 0,
            "total_classes": len(result.classes),
            "total_methods": sum(len(c["methods"]) for c in result.classes),
            "total_functions": len(result.functions),
            "avg_methods_per_class": 0,
            "max_class_complexity": 0,
            "total_complexity": 0
        }
        
        if metrics["total_classes"] > 0:
            metrics["avg_methods_per_class"] = metrics["total_methods"] / metrics["total_classes"]
        
        # 計算總複雜度
        for class_info in result.classes:
            class_complexity = sum(m.get("complexity", 1) for m in class_info["methods"])
            metrics["total_complexity"] += class_complexity
            metrics["max_class_complexity"] = max(metrics["max_class_complexity"], 
                                                  class_complexity)
        
        return metrics
    
    async def generate_enhanced_specification(self, 
                                            analysis_results: Dict[str, EnhancedCodeAnalysis]) -> str:
        """生成增強的規格文檔"""
        print(f"\n📝 生成增強規格文檔")
        
        spec = f"""# PowerAutomation 外部工具整合 - 自動生成規格文檔
生成時間: {datetime.now().isoformat()}
使用增強版 CodeFlow MCP 深度分析生成

## 執行摘要

本文檔通過自動分析 {len(analysis_results)} 個核心文件生成，提供完整的系統架構、接口規格和實現細節。

"""
        
        # 1. 系統概述
        spec += self._generate_system_overview(analysis_results)
        
        # 2. 架構分析
        spec += self._generate_architecture_analysis(analysis_results)
        
        # 3. 核心組件詳解
        spec += self._generate_component_details(analysis_results)
        
        # 4. API 規格
        spec += self._generate_api_specification(analysis_results)
        
        # 5. 數據模型
        spec += self._generate_data_models(analysis_results)
        
        # 6. 集成指南
        spec += self._generate_integration_guide(analysis_results)
        
        # 7. 測試策略
        spec += self._generate_test_strategy(analysis_results)
        
        # 8. 部署建議
        spec += self._generate_deployment_recommendations(analysis_results)
        
        return spec
    
    def _generate_system_overview(self, results: Dict[str, EnhancedCodeAnalysis]) -> str:
        """生成系統概述"""
        overview = "\n## 1. 系統概述\n\n"
        
        # 統計總體信息
        total_classes = sum(len(r.classes) for r in results.values())
        total_methods = sum(r.complexity_metrics.get("total_methods", 0) 
                           for r in results.values())
        total_complexity = sum(r.complexity_metrics.get("total_complexity", 0) 
                              for r in results.values())
        
        overview += f"""### 1.1 系統規模

- **核心文件數**: {len(results)}
- **總類數**: {total_classes}
- **總方法數**: {total_methods}
- **系統複雜度**: {total_complexity}

### 1.2 技術棧

"""
        
        # 統計導入的技術棧
        tech_stack = {}
        for result in results.values():
            for imp in result.imports:
                base_module = imp["module"].split('.')[0]
                if base_module not in ['typing', 'dataclasses', 'datetime']:
                    tech_stack[base_module] = tech_stack.get(base_module, 0) + 1
        
        for tech, count in sorted(tech_stack.items(), key=lambda x: x[1], reverse=True)[:5]:
            overview += f"- **{tech}**: 使用 {count} 次\n"
        
        return overview
    
    def _generate_architecture_analysis(self, results: Dict[str, EnhancedCodeAnalysis]) -> str:
        """生成架構分析"""
        arch = "\n## 2. 架構分析\n\n"
        
        # 收集所有架構模式
        all_patterns = {}
        for result in results.values():
            for pattern in result.architecture_patterns:
                all_patterns[pattern] = all_patterns.get(pattern, 0) + 1
        
        arch += "### 2.1 設計模式使用\n\n"
        arch += "| 模式 | 使用次數 | 說明 |\n"
        arch += "|------|----------|------|\n"
        
        for pattern, count in sorted(all_patterns.items(), key=lambda x: x[1], reverse=True):
            desc = next((p["description"] for p in self.pattern_library.values() 
                        if p["type"] == pattern), "")
            arch += f"| {pattern} | {count} | {desc} |\n"
        
        # 架構圖
        arch += "\n### 2.2 系統架構圖\n\n"
        arch += "```mermaid\ngraph TB\n"
        
        # 生成架構關係
        mcp_components = []
        for path, result in results.items():
            for class_info in result.classes:
                if "MCP" in class_info["name"] or "BaseMCP" in class_info["bases"]:
                    mcp_components.append(class_info["name"])
        
        if mcp_components:
            arch += "    subgraph MCP層\n"
            for comp in mcp_components[:5]:
                arch += f"        {comp}\n"
            arch += "    end\n"
        
        arch += "```\n"
        
        return arch
    
    def _generate_component_details(self, results: Dict[str, EnhancedCodeAnalysis]) -> str:
        """生成組件詳情"""
        details = "\n## 3. 核心組件詳解\n\n"
        
        # 選擇最重要的組件
        important_components = []
        for path, result in results.items():
            for class_info in result.classes:
                if len(class_info["methods"]) > 3:  # 有足夠方法的類
                    important_components.append((path, class_info))
        
        # 按方法數排序
        important_components.sort(key=lambda x: len(x[1]["methods"]), reverse=True)
        
        for i, (path, class_info) in enumerate(important_components[:5], 1):
            details += f"### 3.{i} {class_info['name']}\n\n"
            
            if class_info["docstring"]:
                details += f"{class_info['docstring']}\n\n"
            
            details += f"**文件**: `{os.path.basename(path)}`\n\n"
            
            # 基類
            if class_info["bases"]:
                details += f"**繼承**: {', '.join(class_info['bases'])}\n\n"
            
            # 主要方法
            details += "**主要方法**:\n\n"
            for method in class_info["methods"][:5]:
                async_prefix = "async " if method["is_async"] else ""
                params = ", ".join([p["name"] for p in method["params"]])
                details += f"- `{async_prefix}{method['name']}({params})`"
                if method["docstring"]:
                    first_line = method["docstring"].split('\n')[0]
                    details += f": {first_line}"
                details += "\n"
            
            details += "\n"
        
        return details
    
    def _generate_api_specification(self, results: Dict[str, EnhancedCodeAnalysis]) -> str:
        """生成 API 規格"""
        api_spec = "\n## 4. API 規格\n\n"
        
        # 收集所有 API 端點
        all_endpoints = []
        for result in results.values():
            all_endpoints.extend(result.api_endpoints)
        
        # 按類型分組
        api_groups = {}
        for endpoint in all_endpoints:
            category = endpoint["category"]
            if category not in api_groups:
                api_groups[category] = []
            api_groups[category].append(endpoint)
        
        for category, endpoints in api_groups.items():
            api_spec += f"### 4.{list(api_groups.keys()).index(category) + 1} {category}\n\n"
            
            for endpoint in endpoints[:5]:
                if "class" in endpoint:
                    api_spec += f"- **{endpoint['class']}.{endpoint['method']}**"
                else:
                    api_spec += f"- **{endpoint['match']}**"
                
                if endpoint.get("is_async"):
                    api_spec += " (異步)"
                
                api_spec += "\n"
            
            api_spec += "\n"
        
        return api_spec
    
    def _generate_data_models(self, results: Dict[str, EnhancedCodeAnalysis]) -> str:
        """生成數據模型"""
        models = "\n## 5. 數據模型\n\n"
        
        # 收集所有數據模型
        all_models = []
        for result in results.values():
            all_models.extend(result.data_models)
        
        if not all_models:
            models += "未檢測到數據模型定義。\n"
            return models
        
        for i, model in enumerate(all_models[:5], 1):
            models += f"### 5.{i} {model['name']}\n\n"
            
            if model["docstring"]:
                models += f"{model['docstring']}\n\n"
            
            models += "**字段**:\n\n"
            for field in model["fields"]:
                models += f"- `{field['name']}: {field['type']}`\n"
            
            models += "\n"
        
        return models
    
    def _generate_integration_guide(self, results: Dict[str, EnhancedCodeAnalysis]) -> str:
        """生成集成指南"""
        guide = "\n## 6. 集成指南\n\n"
        
        guide += "### 6.1 快速集成步驟\n\n"
        guide += "基於代碼分析，建議按以下步驟集成：\n\n"
        
        # 查找主要的集成類
        integration_classes = []
        for result in results.values():
            for class_info in result.classes:
                if any(keyword in class_info["name"].lower() 
                      for keyword in ["integration", "bridge", "adapter"]):
                    integration_classes.append(class_info["name"])
        
        guide += "1. **初始化核心組件**\n"
        guide += "   ```python\n"
        guide += "   mcp = ExternalToolsMCP()\n"
        guide += "   await mcp.initialize()\n"
        guide += "   ```\n\n"
        
        if integration_classes:
            guide += "2. **配置集成橋接**\n"
            guide += "   ```python\n"
            for cls in integration_classes[:2]:
                guide += f"   {cls.lower()} = {cls}(mcp)\n"
            guide += "   ```\n\n"
        
        guide += "3. **註冊到系統**\n"
        guide += "   ```python\n"
        guide += "   system.register_component('external_tools', mcp)\n"
        guide += "   ```\n\n"
        
        return guide
    
    def _generate_test_strategy(self, results: Dict[str, EnhancedCodeAnalysis]) -> str:
        """生成測試策略"""
        test = "\n## 7. 測試策略\n\n"
        
        # 收集所有測試提示
        all_hints = []
        for result in results.values():
            all_hints.extend(result.test_coverage_hints)
        
        test += "### 7.1 測試覆蓋建議\n\n"
        for hint in all_hints[:10]:
            test += f"- {hint}\n"
        
        # 計算測試統計
        total_methods = sum(r.complexity_metrics.get("total_methods", 0) 
                           for r in results.values())
        total_complexity = sum(r.complexity_metrics.get("total_complexity", 0) 
                              for r in results.values())
        
        test += f"\n### 7.2 測試指標目標\n\n"
        test += f"- **最小測試用例數**: {total_methods * 2}\n"
        test += f"- **複雜度覆蓋**: 需要 {total_complexity} 個路徑測試\n"
        test += f"- **建議覆蓋率**: 80% 以上\n"
        
        return test
    
    def _generate_deployment_recommendations(self, results: Dict[str, EnhancedCodeAnalysis]) -> str:
        """生成部署建議"""
        deploy = "\n## 8. 部署建議\n\n"
        
        deploy += "### 8.1 環境要求\n\n"
        deploy += "基於代碼分析，系統需要：\n\n"
        
        # 檢查異步代碼
        has_async = any(
            any(m["is_async"] for c in r.classes for m in c["methods"])
            for r in results.values()
        )
        
        if has_async:
            deploy += "- Python 3.7+ (支持異步)\n"
        else:
            deploy += "- Python 3.6+\n"
        
        deploy += "- 異步運行時環境 (asyncio)\n"
        deploy += "- API 密鑰配置\n"
        deploy += "- 緩存系統 (建議 Redis)\n"
        
        deploy += "\n### 8.2 性能優化建議\n\n"
        deploy += "- 使用連接池管理外部 API 連接\n"
        deploy += "- 實現請求緩存減少 API 調用\n"
        deploy += "- 異步並發執行提高吞吐量\n"
        
        return deploy

async def demonstrate_enhanced_codeflow():
    """演示增強版 CodeFlow MCP"""
    print("🚀 增強版 CodeFlow MCP 規格生成演示")
    print("="*70)
    
    # 初始化增強版 CodeFlow
    codeflow = EnhancedCodeFlowMCP()
    
    # 分析文件
    target_directory = "/Users/alexchuang/alexchuangtest/aicore0718"
    core_files = [
        "external_tools_mcp_integration.py",
        "advanced_tool_intelligence_system.py",
        "powerautomation_external_tools_integration.py"
    ]
    
    print(f"\n📊 深度分析核心文件")
    print("-"*50)
    
    analysis_results = {}
    for file_name in core_files:
        file_path = os.path.join(target_directory, file_name)
        if os.path.exists(file_path):
            result = await codeflow.analyze_file_enhanced(file_path)
            analysis_results[file_path] = result
            
            print(f"\n{file_name}:")
            print(f"  - 類: {len(result.classes)}")
            print(f"  - 方法總數: {result.complexity_metrics.get('total_methods', 0)}")
            print(f"  - 總複雜度: {result.complexity_metrics.get('total_complexity', 0)}")
            print(f"  - API 端點: {len(result.api_endpoints)}")
            print(f"  - 數據模型: {len(result.data_models)}")
    
    # 生成增強規格
    enhanced_spec = await codeflow.generate_enhanced_specification(analysis_results)
    
    # 保存規格
    output_path = os.path.join(target_directory, "enhanced_auto_generated_spec.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_spec)
    
    print(f"\n✅ 增強規格文檔已生成: {output_path}")
    
    # 顯示摘要
    print(f"\n📄 增強規格文檔摘要:")
    print("-"*50)
    
    lines = enhanced_spec.split('\n')
    sections = [line for line in lines if line.startswith('##')]
    
    print("主要章節：")
    for section in sections:
        print(f"  {section}")
    
    print(f"\n總行數: {len(lines)}")
    print(f"總字數: {len(enhanced_spec.split())}")
    
    # 與手動規格對比
    print(f"\n🎯 結論：")
    print("-"*50)
    print("增強版 CodeFlow MCP 提供了：")
    print("1. 更深入的代碼結構分析")
    print("2. 自動識別設計模式和架構")
    print("3. 完整的 API 規格提取")
    print("4. 智能測試策略生成")
    print("5. 實用的集成和部署指南")
    print("\n這證明了 CodeFlow MCP 可以成為強大的文檔自動化工具！")

if __name__ == "__main__":
    asyncio.run(demonstrate_enhanced_codeflow())