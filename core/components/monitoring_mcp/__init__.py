"""
PowerAutomation Monitoring MCP
监控 MCP 组件 - 统一监控系统

提供里程碑监控、智能监控和系统健康监控功能
"""

from .monitoring_manager import MonitoringManager, monitoring_manager
from .milestone_progress_monitor import MilestoneProgressMonitor
from .intelligent_monitoring import IntelligentMonitoring

__version__ = "4.6.9.8"
__author__ = "PowerAutomation Team"
__description__ = "PowerAutomation 统一监控系统"

# 导出主要组件
__all__ = [
    'MonitoringManager',
    'monitoring_manager',
    'MilestoneProgressMonitor', 
    'IntelligentMonitoring',
    '__version__',
    '__author__',
    '__description__'
]

# MCP 元数据
MCP_INFO = {
    "name": "monitoring_mcp",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "type": "monitoring",
    "capabilities": [
        "milestone_tracking",
        "progress_monitoring", 
        "risk_assessment",
        "health_monitoring",
        "automated_reporting",
        "notification_system"
    ],
    "dependencies": [
        "aiohttp",
        "PyGithub", 
        "pyyaml",
        "gitpython"
    ],
    "entry_point": "monitoring_manager"
}

