#!/usr/bin/env python3
"""
Command Status Integration - 命令状态集成模块
与 ClaudeEditor 状态显示深度集成，提供实时可视化
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import threading
import time

logger = logging.getLogger(__name__)

class ComponentStatus(Enum):
    """组件状态"""
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    RUNNING = "running"
    IDLE = "idle"
    BUSY = "busy"
    WARNING = "warning"
    ERROR = "error"
    STOPPED = "stopped"

class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class StatusMetric:
    """状态指标"""
    name: str
    value: Union[int, float, str]
    metric_type: MetricType
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None

@dataclass
class ComponentInfo:
    """组件信息"""
    id: str
    name: str
    status: ComponentStatus
    version: str
    uptime: timedelta
    last_activity: datetime
    metrics: List[StatusMetric]
    health_score: float
    description: str = ""

@dataclass
class SystemResource:
    """系统资源"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    timestamp: datetime

class CommandStatusManager:
    """命令状态管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized = False
        
        # 状态数据
        self.components: Dict[str, ComponentInfo] = {}
        self.system_resources: List[SystemResource] = []
        self.status_history: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        
        # 配置
        self.update_interval = 5.0  # 秒
        self.max_history_size = 1000
        self.max_resource_history = 100
        self.enable_monitoring = True
        
        # 监控线程
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # WebSocket 连接（用于实时推送）
        self.websocket_connections: List[Any] = []
        
        # 初始化组件
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化组件"""
        try:
            # 注册核心组件
            self.register_component(
                "enhanced_command_mcp",
                "Enhanced Command MCP",
                "1.0.0",
                "增强命令管理器"
            )
            
            self.register_component(
                "memory_integration",
                "Memory Integration",
                "1.0.0",
                "内存集成模块"
            )
            
            self.register_component(
                "hook_integration",
                "Hook Integration",
                "1.0.0",
                "钩子集成模块"
            )
            
            self.register_component(
                "status_integration",
                "Status Integration",
                "1.0.0",
                "状态集成模块"
            )
            
            self.logger.info("组件初始化完成")
            
        except Exception as e:
            self.logger.error(f"组件初始化失败: {e}")
    
    def register_component(self, component_id: str, name: str, version: str, description: str = ""):
        """注册组件"""
        try:
            component = ComponentInfo(
                id=component_id,
                name=name,
                status=ComponentStatus.INITIALIZING,
                version=version,
                uptime=timedelta(0),
                last_activity=datetime.now(),
                metrics=[],
                health_score=1.0,
                description=description
            )
            
            self.components[component_id] = component
            self.logger.info(f"组件注册成功: {component_id}")
            
            # 通知状态变更
            self._notify_status_change(component_id, ComponentStatus.INITIALIZING)
            
        except Exception as e:
            self.logger.error(f"组件注册失败: {e}")
    
    def update_component_status(self, component_id: str, status: ComponentStatus, 
                              metrics: List[StatusMetric] = None):
        """更新组件状态"""
        try:
            if component_id not in self.components:
                self.logger.warning(f"未找到组件: {component_id}")
                return
            
            component = self.components[component_id]
            old_status = component.status
            
            # 更新状态
            component.status = status
            component.last_activity = datetime.now()
            
            # 更新指标
            if metrics:
                component.metrics = metrics
            
            # 计算健康分数
            component.health_score = self._calculate_health_score(component)
            
            # 记录状态变更
            if old_status != status:
                self._record_status_change(component_id, old_status, status)
                self._notify_status_change(component_id, status)
            
            self.logger.debug(f"组件状态更新: {component_id} -> {status.value}")
            
        except Exception as e:
            self.logger.error(f"更新组件状态失败: {e}")
    
    def add_metric(self, component_id: str, name: str, value: Union[int, float, str], 
                   metric_type: MetricType, unit: str = "", tags: Dict[str, str] = None):
        """添加指标"""
        try:
            if component_id not in self.components:
                self.logger.warning(f"未找到组件: {component_id}")
                return
            
            metric = StatusMetric(
                name=name,
                value=value,
                metric_type=metric_type,
                unit=unit,
                timestamp=datetime.now(),
                tags=tags or {}
            )
            
            component = self.components[component_id]
            
            # 更新或添加指标
            existing_metric = None
            for i, m in enumerate(component.metrics):
                if m.name == name:
                    existing_metric = i
                    break
            
            if existing_metric is not None:
                component.metrics[existing_metric] = metric
            else:
                component.metrics.append(metric)
            
            # 限制指标数量
            if len(component.metrics) > 50:
                component.metrics = component.metrics[-50:]
            
        except Exception as e:
            self.logger.error(f"添加指标失败: {e}")
    
    def start_monitoring(self):
        """开始监控"""
        try:
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.logger.warning("监控已经在运行")
                return
            
            self.stop_monitoring.clear()
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            self.logger.info("状态监控已启动")
            
        except Exception as e:
            self.logger.error(f"启动监控失败: {e}")
    
    def stop_monitoring_service(self):
        """停止监控"""
        try:
            self.stop_monitoring.set()
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5.0)
            
            self.logger.info("状态监控已停止")
            
        except Exception as e:
            self.logger.error(f"停止监控失败: {e}")
    
    def _monitoring_loop(self):
        """监控循环"""
        while not self.stop_monitoring.is_set():
            try:
                # 收集系统资源
                self._collect_system_resources()
                
                # 更新组件运行时间
                self._update_component_uptime()
                
                # 检查组件健康状态
                self._check_component_health()
                
                # 推送状态更新
                self._push_status_updates()
                
                # 等待下次更新
                self.stop_monitoring.wait(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(1.0)
    
    def _collect_system_resources(self):
        """收集系统资源"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # 网络 I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # 进程数量
            process_count = len(psutil.pids())
            
            resource = SystemResource(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io=network_io,
                process_count=process_count,
                timestamp=datetime.now()
            )
            
            self.system_resources.append(resource)
            
            # 限制历史记录大小
            if len(self.system_resources) > self.max_resource_history:
                self.system_resources = self.system_resources[-self.max_resource_history:]
            
        except Exception as e:
            self.logger.error(f"收集系统资源失败: {e}")
    
    def _update_component_uptime(self):
        """更新组件运行时间"""
        try:
            current_time = datetime.now()
            for component in self.components.values():
                if component.status in [ComponentStatus.RUNNING, ComponentStatus.IDLE, ComponentStatus.BUSY]:
                    # 计算运行时间（简化版本）
                    component.uptime = current_time - component.last_activity
                    
        except Exception as e:
            self.logger.error(f"更新组件运行时间失败: {e}")
    
    def _check_component_health(self):
        """检查组件健康状态"""
        try:
            current_time = datetime.now()
            
            for component_id, component in self.components.items():
                # 检查最后活动时间
                inactive_time = current_time - component.last_activity
                
                if inactive_time > timedelta(minutes=5):
                    if component.status != ComponentStatus.ERROR:
                        self.update_component_status(component_id, ComponentStatus.WARNING)
                        self._create_alert(
                            "component_inactive",
                            f"组件 {component.name} 超过5分钟未活动",
                            "warning"
                        )
                
                if inactive_time > timedelta(minutes=10):
                    if component.status != ComponentStatus.ERROR:
                        self.update_component_status(component_id, ComponentStatus.ERROR)
                        self._create_alert(
                            "component_error",
                            f"组件 {component.name} 可能已停止响应",
                            "error"
                        )
                
        except Exception as e:
            self.logger.error(f"检查组件健康状态失败: {e}")
    
    def _calculate_health_score(self, component: ComponentInfo) -> float:
        """计算健康分数"""
        try:
            score = 1.0
            
            # 基于状态的分数
            status_scores = {
                ComponentStatus.RUNNING: 1.0,
                ComponentStatus.IDLE: 0.9,
                ComponentStatus.BUSY: 0.8,
                ComponentStatus.WARNING: 0.5,
                ComponentStatus.ERROR: 0.1,
                ComponentStatus.STOPPED: 0.0,
                ComponentStatus.INITIALIZING: 0.7,
                ComponentStatus.UNKNOWN: 0.3
            }
            
            score *= status_scores.get(component.status, 0.5)
            
            # 基于指标的分数调整
            for metric in component.metrics:
                if metric.name == "error_rate" and isinstance(metric.value, (int, float)):
                    score *= max(0.0, 1.0 - metric.value)
                elif metric.name == "response_time" and isinstance(metric.value, (int, float)):
                    # 响应时间越长，分数越低
                    if metric.value > 1000:  # 毫秒
                        score *= 0.8
                    elif metric.value > 5000:
                        score *= 0.5
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"计算健康分数失败: {e}")
            return 0.5
    
    def _record_status_change(self, component_id: str, old_status: ComponentStatus, new_status: ComponentStatus):
        """记录状态变更"""
        try:
            change_record = {
                "timestamp": datetime.now().isoformat(),
                "component_id": component_id,
                "old_status": old_status.value,
                "new_status": new_status.value
            }
            
            self.status_history.append(change_record)
            
            # 限制历史记录大小
            if len(self.status_history) > self.max_history_size:
                self.status_history = self.status_history[-self.max_history_size:]
            
        except Exception as e:
            self.logger.error(f"记录状态变更失败: {e}")
    
    def _notify_status_change(self, component_id: str, status: ComponentStatus):
        """通知状态变更"""
        try:
            # 这里应该通知 ClaudeEditor UI
            notification = {
                "type": "status_change",
                "component_id": component_id,
                "status": status.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # 推送到 WebSocket 连接
            self._push_to_websockets(notification)
            
        except Exception as e:
            self.logger.error(f"通知状态变更失败: {e}")
    
    def _create_alert(self, alert_type: str, message: str, severity: str):
        """创建警报"""
        try:
            alert = {
                "id": f"alert_{int(time.time())}",
                "type": alert_type,
                "message": message,
                "severity": severity,
                "timestamp": datetime.now().isoformat(),
                "acknowledged": False
            }
            
            self.alerts.append(alert)
            
            # 限制警报数量
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]
            
            # 推送警报
            self._push_to_websockets({
                "type": "alert",
                "alert": alert
            })
            
        except Exception as e:
            self.logger.error(f"创建警报失败: {e}")
    
    def _push_status_updates(self):
        """推送状态更新"""
        try:
            if not self.websocket_connections:
                return
            
            # 准备状态数据
            status_data = {
                "type": "status_update",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    comp_id: {
                        "name": comp.name,
                        "status": comp.status.value,
                        "health_score": comp.health_score,
                        "uptime": str(comp.uptime),
                        "metrics": [asdict(m) for m in comp.metrics[-5:]]  # 最近5个指标
                    }
                    for comp_id, comp in self.components.items()
                },
                "system_resources": asdict(self.system_resources[-1]) if self.system_resources else None,
                "alerts": [alert for alert in self.alerts if not alert["acknowledged"]]
            }
            
            self._push_to_websockets(status_data)
            
        except Exception as e:
            self.logger.error(f"推送状态更新失败: {e}")
    
    def _push_to_websockets(self, data: Dict[str, Any]):
        """推送数据到 WebSocket 连接"""
        try:
            # 这里应该实现 WebSocket 推送逻辑
            # 暂时只记录日志
            self.logger.debug(f"推送数据到 WebSocket: {data['type']}")
            
        except Exception as e:
            self.logger.error(f"推送到 WebSocket 失败: {e}")
    
    # 公共接口方法
    def get_component_status(self, component_id: str = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """获取组件状态"""
        try:
            if component_id:
                if component_id in self.components:
                    component = self.components[component_id]
                    return {
                        "id": component.id,
                        "name": component.name,
                        "status": component.status.value,
                        "version": component.version,
                        "uptime": str(component.uptime),
                        "last_activity": component.last_activity.isoformat(),
                        "health_score": component.health_score,
                        "metrics": [asdict(m) for m in component.metrics],
                        "description": component.description
                    }
                else:
                    return {"error": f"组件未找到: {component_id}"}
            else:
                return [
                    {
                        "id": comp.id,
                        "name": comp.name,
                        "status": comp.status.value,
                        "health_score": comp.health_score,
                        "uptime": str(comp.uptime)
                    }
                    for comp in self.components.values()
                ]
                
        except Exception as e:
            self.logger.error(f"获取组件状态失败: {e}")
            return {"error": str(e)}
    
    def get_system_resources(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取系统资源"""
        try:
            recent_resources = self.system_resources[-limit:] if limit > 0 else self.system_resources
            return [asdict(resource) for resource in recent_resources]
            
        except Exception as e:
            self.logger.error(f"获取系统资源失败: {e}")
            return []
    
    def get_alerts(self, unacknowledged_only: bool = True) -> List[Dict[str, Any]]:
        """获取警报"""
        try:
            if unacknowledged_only:
                return [alert for alert in self.alerts if not alert["acknowledged"]]
            else:
                return self.alerts
                
        except Exception as e:
            self.logger.error(f"获取警报失败: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认警报"""
        try:
            for alert in self.alerts:
                if alert["id"] == alert_id:
                    alert["acknowledged"] = True
                    alert["acknowledged_at"] = datetime.now().isoformat()
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"确认警报失败: {e}")
            return False
    
    def get_status_history(self, component_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取状态历史"""
        try:
            history = self.status_history
            
            if component_id:
                history = [record for record in history if record["component_id"] == component_id]
            
            return history[-limit:] if limit > 0 else history
            
        except Exception as e:
            self.logger.error(f"获取状态历史失败: {e}")
            return []

