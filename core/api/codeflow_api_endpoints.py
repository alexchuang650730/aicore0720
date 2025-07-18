#!/usr/bin/env python3
"""
CodeFlow MCP API 端點實現
提供代碼生成、分析、重構、測試生成和代碼轉規格的API接口
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import logging
import json
import asyncio
from datetime import datetime

# 導入核心組件
from ..components.codeflow_mcp.code_to_spec_generator import code_to_spec_generator

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api/codeflow", tags=["codeflow"])


class CodeFlowService:
    """CodeFlow 服務類 - 處理所有代碼相關操作"""
    
    def __init__(self):
        self.active_sessions = {}
        self.code_cache = {}
        
    async def generate_code(self, requirements: str, workflow: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """生成代碼"""
        logger.info(f"生成代碼 - 工作流: {workflow}")
        
        # 模擬代碼生成過程
        await asyncio.sleep(2)  # 模擬處理時間
        
        # 基於需求生成代碼
        if options.get('framework') == 'react' and options.get('typescript'):
            code = self._generate_react_typescript_code(requirements)
        else:
            code = self._generate_generic_code(requirements)
            
        # 如果需要測試，生成測試代碼
        test_code = None
        if options.get('includeTests'):
            test_code = self._generate_test_code(code)
            
        result = {
            "code": code,
            "testCode": test_code,
            "language": "typescript" if options.get('typescript') else "javascript",
            "framework": options.get('framework', 'none'),
            "timestamp": datetime.now().isoformat()
        }
        
        # 緩存結果
        cache_key = f"gen_{hash(requirements)}_{workflow}"
        self.code_cache[cache_key] = result
        
        return result
        
    async def analyze_code(self, code: str) -> Dict[str, Any]:
        """分析代碼"""
        logger.info("分析代碼質量和結構")
        
        # 模擬代碼分析
        await asyncio.sleep(1.5)
        
        # 執行各種分析
        complexity = self._calculate_complexity(code)
        issues = self._find_issues(code)
        suggestions = self._generate_suggestions(code)
        metrics = self._calculate_metrics(code)
        
        return {
            "complexity": complexity,
            "issues": issues,
            "suggestions": suggestions,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    async def refactor_code(self, code: str) -> Dict[str, Any]:
        """重構代碼"""
        logger.info("分析重構機會")
        
        await asyncio.sleep(2)
        
        # 生成重構建議
        suggestions = self._generate_refactoring_suggestions(code)
        
        return {
            "suggestions": suggestions,
            "originalCode": code,
            "timestamp": datetime.now().isoformat()
        }
        
    async def generate_tests(self, code: str, specifications: str) -> Dict[str, Any]:
        """生成測試代碼"""
        logger.info("生成測試用例")
        
        await asyncio.sleep(1.5)
        
        # 生成測試
        test_code = self._generate_comprehensive_tests(code, specifications)
        test_cases = self._extract_test_cases(test_code)
        
        return {
            "testCode": test_code,
            "testCases": test_cases,
            "coverage": 85,  # 模擬覆蓋率
            "timestamp": datetime.now().isoformat()
        }
        
    async def code_to_spec(self, code: str, language: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """從代碼生成規格文檔"""
        logger.info(f"從{language}代碼生成規格")
        
        try:
            # 使用 code_to_spec_generator
            spec = await code_to_spec_generator.generate_spec_from_code(
                code_path="inline_code",  # 特殊標記表示直接傳入代碼
                language=language
            )
            
            # 生成文檔
            specification = await code_to_spec_generator.generate_spec_document(
                spec, 
                output_format="markdown"
            )
            
            return {
                "specification": specification,
                "spec_data": spec.__dict__,
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成規格失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
            
    async def apply_refactoring(self, refactoring_id: str) -> Dict[str, Any]:
        """應用重構建議"""
        logger.info(f"應用重構: {refactoring_id}")
        
        # 模擬應用重構
        await asyncio.sleep(1)
        
        # 這裡應該根據 refactoring_id 查找並應用具體的重構
        refactored_code = self._apply_specific_refactoring(refactoring_id)
        
        return {
            "refactoredCode": refactored_code,
            "refactoringId": refactoring_id,
            "timestamp": datetime.now().isoformat()
        }
        
    # 私有輔助方法
    def _generate_react_typescript_code(self, requirements: str) -> str:
        """生成 React TypeScript 代碼"""
        return f"""import React, {{ useState, useEffect }} from 'react';
import {{ Card, Button }} from 'antd';

interface Props {{
  // Generated based on: {requirements}
}}

export const GeneratedComponent: React.FC<Props> = (props) => {{
  const [state, setState] = useState<any>(null);
  
  useEffect(() => {{
    // Initialize component
  }}, []);
  
  return (
    <Card title="Generated Component">
      <p>This component was generated based on your requirements.</p>
      <Button type="primary">Action</Button>
    </Card>
  );
}};
"""
        
    def _generate_generic_code(self, requirements: str) -> str:
        """生成通用代碼"""
        return f"""// Generated code based on requirements: {requirements}

function generatedFunction() {{
  // Implementation goes here
  console.log('Function generated successfully');
}}

