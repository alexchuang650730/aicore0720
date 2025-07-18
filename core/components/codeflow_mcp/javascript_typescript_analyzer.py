#!/usr/bin/env python3
"""
JavaScript/TypeScript 代碼分析器
擴展 code_to_spec_generator 支持 JS/TS 語言
"""

import re
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import esprima  # JavaScript parser
import logging

from .code_to_spec_generator import (
    FunctionSpec, ClassSpec, ModuleSpec, ProjectSpec,
    CodeToSpecGenerator
)

logger = logging.getLogger(__name__)


class JavaScriptTypeScriptAnalyzer:
    """JavaScript/TypeScript 代碼分析器"""
    
    def __init__(self):
        self.ts_types = {
            "string", "number", "boolean", "void", "any", "unknown",
            "object", "Function", "Array", "Promise", "Date", "RegExp"
        }
        
        self.frameworks = {
            "react": ["React", "useState", "useEffect", "Component"],
            "vue": ["Vue", "createApp", "ref", "computed"],
            "angular": ["@angular", "Component", "Injectable"],
            "express": ["express", "Router", "Request", "Response"],
            "nestjs": ["@nestjs", "Controller", "Injectable", "Module"]
        }
        
    async def analyze_javascript_file(self, file_path: Path) -> ModuleSpec:
        """分析 JavaScript 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            # 使用 esprima 解析 JavaScript
            tree = esprima.parseScript(content, {
                'jsx': True,
                'tolerant': True,
                'loc': True,
                'range': True,
                'comment': True
            })
            
            return self._analyze_js_ast(tree, file_path, content)
            
        except Exception as e:
            logger.error(f"解析 JavaScript 文件失敗 {file_path}: {e}")
            return self._create_empty_module(file_path)
            
    async def analyze_typescript_file(self, file_path: Path) -> ModuleSpec:
        """分析 TypeScript 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # TypeScript 需要先轉換為 JavaScript
        # 這裡簡化處理，移除類型註解
        js_content = self._strip_typescript_annotations(content)
        
        try:
            tree = esprima.parseScript(js_content, {
                'jsx': True,
                'tolerant': True,
                'loc': True,
                'comment': True
            })
            
            # 分析 AST 並保留 TypeScript 類型信息
            module_spec = self._analyze_js_ast(tree, file_path, content)
            
            # 從原始 TypeScript 代碼中提取類型信息
            self._extract_typescript_types(content, module_spec)
            
            return module_spec
            
        except Exception as e:
            logger.error(f"解析 TypeScript 文件失敗 {file_path}: {e}")
            return self._create_empty_module(file_path)
            
    def _analyze_js_ast(self, tree: Any, file_path: Path, source: str) -> ModuleSpec:
        """分析 JavaScript AST"""
        module_spec = ModuleSpec(
            name=file_path.stem,
            description=self._extract_file_comment(tree, source),
            imports=self._extract_imports(tree, source),
            exports=self._extract_exports(tree, source),
            classes=[],
            functions=[],
            constants={},
            dependencies=[]
        )
        
        # 遍歷 AST
        for node in tree.body:
            if node.type == 'FunctionDeclaration':
                func_spec = self._analyze_function(node, source)
                module_spec.functions.append(func_spec)
                
            elif node.type == 'ClassDeclaration':
                class_spec = self._analyze_class(node, source)
                module_spec.classes.append(class_spec)
                
            elif node.type == 'VariableDeclaration':
                self._extract_constants(node, module_spec.constants)
                
        # 檢測使用的框架
        module_spec.dependencies = self._detect_frameworks(module_spec.imports)
        
        return module_spec
        
    def _analyze_function(self, node: Any, source: str) -> FunctionSpec:
        """分析函數節點"""
        params = []
        for param in node.params:
            param_info = {
                "name": self._get_param_name(param),
                "type": "any",  # JavaScript 默認類型
                "default": None,
                "description": ""
            }
            params.append(param_info)
            
        # 提取函數註釋
        description = self._extract_jsdoc(node, source)
        
        # 分析函數體
        is_async = node.async
        returns = self._infer_return_type(node)
        
        return FunctionSpec(
            name=node.id.name if node.id else "anonymous",
            description=description or f"Function {node.id.name if node.id else 'anonymous'}",
            parameters=params,
            return_type=returns,
            exceptions=self._extract_thrown_errors(node),
            examples=self._generate_js_examples(node, params),
            complexity=self._calculate_js_complexity(node),
            dependencies=self._extract_js_dependencies(node)
        )
        
    def _analyze_class(self, node: Any, source: str) -> ClassSpec:
        """分析類節點"""
        class_spec = ClassSpec(
            name=node.id.name,
            description=self._extract_jsdoc(node, source) or f"Class {node.id.name}",
            attributes=[],
            methods=[],
            inheritance=[node.superClass.name] if node.superClass else [],
            interfaces=[],
            design_pattern=None
        )
        
        # 分析類成員
        for item in node.body.body:
            if item.type == 'MethodDefinition':
                if item.key.name == 'constructor':
                    # 從構造函數提取屬性
                    class_spec.attributes = self._extract_class_properties(item)
                    
                method_spec = self._analyze_method(item, source)
                class_spec.methods.append(method_spec)
                
        return class_spec
        
    def _extract_imports(self, tree: Any, source: str) -> List[str]:
        """提取導入語句"""
        imports = []
        
        for node in tree.body:
            if node.type == 'ImportDeclaration':
                module = node.source.value
                imports.append(module)
                
            elif node.type == 'VariableDeclaration':
                # 檢查 require 語句
                for decl in node.declarations:
                    if (decl.init and 
                        decl.init.type == 'CallExpression' and
                        decl.init.callee.name == 'require'):
                        module = decl.init.arguments[0].value
                        imports.append(module)
                        
        return imports
        
    def _extract_exports(self, tree: Any, source: str) -> List[str]:
        """提取導出"""
        exports = []
        
        for node in tree.body:
            if node.type == 'ExportDefaultDeclaration':
                if node.declaration.id:
                    exports.append(f"default: {node.declaration.id.name}")
                else:
                    exports.append("default")
                    
            elif node.type == 'ExportNamedDeclaration':
                if node.declaration:
                    if node.declaration.type == 'FunctionDeclaration':
                        exports.append(node.declaration.id.name)
                    elif node.declaration.type == 'ClassDeclaration':
                        exports.append(node.declaration.id.name)
                    elif node.declaration.type == 'VariableDeclaration':
                        for decl in node.declaration.declarations:
                            exports.append(decl.id.name)
                            
        return exports
        
    def _strip_typescript_annotations(self, content: str) -> str:
        """移除 TypeScript 類型註解"""
        # 移除類型註解
        content = re.sub(r':\s*\w+(\[\])?(\s*[|&]\s*\w+)*', '', content)
        
        # 移除介面定義
        content = re.sub(r'interface\s+\w+\s*{[^}]*}', '', content)
        
        # 移除類型別名
        content = re.sub(r'type\s+\w+\s*=\s*[^;]+;', '', content)
        
        # 移除泛型
        content = re.sub(r'<[^>]+>', '', content)
        
        # 移除類型斷言
        content = re.sub(r'as\s+\w+', '', content)
        
        return content
        
    def _extract_typescript_types(self, content: str, module_spec: ModuleSpec):
        """從 TypeScript 代碼提取類型信息"""
        # 提取介面定義
        interfaces = re.findall(r'interface\s+(\w+)\s*{([^}]*)}', content)
        for name, body in interfaces:
            # 解析介面屬性
            props = re.findall(r'(\w+)\s*:\s*([\w\[\]|&]+)', body)
            # 這些信息可以添加到 module_spec 中
            
        # 提取函數類型註解
        for func in module_spec.functions:
            # 查找函數的類型註解
            pattern = f'function\\s+{func.name}\\s*\\([^)]*\\)\\s*:\\s*([\\w\\[\\]|&]+)'
            match = re.search(pattern, content)
            if match:
                func.return_type = match.group(1)
                
    def _extract_jsdoc(self, node: Any, source: str) -> Optional[str]:
        """提取 JSDoc 註釋"""
        # 查找節點前的註釋
        if hasattr(node, 'leadingComments') and node.leadingComments:
            for comment in node.leadingComments:
                if comment.type == 'Block' and comment.value.startswith('*'):
                    # 解析 JSDoc
                    return self._parse_jsdoc(comment.value)
                    
        return None
        
    def _parse_jsdoc(self, comment: str) -> str:
        """解析 JSDoc 格式註釋"""
        lines = comment.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('*'):
                line = line[1:].strip()
                
            # 跳過 @param, @returns 等標籤
            if not line.startswith('@'):
                description_lines.append(line)
                
        return ' '.join(description_lines).strip()
        
    def _detect_frameworks(self, imports: List[str]) -> List[str]:
        """檢測使用的框架"""
        detected = []
        
        for framework, indicators in self.frameworks.items():
            for imp in imports:
                if any(indicator in imp for indicator in indicators):
                    detected.append(framework)
                    break
                    
        return list(set(detected))
        
    def _calculate_js_complexity(self, node: Any) -> str:
        """計算 JavaScript 函數複雜度"""
        complexity = 1
        
        # 遞歸計算複雜度
        def count_branches(n):
            nonlocal complexity
            if hasattr(n, 'type'):
                if n.type in ['IfStatement', 'ConditionalExpression']:
                    complexity += 1
                elif n.type in ['ForStatement', 'WhileStatement', 'DoWhileStatement']:
                    complexity += 1
                elif n.type == 'SwitchCase':
                    complexity += 1
                    
            # 遍歷子節點
            for key, value in n.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            count_branches(item)
                elif hasattr(value, 'type'):
                    count_branches(value)
                    
        count_branches(node)
        
        if complexity <= 3:
            return "低"
        elif complexity <= 7:
            return "中"
        else:
            return "高"
            
    def _extract_thrown_errors(self, node: Any) -> List[str]:
        """提取可能拋出的錯誤"""
        errors = []
        
        def find_throws(n):
            if hasattr(n, 'type'):
                if n.type == 'ThrowStatement':
                    if n.argument.type == 'NewExpression':
                        errors.append(n.argument.callee.name)
                        
            for key, value in n.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            find_throws(item)
                elif hasattr(value, 'type'):
                    find_throws(value)
                    
        find_throws(node)
        return list(set(errors))
        
    def _infer_return_type(self, node: Any) -> str:
        """推斷返回類型"""
        if node.async:
            return "Promise<any>"
            
        # 簡單的類型推斷
        returns = []
        
        def find_returns(n):
            if hasattr(n, 'type'):
                if n.type == 'ReturnStatement' and n.argument:
                    if n.argument.type == 'Literal':
                        if isinstance(n.argument.value, str):
                            returns.append('string')
                        elif isinstance(n.argument.value, (int, float)):
                            returns.append('number')
                        elif isinstance(n.argument.value, bool):
                            returns.append('boolean')
                    elif n.argument.type == 'ObjectExpression':
                        returns.append('object')
                    elif n.argument.type == 'ArrayExpression':
                        returns.append('Array')
                        
            for key, value in n.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            find_returns(item)
                elif hasattr(value, 'type'):
                    find_returns(value)
                    
        find_returns(node)
        
        if returns:
            unique_types = list(set(returns))
            if len(unique_types) == 1:
                return unique_types[0]
            else:
                return ' | '.join(unique_types)
        
        return 'void'
        
    def _extract_js_dependencies(self, node: Any) -> List[str]:
        """提取 JavaScript 函數依賴"""
        deps = []
        
        def find_calls(n):
            if hasattr(n, 'type'):
                if n.type == 'CallExpression':
                    if n.callee.type == 'Identifier':
                        deps.append(n.callee.name)
                    elif n.callee.type == 'MemberExpression':
                        if n.callee.object.type == 'Identifier':
                            deps.append(f"{n.callee.object.name}.{n.callee.property.name}")
                            
            for key, value in n.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            find_calls(item)
                elif hasattr(value, 'type'):
                    find_calls(value)
                    
        find_calls(node)
        return list(set(deps))[:10]
        
    def _generate_js_examples(self, node: Any, params: List[Dict]) -> List[str]:
        """生成 JavaScript 函數調用示例"""
        func_name = node.id.name if node.id else "anonymous"
        examples = []
        
        # 基本調用
        param_names = [p["name"] for p in params]
        if param_names:
            examples.append(f"{func_name}({', '.join(param_names)})")
        else:
            examples.append(f"{func_name}()")
            
        # 如果是異步函數
        if node.async:
            examples.append(f"await {func_name}({', '.join(param_names) if param_names else ''})")
            
        return examples
        
    def _extract_class_properties(self, constructor: Any) -> List[Dict[str, Any]]:
        """從構造函數提取類屬性"""
        properties = []
        
        # 查找 this.xxx = yyy 模式
        def find_assignments(n):
            if hasattr(n, 'type'):
                if (n.type == 'AssignmentExpression' and
                    n.left.type == 'MemberExpression' and
                    n.left.object.type == 'ThisExpression'):
                    
                    properties.append({
                        "name": n.left.property.name,
                        "type": "any",
                        "description": ""
                    })
                    
            for key, value in n.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            find_assignments(item)
                elif hasattr(value, 'type'):
                    find_assignments(value)
                    
        if constructor.value:
            find_assignments(constructor.value)
            
        return properties
        
    def _analyze_method(self, node: Any, source: str) -> FunctionSpec:
        """分析類方法"""
        # 重用函數分析邏輯
        func_node = {
            'type': 'FunctionDeclaration',
            'id': {'name': node.key.name},
            'params': node.value.params,
            'body': node.value.body,
            'async': node.value.async
        }
        
        # 創建一個簡單的對象來模擬 AST 節點
        class SimpleNode:
            def __init__(self, data):
                for k, v in data.items():
                    setattr(self, k, v)
                    
        return self._analyze_function(SimpleNode(func_node), source)
        
    def _get_param_name(self, param: Any) -> str:
        """獲取參數名稱"""
        if param.type == 'Identifier':
            return param.name
        elif param.type == 'AssignmentPattern':
            return param.left.name
        elif param.type == 'RestElement':
            return f"...{param.argument.name}"
        else:
            return "unknown"
            
    def _extract_file_comment(self, tree: Any, source: str) -> str:
        """提取文件級註釋"""
        if hasattr(tree, 'comments') and tree.comments:
            first_comment = tree.comments[0]
            if first_comment.type == 'Block':
                return self._parse_jsdoc(first_comment.value)
                
        return "JavaScript/TypeScript module"
        
    def _extract_constants(self, node: Any, constants: Dict[str, Any]):
        """提取常量定義"""
        for decl in node.declarations:
            if node.kind == 'const' and decl.id.type == 'Identifier':
                name = decl.id.name
                if name.isupper():  # 全大寫視為常量
                    value = "..."
                    if decl.init and decl.init.type == 'Literal':
                        value = decl.init.value
                    constants[name] = value
                    
    def _create_empty_module(self, file_path: Path) -> ModuleSpec:
        """創建空模組規格"""
        return ModuleSpec(
            name=file_path.stem,
            description="無法解析的模組",
            imports=[],
            exports=[],
            classes=[],
            functions=[],
            constants={},
            dependencies=[]
        )


