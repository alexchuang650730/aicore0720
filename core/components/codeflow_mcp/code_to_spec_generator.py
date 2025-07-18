#!/usr/bin/env python3
"""
CodeFlow MCP - 代碼到規格生成器
從現有代碼逆向生成詳細的技術規格文檔
"""

import ast
import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import inspect

@dataclass
class FunctionSpec:
    """函數規格"""
    name: str
    description: str
    parameters: List[Dict[str, Any]]
    return_type: str
    exceptions: List[str]
    examples: List[str]
    complexity: str
    dependencies: List[str]

@dataclass
class ClassSpec:
    """類規格"""
    name: str
    description: str
    attributes: List[Dict[str, Any]]
    methods: List[FunctionSpec]
    inheritance: List[str]
    interfaces: List[str]
    design_pattern: Optional[str]

@dataclass
class ModuleSpec:
    """模組規格"""
    name: str
    description: str
    imports: List[str]
    exports: List[str]
    classes: List[ClassSpec]
    functions: List[FunctionSpec]
    constants: Dict[str, Any]
    dependencies: List[str]

@dataclass
class ProjectSpec:
    """項目規格"""
    name: str
    version: str
    description: str
    architecture: Dict[str, Any]
    modules: List[ModuleSpec]
    api_endpoints: List[Dict[str, Any]]
    database_schema: Dict[str, Any]
    deployment_requirements: Dict[str, Any]
    business_rules: List[str]

