#!/usr/bin/env python3
"""
PowerAutomation 代碼重構分析器
使用 CodeFlow MCP 識別代碼重複、未使用代碼、代碼異味等問題
"""

import ast
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeFlowRefactoringAnalyzer:
    """代碼重構分析器"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.code_duplicates = []
        self.unused_code = []
        self.code_smells = []
        self.refactoring_suggestions = []
        
    def analyze(self) -> Dict[str, Any]:
        """執行完整的代碼分析"""
        logger.info(f"🔍 開始分析項目: {self.project_path}")
        
        # 1. 識別代碼重複
        self.find_code_duplicates()
        
        # 2. 查找未使用的代碼
        self.find_unused_code()
        
        # 3. 檢測代碼異味
        self.detect_code_smells()
        
        # 4. 生成重構建議
        self.generate_refactoring_suggestions()
        
        # 5. 生成執行計劃
        execution_plan = self.create_execution_plan()
        
        return {
            "project_path": str(self.project_path),
            "code_duplicates": self.code_duplicates,
            "unused_code": self.unused_code,
            "code_smells": self.code_smells,
            "refactoring_suggestions": self.refactoring_suggestions,
            "execution_plan": execution_plan
        }
    
    def find_code_duplicates(self):
        """識別代碼重複"""
        logger.info("🔎 識別代碼重複...")
        
        # 收集所有Python文件
        python_files = list(self.project_path.rglob("*.py"))
        
        # 分析函數和類的相似度
        function_signatures = defaultdict(list)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # 生成函數簽名的哈希
                            signature = self._get_function_signature(node)
                            sig_hash = hashlib.md5(signature.encode()).hexdigest()
                            function_signatures[sig_hash].append({
                                "file": str(file_path.relative_to(self.project_path)),
                                "function": node.name,
                                "line": node.lineno
                            })
                            
            except Exception as e:
                logger.warning(f"無法分析文件 {file_path}: {e}")
        
        # 找出重複的函數
        for sig_hash, occurrences in function_signatures.items():
            if len(occurrences) > 1:
                self.code_duplicates.append({
                    "type": "duplicate_function",
                    "occurrences": occurrences,
                    "suggestion": "考慮將重複的函數提取到共用模塊"
                })
        
        logger.info(f"✅ 找到 {len(self.code_duplicates)} 處代碼重複")
    
    def find_unused_code(self):
        """查找未使用的代碼"""
        logger.info("🔍 查找未使用的代碼...")
        
        # 收集所有定義的函數、類和變量
        definitions = set()
        usages = set()
        
        python_files = list(self.project_path.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    # 收集定義
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            definitions.add(("function", node.name, str(file_path)))
                        elif isinstance(node, ast.ClassDef):
                            definitions.add(("class", node.name, str(file_path)))
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                definitions.add(("import", alias.name, str(file_path)))
                    
                    # 收集使用
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name):
                            usages.add(node.id)
                        elif isinstance(node, ast.Attribute):
                            usages.add(node.attr)
                            
            except Exception as e:
                logger.warning(f"無法分析文件 {file_path}: {e}")
        
        # 找出未使用的定義
        for def_type, name, file_path in definitions:
            if name not in usages and not name.startswith("_"):
                self.unused_code.append({
                    "type": def_type,
                    "name": name,
                    "file": file_path,
                    "suggestion": f"移除未使用的{def_type}: {name}"
                })
        
        logger.info(f"✅ 找到 {len(self.unused_code)} 處未使用的代碼")
    
    def detect_code_smells(self):
        """檢測代碼異味"""
        logger.info("👃 檢測代碼異味...")
        
        python_files = list(self.project_path.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    # 檢測各種代碼異味
                    self._check_long_functions(tree, file_path)
                    self._check_complex_conditions(tree, file_path)
                    self._check_large_classes(tree, file_path)
                    self._check_deep_nesting(tree, file_path)
                    
            except Exception as e:
                logger.warning(f"無法分析文件 {file_path}: {e}")
        
        logger.info(f"✅ 檢測到 {len(self.code_smells)} 處代碼異味")
    
    def _check_long_functions(self, tree: ast.AST, file_path: Path):
        """檢查過長的函數"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 計算函數行數
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    lines = node.end_lineno - node.lineno
                    if lines > 50:  # 函數超過50行
                        self.code_smells.append({
                            "type": "long_function",
                            "file": str(file_path.relative_to(self.project_path)),
                            "function": node.name,
                            "lines": lines,
                            "suggestion": "考慮將函數拆分為更小的函數"
                        })
    
    def _check_complex_conditions(self, tree: ast.AST, file_path: Path):
        """檢查複雜的條件語句"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While)):
                complexity = self._calculate_condition_complexity(node.test)
                if complexity > 3:  # 條件複雜度超過3
                    self.code_smells.append({
                        "type": "complex_condition",
                        "file": str(file_path.relative_to(self.project_path)),
                        "line": node.lineno,
                        "complexity": complexity,
                        "suggestion": "簡化條件邏輯或提取為單獨的函數"
                    })
    
    def _check_large_classes(self, tree: ast.AST, file_path: Path):
        """檢查過大的類"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                if method_count > 20:  # 類有超過20個方法
                    self.code_smells.append({
                        "type": "large_class",
                        "file": str(file_path.relative_to(self.project_path)),
                        "class": node.name,
                        "method_count": method_count,
                        "suggestion": "考慮將類拆分或使用組合模式"
                    })
    
    def _check_deep_nesting(self, tree: ast.AST, file_path: Path):
        """檢查深度嵌套"""
        class NestingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.max_depth = 0
                self.current_depth = 0
                
            def visit(self, node):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                    self.current_depth += 1
                    self.max_depth = max(self.max_depth, self.current_depth)
                    self.generic_visit(node)
                    self.current_depth -= 1
                else:
                    self.generic_visit(node)
        
        visitor = NestingVisitor()
        visitor.visit(tree)
        
        if visitor.max_depth > 4:  # 嵌套深度超過4
            self.code_smells.append({
                "type": "deep_nesting",
                "file": str(file_path.relative_to(self.project_path)),
                "max_depth": visitor.max_depth,
                "suggestion": "減少嵌套層級，考慮早期返回或提取函數"
            })
    
    def generate_refactoring_suggestions(self):
        """生成重構建議"""
        logger.info("💡 生成重構建議...")
        
        # 基於發現的問題生成建議
        if self.code_duplicates:
            self.refactoring_suggestions.append({
                "priority": "high",
                "type": "extract_common_code",
                "description": "提取重複代碼到共用模塊",
                "affected_files": len(set(d["occurrences"][0]["file"] 
                                        for d in self.code_duplicates)),
                "estimated_effort": "medium"
            })
        
        if self.unused_code:
            self.refactoring_suggestions.append({
                "priority": "medium",
                "type": "remove_dead_code",
                "description": "移除未使用的代碼",
                "affected_items": len(self.unused_code),
                "estimated_effort": "low"
            })
        
        long_functions = [s for s in self.code_smells if s["type"] == "long_function"]
        if long_functions:
            self.refactoring_suggestions.append({
                "priority": "high",
                "type": "split_functions",
                "description": "拆分過長的函數",
                "affected_functions": len(long_functions),
                "estimated_effort": "high"
            })
        
        large_classes = [s for s in self.code_smells if s["type"] == "large_class"]
        if large_classes:
            self.refactoring_suggestions.append({
                "priority": "medium",
                "type": "refactor_classes",
                "description": "重構過大的類",
                "affected_classes": len(large_classes),
                "estimated_effort": "high"
            })
        
        logger.info(f"✅ 生成了 {len(self.refactoring_suggestions)} 個重構建議")
    
    def create_execution_plan(self) -> List[Dict[str, Any]]:
        """創建重構執行計劃"""
        logger.info("📝 創建執行計劃...")
        
        execution_plan = []
        
        # 按優先級排序建議
        sorted_suggestions = sorted(
            self.refactoring_suggestions, 
            key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]]
        )
        
        for i, suggestion in enumerate(sorted_suggestions, 1):
            plan_item = {
                "step": i,
                "action": suggestion["type"],
                "description": suggestion["description"],
                "priority": suggestion["priority"],
                "estimated_effort": suggestion["estimated_effort"],
                "tasks": []
            }
            
            # 根據建議類型生成具體任務
            if suggestion["type"] == "extract_common_code":
                plan_item["tasks"] = [
                    "識別所有重複代碼片段",
                    "創建共用模塊",
                    "將重複代碼提取到共用模塊",
                    "更新所有引用",
                    "運行測試確保功能正常"
                ]
            elif suggestion["type"] == "remove_dead_code":
                plan_item["tasks"] = [
                    "確認代碼確實未使用",
                    "刪除未使用的代碼",
                    "運行測試確保沒有破壞功能"
                ]
            elif suggestion["type"] == "split_functions":
                plan_item["tasks"] = [
                    "分析函數邏輯",
                    "識別可拆分的部分",
                    "創建新的子函數",
                    "重構原函數調用子函數",
                    "添加適當的文檔和測試"
                ]
            elif suggestion["type"] == "refactor_classes":
                plan_item["tasks"] = [
                    "分析類的職責",
                    "應用單一職責原則",
                    "考慮使用設計模式（如策略模式、組合模式）",
                    "重構類結構",
                    "更新相關測試"
                ]
            
            execution_plan.append(plan_item)
        
        logger.info(f"✅ 創建了包含 {len(execution_plan)} 個步驟的執行計劃")
        return execution_plan
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """獲取函數簽名"""
        # 簡化的實現，實際可以更複雜
        params = [arg.arg for arg in node.args.args]
        body_hash = hashlib.md5(ast.dump(node).encode()).hexdigest()[:8]
        return f"{node.name}({','.join(params)})_{body_hash}"
    
    def _calculate_condition_complexity(self, node: ast.AST) -> int:
        """計算條件的複雜度"""
        if isinstance(node, (ast.And, ast.Or)):
            return 1 + sum(self._calculate_condition_complexity(value) 
                          for value in node.values)
        elif isinstance(node, ast.BoolOp):
            return 1 + sum(self._calculate_condition_complexity(value) 
                          for value in node.values)
        elif isinstance(node, ast.Compare):
            return 1
        else:
            return 0
    
    def save_report(self, output_path: str):
        """保存分析報告"""
        report = self.analyze()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 報告已保存至: {output_path}")
        
        # 同時生成Markdown報告
        md_path = Path(output_path).with_suffix('.md')
        self._generate_markdown_report(report, md_path)
        logger.info(f"📄 Markdown報告已保存至: {md_path}")
    
    def _generate_markdown_report(self, report: Dict[str, Any], output_path: Path):
        """生成Markdown格式的報告"""
        md_content = f"""# PowerAutomation 代碼重構分析報告

項目路徑: `{report['project_path']}`
生成時間: {Path.ctime(output_path)}

## 📊 分析摘要

- 代碼重複: {len(report['code_duplicates'])} 處
- 未使用代碼: {len(report['unused_code'])} 處
- 代碼異味: {len(report['code_smells'])} 處
- 重構建議: {len(report['refactoring_suggestions'])} 個

## 🔁 代碼重複

"""
        
        for dup in report['code_duplicates']:
            md_content += f"### {dup['type']}\n"
            for occ in dup['occurrences']:
                md_content += f"- {occ['file']}:{occ['line']} - `{occ['function']}`\n"
            md_content += f"**建議**: {dup['suggestion']}\n\n"
        
        md_content += "## 🗑️ 未使用的代碼\n\n"
        for unused in report['unused_code']:
            md_content += f"- {unused['type']} `{unused['name']}` in {unused['file']}\n"
        
        md_content += "\n## 👃 代碼異味\n\n"
        for smell in report['code_smells']:
            md_content += f"### {smell['type']}\n"
            md_content += f"- 文件: {smell['file']}\n"
            if 'function' in smell:
                md_content += f"- 函數: {smell['function']}\n"
            if 'class' in smell:
                md_content += f"- 類: {smell['class']}\n"
            md_content += f"- 建議: {smell['suggestion']}\n\n"
        
        md_content += "## 📋 執行計劃\n\n"
        for step in report['execution_plan']:
            md_content += f"### 步驟 {step['step']}: {step['description']}\n"
            md_content += f"- 優先級: {step['priority']}\n"
            md_content += f"- 預估工作量: {step['estimated_effort']}\n"
            md_content += "- 任務:\n"
            for task in step['tasks']:
                md_content += f"  - {task}\n"
            md_content += "\n"
        
        output_path.write_text(md_content, encoding='utf-8')


# 主程序
def main():
    """演示代碼重構分析器"""
    import sys
    
    if len(sys.argv) < 2:
        project_path = "."
    else:
        project_path = sys.argv[1]
    
    analyzer = CodeFlowRefactoringAnalyzer(project_path)
    analyzer.save_report("refactoring_analysis_report.json")
    
    print("\n✅ 代碼重構分析完成！")
    print("📄 報告已生成:")
    print("   - refactoring_analysis_report.json")
    print("   - refactoring_analysis_report.md")


if __name__ == "__main__":
    main()