# 整合到主生成器
class EnhancedCodeToSpecGenerator(CodeToSpecGenerator):
    """增強的代碼到規格生成器 - 支持 JS/TS"""
    
    def __init__(self):
        super().__init__()
        self.js_analyzer = JavaScriptTypeScriptAnalyzer()
        
    async def _generate_javascript_spec(self, code_path: str) -> ProjectSpec:
        """從 JavaScript 代碼生成規格"""
        path = Path(code_path)
        
        if path.is_file():
            module_spec = await self.js_analyzer.analyze_javascript_file(path)
            return self._create_project_spec_from_module(module_spec, path)
        else:
            # 分析整個項目
            modules = []
            for js_file in path.rglob("*.js"):
                if not any(skip in str(js_file) for skip in ["node_modules", "dist", "build"]):
                    module_spec = await self.js_analyzer.analyze_javascript_file(js_file)
                    modules.append(module_spec)
                    
            return self._create_js_project_spec(path, modules)
            
    async def _generate_typescript_spec(self, code_path: str) -> ProjectSpec:
        """從 TypeScript 代碼生成規格"""
        path = Path(code_path)
        
        if path.is_file():
            module_spec = await self.js_analyzer.analyze_typescript_file(path)
            return self._create_project_spec_from_module(module_spec, path)
        else:
            # 分析整個項目
            modules = []
            for ts_file in path.rglob("*.ts"):
                if not any(skip in str(ts_file) for skip in ["node_modules", "dist", "build"]):
                    module_spec = await self.js_analyzer.analyze_typescript_file(ts_file)
                    modules.append(module_spec)
                    
            # 也包括 .tsx 文件
            for tsx_file in path.rglob("*.tsx"):
                if not any(skip in str(tsx_file) for skip in ["node_modules", "dist", "build"]):
                    module_spec = await self.js_analyzer.analyze_typescript_file(tsx_file)
                    modules.append(module_spec)
                    
            return self._create_js_project_spec(path, modules)
            
    def _create_project_spec_from_module(self, module: ModuleSpec, path: Path) -> ProjectSpec:
        """從單個模組創建項目規格"""
        return ProjectSpec(
            name=module.name,
            version="1.0.0",
            description=module.description,
            architecture={"type": "single_module", "language": "javascript"},
            modules=[module],
            api_endpoints=[],
            database_schema={},
            deployment_requirements={},
            business_rules=[]
        )
        
    def _create_js_project_spec(self, path: Path, modules: List[ModuleSpec]) -> ProjectSpec:
        """創建 JavaScript/TypeScript 項目規格"""
        # 檢測項目類型
        project_type = self._detect_js_project_type(path, modules)
        
        # 提取 API 端點（如果是後端項目）
        api_endpoints = []
        if project_type in ["express", "nestjs", "fastify"]:
            api_endpoints = self._extract_js_api_endpoints(modules)
            
        # 分析架構
        architecture = {
            "type": project_type,
            "language": "javascript/typescript",
            "frameworks": self._detect_frameworks(modules)
        }
        
        return ProjectSpec(
            name=path.name,
            version=self._detect_js_version(path),
            description=self._generate_js_project_description(modules, project_type),
            architecture=architecture,
            modules=modules,
            api_endpoints=api_endpoints,
            database_schema={},
            deployment_requirements=self._analyze_js_deployment(path),
            business_rules=[]
        )
        
    def _detect_js_project_type(self, path: Path, modules: List[ModuleSpec]) -> str:
        """檢測 JavaScript 項目類型"""
        # 檢查 package.json
        package_json = path / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
                deps = data.get('dependencies', {})
                
                if 'react' in deps:
                    return 'react'
                elif 'vue' in deps:
                    return 'vue'
                elif '@angular/core' in deps:
                    return 'angular'
                elif 'express' in deps:
                    return 'express'
                elif '@nestjs/core' in deps:
                    return 'nestjs'
                    
        return 'generic'
        
    def _detect_frameworks(self, modules: List[ModuleSpec]) -> List[str]:
        """檢測使用的框架"""
        frameworks = set()
        for module in modules:
            frameworks.update(module.dependencies)
        return list(frameworks)
        
    def _detect_js_version(self, path: Path) -> str:
        """檢測項目版本"""
        package_json = path / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
                return data.get('version', '1.0.0')
        return '1.0.0'
        
    def _generate_js_project_description(self, modules: List[ModuleSpec], project_type: str) -> str:
        """生成項目描述"""
        total_classes = sum(len(m.classes) for m in modules)
        total_functions = sum(len(m.functions) for m in modules)
        
        return f"{project_type.capitalize()} 項目，包含 {len(modules)} 個模組、{total_classes} 個類和 {total_functions} 個函數"
        
    def _extract_js_api_endpoints(self, modules: List[ModuleSpec]) -> List[Dict[str, Any]]:
        """提取 API 端點"""
        endpoints = []
        
        # 簡單的 Express 路由檢測
        for module in modules:
            for func in module.functions:
                for dep in func.dependencies:
                    if any(method in dep for method in ['get', 'post', 'put', 'delete', 'patch']):
                        endpoints.append({
                            "path": f"/{func.name}",
                            "method": dep.split('.')[-1].upper(),
                            "description": func.description,
                            "parameters": func.parameters,
                            "response": {"type": "object"}
                        })
                        
        return endpoints
        
    def _analyze_js_deployment(self, path: Path) -> Dict[str, Any]:
        """分析 JavaScript 項目部署需求"""
        requirements = {
            "runtime": "node.js",
            "dependencies": [],
            "scripts": {},
            "environment_variables": []
        }
        
        # 讀取 package.json
        package_json = path / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
                requirements["dependencies"] = list(data.get('dependencies', {}).keys())
                requirements["scripts"] = data.get('scripts', {})
                
        return requirements


# 創建增強的全局實例
enhanced_code_to_spec_generator = EnhancedCodeToSpecGenerator()