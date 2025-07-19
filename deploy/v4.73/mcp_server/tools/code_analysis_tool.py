"""
代码分析工具
提供代码质量分析、安全检查、性能优化建议等功能
"""

import ast
import logging
import re
from typing import Any, Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class CodeAnalysisTool:
    """代码分析工具类"""
    
    def __init__(self):
        """初始化代码分析工具"""
        self.analyzers = {
            "python": self._analyze_python,
            "javascript": self._analyze_javascript,
            "typescript": self._analyze_typescript,
            "java": self._analyze_java,
            "cpp": self._analyze_cpp,
            "go": self._analyze_go,
            "rust": self._analyze_rust
        }
    
    async def analyze(self, code: str, language: str, analysis_type: str = "all") -> Dict[str, Any]:
        """
        分析代码
        
        Args:
            code: 代码内容
            language: 编程语言
            analysis_type: 分析类型
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"🔍 代码分析: {language} - {analysis_type}")
            
            # 基础分析
            basic_analysis = self._basic_analysis(code)
            
            # 语言特定分析
            language_analysis = {}
            if language in self.analyzers:
                language_analysis = await self.analyzers[language](code)
            
            # 根据分析类型筛选结果
            result = {
                "language": language,
                "analysis_type": analysis_type,
                "basic_metrics": basic_analysis,
                "language_specific": language_analysis,
                "recommendations": self._generate_recommendations(basic_analysis, language_analysis),
                "status": "success"
            }
            
            # 根据analysis_type过滤结果
            if analysis_type != "all":
                result = self._filter_by_analysis_type(result, analysis_type)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 代码分析失败: {e}")
            return {
                "language": language,
                "analysis_type": analysis_type,
                "error": str(e),
                "status": "error"
            }
    
    def _basic_analysis(self, code: str) -> Dict[str, Any]:
        """基础代码分析"""
        lines = code.split('\\n')
        
        return {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0,
            "max_line_length": max(len(line) for line in lines) if lines else 0,
            "character_count": len(code),
            "estimated_complexity": self._estimate_complexity(code)
        }
    
    def _estimate_complexity(self, code: str) -> str:
        """估算代码复杂度"""
        # 简单的复杂度估算
        complexity_indicators = [
            'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally',
            'switch', 'case', 'catch', 'function', 'def', 'class'
        ]
        
        complexity_score = 0
        for indicator in complexity_indicators:
            complexity_score += len(re.findall(r'\\b' + indicator + r'\\b', code, re.IGNORECASE))
        
        if complexity_score < 5:
            return "low"
        elif complexity_score < 15:
            return "medium"
        else:
            return "high"
    
    async def _analyze_python(self, code: str) -> Dict[str, Any]:
        """Python代码分析"""
        try:
            tree = ast.parse(code)
            
            # 统计不同类型的节点
            node_counts = {}
            security_issues = []
            quality_issues = []
            
            for node in ast.walk(tree):
                node_type = type(node).__name__
                node_counts[node_type] = node_counts.get(node_type, 0) + 1
                
                # 安全检查
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', 'compile']:
                            security_issues.append(f"潜在安全风险: 使用了 {node.func.id} 函数")
                
                # 质量检查
                if isinstance(node, ast.FunctionDef):
                    if len(node.args.args) > 5:
                        quality_issues.append(f"函数 {node.name} 参数过多 ({len(node.args.args)}个)")
            
            return {
                "node_counts": node_counts,
                "functions": node_counts.get('FunctionDef', 0),
                "classes": node_counts.get('ClassDef', 0),
                "imports": node_counts.get('Import', 0) + node_counts.get('ImportFrom', 0),
                "security_issues": security_issues,
                "quality_issues": quality_issues,
                "syntax_valid": True
            }
            
        except SyntaxError as e:
            return {
                "syntax_valid": False,
                "syntax_error": str(e),
                "error_line": e.lineno,
                "error_offset": e.offset
            }
    
    async def _analyze_javascript(self, code: str) -> Dict[str, Any]:
        """JavaScript代码分析"""
        # 基础的JavaScript分析
        patterns = {
            'functions': r'function\\s+\\w+|\\w+\\s*=>|\\w+\\s*:\\s*function',
            'variables': r'(?:var|let|const)\\s+\\w+',
            'classes': r'class\\s+\\w+',
            'imports': r'import\\s+.*?from|require\\s*\\(',
            'exports': r'export\\s+|module\\.exports',
            'async_await': r'async\\s+function|await\\s+',
            'promises': r'\\.then\\s*\\(|\\.catch\\s*\\(',
            'console_logs': r'console\\.log\\s*\\('
        }
        
        results = {}
        issues = []
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, code, re.IGNORECASE)
            results[pattern_name] = len(matches)
        
        # 检查潜在问题
        if results['console_logs'] > 0:
            issues.append(f"发现 {results['console_logs']} 个console.log，建议在生产环境中移除")
        
        return {
            "counts": results,
            "quality_issues": issues,
            "estimated_functions": results['functions'],
            "uses_modern_syntax": results['async_await'] > 0 or 'const' in code or 'let' in code
        }
    
    async def _analyze_typescript(self, code: str) -> Dict[str, Any]:
        """TypeScript代码分析"""
        # 继承JavaScript分析，添加TypeScript特定检查
        js_analysis = await self._analyze_javascript(code)
        
        # TypeScript特定模式
        ts_patterns = {
            'interfaces': r'interface\\s+\\w+',
            'types': r'type\\s+\\w+\\s*=',
            'generics': r'<[^>]+>',
            'type_annotations': r':\\s*\\w+',
            'enums': r'enum\\s+\\w+'
        }
        
        ts_results = {}
        for pattern_name, pattern in ts_patterns.items():
            matches = re.findall(pattern, code)
            ts_results[pattern_name] = len(matches)
        
        return {
            **js_analysis,
            "typescript_specific": ts_results,
            "has_type_annotations": ts_results['type_annotations'] > 0,
            "type_safety_score": self._calculate_type_safety_score(code, ts_results)
        }
    
    def _calculate_type_safety_score(self, code: str, ts_results: Dict[str, int]) -> str:
        """计算类型安全评分"""
        score = 0
        
        # 有类型注解加分
        if ts_results['type_annotations'] > 0:
            score += 2
        
        # 有接口定义加分
        if ts_results['interfaces'] > 0:
            score += 2
        
        # 有泛型使用加分
        if ts_results['generics'] > 0:
            score += 1
        
        # 检查any类型的使用（减分）
        any_count = len(re.findall(r':\\s*any\\b', code))
        score -= any_count
        
        if score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"
    
    async def _analyze_java(self, code: str) -> Dict[str, Any]:
        """Java代码分析"""
        patterns = {
            'classes': r'class\\s+\\w+',
            'methods': r'(?:public|private|protected)\\s+.*?\\w+\\s*\\(',
            'imports': r'import\\s+[\\w.]+;',
            'packages': r'package\\s+[\\w.]+;',
            'annotations': r'@\\w+',
            'try_catch': r'try\\s*\\{|catch\\s*\\(',
            'synchronized': r'synchronized\\s*\\('
        }
        
        results = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, code)
            results[pattern_name] = len(matches)
        
        return {
            "counts": results,
            "has_error_handling": results['try_catch'] > 0,
            "uses_annotations": results['annotations'] > 0,
            "thread_safety_indicators": results['synchronized']
        }
    
    async def _analyze_cpp(self, code: str) -> Dict[str, Any]:
        """C++代码分析"""
        patterns = {
            'classes': r'class\\s+\\w+',
            'functions': r'\\w+\\s+\\w+\\s*\\(',
            'includes': r'#include\\s*<.*?>|#include\\s*".*?"',
            'namespaces': r'namespace\\s+\\w+',
            'templates': r'template\\s*<.*?>',
            'pointers': r'\\*\\w+|\\w+\\s*\\*',
            'references': r'&\\w+|\\w+\\s*&',
            'new_delete': r'\\bnew\\b|\\bdelete\\b'
        }
        
        results = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, code)
            results[pattern_name] = len(matches)
        
        return {
            "counts": results,
            "uses_templates": results['templates'] > 0,
            "memory_management": results['new_delete'] > 0,
            "uses_modern_cpp": 'auto' in code or 'nullptr' in code
        }
    
    async def _analyze_go(self, code: str) -> Dict[str, Any]:
        """Go代码分析"""
        patterns = {
            'functions': r'func\\s+\\w+',
            'structs': r'type\\s+\\w+\\s+struct',
            'interfaces': r'type\\s+\\w+\\s+interface',
            'imports': r'import\\s+.*?\\n',
            'goroutines': r'go\\s+\\w+',
            'channels': r'make\\s*\\(\\s*chan|<-\\s*\\w+|\\w+\\s*<-',
            'defer': r'\\bdefer\\b'
        }
        
        results = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, code)
            results[pattern_name] = len(matches)
        
        return {
            "counts": results,
            "uses_concurrency": results['goroutines'] > 0 or results['channels'] > 0,
            "uses_defer": results['defer'] > 0,
            "go_specific_features": results['goroutines'] + results['channels'] + results['defer']
        }
    
    async def _analyze_rust(self, code: str) -> Dict[str, Any]:
        """Rust代码分析"""
        patterns = {
            'functions': r'fn\\s+\\w+',
            'structs': r'struct\\s+\\w+',
            'enums': r'enum\\s+\\w+',
            'traits': r'trait\\s+\\w+',
            'impls': r'impl\\s+.*?\\{',
            'macros': r'\\w+!\\s*\\(',
            'unsafe': r'unsafe\\s*\\{',
            'lifetimes': r"\\\\'\\w+",
            'generics': r'<[^>]*>'
        }
        
        results = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, code)
            results[pattern_name] = len(matches)
        
        return {
            "counts": results,
            "uses_unsafe": results['unsafe'] > 0,
            "uses_lifetimes": results['lifetimes'] > 0,
            "macro_usage": results['macros'],
            "safety_score": "high" if results['unsafe'] == 0 else "medium"
        }
    
    def _generate_recommendations(self, basic_analysis: Dict[str, Any], language_analysis: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于基础分析的建议
        if basic_analysis["max_line_length"] > 100:
            recommendations.append("建议将长行代码拆分为多行，提高可读性")
        
        if basic_analysis["estimated_complexity"] == "high":
            recommendations.append("代码复杂度较高，建议重构为更小的函数")
        
        comment_ratio = basic_analysis["comment_lines"] / basic_analysis["total_lines"] if basic_analysis["total_lines"] > 0 else 0
        if comment_ratio < 0.1:
            recommendations.append("代码注释较少，建议增加必要的注释")
        
        # 基于语言特定分析的建议
        if "security_issues" in language_analysis and language_analysis["security_issues"]:
            recommendations.extend(language_analysis["security_issues"])
        
        if "quality_issues" in language_analysis and language_analysis["quality_issues"]:
            recommendations.extend(language_analysis["quality_issues"])
        
        return recommendations
    
    def _filter_by_analysis_type(self, result: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """根据分析类型过滤结果"""
        if analysis_type == "quality":
            return {
                "language": result["language"],
                "analysis_type": analysis_type,
                "basic_metrics": result["basic_metrics"],
                "quality_issues": result["language_specific"].get("quality_issues", []),
                "recommendations": result["recommendations"],
                "status": result["status"]
            }
        elif analysis_type == "security":
            return {
                "language": result["language"],
                "analysis_type": analysis_type,
                "security_issues": result["language_specific"].get("security_issues", []),
                "recommendations": [r for r in result["recommendations"] if "安全" in r],
                "status": result["status"]
            }
        elif analysis_type == "performance":
            return {
                "language": result["language"],
                "analysis_type": analysis_type,
                "complexity": result["basic_metrics"]["estimated_complexity"],
                "recommendations": [r for r in result["recommendations"] if "性能" in r or "复杂" in r],
                "status": result["status"]
            }
        elif analysis_type == "structure":
            return {
                "language": result["language"],
                "analysis_type": analysis_type,
                "basic_metrics": result["basic_metrics"],
                "language_specific": result["language_specific"],
                "status": result["status"]
            }
        
        return result