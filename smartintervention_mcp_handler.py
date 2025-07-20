#!/usr/bin/env python3
"""
SmartIntervention MCP處理器
處理需要智能介入的場景，如PDF讀取、複雜文件處理等
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import mimetypes
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartInterventionMCP:
    """智能介入MCP處理器"""
    
    def __init__(self):
        self.base_dir = Path("/Users/alexchuang/alexchuangtest/aicore0720")
        self.intervention_log = self.base_dir / "monitoring" / "smart_interventions.jsonl"
        self.intervention_log.parent.mkdir(exist_ok=True)
        
        # 定義需要智能介入的場景
        self.intervention_scenarios = {
            "binary_file_read": {
                "patterns": ["cannot read binary files", "binary .pdf file", "binary file analysis"],
                "handler": self.handle_binary_file,
                "tools": ["pdf-reader", "ocr-tool", "file-converter"]
            },
            "complex_search": {
                "patterns": ["search failed", "no results found", "too many results"],
                "handler": self.handle_complex_search,
                "tools": ["semantic-search", "ai-search", "context-search"]
            },
            "tool_not_found": {
                "patterns": ["tool not found", "no appropriate tool", "missing capability"],
                "handler": self.handle_missing_tool,
                "tools": ["mcp-zero", "tool-discovery", "capability-expansion"]
            },
            "permission_denied": {
                "patterns": ["permission denied", "access denied", "unauthorized"],
                "handler": self.handle_permission_issue,
                "tools": ["permission-manager", "sudo-wrapper", "access-controller"]
            },
            "encoding_error": {
                "patterns": ["encoding error", "decode error", "unicode error"],
                "handler": self.handle_encoding_issue,
                "tools": ["encoding-detector", "file-converter", "text-normalizer"]
            }
        }
        
        # MCP工具註冊表
        self.mcp_tools = {
            "pdf-reader": {
                "command": "pdftotext",
                "fallback": "python-pdfplumber",
                "capability": "read_pdf"
            },
            "ocr-tool": {
                "command": "tesseract",
                "fallback": "python-pytesseract",
                "capability": "ocr_text"
            },
            "file-converter": {
                "command": "pandoc",
                "fallback": "python-converter",
                "capability": "convert_format"
            }
        }
    
    async def detect_intervention_needed(self, error_message: str) -> Optional[str]:
        """檢測是否需要智能介入"""
        error_lower = error_message.lower()
        
        for scenario, config in self.intervention_scenarios.items():
            if any(pattern in error_lower for pattern in config["patterns"]):
                logger.info(f"檢測到需要智能介入的場景: {scenario}")
                return scenario
        
        return None
    
    async def handle_binary_file(self, file_path: str, error_info: Dict) -> Dict:
        """處理二進制文件讀取"""
        result = {
            "success": False,
            "intervention_type": "binary_file_read",
            "original_error": error_info,
            "solution": None,
            "output": None
        }
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            result["error"] = "文件不存在"
            return result
        
        # 檢測文件類型
        mime_type, _ = mimetypes.guess_type(str(file_path_obj))
        logger.info(f"文件類型: {mime_type}")
        
        if mime_type == "application/pdf" or file_path_obj.suffix.lower() == ".pdf":
            # 嘗試使用PDF工具
            try:
                # 方法1: 使用pdftotext
                if self._check_tool_available("pdftotext"):
                    output = subprocess.run(
                        ["pdftotext", str(file_path_obj), "-"],
                        capture_output=True,
                        text=True
                    )
                    if output.returncode == 0:
                        result["success"] = True
                        result["solution"] = "pdftotext"
                        result["output"] = output.stdout
                        return result
                
                # 方法2: 使用Python PDF庫
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path_obj) as pdf:
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() + "\n"
                        result["success"] = True
                        result["solution"] = "pdfplumber"
                        result["output"] = text
                        return result
                except ImportError:
                    logger.warning("pdfplumber未安裝")
                
                # 方法3: 建議安裝工具
                result["solution"] = "suggested_installation"
                result["suggestions"] = [
                    "pip install pdfplumber",
                    "brew install poppler",  # for pdftotext
                    "使用OCR工具處理掃描版PDF"
                ]
                
            except Exception as e:
                result["error"] = str(e)
        
        return result
    
    async def handle_complex_search(self, query: str, context: Dict) -> Dict:
        """處理複雜搜索場景"""
        result = {
            "success": False,
            "intervention_type": "complex_search",
            "query": query,
            "enhanced_strategies": []
        }
        
        # 策略1: 語義搜索增強
        result["enhanced_strategies"].append({
            "strategy": "semantic_search",
            "description": "使用語義相似度而非關鍵詞匹配",
            "implementation": "使用embedding進行向量搜索"
        })
        
        # 策略2: 上下文感知搜索
        result["enhanced_strategies"].append({
            "strategy": "context_aware_search",
            "description": "基於當前任務上下文優化搜索",
            "implementation": "分析用戶意圖和歷史操作"
        })
        
        # 策略3: 多模態搜索
        result["enhanced_strategies"].append({
            "strategy": "multimodal_search",
            "description": "結合代碼、文檔、註釋等多種信息",
            "implementation": "跨文件類型綜合搜索"
        })
        
        result["success"] = True
        return result
    
    async def handle_missing_tool(self, required_capability: str) -> Dict:
        """處理缺失工具場景"""
        result = {
            "success": False,
            "intervention_type": "tool_not_found",
            "required_capability": required_capability,
            "solutions": []
        }
        
        # 解決方案1: MCP Zero自動發現
        result["solutions"].append({
            "method": "mcp_zero_discovery",
            "description": "使用MCP Zero自動發現並註冊新工具",
            "command": "mcp-zero discover --capability " + required_capability
        })
        
        # 解決方案2: 動態工具生成
        result["solutions"].append({
            "method": "dynamic_tool_generation",
            "description": "基於需求動態生成工具包裝器",
            "implementation": "創建Python腳本封裝現有命令行工具"
        })
        
        # 解決方案3: 替代工具推薦
        result["solutions"].append({
            "method": "alternative_tools",
            "description": "推薦具有類似功能的替代工具",
            "alternatives": self._find_alternative_tools(required_capability)
        })
        
        result["success"] = True
        return result
    
    async def handle_permission_issue(self, file_path: str) -> Dict:
        """處理權限問題"""
        result = {
            "success": False,
            "intervention_type": "permission_denied",
            "file_path": file_path,
            "solutions": []
        }
        
        # 檢查當前權限
        import os
        import stat
        
        try:
            file_stat = os.stat(file_path)
            current_perms = stat.filemode(file_stat.st_mode)
            result["current_permissions"] = current_perms
            
            # 解決方案
            result["solutions"] = [
                {"method": "change_permissions", "command": f"chmod +r {file_path}"},
                {"method": "copy_with_permissions", "description": "複製文件到可訪問位置"},
                {"method": "use_sudo", "command": f"sudo cat {file_path}", "warning": "需要管理員權限"}
            ]
            
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def handle_encoding_issue(self, file_path: str, original_error: str) -> Dict:
        """處理編碼問題"""
        result = {
            "success": False,
            "intervention_type": "encoding_error",
            "file_path": file_path,
            "detected_encoding": None,
            "solutions": []
        }
        
        try:
            # 嘗試檢測編碼
            import chardet
            
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 讀取前10KB
                detection = chardet.detect(raw_data)
                result["detected_encoding"] = detection['encoding']
                result["confidence"] = detection['confidence']
            
            # 提供解決方案
            result["solutions"] = [
                {
                    "method": "explicit_encoding",
                    "description": f"使用檢測到的編碼: {detection['encoding']}",
                    "code": f"open('{file_path}', 'r', encoding='{detection['encoding']}')"
                },
                {
                    "method": "try_common_encodings",
                    "description": "嘗試常見編碼",
                    "encodings": ["utf-8", "gbk", "gb2312", "big5", "latin-1"]
                },
                {
                    "method": "ignore_errors",
                    "description": "忽略編碼錯誤",
                    "code": f"open('{file_path}', 'r', encoding='utf-8', errors='ignore')"
                }
            ]
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            result["solutions"].append({
                "method": "install_chardet",
                "command": "pip install chardet"
            })
        
        return result
    
    def _check_tool_available(self, tool_name: str) -> bool:
        """檢查工具是否可用"""
        try:
            subprocess.run(["which", tool_name], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _find_alternative_tools(self, capability: str) -> List[str]:
        """查找替代工具"""
        alternatives = {
            "read_pdf": ["pdftotext", "pdfplumber", "PyPDF2", "pymupdf"],
            "ocr_text": ["tesseract", "pytesseract", "easyocr", "paddleocr"],
            "convert_format": ["pandoc", "libreoffice", "unoconv"]
        }
        return alternatives.get(capability, [])
    
    async def log_intervention(self, intervention_data: Dict):
        """記錄智能介入事件"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "intervention": intervention_data
        }
        
        with open(self.intervention_log, 'a') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    async def process_error(self, error_message: str, context: Dict) -> Dict:
        """處理錯誤並提供智能介入"""
        # 檢測場景
        scenario = await self.detect_intervention_needed(error_message)
        
        if not scenario:
            return {
                "success": False,
                "message": "未檢測到需要智能介入的場景"
            }
        
        # 獲取處理器
        handler = self.intervention_scenarios[scenario]["handler"]
        
        # 執行智能介入
        if scenario == "binary_file_read":
            result = await handler(context.get("file_path", ""), {"error": error_message})
        elif scenario == "complex_search":
            result = await handler(context.get("query", ""), context)
        elif scenario == "tool_not_found":
            result = await handler(context.get("capability", ""))
        elif scenario == "permission_denied":
            result = await handler(context.get("file_path", ""))
        elif scenario == "encoding_error":
            result = await handler(context.get("file_path", ""), error_message)
        else:
            result = {"success": False, "message": "未實現的處理器"}
        
        # 記錄介入
        await self.log_intervention(result)
        
        return result


# MCP整合配置
MCP_CONFIG = {
    "smart_intervention": {
        "enabled": True,
        "auto_retry": True,
        "learning_mode": True,
        "scenarios": [
            "binary_file_read",
            "complex_search",
            "tool_not_found",
            "permission_denied",
            "encoding_error"
        ]
    },
    "integration": {
        "mcp_zero": True,
        "smart_tool": True,
        "auto_discovery": True
    }
}


async def main():
    """測試智能介入"""
    handler = SmartInterventionMCP()
    
    # 測試PDF讀取錯誤
    test_error = "Error: This tool cannot read binary files. The file appears to be a binary .pdf file."
    test_context = {
        "file_path": "../../../Desktop/振华创新机器人科技有限公司.pdf"
    }
    
    result = await handler.process_error(test_error, test_context)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())