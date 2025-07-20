#!/usr/bin/env python3
"""
MCP適配器基類和工廠
統一加載和管理所有MCP組件
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class MCPInterface(ABC):
    """MCP統一接口"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化MCP"""
        pass
    
    @abstractmethod
    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """執行MCP動作"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理資源"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """獲取能力列表"""
        pass

class MCPAdapter(MCPInterface):
    """MCP適配器基類"""
    
    def __init__(self, mcp_instance):
        self.mcp_instance = mcp_instance
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize(self) -> None:
        """初始化MCP"""
        if hasattr(self.mcp_instance, 'initialize'):
            return await self.mcp_instance.initialize()
        return True
    
    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """執行MCP動作"""
        if hasattr(self.mcp_instance, action):
            method = getattr(self.mcp_instance, action)
            if callable(method):
                return await method(**params)
        
        self.logger.warning(f"MCP {self.mcp_instance.__class__.__name__} 不支持動作: {action}")
        return None
    
    async def cleanup(self) -> None:
        """清理資源"""
        if hasattr(self.mcp_instance, 'shutdown'):
            return await self.mcp_instance.shutdown()
        return True
    
    def get_capabilities(self) -> list[str]:
        """獲取能力列表"""
        if hasattr(self.mcp_instance, 'get_capabilities'):
            return self.mcp_instance.get_capabilities()
        
        # 默認從類的方法中推斷能力
        capabilities = []
        for attr in dir(self.mcp_instance):
            if not attr.startswith('_') and callable(getattr(self.mcp_instance, attr)):
                capabilities.append(attr)
        
        return capabilities

class MCPAdapterFactory:
    """MCP適配器工廠"""
    
    @staticmethod
    def create_adapter(mcp_name: str) -> Optional[MCPInterface]:
        """創建MCP適配器"""
        try:
            # 動態導入MCP模塊
            if mcp_name == "claude_realtime_mcp":
                from ..components.claude_realtime_mcp import ClaudeRealtimeMCPManager
                mcp_instance = ClaudeRealtimeMCPManager()
                
            elif mcp_name == "memoryrag_mcp":
                from ..components.memoryrag_mcp.auto_training_collector import auto_training_collector
                mcp_instance = auto_training_collector
                
            elif mcp_name == "smart_intervention":
                from ..components.smart_intervention.mcp_server import smart_intervention_mcp
                mcp_instance = smart_intervention_mcp
                
            elif mcp_name == "codeflow_mcp":
                from ..components.codeflow_mcp.codeflow_manager import codeflow_manager
                mcp_instance = codeflow_manager
                
            elif mcp_name == "smartui_mcp":
                from ..components.smartui_mcp.smartui_manager import smartui_manager
                mcp_instance = smartui_manager
                
            elif mcp_name == "ag_ui_mcp":
                from ..components.ag_ui_mcp.ag_ui_manager import ag_ui_manager
                mcp_instance = ag_ui_manager
                
            elif mcp_name == "test_mcp":
                from ..components.test_mcp.test_mcp_manager import test_mcp_manager
                mcp_instance = test_mcp_manager
                
            elif mcp_name == "stagewise_mcp":
                from ..components.stagewise_mcp.stagewise_manager import stagewise_manager
                mcp_instance = stagewise_manager
                
            elif mcp_name == "smarttool_mcp":
                from ..components.smarttool_mcp.smarttool_manager import smarttool_manager
                mcp_instance = smarttool_manager
                
            else:
                logger.error(f"未知的MCP類型: {mcp_name}")
                return None
            
            # 創建適配器
            adapter = MCPAdapter(mcp_instance)
            logger.info(f"成功創建MCP適配器: {mcp_name}")
            
            return adapter
            
        except ImportError as e:
            logger.error(f"導入MCP {mcp_name} 失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"創建MCP適配器 {mcp_name} 失敗: {e}")
            return None