"""
PowerAutomation Monitoring MCP Manager
监控 MCP 管理器 - 统一监控系统管理接口
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from .milestone_progress_monitor import MilestoneProgressMonitor
from .intelligent_monitoring import IntelligentMonitoring

logger = logging.getLogger(__name__)

class MonitoringManager:
    """监控 MCP 管理器"""
    
    def __init__(self):
        self.name = "monitoring_mcp"
        self.version = "4.6.9.8"
        self.status = "available"
        self.description = "PowerAutomation 统一监控系统"
        
        # 初始化监控组件
        self.milestone_monitor = None
        self.intelligent_monitor = None
        self.is_initialized = False
        
        # 监控配置
        self.config = {
            "check_interval_hours": 6,
            "report_interval_hours": 24,
            "risk_threshold_days": 7,
            "auto_notifications": True,
            "quality_gates": {
                "min_test_coverage": 80,
                "max_critical_issues": 0,
                "max_high_priority_bugs": 3,
                "required_reviewers": 2
            }
        }
        
        # 监控状态
        self.monitoring_status = {
            "milestone_monitoring": False,
            "intelligent_monitoring": False,
            "health_monitoring": False,
            "last_check": None,
            "last_report": None
        }
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """初始化监控 MCP"""
        try:
            logger.info(f"Initializing {self.name} v{self.version}")
            
            # 更新配置
            if config:
                self.config.update(config)
            
            # 初始化里程碑监控器
            self.milestone_monitor = MilestoneProgressMonitor()
            await self.milestone_monitor.initialize(self.config)
            
            # 初始化智能监控器
            self.intelligent_monitor = IntelligentMonitoring()
            await self.intelligent_monitor.initialize(self.config)
            
            self.is_initialized = True
            self.status = "running"
            
            logger.info(f"{self.name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}: {e}")
            self.status = "error"
            return False
    
    async def start_monitoring(self) -> Dict[str, Any]:
        """启动监控服务"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 启动里程碑监控
            if self.milestone_monitor:
                await self.milestone_monitor.start()
                self.monitoring_status["milestone_monitoring"] = True
            
            # 启动智能监控
            if self.intelligent_monitor:
                await self.intelligent_monitor.start()
                self.monitoring_status["intelligent_monitoring"] = True
            
            # 启动健康监控
            await self._start_health_monitoring()
            self.monitoring_status["health_monitoring"] = True
            
            self.monitoring_status["last_check"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "message": "Monitoring services started",
                "monitoring_status": self.monitoring_status
            }
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return {
                "status": "error",
                "message": f"Failed to start monitoring: {e}"
            }
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """停止监控服务"""
        try:
            # 停止里程碑监控
            if self.milestone_monitor:
                await self.milestone_monitor.stop()
                self.monitoring_status["milestone_monitoring"] = False
            
            # 停止智能监控
            if self.intelligent_monitor:
                await self.intelligent_monitor.stop()
                self.monitoring_status["intelligent_monitoring"] = False
            
            # 停止健康监控
            self.monitoring_status["health_monitoring"] = False
            
            return {
                "status": "success",
                "message": "Monitoring services stopped",
                "monitoring_status": self.monitoring_status
            }
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return {
                "status": "error",
                "message": f"Failed to stop monitoring: {e}"
            }
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        return {
            "mcp_info": {
                "name": self.name,
                "version": self.version,
                "status": self.status,
                "description": self.description
            },
            "monitoring_status": self.monitoring_status,
            "config": self.config,
            "is_initialized": self.is_initialized
        }
    
    async def get_milestone_progress(self) -> Dict[str, Any]:
        """获取里程碑进度"""
        if not self.milestone_monitor:
            return {"error": "Milestone monitor not initialized"}
        
        return await self.milestone_monitor.get_progress_report()
    
    async def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        if not self.intelligent_monitor:
            return {"error": "Intelligent monitor not initialized"}
        
        return await self.intelligent_monitor.get_health_report()
    
    async def generate_report(self, report_type: str = "full") -> Dict[str, Any]:
        """生成监控报告"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "report_type": report_type,
                "mcp_status": await self.get_monitoring_status()
            }
            
            if report_type in ["full", "milestone"]:
                report["milestone_progress"] = await self.get_milestone_progress()
            
            if report_type in ["full", "health"]:
                report["system_health"] = await self.get_system_health()
            
            # 更新最后报告时间
            self.monitoring_status["last_report"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate report: {e}"
            }
    
    async def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """更新监控配置"""
        try:
            self.config.update(new_config)
            
            # 更新子组件配置
            if self.milestone_monitor:
                await self.milestone_monitor.update_config(new_config)
            
            if self.intelligent_monitor:
                await self.intelligent_monitor.update_config(new_config)
            
            return {
                "status": "success",
                "message": "Configuration updated",
                "config": self.config
            }
            
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return {
                "status": "error",
                "message": f"Failed to update config: {e}"
            }
    
    async def _start_health_monitoring(self):
        """启动健康监控"""
        # 这里可以添加系统健康监控逻辑
        logger.info("Health monitoring started")
    
    # MCP 标准接口方法
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        return [
            {
                "name": "start_monitoring",
                "description": "启动监控服务",
                "parameters": {}
            },
            {
                "name": "stop_monitoring", 
                "description": "停止监控服务",
                "parameters": {}
            },
            {
                "name": "get_monitoring_status",
                "description": "获取监控状态",
                "parameters": {}
            },
            {
                "name": "get_milestone_progress",
                "description": "获取里程碑进度",
                "parameters": {}
            },
            {
                "name": "get_system_health",
                "description": "获取系统健康状态", 
                "parameters": {}
            },
            {
                "name": "generate_report",
                "description": "生成监控报告",
                "parameters": {
                    "report_type": {
                        "type": "string",
                        "description": "报告类型: full, milestone, health",
                        "default": "full"
                    }
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        try:
            if name == "start_monitoring":
                return await self.start_monitoring()
            elif name == "stop_monitoring":
                return await self.stop_monitoring()
            elif name == "get_monitoring_status":
                return await self.get_monitoring_status()
            elif name == "get_milestone_progress":
                return await self.get_milestone_progress()
            elif name == "get_system_health":
                return await self.get_system_health()
            elif name == "generate_report":
                report_type = arguments.get("report_type", "full")
                return await self.generate_report(report_type)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown tool: {name}"
                }
                
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return {
                "status": "error",
                "message": f"Error calling tool {name}: {e}"
            }

# 全局实例
monitoring_manager = MonitoringManager()

