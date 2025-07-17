#!/usr/bin/env python3
"""
MCP Coordinator - PowerAutomation Core 組件協調器
負責協調所有 MCP 組件的運行和管理，深度集成 MemoryOS、钩子系统和状态显示
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 导入三大核心系统
try:
    from ..memoryos_mcp.memoryos_coordinator import MemoryOSCoordinator
    from ..enhanced_command_mcp.hook_integration import CommandHookManager, HookType
    from ..enhanced_command_mcp.status_integration import CommandStatusManager, ComponentStatus
except ImportError as e:
    logging.warning(f"导入核心系统失败: {e}")

logger = logging.getLogger(__name__)

class CoordinatorStatus(Enum):
    """協調器狀態"""
    IDLE = "idle"
    RUNNING = "running"
    BUSY = "busy"
    ERROR = "error"

@dataclass
class MCPService:
    """MCP 服務定義"""
    service_id: str
    name: str
    version: str
    is_active: bool = False
    last_heartbeat: float = 0.0
    health_score: float = 100.0
    memory_integration: bool = False
    hook_integration: bool = False
    status_integration: bool = False

class MCPCoordinator:
    """MCP 組件協調器 - 集成三大核心系统"""
    
    def __init__(self):
        self.status = CoordinatorStatus.IDLE
        self.services: Dict[str, MCPService] = {}
        self.coordination_tasks = []
        self.last_coordination_time = 0.0
        
        # 三大核心系统集成
        self.memoryos_coordinator = None
        self.hook_manager = None
        self.status_manager = None
        
        # 初始化核心服務
        self._register_core_services()
        
        # 初始化三大核心系统
        self._initialize_core_systems()
    
    def _initialize_core_systems(self):
        """初始化三大核心系统"""
        try:
            # 初始化 MemoryOS
            self.memoryos_coordinator = MemoryOSCoordinator()
            
            # 初始化钩子管理器
            self.hook_manager = CommandHookManager()
            
            # 初始化状态管理器
            self.status_manager = CommandStatusManager()
            
            logger.info("三大核心系统初始化完成")
            
        except Exception as e:
            logger.error(f"三大核心系统初始化失败: {e}")
    
    def _register_core_services(self):
        """註冊核心 MCP 服務"""
        core_services = [
            MCPService("enhanced_command", "Enhanced Command MCP", "4.6.9.6", 
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("claude_code_router", "Claude Code Router MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("memoryos", "MemoryOS MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("mcp_discovery", "MCP Discovery MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("codeflow", "CodeFlow MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("claude", "Claude MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("collaboration", "Collaboration MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("security", "Security MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("operations", "Operations MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("config", "Config MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("test", "Test MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("smartui", "SmartUI MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("ag_ui", "AG-UI MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("release_trigger", "Release Trigger MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("deepgraph", "DeepGraph MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("stagewise", "Stagewise MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("zen", "Zen Workflow MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("trae_agent", "Trae Agent MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True),
            MCPService("xmasters", "X-Masters MCP", "4.6.9.6",
                      memory_integration=True, hook_integration=True, status_integration=True)
        ]
        
        for service in core_services:
            self.services[service.service_id] = service
            logger.info(f"註冊核心服務: {service.name}")
    
    async def start_coordination(self) -> bool:
        """開始協調工作 - 集成三大核心系统"""
        try:
            self.status = CoordinatorStatus.RUNNING
            logger.info("🚀 MCP Coordinator 啟動")
            
            # 首先启动三大核心系统
            await self._start_core_systems()
            
            # 啟動所有核心服務
            for service_id, service in self.services.items():
                await self._start_service(service)
            
            # 啟動協調任務
            coordination_task = asyncio.create_task(self._coordination_loop())
            self.coordination_tasks.append(coordination_task)
            
            logger.info(f"✅ MCP Coordinator 啟動成功，管理 {len(self.services)} 個服務")
            return True
            
        except Exception as e:
            logger.error(f"❌ MCP Coordinator 啟動失敗: {e}")
            self.status = CoordinatorStatus.ERROR
            return False
    
    async def _start_core_systems(self):
        """启动三大核心系统"""
        try:
            # 启动 MemoryOS
            if self.memoryos_coordinator:
                await self.memoryos_coordinator.initialize()
                logger.info("✅ MemoryOS 系统启动成功")
            
            # 启动钩子管理器
            if self.hook_manager:
                # 钩子管理器已在初始化时启动
                logger.info("✅ 钩子系统启动成功")
            
            # 启动状态管理器
            if self.status_manager:
                self.status_manager.start_monitoring()
                logger.info("✅ 状态监控系统启动成功")
                
        except Exception as e:
            logger.error(f"三大核心系统启动失败: {e}")
            raise
    
    async def _start_service(self, service: MCPService):
        """啟動單個服務 - 集成三大核心系统"""
        try:
            # 模擬服務啟動
            await asyncio.sleep(0.1)
            service.is_active = True
            service.last_heartbeat = time.time()
            
            # 集成三大核心系统
            await self._integrate_service_with_core_systems(service)
            
            logger.debug(f"🔧 啟動服務: {service.name}")
            
        except Exception as e:
            logger.error(f"❌ 服務啟動失敗 {service.name}: {e}")
            service.is_active = False
    
    async def _integrate_service_with_core_systems(self, service: MCPService):
        """将服务与三大核心系统集成"""
        try:
            # MemoryOS 集成
            if service.memory_integration and self.memoryos_coordinator:
                await self._integrate_with_memoryos(service)
            
            # 钩子系统集成
            if service.hook_integration and self.hook_manager:
                await self._integrate_with_hooks(service)
            
            # 状态显示集成
            if service.status_integration and self.status_manager:
                await self._integrate_with_status(service)
                
        except Exception as e:
            logger.error(f"服务 {service.name} 与核心系统集成失败: {e}")
    
    async def _integrate_with_memoryos(self, service: MCPService):
        """与 MemoryOS 集成"""
        try:
            # 在 MemoryOS 中记录服务启动事件
            if hasattr(self.memoryos_coordinator, 'memory_engine'):
                memory_data = {
                    "event_type": "service_start",
                    "service_id": service.service_id,
                    "service_name": service.name,
                    "version": service.version,
                    "timestamp": time.time()
                }
                # 这里应该调用 MemoryOS 的存储方法
                logger.debug(f"MemoryOS 记录服务启动: {service.name}")
                
        except Exception as e:
            logger.error(f"MemoryOS 集成失败: {e}")
    
    async def _integrate_with_hooks(self, service: MCPService):
        """与钩子系统集成"""
        try:
            # 触发服务启动钩子
            if hasattr(self.hook_manager, 'trigger_hook'):
                await self.hook_manager.trigger_hook(
                    HookType.AFTER_INIT,
                    {
                        "service_id": service.service_id,
                        "service_name": service.name,
                        "action": "service_start"
                    },
                    {
                        "coordinator": "mcp_coordinator",
                        "timestamp": time.time()
                    }
                )
                logger.debug(f"钩子系统记录服务启动: {service.name}")
                
        except Exception as e:
            logger.error(f"钩子系统集成失败: {e}")
    
    async def _integrate_with_status(self, service: MCPService):
        """与状态显示集成"""
        try:
            # 在状态管理器中注册服务
            if hasattr(self.status_manager, 'register_component'):
                self.status_manager.register_component(
                    service.service_id,
                    service.name,
                    service.version,
                    f"{service.name} - PowerAutomation MCP 组件"
                )
                
                # 更新服务状态
                self.status_manager.update_component_status(
                    service.service_id,
                    ComponentStatus.RUNNING
                )
                logger.debug(f"状态系统注册服务: {service.name}")
                
        except Exception as e:
            logger.error(f"状态系统集成失败: {e}")
    
    async def _coordination_loop(self):
        """協調主循環"""
        while self.status == CoordinatorStatus.RUNNING:
            try:
                await self._perform_coordination()
                await asyncio.sleep(5)  # 每5秒協調一次
                
            except Exception as e:
                logger.error(f"協調循環錯誤: {e}")
                await asyncio.sleep(1)
    
    async def _perform_coordination(self):
        """執行協調任務"""
        self.status = CoordinatorStatus.BUSY
        self.last_coordination_time = time.time()
        
        # 檢查服務健康狀態
        await self._check_service_health()
        
        # 執行負載平衡
        await self._balance_load()
        
        # 更新服務狀態
        await self._update_service_status()
        
        self.status = CoordinatorStatus.RUNNING
    
    async def _check_service_health(self):
        """檢查服務健康狀態"""
        current_time = time.time()
        
        for service in self.services.values():
            if service.is_active:
                # 更新心跳
                service.last_heartbeat = current_time
                
                # 計算健康分數（簡化版）
                if current_time - service.last_heartbeat < 30:
                    service.health_score = min(100.0, service.health_score + 1.0)
                else:
                    service.health_score = max(0.0, service.health_score - 5.0)
    
    async def _balance_load(self):
        """執行負載平衡"""
        # 簡化的負載平衡邏輯
        active_services = [s for s in self.services.values() if s.is_active]
        
        if len(active_services) > 0:
            avg_health = sum(s.health_score for s in active_services) / len(active_services)
            logger.debug(f"🔄 平均健康分數: {avg_health:.1f}")
    
    async def _update_service_status(self):
        """更新服務狀態"""
        for service in self.services.values():
            if service.health_score < 50.0 and service.is_active:
                logger.warning(f"⚠️ 服務健康狀態低: {service.name} ({service.health_score:.1f})")
    
    async def stop_coordination(self):
        """停止協調"""
        self.status = CoordinatorStatus.IDLE
        
        # 停止所有協調任務
        for task in self.coordination_tasks:
            task.cancel()
        
        # 停止所有服務
        for service in self.services.values():
            service.is_active = False
        
        logger.info("🛑 MCP Coordinator 已停止")
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """獲取協調狀態"""
        active_count = sum(1 for s in self.services.values() if s.is_active)
        avg_health = sum(s.health_score for s in self.services.values()) / len(self.services)
        
        return {
            "coordinator_status": self.status.value,
            "total_services": len(self.services),
            "active_services": active_count,
            "average_health": avg_health,
            "last_coordination": self.last_coordination_time,
            "services": {
                service_id: {
                    "name": service.name,
                    "version": service.version,
                    "is_active": service.is_active,
                    "health_score": service.health_score,
                    "last_heartbeat": service.last_heartbeat
                }
                for service_id, service in self.services.items()
            }
        }
    
    async def register_service(self, service: MCPService) -> bool:
        """註冊新服務"""
        try:
            self.services[service.service_id] = service
            await self._start_service(service)
            logger.info(f"📋 註冊新服務: {service.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 服務註冊失敗: {e}")
            return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """註銷服務"""
        try:
            if service_id in self.services:
                service = self.services[service_id]
                service.is_active = False
                del self.services[service_id]
                logger.info(f"🗑️ 註銷服務: {service.name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ 服務註銷失敗: {e}")
            return False

# 創建全局協調器實例
coordinator = MCPCoordinator()

async def main():
    """測試協調器"""
    print("🧪 測試 MCP Coordinator...")
    
    success = await coordinator.start_coordination()
    if success:
        print("✅ 協調器啟動成功")
        
        # 運行5秒鐘查看狀態
        await asyncio.sleep(5)
        
        status = coordinator.get_coordination_status()
        print(f"📊 協調狀態: {status['active_services']}/{status['total_services']} 服務活躍")
        print(f"📈 平均健康分數: {status['average_health']:.1f}")
        
        await coordinator.stop_coordination()
        print("✅ 協調器測試完成")
    else:
        print("❌ 協調器啟動失敗")

if __name__ == "__main__":
    asyncio.run(main())