"""
Document Processor - PowerAutomation v4.8

专业的文档处理和预处理功能，包括:
- 代码文件智能解析
- 多语言代码注释提取
- 函数和类结构分析
- 智能语义分块
- 代码依赖关系分析

设计原则:
- 针对编程项目优化
- 保持代码结构的语义完整性
- 支持多种编程语言
- 与 Claude Code 工具输出兼容
"""

import os
import re
import ast
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import asyncio

# 代码解析库
try:
    import tree_sitter
    from tree_sitter import Language, Parser
except ImportError:
    tree_sitter = None
    Language = None
    Parser = None

@dataclass
class CodeElement:
    """代码元素数据结构"""
    element_type: str  # function, class, method, variable, import
    name: str
    content: str
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    parameters: List[str] = None
    return_type: Optional[str] = None
    decorators: List[str] = None
    parent: Optional[str] = None

@dataclass
class ProcessedDocument:
    """处理后的文档数据结构"""
    file_path: str
    file_type: str
    language: Optional[str]
    raw_content: str
    processed_content: str
    code_elements: List[CodeElement]
    imports: List[str]
    dependencies: List[str]
    metadata: Dict[str, Any]
    processing_time: float

class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化文档处理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 配置参数
        self.preserve_code_structure = self.config.get("preserve_code_structure", True)
        self.extract_docstrings = self.config.get("extract_docstrings", True)
        self.analyze_dependencies = self.config.get("analyze_dependencies", True)
        self.min_function_lines = self.config.get("min_function_lines", 3)
        
        # 支持的编程语言
        self.supported_languages = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".less": "less",
            ".xml": "xml",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".ini": "ini",
            ".cfg": "ini",
            ".conf": "ini"
        }
        
        # 初始化组件
        self.logger = logging.getLogger(__name__)
        
        # 处理统计
        self.stats = {
            "files_processed": 0,
            "code_elements_extracted": 0,
            "total_processing_time": 0.0,
            "language_distribution": {},
            "last_updated": datetime.now()
        }
    
    async def process_document(self, file_path: str, content: str = None) -> ProcessedDocument:
        """
        处理单个文档
        
        Args:
            file_path: 文件路径
            content: 文件内容（可选，如果不提供则从文件读取）
            
        Returns:
            处理后的文档对象
        """
        try:
            start_time = datetime.now()
            
            path = Path(file_path)
            file_type = path.suffix.lower()
            language = self.supported_languages.get(file_type)
            
            # 读取内容
            if content is None:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            # 根据文件类型选择处理方法
            if language in ["python", "javascript", "typescript", "java", "cpp", "c"]:
                processed_content, code_elements, imports, dependencies = await self._process_code_file(
                    content, language, file_path
                )
            elif file_type in [".md", ".rst", ".txt"]:
                processed_content, code_elements, imports, dependencies = await self._process_text_file(
                    content, file_path
                )
            elif file_type in [".json", ".yaml", ".yml"]:
                processed_content, code_elements, imports, dependencies = await self._process_config_file(
                    content, file_type, file_path
                )
            else:
                # 默认文本处理
                processed_content = content
                code_elements = []
                imports = []
                dependencies = []
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 生成元数据
            metadata = {
                "file_size": len(content),
                "line_count": len(content.splitlines()),
                "language": language,
                "file_type": file_type,
                "has_code_elements": len(code_elements) > 0,
                "imports_count": len(imports),
                "dependencies_count": len(dependencies),
                "processed_at": datetime.now().isoformat(),
                "processing_time": processing_time
            }
            
            # 更新统计
            self.stats["files_processed"] += 1
            self.stats["code_elements_extracted"] += len(code_elements)
            self.stats["total_processing_time"] += processing_time
            
            if language:
                self.stats["language_distribution"][language] = \
                    self.stats["language_distribution"].get(language, 0) + 1
            
            result = ProcessedDocument(
                file_path=file_path,
                file_type=file_type,
                language=language,
                raw_content=content,
                processed_content=processed_content,
                code_elements=code_elements,
                imports=imports,
                dependencies=dependencies,
                metadata=metadata,
                processing_time=processing_time
            )
            
            self.logger.info(f"文档处理完成: {path.name} ({len(code_elements)} 个代码元素)")
            return result
            
        except Exception as e:
            self.logger.error(f"文档处理失败 {file_path}: {str(e)}")
            raise
    
    async def _process_code_file(self, content: str, language: str, file_path: str) -> Tuple[str, List[CodeElement], List[str], List[str]]:
        """处理代码文件"""
        try:
            if language == "python":
                return await self._process_python_file(content, file_path)
            elif language in ["javascript", "typescript"]:
                return await self._process_javascript_file(content, file_path)
            elif language == "java":
                return await self._process_java_file(content, file_path)
            elif language in ["cpp", "c"]:
                return await self._process_cpp_file(content, file_path)
            else:
                # 通用代码处理
                return await self._process_generic_code_file(content, language, file_path)
                
        except Exception as e:
            self.logger.error(f"代码文件处理失败: {str(e)}")
            return content, [], [], []
    
    async def _process_python_file(self, content: str, file_path: str) -> Tuple[str, List[CodeElement], List[str], List[str]]:
        """处理 Python 文件"""
        try:
            code_elements = []
            imports = []
            dependencies = []
            
            # 解析 AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.logger.warning(f"Python 语法错误 {file_path}: {str(e)}")
                return content, [], [], []
            
            # 遍历 AST 节点
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    element = self._extract_python_function(node, content)
                    code_elements.append(element)
                
                elif isinstance(node, ast.ClassDef):
                    element = self._extract_python_class(node, content)
                    code_elements.append(element)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._extract_python_import(node)
                    imports.extend(import_info)
            
            # 提取依赖关系
            dependencies = self._extract_python_dependencies(imports)
            
            # 生成处理后的内容
            processed_content = self._generate_processed_content(content, code_elements)
            
            return processed_content, code_elements, imports, dependencies
            
        except Exception as e:
            self.logger.error(f"Python 文件处理失败: {str(e)}")
            return content, [], [], []
    
    def _extract_python_function(self, node: ast.FunctionDef, content: str) -> CodeElement:
        """提取 Python 函数信息"""
        lines = content.splitlines()
        
        # 获取函数内容
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
        function_content = '\n'.join(lines[start_line:end_line])
        
        # 提取文档字符串
        docstring = None
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
        
        # 提取参数
        parameters = [arg.arg for arg in node.args.args]
        
        # 提取装饰器
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(f"{decorator.attr}")
        
        # 提取返回类型
        return_type = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return_type = str(node.returns.value)
        
        return CodeElement(
            element_type="function",
            name=node.name,
            content=function_content,
            start_line=start_line + 1,
            end_line=end_line,
            docstring=docstring,
            parameters=parameters,
            return_type=return_type,
            decorators=decorators
        )
    
    def _extract_python_class(self, node: ast.ClassDef, content: str) -> CodeElement:
        """提取 Python 类信息"""
        lines = content.splitlines()
        
        # 获取类内容
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
        class_content = '\n'.join(lines[start_line:end_line])
        
        # 提取文档字符串
        docstring = None
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
        
        # 提取基类
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
        
        # 提取装饰器
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
        
        return CodeElement(
            element_type="class",
            name=node.name,
            content=class_content,
            start_line=start_line + 1,
            end_line=end_line,
            docstring=docstring,
            parameters=base_classes,  # 使用 parameters 存储基类
            decorators=decorators
        )
    
    def _extract_python_import(self, node) -> List[str]:
        """提取 Python 导入信息"""
        imports = []
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    imports.append(f"{module}.*")
                else:
                    imports.append(f"{module}.{alias.name}")
        
        return imports
    
    def _extract_python_dependencies(self, imports: List[str]) -> List[str]:
        """提取 Python 依赖关系"""
        dependencies = []
        
        # 标准库模块（部分）
        stdlib_modules = {
            "os", "sys", "json", "re", "datetime", "time", "math", "random",
            "collections", "itertools", "functools", "pathlib", "typing",
            "asyncio", "threading", "multiprocessing", "logging", "unittest"
        }
        
        for imp in imports:
            # 提取顶级模块名
            top_module = imp.split('.')[0]
            
            # 跳过标准库
            if top_module not in stdlib_modules:
                if top_module not in dependencies:
                    dependencies.append(top_module)
        
        return dependencies
    
    async def _process_javascript_file(self, content: str, file_path: str) -> Tuple[str, List[CodeElement], List[str], List[str]]:
        """处理 JavaScript/TypeScript 文件"""
        try:
            code_elements = []
            imports = []
            dependencies = []
            
            lines = content.splitlines()
            
            # 使用正则表达式提取函数
            function_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))'
            for match in re.finditer(function_pattern, content, re.MULTILINE):
                func_name = match.group(1) or match.group(2)
                start_pos = match.start()
                
                # 找到函数的行号
                start_line = content[:start_pos].count('\n')
                
                # 简单的函数内容提取（可以改进）
                element = CodeElement(
                    element_type="function",
                    name=func_name,
                    content=lines[start_line] if start_line < len(lines) else "",
                    start_line=start_line + 1,
                    end_line=start_line + 1
                )
                code_elements.append(element)
            
            # 提取导入
            import_patterns = [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]',
                r'require\([\'"]([^\'"]+)[\'"]\)'
            ]
            
            for pattern in import_patterns:
                for match in re.finditer(pattern, content):
                    module_name = match.group(1)
                    imports.append(module_name)
                    
                    # 提取依赖（非相对路径）
                    if not module_name.startswith('.') and not module_name.startswith('/'):
                        dep_name = module_name.split('/')[0]
                        if dep_name not in dependencies:
                            dependencies.append(dep_name)
            
            processed_content = content
            return processed_content, code_elements, imports, dependencies
            
        except Exception as e:
            self.logger.error(f"JavaScript 文件处理失败: {str(e)}")
            return content, [], [], []
    
    async def _process_java_file(self, content: str, file_path: str) -> Tuple[str, List[CodeElement], List[str], List[str]]:
        """处理 Java 文件"""
        try:
            code_elements = []
            imports = []
            dependencies = []
            
            lines = content.splitlines()
            
            # 提取类
            class_pattern = r'(?:public\s+|private\s+|protected\s+)?class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                start_pos = match.start()
                start_line = content[:start_pos].count('\n')
                
                element = CodeElement(
                    element_type="class",
                    name=class_name,
                    content=lines[start_line] if start_line < len(lines) else "",
                    start_line=start_line + 1,
                    end_line=start_line + 1
                )
                code_elements.append(element)
            
            # 提取方法
            method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*{'
            for match in re.finditer(method_pattern, content):
                method_name = match.group(1)
                if method_name not in ['if', 'for', 'while', 'switch']:  # 排除关键字
                    start_pos = match.start()
                    start_line = content[:start_pos].count('\n')
                    
                    element = CodeElement(
                        element_type="method",
                        name=method_name,
                        content=lines[start_line] if start_line < len(lines) else "",
                        start_line=start_line + 1,
                        end_line=start_line + 1
                    )
                    code_elements.append(element)
            
            # 提取导入
            import_pattern = r'import\s+(?:static\s+)?([^;]+);'
            for match in re.finditer(import_pattern, content):
                import_name = match.group(1).strip()
                imports.append(import_name)
                
                # 提取包名作为依赖
                if '.' in import_name:
                    package = import_name.split('.')[0]
                    if package not in ['java', 'javax'] and package not in dependencies:
                        dependencies.append(package)
            
            processed_content = content
            return processed_content, code_elements, imports, dependencies
            
        except Exception as e:
            self.logger.error(f"Java 文件处理失败: {str(e)}")
            return content, [], [], []
    
    async def _process_cpp_file(self, content: str, file_path: str) -> Tuple[str, List[CodeElement], List[str], List[str]]:
        """处理 C/C++ 文件"""
        try:
            code_elements = []
            imports = []
            dependencies = []
            
            lines = content.splitlines()
            
            # 提取函数
            function_pattern = r'(?:(?:inline\s+)?(?:static\s+)?(?:virtual\s+)?(?:\w+\s+)*)?(\w+)\s*\([^)]*\)\s*(?:const\s*)?{'
            for match in re.finditer(function_pattern, content, re.MULTILINE):
                func_name = match.group(1)
                if func_name not in ['if', 'for', 'while', 'switch']:  # 排除关键字
                    start_pos = match.start()
                    start_line = content[:start_pos].count('\n')
                    
                    element = CodeElement(
                        element_type="function",
                        name=func_name,
                        content=lines[start_line] if start_line < len(lines) else "",
                        start_line=start_line + 1,
                        end_line=start_line + 1
                    )
                    code_elements.append(element)
            
            # 提取类
            class_pattern = r'class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                start_pos = match.start()
                start_line = content[:start_pos].count('\n')
                
                element = CodeElement(
                    element_type="class",
                    name=class_name,
                    content=lines[start_line] if start_line < len(lines) else "",
                    start_line=start_line + 1,
                    end_line=start_line + 1
                )
                code_elements.append(element)
            
            # 提取包含文件
            include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
            for match in re.finditer(include_pattern, content):
                include_name = match.group(1)
                imports.append(include_name)
                
                # 提取依赖（非标准库）
                if not include_name.startswith('std') and '/' not in include_name:
                    dep_name = include_name.replace('.h', '').replace('.hpp', '')
                    if dep_name not in dependencies:
                        dependencies.append(dep_name)
            
            processed_content = content
            return processed_content, code_elements, imports, dependencies
            
        except Exception as e:
            self.logger.error(f"C/C++ 文件处理失败: {str(e)}")
            return content, [], [], []
    
    async def _process_generic_code_file(self, content: str, language: str, file_path: str) -> Tuple[str, List[CodeElement], List[str], List[str]]:
        """处理通用代码文件"""
        # 简单的通用处理
        return content, [], [], []
    
    async def _process_text_file(self, content: str, file_path: str) -> Tuple[str, List[CodeElement], List[str], List[str]]:
        """处理文本文件"""
        # 对于文本文件，主要是清理和格式化
        processed_content = content.strip()
        
        # 提取代码块（如果是 Markdown）
        code_elements = []
        if file_path.endswith('.md'):
            code_block_pattern = r'```(\w+)?\n(.*?)\n```'
            for match in re.finditer(code_block_pattern, content, re.DOTALL):
                language = match.group(1) or "unknown"
                code_content = match.group(2)
                
                element = CodeElement(
                    element_type="code_block",
                    name=f"code_block_{language}",
                    content=code_content,
                    start_line=content[:match.start()].count('\n') + 1,
                    end_line=content[:match.end()].count('\n') + 1
                )
                code_elements.append(element)
        
        return processed_content, code_elements, [], []
    
    async def _process_config_file(self, content: str, file_type: str, file_path: str) -> Tuple[str, List[CodeElement], List[str], List[str]]:
        """处理配置文件"""
        try:
            dependencies = []
            
            if file_type == ".json":
                # 解析 JSON 配置
                data = json.loads(content)
                
                # 如果是 package.json，提取依赖
                if "dependencies" in data:
                    dependencies.extend(data["dependencies"].keys())
                if "devDependencies" in data:
                    dependencies.extend(data["devDependencies"].keys())
            
            return content, [], [], dependencies
            
        except Exception as e:
            self.logger.error(f"配置文件处理失败: {str(e)}")
            return content, [], [], []
    
    def _generate_processed_content(self, content: str, code_elements: List[CodeElement]) -> str:
        """生成处理后的内容"""
        if not self.preserve_code_structure:
            return content
        
        # 为代码元素添加注释
        lines = content.splitlines()
        processed_lines = []
        
        for i, line in enumerate(lines):
            processed_lines.append(line)
            
            # 检查是否有代码元素在这一行开始
            for element in code_elements:
                if element.start_line == i + 1:
                    comment = f"# {element.element_type.upper()}: {element.name}"
                    if element.docstring:
                        comment += f" - {element.docstring[:50]}..."
                    processed_lines.insert(-1, comment)
                    break
        
        return '\n'.join(processed_lines)
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            "processing_stats": self.stats.copy(),
            "supported_languages": list(self.supported_languages.values()),
            "timestamp": datetime.now().isoformat()
        }