module.exports = {{ generatedFunction }};
"""
        
    def _generate_test_code(self, code: str) -> str:
        """生成測試代碼"""
        return """describe('Generated Component', () => {
  it('should render without errors', () => {
    // Test implementation
  });
  
  it('should handle user interactions', () => {
    // Test implementation
  });
});
"""
        
    def _calculate_complexity(self, code: str) -> str:
        """計算代碼複雜度"""
        lines = code.split('\n')
        if len(lines) < 50:
            return "low"
        elif len(lines) < 200:
            return "medium"
        else:
            return "high"
            
    def _find_issues(self, code: str) -> List[Dict[str, Any]]:
        """查找代碼問題"""
        issues = []
        
        # 簡單的代碼檢查
        if 'console.log' in code:
            issues.append({
                "type": "warning",
                "severity": "warning",
                "message": "發現 console.log 語句",
                "line": 10
            })
            
        if 'var ' in code:
            issues.append({
                "type": "info",
                "severity": "info",
                "message": "建議使用 const 或 let 替代 var",
                "line": 5
            })
            
        return issues
        
    def _generate_suggestions(self, code: str) -> List[str]:
        """生成優化建議"""
        suggestions = []
        
        if 'function' in code and 'async' not in code:
            suggestions.append("考慮使用 async/await 處理異步操作")
            
        if len(code.split('\n')) > 100:
            suggestions.append("考慮將大函數拆分為更小的功能單元")
            
        return suggestions
        
    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """計算代碼指標"""
        lines = code.split('\n')
        return {
            "lines": len(lines),
            "functions": code.count('function') + code.count('=>'),
            "cyclomaticComplexity": 5,  # 模擬值
            "maintainabilityIndex": 75  # 模擬值
        }
        
    def _generate_refactoring_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """生成重構建議"""
        suggestions = []
        
        # 示例重構建議
        suggestions.append({
            "id": "ref_001",
            "type": "函數提取",
            "description": "將重複的邏輯提取為獨立函數",
            "before": "// Repeated logic here\n// More repeated logic",
            "after": "function extractedFunction() {\n  // Extracted logic\n}",
            "impact": "中等"
        })
        
        return suggestions
        
    def _generate_comprehensive_tests(self, code: str, specs: str) -> str:
        """生成完整測試"""
        return f"""// Tests for specifications: {specs}

describe('Comprehensive Test Suite', () => {{
  beforeEach(() => {{
    // Setup
  }});
  
  it('should meet specification requirements', () => {{
    // Test implementation
    expect(true).toBe(true);
  }});
  
  it('should handle edge cases', () => {{
    // Edge case testing
  }});
}});
"""
        
    def _extract_test_cases(self, test_code: str) -> List[Dict[str, str]]:
        """提取測試用例"""
        return [
            {"name": "基本功能測試", "status": "pending"},
            {"name": "邊界條件測試", "status": "pending"},
            {"name": "錯誤處理測試", "status": "pending"}
        ]
        
    def _apply_specific_refactoring(self, refactoring_id: str) -> str:
        """應用特定重構"""
        # 這裡應該根據ID查找具體的重構
        return """// Refactored code
function improvedFunction() {
  // Cleaner implementation
  return result;
}
"""


# 創建服務實例
codeflow_service = CodeFlowService()


# API 端點定義
@router.post("/generate")
async def generate_code(request: Request) -> JSONResponse:
    """生成代碼 API"""
    try:
        data = await request.json()
        result = await codeflow_service.generate_code(
            requirements=data.get('requirements', ''),
            workflow=data.get('workflow', 'code_generation'),
            options=data.get('options', {})
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"生成代碼失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_code(request: Request) -> JSONResponse:
    """分析代碼 API"""
    try:
        data = await request.json()
        result = await codeflow_service.analyze_code(
            code=data.get('code', '')
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"分析代碼失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refactor")
async def refactor_code(request: Request) -> JSONResponse:
    """重構代碼 API"""
    try:
        data = await request.json()
        result = await codeflow_service.refactor_code(
            code=data.get('code', '')
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"重構分析失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-tests")
async def generate_tests(request: Request) -> JSONResponse:
    """生成測試 API"""
    try:
        data = await request.json()
        result = await codeflow_service.generate_tests(
            code=data.get('code', ''),
            specifications=data.get('specifications', '')
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"生成測試失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code-to-spec")
async def code_to_spec(request: Request) -> JSONResponse:
    """代碼轉規格 API"""
    try:
        data = await request.json()
        result = await codeflow_service.code_to_spec(
            code=data.get('code', ''),
            language=data.get('language', 'python'),
            options=data.get('options', {})
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"代碼轉規格失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-refactoring")
async def apply_refactoring(request: Request) -> JSONResponse:
    """應用重構 API"""
    try:
        data = await request.json()
        result = await codeflow_service.apply_refactoring(
            refactoring_id=data.get('refactoringId', '')
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"應用重構失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status() -> JSONResponse:
    """獲取 CodeFlow 服務狀態"""
    return JSONResponse(content={
        "status": "healthy",
        "active_sessions": len(codeflow_service.active_sessions),
        "cache_size": len(codeflow_service.code_cache),
        "timestamp": datetime.now().isoformat()
    })


# 導出路由器
__all__ = ['router']