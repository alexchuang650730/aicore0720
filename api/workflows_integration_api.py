"""
工作流集成狀態 API
提供 P1 MCP 與六大工作流的集成狀態查詢
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

# 導入工作流 MCP 集成器
from ..core.workflows.workflow_mcp_integration import workflow_mcp_integrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/workflows", tags=["workflow_integration"])


@router.get("/integration-status")
async def get_integration_status() -> Dict[str, Any]:
    """
    獲取 P1 MCP 與工作流的集成狀態
    
    Returns:
        包含集成狀態的詳細信息
    """
    try:
        # 獲取集成狀態
        status = await workflow_mcp_integrator.get_integration_status()
        
        logger.info(f"集成狀態查詢成功: {status['overall_integration_percentage']}")
        
        return {
            "success": True,
            **status
        }
        
    except Exception as e:
        logger.error(f"獲取集成狀態失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"獲取集成狀態失敗: {str(e)}"
        )


@router.post("/validate-integration")
async def validate_integration() -> Dict[str, Any]:
    """
    驗證 MCP 集成的完整性
    
    Returns:
        驗證結果報告
    """
    try:
        # 執行驗證
        validation_result = await workflow_mcp_integrator.validate_integration()
        
        logger.info(f"集成驗證完成: {validation_result['success_rate']}")
        
        return {
            "success": True,
            **validation_result
        }
        
    except Exception as e:
        logger.error(f"驗證集成失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"驗證集成失敗: {str(e)}"
        )


@router.post("/integrate-mcp/{workflow_type}/{stage}")
async def integrate_mcp_to_workflow(workflow_type: str, stage: str) -> Dict[str, Any]:
    """
    將 MCP 集成到特定工作流階段
    
    Args:
        workflow_type: 工作流類型
        stage: 工作流階段
        
    Returns:
        集成結果
    """
    try:
        # 執行集成
        result = await workflow_mcp_integrator.integrate_mcp_to_workflow(
            workflow_type, stage
        )
        
        logger.info(f"MCP 集成成功: {workflow_type}.{stage} - {result['integrated_mcps']}")
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"MCP 集成失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"MCP 集成失敗: {str(e)}"
        )


@router.get("/mcp-mappings")
async def get_mcp_mappings() -> Dict[str, Any]:
    """
    獲取 MCP 與工作流的映射關係
    
    Returns:
        MCP 映射配置
    """
    try:
        # 獲取映射關係
        mappings = {}
        for mcp_name, mapping in workflow_mcp_integrator.mcp_mappings.items():
            mappings[mcp_name] = {
                "workflow_stages": mapping.workflow_stages,
                "integration_level": mapping.integration_level.value,
                "capabilities": mapping.capabilities
            }
        
        return {
            "success": True,
            "total_mcps": len(mappings),
            "mappings": mappings
        }
        
    except Exception as e:
        logger.error(f"獲取映射關係失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"獲取映射關係失敗: {str(e)}"
        )


@router.get("/workflow-mcps/{workflow_type}")
async def get_workflow_mcps(workflow_type: str) -> Dict[str, Any]:
    """
    獲取特定工作流使用的 MCP
    
    Args:
        workflow_type: 工作流類型
        
    Returns:
        該工作流使用的 MCP 列表
    """
    try:
        # 收集該工作流的所有 MCP
        workflow_mcps = []
        
        for mcp_name, mapping in workflow_mcp_integrator.mcp_mappings.items():
            for pattern in mapping.workflow_stages:
                if workflow_type in pattern or pattern == "*.*":
                    workflow_mcps.append({
                        "mcp_name": mcp_name,
                        "integration_level": mapping.integration_level.value,
                        "capabilities": mapping.capabilities
                    })
                    break
        
        return {
            "success": True,
            "workflow_type": workflow_type,
            "total_mcps": len(workflow_mcps),
            "mcps": workflow_mcps
        }
        
    except Exception as e:
        logger.error(f"獲取工作流 MCP 失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"獲取工作流 MCP 失敗: {str(e)}"
        )