class CodeToSpecGenerator:
    """從代碼生成規格的核心類"""
    
    def __init__(self):
        self.patterns = {
            # 設計模式識別
            "singleton": ["instance", "getInstance", "_instance"],
            "factory": ["create", "factory", "build"],
            "observer": ["subscribe", "notify", "observers"],
            "strategy": ["strategy", "algorithm", "execute"],
            "decorator": ["wrap", "decorate", "enhance"]
        }
        
        self.business_keywords = [
            "validate", "calculate", "process", "transform",
            "authenticate", "authorize", "payment", "order",
            "user", "product", "inventory", "report"
        ]
        
    async def generate_spec_from_code(self, code_path: str, language: str = "python") -> ProjectSpec:
        """從代碼生成完整規格"""
        print(f"🔍 分析代碼生成規格: {code_path}")
        
        if language == "python":
            return await self._generate_python_spec(code_path)
        elif language == "javascript":
            return await self._generate_javascript_spec(code_path)
        elif language == "typescript":
            return await self._generate_typescript_spec(code_path)
        else:
            raise ValueError(f"不支持的語言: {language}")
            
    async def _generate_python_spec(self, code_path: str) -> ProjectSpec:
        """從 Python 代碼生成規格"""
        path = Path(code_path)
        
        if path.is_file():
            # 單文件分析
            module_spec = await self._analyze_python_file(path)
            return ProjectSpec(
                name=path.stem,
                version="1.0.0",
                description=f"從 {path.name} 生成的規格",
                architecture={"type": "single_module"},
                modules=[module_spec],
                api_endpoints=[],
                database_schema={},
                deployment_requirements={},
                business_rules=self._extract_business_rules([module_spec])
            )
        else:
            # 目錄分析
            modules = []
            for py_file in path.rglob("*.py"):
                if not any(skip in str(py_file) for skip in ["__pycache__", ".pyc", "test_"]):
                    module_spec = await self._analyze_python_file(py_file)
                    modules.append(module_spec)
                    
            # 分析項目結構
            architecture = self._analyze_project_architecture(path, modules)
            api_endpoints = self._extract_api_endpoints(modules)
            db_schema = self._extract_database_schema(modules)
            
            return ProjectSpec(
                name=path.name,
                version=self._detect_version(path),
                description=self._generate_project_description(modules),
                architecture=architecture,
                modules=modules,
                api_endpoints=api_endpoints,
                database_schema=db_schema,
                deployment_requirements=self._analyze_deployment_requirements(path),
                business_rules=self._extract_business_rules(modules)
            )
            
    async def _analyze_python_file(self, file_path: Path) -> ModuleSpec:
        """分析單個 Python 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"⚠️ 語法錯誤 {file_path}: {e}")
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
            
        # 提取模組級信息
        module_spec = ModuleSpec(
            name=file_path.stem,
            description=self._extract_module_docstring(tree),
            imports=self._extract_imports(tree),
            exports=self._extract_exports(tree),
            classes=[],
            functions=[],
            constants={},
            dependencies=[]
        )
        
        # 分析類和函數
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_spec = self._analyze_class(node, content)
                module_spec.classes.append(class_spec)
                
            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                # 只分析模組級函數
                func_spec = self._analyze_function(node, content)
                module_spec.functions.append(func_spec)
                
            elif isinstance(node, ast.Assign) and node.col_offset == 0:
                # 提取常量
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        module_spec.constants[target.id] = self._get_value_repr(node.value)
                        
        # 分析依賴
        module_spec.dependencies = self._analyze_dependencies(module_spec)
        
        return module_spec
        
    def _analyze_class(self, node: ast.ClassDef, source: str) -> ClassSpec:
        """分析類定義"""
        class_spec = ClassSpec(
            name=node.name,
            description=ast.get_docstring(node) or "未提供描述",
            attributes=[],
            methods=[],
            inheritance=[base.id for base in node.bases if isinstance(base, ast.Name)],
            interfaces=[],
            design_pattern=None
        )
        
        # 分析屬性和方法
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "__init__":
                    # 從構造函數提取屬性
                    class_spec.attributes = self._extract_attributes_from_init(item)
                    
                method_spec = self._analyze_function(item, source)
                class_spec.methods.append(method_spec)
                
        # 識別設計模式
        class_spec.design_pattern = self._detect_design_pattern(class_spec)
        
        return class_spec
        
    def _analyze_function(self, node: ast.FunctionDef, source: str) -> FunctionSpec:
        """分析函數定義"""
        # 提取參數信息
        parameters = []
        for arg in node.args.args:
            param = {
                "name": arg.arg,
                "type": self._get_annotation(arg.annotation),
                "default": None,
                "description": ""
            }
            parameters.append(param)
            
        # 提取返回類型
        return_type = self._get_annotation(node.returns) if node.returns else "Any"
        
        # 分析函數體
        complexity = self._calculate_complexity(node)
        exceptions = self._extract_exceptions(node)
        dependencies = self._extract_function_dependencies(node)
        
        # 生成示例
        examples = self._generate_function_examples(node, parameters)
        
        return FunctionSpec(
            name=node.name,
            description=ast.get_docstring(node) or self._infer_function_purpose(node),
            parameters=parameters,
            return_type=return_type,
            exceptions=exceptions,
            examples=examples,
            complexity=complexity,
            dependencies=dependencies
        )
        
    def _extract_business_rules(self, modules: List[ModuleSpec]) -> List[str]:
        """提取業務規則"""
        rules = []
        
        for module in modules:
            # 從函數名和文檔中提取
            for func in module.functions:
                if any(keyword in func.name.lower() for keyword in self.business_keywords):
                    rule = self._infer_business_rule(func)
                    if rule:
                        rules.append(rule)
                        
            # 從類方法中提取
            for cls in module.classes:
                for method in cls.methods:
                    if any(keyword in method.name.lower() for keyword in self.business_keywords):
                        rule = self._infer_business_rule(method)
                        if rule:
                            rules.append(rule)
                            
        return list(set(rules))  # 去重
        
    def _infer_business_rule(self, func: FunctionSpec) -> Optional[str]:
        """推斷業務規則"""
        name_lower = func.name.lower()
        
        # 基於函數名推斷
        if "validate" in name_lower:
            entity = self._extract_entity_from_name(func.name)
            return f"{entity} 必須通過驗證規則"
            
        elif "calculate" in name_lower:
            entity = self._extract_entity_from_name(func.name)
            return f"{entity} 的計算邏輯已定義"
            
        elif "authenticate" in name_lower:
            return "用戶必須通過身份驗證才能訪問系統"
            
        elif "authorize" in name_lower:
            return "系統實施基於角色的訪問控制"
            
        # 從描述中提取
        if func.description:
            if "必須" in func.description or "must" in func.description.lower():
                return func.description.split("。")[0]
                
        return None
        
    def _extract_entity_from_name(self, name: str) -> str:
        """從函數名提取實體名"""
        # 移除常見前綴
        prefixes = ["validate_", "calculate_", "process_", "get_", "set_", "update_"]
        clean_name = name
        for prefix in prefixes:
            if name.startswith(prefix):
                clean_name = name[len(prefix):]
                break
                
        # 轉換為可讀格式
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', clean_name)
        return " ".join(words).capitalize()
        
    def _analyze_project_architecture(self, path: Path, modules: List[ModuleSpec]) -> Dict[str, Any]:
        """分析項目架構"""
        architecture = {
            "type": "unknown",
            "layers": [],
            "patterns": [],
            "style": "monolithic"  # or "microservices"
        }
        
        # 檢測常見架構模式
        dir_names = [d.name for d in path.iterdir() if d.is_dir()]
        
        # MVC/MVP/MVVM
        if any(name in dir_names for name in ["models", "views", "controllers"]):
            architecture["type"] = "MVC"
            architecture["layers"] = ["Model", "View", "Controller"]
            
        # 分層架構
        elif any(name in dir_names for name in ["domain", "application", "infrastructure"]):
            architecture["type"] = "DDD"
            architecture["layers"] = ["Domain", "Application", "Infrastructure", "Presentation"]
            
        # 微服務
        elif any(name in dir_names for name in ["services", "api-gateway"]):
            architecture["style"] = "microservices"
            
        # 分析使用的設計模式
        patterns = set()
        for module in modules:
            for cls in module.classes:
                if cls.design_pattern:
                    patterns.add(cls.design_pattern)
                    
        architecture["patterns"] = list(patterns)
        
        return architecture
        
    def _extract_api_endpoints(self, modules: List[ModuleSpec]) -> List[Dict[str, Any]]:
        """提取 API 端點"""
        endpoints = []
        
        # 常見的 API 裝飾器
        api_decorators = ["route", "app.route", "api.route", "get", "post", "put", "delete"]
        
        for module in modules:
            for func in module.functions:
                # 檢查函數名和參數
                if any(keyword in func.name.lower() for keyword in ["api", "endpoint", "route"]):
                    endpoint = {
                        "path": f"/{func.name}",
                        "method": self._infer_http_method(func.name),
                        "description": func.description,
                        "parameters": func.parameters,
                        "response": {"type": func.return_type}
                    }
                    endpoints.append(endpoint)
                    
        return endpoints
        
    def _infer_http_method(self, func_name: str) -> str:
        """推斷 HTTP 方法"""
        name_lower = func_name.lower()
        
        if any(keyword in name_lower for keyword in ["get", "fetch", "list", "retrieve"]):
            return "GET"
        elif any(keyword in name_lower for keyword in ["create", "add", "post"]):
            return "POST"
        elif any(keyword in name_lower for keyword in ["update", "modify", "put"]):
            return "PUT"
        elif any(keyword in name_lower for keyword in ["delete", "remove"]):
            return "DELETE"
        else:
            return "GET"
            
    def _extract_database_schema(self, modules: List[ModuleSpec]) -> Dict[str, Any]:
        """提取數據庫模式"""
        schema = {
            "tables": [],
            "relationships": []
        }
        
        # 查找模型類
        for module in modules:
            if "model" in module.name.lower():
                for cls in module.classes:
                    # 檢查是否是數據模型
                    if any(base in cls.inheritance for base in ["Model", "Base", "Document"]):
                        table = {
                            "name": cls.name.lower() + "s",  # 複數形式
                            "columns": []
                        }
                        
                        # 從屬性提取列
                        for attr in cls.attributes:
                            column = {
                                "name": attr["name"],
                                "type": self._map_to_db_type(attr["type"]),
                                "nullable": True,
                                "description": attr.get("description", "")
                            }
                            table["columns"].append(column)
                            
                        schema["tables"].append(table)
                        
        return schema
        
    def _map_to_db_type(self, python_type: str) -> str:
        """映射 Python 類型到數據庫類型"""
        type_mapping = {
            "str": "VARCHAR",
            "int": "INTEGER",
            "float": "DECIMAL",
            "bool": "BOOLEAN",
            "datetime": "TIMESTAMP",
            "date": "DATE",
            "list": "JSON",
            "dict": "JSON"
        }
        
        return type_mapping.get(python_type, "VARCHAR")
        
    def _analyze_deployment_requirements(self, path: Path) -> Dict[str, Any]:
        """分析部署需求"""
        requirements = {
            "runtime": "python3.8+",
            "dependencies": [],
            "environment_variables": [],
            "ports": [],
            "volumes": [],
            "services": []
        }
        
        # 檢查 requirements.txt
        req_file = path / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                requirements["dependencies"] = [
                    line.strip() for line in f 
                    if line.strip() and not line.startswith("#")
                ]
                
        # 檢查 Dockerfile
        dockerfile = path / "Dockerfile"
        if dockerfile.exists():
            with open(dockerfile, 'r') as f:
                content = f.read()
                # 提取端口
                ports = re.findall(r'EXPOSE\s+(\d+)', content)
                requirements["ports"] = ports
                
        # 檢查 docker-compose.yml
        compose_file = path / "docker-compose.yml"
        if compose_file.exists():
            # 簡單提取服務名
            with open(compose_file, 'r') as f:
                content = f.read()
                services = re.findall(r'^  (\w+):', content, re.MULTILINE)
                requirements["services"] = services
                
        return requirements
        
    def _detect_version(self, path: Path) -> str:
        """檢測項目版本"""
        # 檢查常見版本文件
        version_files = ["version.py", "__version__.py", "VERSION", "version.txt"]
        
        for vf in version_files:
            version_file = path / vf
            if version_file.exists():
                with open(version_file, 'r') as f:
                    content = f.read()
                    # 提取版本號
                    match = re.search(r'(\d+\.\d+\.\d+)', content)
                    if match:
                        return match.group(1)
                        
        # 檢查 setup.py
        setup_file = path / "setup.py"
        if setup_file.exists():
            with open(setup_file, 'r') as f:
                content = f.read()
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
                    
        return "1.0.0"
        
    def _generate_project_description(self, modules: List[ModuleSpec]) -> str:
        """生成項目描述"""
        # 統計信息
        total_classes = sum(len(m.classes) for m in modules)
        total_functions = sum(len(m.functions) for m in modules)
        
        # 識別主要功能
        main_features = set()
        for module in modules:
            for keyword in self.business_keywords:
                if keyword in module.name.lower():
                    main_features.add(keyword)
                    
        features_str = ", ".join(main_features) if main_features else "通用功能"
        
        return f"包含 {len(modules)} 個模組、{total_classes} 個類和 {total_functions} 個函數的項目。主要功能包括: {features_str}"
        
    def _extract_module_docstring(self, tree: ast.Module) -> str:
        """提取模組文檔字符串"""
        return ast.get_docstring(tree) or "未提供模組描述"
        
    def _extract_imports(self, tree: ast.Module) -> List[str]:
        """提取導入"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports
        
    def _extract_exports(self, tree: ast.Module) -> List[str]:
        """提取導出（__all__）"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            return [
                                elt.s for elt in node.value.elts 
                                if isinstance(elt, ast.Str)
                            ]
        return []
        
    def _get_annotation(self, annotation) -> str:
        """獲取類型註解"""
        if annotation is None:
            return "Any"
        elif isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        else:
            return "Any"
            
    def _get_value_repr(self, value) -> Any:
        """獲取值的表示"""
        if isinstance(value, ast.Constant):
            return value.value
        elif isinstance(value, ast.List):
            return [self._get_value_repr(elt) for elt in value.elts]
        elif isinstance(value, ast.Dict):
            return {
                self._get_value_repr(k): self._get_value_repr(v)
                for k, v in zip(value.keys, value.values)
            }
        else:
            return "..."
            
    def _extract_attributes_from_init(self, init_func: ast.FunctionDef) -> List[Dict[str, Any]]:
        """從 __init__ 方法提取屬性"""
        attributes = []
        
        for node in ast.walk(init_func):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                        if target.value.id == "self":
                            attr = {
                                "name": target.attr,
                                "type": "Any",  # 需要更複雜的類型推斷
                                "description": ""
                            }
                            attributes.append(attr)
                            
        return attributes
        
    def _detect_design_pattern(self, class_spec: ClassSpec) -> Optional[str]:
        """檢測設計模式"""
        method_names = [m.name for m in class_spec.methods]
        
        # 檢查各種模式
        for pattern, indicators in self.patterns.items():
            if any(indicator in method_names for indicator in indicators):
                return pattern
                
        # 檢查特殊模式
        if "__new__" in method_names and "_instance" in [a["name"] for a in class_spec.attributes]:
            return "singleton"
            
        return None
        
    def _calculate_complexity(self, node: ast.FunctionDef) -> str:
        """計算函數複雜度"""
        # 簡單的圈複雜度計算
        complexity = 1  # 基礎複雜度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
                
        if complexity <= 3:
            return "低"
        elif complexity <= 7:
            return "中"
        else:
            return "高"
            
    def _extract_exceptions(self, node: ast.FunctionDef) -> List[str]:
        """提取可能拋出的異常"""
        exceptions = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
                    exceptions.append(child.exc.func.id)
                    
        return list(set(exceptions))
        
    def _extract_function_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """提取函數依賴"""
        dependencies = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    dependencies.append(f"{child.func.value.id if isinstance(child.func.value, ast.Name) else '...'}.{child.func.attr}")
                    
        return list(set(dependencies))[:10]  # 限制數量
        
    def _generate_function_examples(self, node: ast.FunctionDef, parameters: List[Dict]) -> List[str]:
        """生成函數使用示例"""
        examples = []
        
        # 基本調用示例
        param_names = [p["name"] for p in parameters if p["name"] != "self"]
        if param_names:
            example = f"{node.name}({', '.join(param_names)})"
        else:
            example = f"{node.name}()"
            
        examples.append(example)
        
        # 如果有類型信息，生成具體示例
        if parameters:
            concrete_params = []
            for param in parameters:
                if param["name"] == "self":
                    continue
                    
                param_type = param.get("type", "Any")
                if param_type == "str":
                    concrete_params.append('"example"')
                elif param_type == "int":
                    concrete_params.append("42")
                elif param_type == "bool":
                    concrete_params.append("True")
                elif param_type == "list":
                    concrete_params.append("[]")
                elif param_type == "dict":
                    concrete_params.append("{}")
                else:
                    concrete_params.append(f"{param['name']}_value")
                    
            if concrete_params:
                concrete_example = f"{node.name}({', '.join(concrete_params)})"
                examples.append(concrete_example)
                
        return examples
        
    def _infer_function_purpose(self, node: ast.FunctionDef) -> str:
        """推斷函數用途"""
        name_lower = node.name.lower()
        
        # 基於常見模式推斷
        if name_lower.startswith("get_"):
            return f"獲取 {self._extract_entity_from_name(node.name)}"
        elif name_lower.startswith("set_"):
            return f"設置 {self._extract_entity_from_name(node.name)}"
        elif name_lower.startswith("is_"):
            return f"檢查 {self._extract_entity_from_name(node.name)} 狀態"
        elif name_lower.startswith("validate_"):
            return f"驗證 {self._extract_entity_from_name(node.name)}"
        elif name_lower.startswith("calculate_"):
            return f"計算 {self._extract_entity_from_name(node.name)}"
        else:
            return f"處理 {self._extract_entity_from_name(node.name)} 相關邏輯"
            
    def _analyze_dependencies(self, module_spec: ModuleSpec) -> List[str]:
        """分析模組依賴"""
        deps = set()
        
        # 從導入提取
        for imp in module_spec.imports:
            base_module = imp.split('.')[0]
            if base_module not in ['os', 'sys', 'json', 'datetime', 're']:  # 排除標準庫
                deps.add(base_module)
                
        # 從函數依賴提取
        for func in module_spec.functions:
            for dep in func.dependencies:
                if '.' in dep:
                    base = dep.split('.')[0]
                    if base not in ['self', 'cls']:
                        deps.add(base)
                        
        return list(deps)
        
    async def generate_spec_document(self, spec: ProjectSpec, output_format: str = "markdown") -> str:
        """生成規格文檔"""
        if output_format == "markdown":
            return self._generate_markdown_spec(spec)
        elif output_format == "json":
            return json.dumps(asdict(spec), indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的輸出格式: {output_format}")
            
    def _generate_markdown_spec(self, spec: ProjectSpec) -> str:
        """生成 Markdown 格式的規格文檔"""
        md = f"""# {spec.name} 技術規格文檔

