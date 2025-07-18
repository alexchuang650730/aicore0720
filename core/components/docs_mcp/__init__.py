"""
Documentation MCP - 統一文檔管理平台
負責管理所有版本化的文檔
"""

from .docs_manager import docs_manager, DocumentationManager

__all__ = [
    'docs_manager',
    'DocumentationManager'
]