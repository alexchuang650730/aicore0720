"""
Test MCP - 統一測試管理平台
支持單元測試、集成測試、性能測試、UI操作測試
自動生成測試案例並執行
"""

from .test_mcp_manager import test_mcp, TestMCPManager
from .test_case_generator import test_case_generator, TestCaseGenerator
from .test_executors import test_executor_manager, TestExecutorManager

__all__ = [
    'test_mcp',
    'TestMCPManager',
    'test_case_generator',
    'TestCaseGenerator',
    'test_executor_manager',
    'TestExecutorManager'
]