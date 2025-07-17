"""
SmartUI MCP - 智能响应式UI系统
PowerAutomation v4.6.9.6 基于AG-UI指导的智能UI适配系统

基于现有AG-UI MCP的智能指导，提供：
- 智能响应式布局适配
- Desktop/PC优化设计
- 基于AG-UI的智能UI决策
- 实时设备检测和适配
"""

from .smartui_manager import SmartUIManager
from .responsive_engine import ResponsiveEngine
from .device_detector import DeviceDetector
from .layout_optimizer import LayoutOptimizer

__version__ = "4.6.9.6"
__author__ = "PowerAutomation Team"

__all__ = [
    "SmartUIManager",
    "ResponsiveEngine", 
    "DeviceDetector",
    "LayoutOptimizer"
]

