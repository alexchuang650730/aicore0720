"""
MCP-Zero 動態加載架構
實現按需加載 MCP，優化上下文使用
"""

from .mcp_registry import MCPRegistry, MCPMetadata, MCPInterface, mcp_registry
from .task_planner import TaskPlanner, TaskStep, TaskContext, TaskType
from .context_manager import ContextManager, ContextWindow
from .mcp_zero_engine import MCPZeroEngine, ExecutionResult, StepResult, mcp_zero_engine

__all__ = [
    # Registry
    'MCPRegistry',
    'MCPMetadata', 
    'MCPInterface',
    'mcp_registry',
    
    # Planner
    'TaskPlanner',
    'TaskStep',
    'TaskContext',
    'TaskType',
    
    # Context Manager
    'ContextManager',
    'ContextWindow',
    
    # Engine
    'MCPZeroEngine',
    'ExecutionResult',
    'StepResult',
    'mcp_zero_engine'
]

__version__ = '0.1.0'