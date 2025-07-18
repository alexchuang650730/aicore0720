#!/usr/bin/env python3
"""
MCP-Zero API 端點
提供動態 MCP 加載和任務執行的 REST API
"""

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import logging
import json
import asyncio
from datetime import datetime

from ..mcp_zero import mcp_zero_engine, mcp_registry

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api/mcpzero", tags=["mcpzero"])

# WebSocket 連接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
            
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
            
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()


@router.post("/execute")
async def execute_task(request: Request) -> JSONResponse:
    """執行任務 - MCP-Zero 模式"""
    try:
        data = await request.json()
        
        user_request = data.get('task', '')
        options = data.get('options', {})
        
        # 執行任務
        result = await mcp_zero_engine.execute_task(user_request, options)
        
        return JSONResponse(content={
            "task_id": result.task_id,
            "success": result.success,
            "steps_completed": result.steps_completed,
            "total_steps": result.total_steps,
            "execution_time": result.execution_time,
            "tokens_used": result.tokens_used,
            "cost_estimate": result.cost_estimate,
            "results": result.results,
            "errors": result.errors
        })
        
    except Exception as e:
        logger.error(f"任務執行失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_task(request: Request) -> JSONResponse:
    """分析任務複雜度"""
    try:
        data = await request.json()
        user_request = data.get('task', '')
        
        # 分解任務
        steps = await mcp_zero_engine.planner.decompose_task(user_request)
        
        # 評估複雜度
        complexity = await mcp_zero_engine.planner.estimate_task_complexity(steps)
        
        return JSONResponse(content={
            "task": user_request,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "description": step.description,
                    "required_mcps": step.required_mcps,
                    "estimated_time": step.estimated_time
                }
                for step in steps
            ],
            "complexity": complexity
        })
        
    except Exception as e:
        logger.error(f"任務分析失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcps")
async def list_mcps() -> JSONResponse:
    """列出所有可用的 MCP"""
    mcps = []
    
    for name, metadata in mcp_registry.mcp_catalog.items():
        mcps.append({
            "name": name,
            "description": metadata.description,
            "capabilities": metadata.capabilities,
            "context_size": metadata.context_size,
            "priority": metadata.priority,
            "tags": metadata.tags
        })
        
    return JSONResponse(content={"mcps": mcps})


@router.get("/mcps/loaded")
async def get_loaded_mcps() -> JSONResponse:
    """獲取當前已加載的 MCP"""
    loaded = await mcp_registry.get_loaded_mcps()
    context_usage = mcp_registry.get_context_usage()
    
    return JSONResponse(content={
        "loaded_mcps": loaded,
        "context_usage": context_usage
    })


@router.post("/mcps/load")
async def load_mcp(request: Request) -> JSONResponse:
    """手動加載指定 MCP"""
    try:
        data = await request.json()
        mcp_name = data.get('mcp_name', '')
        
        mcp = await mcp_registry.load_mcp(mcp_name)
        
        if mcp:
            return JSONResponse(content={
                "success": True,
                "message": f"MCP {mcp_name} 加載成功"
            })
        else:
            raise HTTPException(status_code=404, detail=f"MCP {mcp_name} 不存在或加載失敗")
            
    except Exception as e:
        logger.error(f"加載 MCP 失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcps/unload")
async def unload_mcp(request: Request) -> JSONResponse:
    """手動卸載指定 MCP"""
    try:
        data = await request.json()
        mcp_name = data.get('mcp_name', '')
        
        success = await mcp_registry.unload_mcp(mcp_name)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": f"MCP {mcp_name} 卸載成功"
            })
        else:
            return JSONResponse(content={
                "success": False,
                "message": f"MCP {mcp_name} 卸載失敗（可能被其他 MCP 依賴）"
            })
            
    except Exception as e:
        logger.error(f"卸載 MCP 失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcps/search")
async def search_mcps(request: Request) -> JSONResponse:
    """搜索適合任務的 MCP"""
    try:
        data = await request.json()
        task_description = data.get('task_description', '')
        max_results = data.get('max_results', 5)
        
        results = await mcp_registry.search_mcps(task_description, max_results)
        
        # 獲取詳細信息
        mcp_details = []
        for mcp_name in results:
            metadata = await mcp_registry.get_mcp_metadata(mcp_name)
            if metadata:
                mcp_details.append({
                    "name": mcp_name,
                    "description": metadata.description,
                    "capabilities": metadata.capabilities,
                    "priority": metadata.priority,
                    "performance_score": metadata.performance_score
                })
                
        return JSONResponse(content={"results": mcp_details})
        
    except Exception as e:
        logger.error(f"搜索 MCP 失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str) -> JSONResponse:
    """獲取任務執行狀態"""
    status = await mcp_zero_engine.get_task_status(task_id)
    
    if status:
        return JSONResponse(content=status)
    else:
        raise HTTPException(status_code=404, detail=f"任務 {task_id} 不存在")


@router.post("/tasks/{task_id}/pause")
async def pause_task(task_id: str) -> JSONResponse:
    """暫停任務執行"""
    success = await mcp_zero_engine.pause_task(task_id)
    
    if success:
        return JSONResponse(content={
            "success": True,
            "message": f"任務 {task_id} 已暫停"
        })
    else:
        raise HTTPException(status_code=404, detail=f"任務 {task_id} 不存在或無法暫停")


@router.post("/tasks/{task_id}/resume")
async def resume_task(task_id: str) -> JSONResponse:
    """恢復任務執行"""
    success = await mcp_zero_engine.resume_task(task_id)
    
    if success:
        return JSONResponse(content={
            "success": True,
            "message": f"任務 {task_id} 已恢復"
        })
    else:
        raise HTTPException(status_code=404, detail=f"任務 {task_id} 不存在或無法恢復")


@router.get("/context/stats")
async def get_context_stats() -> JSONResponse:
    """獲取上下文使用統計"""
    stats = mcp_zero_engine.context_manager.get_usage_stats()
    return JSONResponse(content=stats)


@router.post("/context/optimize")
async def optimize_context(request: Request) -> JSONResponse:
    """優化上下文 for 特定工作流"""
    try:
        data = await request.json()
        workflow_type = data.get('workflow_type', '')
        
        mcp_zero_engine.context_manager.optimize_for_workflow(workflow_type)
        
        return JSONResponse(content={
            "success": True,
            "message": f"上下文已優化 for {workflow_type}"
        })
        
    except Exception as e:
        logger.error(f"優化上下文失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 端點 - 實時任務進度推送"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # 接收客戶端消息
            data = await websocket.receive_json()
            
            if data.get("type") == "subscribe_task":
                task_id = data.get("task_id")
                # 這裡可以設置任務訂閱邏輯
                await manager.send_message(client_id, {
                    "type": "subscription_confirmed",
                    "task_id": task_id
                })
                
            elif data.get("type") == "ping":
                await manager.send_message(client_id, {"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket 錯誤: {str(e)}")
        manager.disconnect(client_id)


# 任務進度推送函數（供引擎調用）
async def push_task_progress(task_id: str, progress: Dict[str, Any]):
    """推送任務進度到所有訂閱的客戶端"""
    await manager.broadcast({
        "type": "task_progress",
        "task_id": task_id,
        "progress": progress,
        "timestamp": datetime.now().isoformat()
    })


# 導出路由器
__all__ = ['router', 'push_task_progress']