## 項目概述

**版本**: {spec.version}

**描述**: {spec.description}

## 系統架構

**架構類型**: {spec.architecture['type']}
**架構風格**: {spec.architecture['style']}

### 架構層次
{self._format_list(spec.architecture.get('layers', []))}

### 使用的設計模式
{self._format_list(spec.architecture.get('patterns', []))}

## 模組結構

"""
        
        # 添加模組詳情
        for module in spec.modules:
            md += f"\n### 📦 {module.name}\n\n"
            md += f"**描述**: {module.description}\n\n"
            
            if module.classes:
                md += "#### 類定義\n\n"
                for cls in module.classes:
                    md += f"##### `{cls.name}`\n"
                    if cls.inheritance:
                        md += f"- 繼承: {', '.join(cls.inheritance)}\n"
                    if cls.design_pattern:
                        md += f"- 設計模式: {cls.design_pattern}\n"
                    md += f"- 描述: {cls.description}\n"
                    
                    if cls.methods:
                        md += "\n**方法**:\n"
                        for method in cls.methods[:5]:  # 限制顯示數量
                            params = ", ".join([p['name'] for p in method.parameters])
                            md += f"- `{method.name}({params})` -> {method.return_type}\n"
                            
                    md += "\n"
                    
            if module.functions:
                md += "#### 函數\n\n"
                for func in module.functions[:10]:  # 限制顯示數量
                    params = ", ".join([p['name'] for p in func.parameters])
                    md += f"- `{func.name}({params})` -> {func.return_type}\n"
                    md += f"  - {func.description}\n"
                    md += f"  - 複雜度: {func.complexity}\n\n"
                    
        # API 端點
        if spec.api_endpoints:
            md += "\n## API 端點\n\n"
            for endpoint in spec.api_endpoints:
                md += f"### {endpoint['method']} {endpoint['path']}\n"
                md += f"**描述**: {endpoint['description']}\n\n"
                
        # 數據庫結構
        if spec.database_schema.get('tables'):
            md += "\n## 數據庫結構\n\n"
            for table in spec.database_schema['tables']:
                md += f"### 表: {table['name']}\n\n"
                md += "| 列名 | 類型 | 描述 |\n"
                md += "|------|------|------|\n"
                for col in table['columns']:
                    md += f"| {col['name']} | {col['type']} | {col['description']} |\n"
                md += "\n"
                
        # 業務規則
        if spec.business_rules:
            md += "\n## 業務規則\n\n"
            for i, rule in enumerate(spec.business_rules, 1):
                md += f"{i}. {rule}\n"
                
        # 部署需求
        if spec.deployment_requirements:
            md += "\n## 部署需求\n\n"
            md += f"**運行時**: {spec.deployment_requirements['runtime']}\n\n"
            
            if spec.deployment_requirements['dependencies']:
                md += "### 依賴\n"
                for dep in spec.deployment_requirements['dependencies'][:20]:
                    md += f"- {dep}\n"
                    
            if spec.deployment_requirements['services']:
                md += "\n### 服務\n"
                for service in spec.deployment_requirements['services']:
                    md += f"- {service}\n"
                    
        return md
        
    def _format_list(self, items: List[str]) -> str:
        """格式化列表"""
        if not items:
            return "- 無\n"
        return "\n".join([f"- {item}" for item in items]) + "\n"
        
    async def _generate_javascript_spec(self, code_path: str) -> ProjectSpec:
        """從 JavaScript 代碼生成規格（待實現）"""
        # TODO: 實現 JavaScript 代碼分析
        raise NotImplementedError("JavaScript 代碼分析尚未實現")
        
    async def _generate_typescript_spec(self, code_path: str) -> ProjectSpec:
        """從 TypeScript 代碼生成規格（待實現）"""
        # TODO: 實現 TypeScript 代碼分析
        raise NotImplementedError("TypeScript 代碼分析尚未實現")


# 創建全局實例
code_to_spec_generator = CodeToSpecGenerator()


async def generate_spec_from_code(code_path: str, language: str = "python") -> str:
    """便捷函數：從代碼生成規格文檔"""
    spec = await code_to_spec_generator.generate_spec_from_code(code_path, language)
    doc = await code_to_spec_generator.generate_spec_document(spec, "markdown")
    
    # 保存到文件
    output_path = Path(code_path).with_suffix('.spec.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc)
        
    print(f"✅ 規格文檔已生成: {output_path}")
    return doc