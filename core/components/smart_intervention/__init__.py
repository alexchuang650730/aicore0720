"""
智能啟動系統
通過關鍵詞和鉤子自動啟動 ClaudeEditor & PowerAutomation
"""

from .claude_keyword_listener import (
    ClaudeKeywordListener,
    ClaudeHookSystem,
    hook_system
)
from .claude_integration import ClaudeIntegration
from .auto_launcher import AutoLauncher

__all__ = [
    'ClaudeKeywordListener',
    'ClaudeHookSystem', 
    'hook_system',
    'ClaudeIntegration',
    'AutoLauncher'
]