#!/usr/bin/env python3
"""
Local Adapter MCP - 本地适配器 MCP 组件
PowerAutomation v4.6.1 本地系统集成和适配层
"""

from .local_adapter_manager import local_adapter_mcp, LocalAdapterMCPManager
from .file_system_adapter import file_system_adapter, FileSystemAdapter

__all__ = [
    'local_adapter_mcp',
    'LocalAdapterMCPManager', 
    'file_system_adapter',
    'FileSystemAdapter'
]

__version__ = '4.6.1'

