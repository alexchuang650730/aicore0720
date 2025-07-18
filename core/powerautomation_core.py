"""
PowerAutomation Core
核心驅動器，統一管理所有MCP組件並驅動ClaudeEditor
"""

import asyncio
import json
import logging
import websockets
import httpx
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import uuid

# 導入所有MCP組件
from mcp_components.claude_router_mcp import ClaudeRouterMCP
from mcp_components.member_system_mcp import MemberSystemMCP
from mcp_components.command_mcp import CommandMCP
from mcp_components.memory_rag_mcp import MemoryRAGMCP
from mcp_components.data_collection_mcp import DataCollectionMCP

logger = logging.getLogger(__name__)

class PowerAutomationCore:
    """PowerAutomation核心驅動器"""
    
    def __init__(self):
        self.core_id = str(uuid.uuid4())
        self.status = "initializing"
        self.created_at = datetime.now()
        
        # MCP組件管理
        self.mcp_components: Dict[str, Any] = {}
        self.active_connections: Set[websockets.WebSocketServerProtocol] = set()
        
        # ClaudeEditor連接
        self.claudeditor_instances: Dict[str, Dict[str, Any]] = {}
        self.claudeditor_websockets: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # 核心配置
        self.config = {
            "core": {
                "host": "localhost",
                "port": 8080,
                "websocket_port": 8081
            },
            "claudeditor": {
                "default_host": "localhost",
                "default_port": 8000,
                "connection_timeout": 30
            }
        }
        
        logger.info(f"🚀 PowerAutomation Core 初始化: {self.core_id}")
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化核心系統"""
        try:
            # 初始化所有MCP組件
            await self._initialize_mcp_components()
            
            # 啟動WebSocket服務器
            await self._start_websocket_server()
            
            self.status = "running"
            logger.info("✅ PowerAutomation Core 初始化成功")
            
            return {
                "status": "success",
                "core_id": self.core_id,
                "message": "PowerAutomation Core 初始化成功",
                "mcp_components": list(self.mcp_components.keys()),
                "websocket_port": self.config["core"]["websocket_port"]
            }
            
        except Exception as e:
            self.status = "error"
            logger.error(f"PowerAutomation Core 初始化失敗: {e}")
            return {
                "status": "error",
                "core_id": self.core_id,
                "error": str(e)
            }
    
    async def _initialize_mcp_components(self):
        """初始化所有MCP組件"""
        # 初始化Claude Router MCP
        claude_router = ClaudeRouterMCP()
        await claude_router.initialize()
        self.mcp_components["claude_router"] = claude_router
        
        # 初始化Member System MCP
        member_system = MemberSystemMCP()
        await member_system.initialize()
        self.mcp_components["member_system"] = member_system
        
        # 初始化Command MCP
        command_mcp = CommandMCP()
        await command_mcp.initialize()
        self.mcp_components["command"] = command_mcp
        
        # 初始化Memory RAG MCP
        memory_rag = MemoryRAGMCP()
        await memory_rag.initialize()
        self.mcp_components["memory_rag"] = memory_rag
        
        # 初始化Data Collection MCP
        data_collection = DataCollectionMCP()
        await data_collection.initialize()
        self.mcp_components["data_collection"] = data_collection
        
        logger.info(f"✅ 已初始化 {len(self.mcp_components)} 個MCP組件")
    
    async def _start_websocket_server(self):
        """啟動WebSocket服務器"""
        async def handle_websocket(websocket, path):
            await self._handle_websocket_connection(websocket, path)
        
        # 啟動WebSocket服務器（非阻塞）
        start_server = websockets.serve(
            handle_websocket,
            self.config["core"]["host"],
            self.config["core"]["websocket_port"]
        )
        
        # 在後台運行
        asyncio.create_task(start_server)
        logger.info(f"✅ WebSocket服務器啟動在 ws://{self.config['core']['host']}:{self.config['core']['websocket_port']}")
    
    async def _handle_websocket_connection(self, websocket, path):
        """處理WebSocket連接"""
        try:
            self.active_connections.add(websocket)
            logger.info(f"📡 新的WebSocket連接: {path}")
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self._process_websocket_message(data, websocket)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "status": "error",
                        "message": "無效的JSON格式"
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        "status": "error",
                        "message": str(e)
                    }))
        except websockets.exceptions.ConnectionClosed:
            logger.info("📡 WebSocket連接已關閉")
        finally:
            self.active_connections.discard(websocket)
    
    async def _process_websocket_message(self, data: Dict[str, Any], websocket) -> Dict[str, Any]:
        """處理WebSocket消息"""
        action = data.get("action")
        params = data.get("params", {})
        
        if action == "register_claudeditor":
            return await self._register_claudeditor(params, websocket)
        
        elif action == "drive_claudeditor":
            return await self._drive_claudeditor(params)
        
        elif action == "call_mcp":
            return await self._call_mcp_component(params)
        
        elif action == "get_status":
            return await self._get_core_status()
        
        elif action == "get_claudeditor_instances":
            return await self._get_claudeditor_instances()
        
        else:
            return {
                "status": "error",
                "message": f"未知操作: {action}"
            }
    
    async def _register_claudeditor(self, params: Dict[str, Any], websocket) -> Dict[str, Any]:
        """註冊ClaudeEditor實例"""
        try:
            claudeditor_info = {
                "id": str(uuid.uuid4()),
                "name": params.get("name", "ClaudeEditor"),
                "version": params.get("version", "unknown"),
                "host": params.get("host", self.config["claudeditor"]["default_host"]),
                "port": params.get("port", self.config["claudeditor"]["default_port"]),
                "websocket": websocket,
                "registered_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            claudeditor_id = claudeditor_info["id"]
            self.claudeditor_instances[claudeditor_id] = claudeditor_info
            self.claudeditor_websockets[claudeditor_id] = websocket
            
            logger.info(f"✅ ClaudeEditor 註冊成功: {claudeditor_id}")
            
            return {
                "status": "success",
                "message": "ClaudeEditor註冊成功",
                "claudeditor_id": claudeditor_id,
                "core_id": self.core_id
            }
            
        except Exception as e:
            logger.error(f"ClaudeEditor註冊失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _drive_claudeditor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """驅動ClaudeEditor執行操作"""
        try:
            claudeditor_id = params.get("claudeditor_id")
            command = params.get("command")
            command_params = params.get("command_params", {})
            
            if not claudeditor_id or claudeditor_id not in self.claudeditor_instances:
                return {
                    "status": "error",
                    "message": "無效的ClaudeEditor ID"
                }
            
            claudeditor_ws = self.claudeditor_websockets.get(claudeditor_id)
            if not claudeditor_ws:
                return {
                    "status": "error",
                    "message": "ClaudeEditor連接已斷開"
                }
            
            # 構建驅動命令
            drive_command = {
                "type": "core_command",
                "command": command,
                "params": command_params,
                "timestamp": datetime.now().isoformat(),
                "core_id": self.core_id
            }
            
            # 發送命令到ClaudeEditor
            await claudeditor_ws.send(json.dumps(drive_command))
            
            logger.info(f"🎛️ 向ClaudeEditor {claudeditor_id} 發送命令: {command}")
            
            return {
                "status": "success",
                "message": f"命令已發送到ClaudeEditor",
                "command": command,
                "claudeditor_id": claudeditor_id
            }
            
        except Exception as e:
            logger.error(f"驅動ClaudeEditor失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _call_mcp_component(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """調用MCP組件"""
        try:
            component_name = params.get("component")
            method = params.get("method")
            method_params = params.get("params", {})
            
            if component_name not in self.mcp_components:
                return {
                    "status": "error",
                    "message": f"未知的MCP組件: {component_name}"
                }
            
            component = self.mcp_components[component_name]
            result = await component.call_mcp(method, method_params)
            
            return {
                "status": "success",
                "component": component_name,
                "method": method,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"調用MCP組件失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _get_core_status(self) -> Dict[str, Any]:
        """獲取核心狀態"""
        try:
            # 獲取所有MCP組件狀態
            mcp_status = {}
            for name, component in self.mcp_components.items():
                mcp_status[name] = component.get_status()
            
            # 獲取ClaudeEditor實例狀態
            claudeditor_status = {}
            for cid, instance in self.claudeditor_instances.items():
                claudeditor_status[cid] = {
                    "name": instance["name"],
                    "host": instance["host"],
                    "port": instance["port"],
                    "status": instance["status"],
                    "registered_at": instance["registered_at"]
                }
            
            return {
                "status": "success",
                "core_status": {
                    "core_id": self.core_id,
                    "status": self.status,
                    "created_at": self.created_at.isoformat(),
                    "active_connections": len(self.active_connections),
                    "mcp_components": mcp_status,
                    "claudeditor_instances": claudeditor_status
                }
            }
            
        except Exception as e:
            logger.error(f"獲取核心狀態失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _get_claudeditor_instances(self) -> Dict[str, Any]:
        """獲取ClaudeEditor實例列表"""
        try:
            instances = []
            for cid, instance in self.claudeditor_instances.items():
                instances.append({
                    "id": cid,
                    "name": instance["name"],
                    "version": instance["version"],
                    "host": instance["host"],
                    "port": instance["port"],
                    "status": instance["status"],
                    "registered_at": instance["registered_at"]
                })
            
            return {
                "status": "success",
                "claudeditor_instances": instances,
                "total_count": len(instances)
            }
            
        except Exception as e:
            logger.error(f"獲取ClaudeEditor實例失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def drive_claudeditor_workflow(self, claudeditor_id: str, workflow_type: str, 
                                       workflow_params: Dict[str, Any]) -> Dict[str, Any]:
        """驅動ClaudeEditor執行特定工作流"""
        try:
            # 構建工作流命令
            workflow_command = {
                "command": "execute_workflow",
                "command_params": {
                    "workflow_type": workflow_type,
                    "params": workflow_params,
                    "core_driven": True
                }
            }
            
            # 通過核心驅動ClaudeEditor
            result = await self._drive_claudeditor({
                "claudeditor_id": claudeditor_id,
                **workflow_command
            })
            
            return result
            
        except Exception as e:
            logger.error(f"驅動工作流失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def integrate_with_claude_code(self, claudeditor_id: str, 
                                       claude_command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """整合Claude Code Tool"""
        try:
            # 首先通過Claude Router MCP處理請求
            claude_router = self.mcp_components.get("claude_router")
            if claude_router:
                # 路由到K2或Claude
                route_result = await claude_router.call_mcp("route_request", {
                    "message": claude_command,
                    "params": params
                })
                
                # 將結果發送到ClaudeEditor
                drive_result = await self._drive_claudeditor({
                    "claudeditor_id": claudeditor_id,
                    "command": "handle_claude_code_response",
                    "command_params": {
                        "original_command": claude_command,
                        "route_result": route_result
                    }
                })
                
                return {
                    "status": "success",
                    "claude_command": claude_command,
                    "route_result": route_result,
                    "drive_result": drive_result
                }
            
            return {
                "status": "error",
                "message": "Claude Router MCP未初始化"
            }
            
        except Exception as e:
            logger.error(f"Claude Code整合失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def shutdown(self) -> Dict[str, Any]:
        """關閉核心系統"""
        try:
            # 關閉所有WebSocket連接
            for websocket in self.active_connections.copy():
                await websocket.close()
            
            # 關閉MCP組件
            for component in self.mcp_components.values():
                if hasattr(component, 'shutdown'):
                    await component.shutdown()
            
            self.status = "shutdown"
            logger.info("✅ PowerAutomation Core 已關閉")
            
            return {
                "status": "success",
                "message": "PowerAutomation Core 已成功關閉"
            }
            
        except Exception as e:
            logger.error(f"關閉核心系統失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }