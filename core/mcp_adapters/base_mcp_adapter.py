#!/usr/bin/env python3
"""
MCP 適配器基類
讓現有 MCP 支持 MCP-Zero 動態加載
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import importlib
import inspect

from ..mcp_zero.mcp_registry import MCPInterface

logger = logging.getLogger(__name__)


class BaseMCPAdapter(MCPInterface):
    """MCP 適配器基類 - 讓現有 MCP 兼容 MCP-Zero"""
    
    def __init__(self, mcp_name: str):
        self.mcp_name = mcp_name
        self.mcp_instance = None
        self.is_initialized = False
        self.capabilities_cache = None
        
    async def initialize(self) -> None:
        """初始化 MCP"""
        if self.is_initialized:
            return
            
        logger.info(f"初始化 MCP 適配器: {self.mcp_name}")
        
        try:
            # 動態導入原始 MCP
            module_path = f"core.mcp.{self.mcp_name}"
            module = importlib.import_module(module_path)
            
            # 查找 MCP 類
            mcp_class = self._find_mcp_class(module)
            if not mcp_class:
                raise Exception(f"無法找到 MCP 類: {self.mcp_name}")
                
            # 創建實例
            self.mcp_instance = mcp_class()
            
            # 調用原始初始化方法
            if hasattr(self.mcp_instance, 'initialize'):
                await self.mcp_instance.initialize()
            elif hasattr(self.mcp_instance, 'init'):
                await self.mcp_instance.init()
            elif hasattr(self.mcp_instance, 'setup'):
                await self.mcp_instance.setup()
                
            self.is_initialized = True
            logger.info(f"MCP {self.mcp_name} 初始化成功")
            
        except Exception as e:
            logger.error(f"初始化 MCP {self.mcp_name} 失敗: {str(e)}")
            raise
            
    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """執行 MCP 動作"""
        if not self.is_initialized:
            await self.initialize()
            
        logger.info(f"執行 MCP {self.mcp_name} 動作: {action}")
        
        # 查找對應的方法
        if hasattr(self.mcp_instance, action):
            method = getattr(self.mcp_instance, action)
            
            # 檢查是否是異步方法
            if inspect.iscoroutinefunction(method):
                return await method(**params)
            else:
                return method(**params)
        else:
            # 嘗試通用執行方法
            if hasattr(self.mcp_instance, 'execute'):
                return await self.mcp_instance.execute(action, params)
            elif hasattr(self.mcp_instance, 'run'):
                return await self.mcp_instance.run(action, params)
            else:
                raise Exception(f"MCP {self.mcp_name} 不支持動作: {action}")
                
    async def cleanup(self) -> None:
        """清理資源"""
        if not self.is_initialized:
            return
            
        logger.info(f"清理 MCP {self.mcp_name}")
        
        # 調用原始清理方法
        if hasattr(self.mcp_instance, 'cleanup'):
            await self.mcp_instance.cleanup()
        elif hasattr(self.mcp_instance, 'close'):
            await self.mcp_instance.close()
        elif hasattr(self.mcp_instance, 'shutdown'):
            await self.mcp_instance.shutdown()
            
        self.mcp_instance = None
        self.is_initialized = False
        
    def get_capabilities(self) -> List[str]:
        """獲取能力列表"""
        if self.capabilities_cache:
            return self.capabilities_cache
            
        if not self.mcp_instance:
            return []
            
        # 嘗試從實例獲取
        if hasattr(self.mcp_instance, 'get_capabilities'):
            self.capabilities_cache = self.mcp_instance.get_capabilities()
        elif hasattr(self.mcp_instance, 'capabilities'):
            self.capabilities_cache = self.mcp_instance.capabilities
        else:
            # 通過反射獲取公開方法
            methods = []
            for name, method in inspect.getmembers(self.mcp_instance, inspect.ismethod):
                if not name.startswith('_'):  # 排除私有方法
                    methods.append(name)
            self.capabilities_cache = methods
            
        return self.capabilities_cache
        
    def _find_mcp_class(self, module):
        """查找模塊中的 MCP 類"""
        # 嘗試常見的類名模式
        class_name_patterns = [
            ''.join(word.capitalize() for word in self.mcp_name.split('_')),  # CodeflowMcp
            self.mcp_name.upper().replace('_', ''),  # CODEFLOWMCP
            self.mcp_name.replace('_mcp', '').capitalize() + 'MCP',  # CodeflowMCP
            self.mcp_name.replace('_mcp', '').capitalize() + 'Manager'  # CodeflowManager
        ]
        
        for pattern in class_name_patterns:
            if hasattr(module, pattern):
                return getattr(module, pattern)
                
        # 如果找不到，返回第一個類
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if module.__name__ in str(obj):  # 確保是本模塊的類
                return obj
                
        return None


# 具體的 MCP 適配器實現
class CodeflowMCPAdapter(BaseMCPAdapter):
    """CodeFlow MCP 適配器"""
    
    def __init__(self):
        super().__init__("codeflow_mcp")
        
    def get_capabilities(self) -> List[str]:
        """CodeFlow 特定能力"""
        return [
            "generate_code",
            "analyze_code", 
            "refactor_code",
            "generate_tests",
            "code_to_spec"
        ]


class SmartUIMCPAdapter(BaseMCPAdapter):
    """SmartUI MCP 適配器"""
    
    def __init__(self):
        super().__init__("smartui_mcp")
        
    def get_capabilities(self) -> List[str]:
        return [
            "generate_ui",
            "responsive_design",
            "theme_management",
            "device_adaptation"
        ]


class TestMCPAdapter(BaseMCPAdapter):
    """Test MCP 適配器"""
    
    def __init__(self):
        super().__init__("test_mcp")
        
    def get_capabilities(self) -> List[str]:
        return [
            "generate_unit_tests",
            "integration_testing",
            "coverage_analysis",
            "test_execution"
        ]


# 適配器工廠
class MCPAdapterFactory:
    """MCP 適配器工廠"""
    
    # 註冊的適配器
    _adapters = {
        "codeflow_mcp": CodeflowMCPAdapter,
        "smartui_mcp": SmartUIMCPAdapter,
        "test_mcp": TestMCPAdapter,
        # 可以繼續添加其他適配器
    }
    
    @classmethod
    def create_adapter(cls, mcp_name: str) -> BaseMCPAdapter:
        """創建適配器實例"""
        if mcp_name in cls._adapters:
            # 使用特定適配器
            return cls._adapters[mcp_name]()
        else:
            # 使用通用適配器
            return BaseMCPAdapter(mcp_name)
            
    @classmethod
    def register_adapter(cls, mcp_name: str, adapter_class):
        """註冊新的適配器"""
        cls._adapters[mcp_name] = adapter_class
        
    @classmethod
    def list_registered_adapters(cls) -> List[str]:
        """列出已註冊的適配器"""
        return list(cls._adapters.keys())