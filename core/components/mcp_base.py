"""
MCP Base Module - PowerAutomation v4.8
提供 MCP (Model Context Protocol) 的基础实现
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class MCPBase(ABC):
    """MCP組件基類"""
    
    def __init__(self):
        self.name = ""
        self.version = "1.0.0"
        self.description = ""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized = False
        
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化MCP組件"""
        pass
    
    async def shutdown(self):
        """關閉MCP組件"""
        self.initialized = False
        self.logger.info(f"MCP組件 {self.name} 已關閉")
    
    def get_capabilities(self) -> List[str]:
        """獲取能力列表"""
        return []