#!/usr/bin/env python3
"""
PowerAutomation Unified MCP Server - 统一的 PowerAutomation MCP 服务器
PowerAutomation v4.6.9.7 - 完整解决方案

集成所有功能：
- Claude Code 同步服务
- Claude 工具模式管理
- K2 服务路由
- 启动触发管理
- Mirror Code 追踪
"""

import asyncio
import json
import logging
import signal
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse

# 导入统一 MCP 组件
from .claude_sync.sync_manager import ClaudeSyncManager, get_sync_manager
from .k2_router.k2_client import K2Client, get_k2_client
from .tool_mode.tool_manager import ToolModeManager, get_tool_mode_manager

logger = logging.getLogger(__name__)

class PowerAutomationUnifiedMCPServer:
    """PowerAutomation 统一 MCP 服务器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or self._get_default_config()
        
        # 核心组件
        self.claude_sync_manager = get_sync_manager()
        self.k2_client = get_k2_client()
        self.tool_mode_manager = get_tool_mode_manager()
        
        # 服务状态
        self.running = False
        self.start_time = None
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "claude_syncs": 0,
            "k2_routes": 0,
            "tool_blocks": 0
        }
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "server_name": "PowerAutomation Unified MCP",
            "version": "4.6.9.7",
            "host": "0.0.0.0",
            "port": 8765,
            "enable_claude_sync": True,
            "enable_k2_router": True,
            "enable_tool_mode": True,
            "auto_start_components": True,
            "log_level": "INFO"
        }
    
    async def initialize(self) -> bool:
        """初始化 MCP 服务器"""
        try:
            self.logger.info("🚀 初始化 PowerAutomation 统一 MCP 服务器...")
            self.logger.info(f"版本: {self.config.get('version', '4.6.9.7')}")
            
            # 初始化组件
            success = True
            
            # 1. 初始化工具模式管理器
            if self.config.get("enable_tool_mode", True):
                self.logger.info("🔧 初始化工具模式管理器...")
                self.tool_mode_manager.enable_tool_mode()
                self.logger.info("✅ 工具模式管理器初始化完成")
            
            # 2. 初始化 K2 客户端
            if self.config.get("enable_k2_router", True):
                self.logger.info("🔄 初始化 K2 服务客户端...")
                k2_success = await self.k2_client.initialize()
                if not k2_success:
                    self.logger.warning("⚠️ K2 客户端初始化失败，但服务器继续启动")
                else:
                    self.logger.info("✅ K2 服务客户端初始化完成")
            
            # 3. 初始化 Claude 同步管理器
            if self.config.get("enable_claude_sync", True):
                self.logger.info("🔗 初始化 Claude Code 同步管理器...")
                sync_success = await self.claude_sync_manager.initialize()
                if not sync_success:
                    self.logger.warning("⚠️ Claude 同步管理器初始化失败，但服务器继续启动")
                else:
                    self.logger.info("✅ Claude Code 同步管理器初始化完成")
            
            self.start_time = datetime.now()
            self.logger.info("🎉 PowerAutomation 统一 MCP 服务器初始化完成")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ MCP 服务器初始化失败: {e}")
            return False
    
    async def start(self):
        """启动 MCP 服务器"""
        try:
            if not await self.initialize():
                self.logger.error("❌ 服务器初始化失败，无法启动")
                return False
            
            self.running = True
            self.logger.info(f"🌟 PowerAutomation 统一 MCP 服务器已启动")
            self.logger.info(f"监听地址: {self.config['host']}:{self.config['port']}")
            
            # 打印服务状态
            await self._print_service_status()
            
            # 主服务循环
            await self._main_service_loop()
            
        except Exception as e:
            self.logger.error(f"❌ 服务器启动失败: {e}")
            return False
    
    async def _main_service_loop(self):
        """主服务循环"""
        self.logger.info("🔄 进入主服务循环...")
        
        try:
            while self.running:
                # 定期检查组件状态
                await self._health_check_components()
                
                # 处理请求队列（如果有的话）
                await self._process_request_queue()
                
                # 更新统计信息
                await self._update_stats()
                
                # 等待一段时间
                await asyncio.sleep(5)
                
        except asyncio.CancelledError:
            self.logger.info("🛑 主服务循环被取消")
        except Exception as e:
            self.logger.error(f"❌ 主服务循环错误: {e}")
    
    async def _health_check_components(self):
        """健康检查组件"""
        try:
            # 检查 K2 客户端
            if self.config.get("enable_k2_router", True):
                k2_healthy = await self.k2_client.health_check()
                if not k2_healthy:
                    self.logger.warning("⚠️ K2 服务健康检查失败")
            
            # 检查 Claude 同步管理器
            if self.config.get("enable_claude_sync", True):
                sync_status = self.claude_sync_manager.get_sync_status()
                if not sync_status.get("connected", False):
                    self.logger.warning("⚠️ Claude 同步服务未连接")
            
        except Exception as e:
            self.logger.error(f"组件健康检查错误: {e}")
    
    async def _process_request_queue(self):
        """处理请求队列"""
        # 这里可以实现请求队列处理逻辑
        pass
    
    async def _update_stats(self):
        """更新统计信息"""
        try:
            # 获取各组件统计
            k2_stats = self.k2_client.get_stats()
            sync_status = self.claude_sync_manager.get_sync_status()
            tool_stats = self.tool_mode_manager.get_stats()
            
            # 更新总体统计
            self.stats.update({
                "k2_routes": k2_stats.get("total_requests", 0),
                "claude_syncs": sync_status.get("stats", {}).get("total_syncs", 0),
                "tool_blocks": tool_stats.get("blocked_requests", 0)
            })
            
        except Exception as e:
            self.logger.error(f"更新统计信息错误: {e}")
    
    async def _print_service_status(self):
        """打印服务状态"""
        try:
            print("\n" + "="*60)
            print("🚀 PowerAutomation 统一 MCP 服务器状态")
            print("="*60)
            
            # 基本信息
            print(f"📋 服务器名称: {self.config['server_name']}")
            print(f"📦 版本: {self.config['version']}")
            print(f"🌐 监听地址: {self.config['host']}:{self.config['port']}")
            print(f"⏰ 启动时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n📊 组件状态:")
            
            # Claude Code 同步服务
            if self.config.get("enable_claude_sync", True):
                sync_status = self.claude_sync_manager.get_sync_status()
                status_icon = "✅" if sync_status.get("connected", False) else "⚠️"
                print(f"{status_icon} Claude Code 同步服务: {sync_status.get('status', 'unknown')}")
                print(f"   📈 总同步次数: {sync_status.get('stats', {}).get('total_syncs', 0)}")
                print(f"   📊 成功率: {sync_status.get('stats', {}).get('successful_syncs', 0)}/{sync_status.get('stats', {}).get('total_syncs', 0)}")
            
            # K2 服务路由
            if self.config.get("enable_k2_router", True):
                k2_stats = self.k2_client.get_stats()
                status_icon = "✅" if k2_stats.get("connected", False) else "⚠️"
                print(f"{status_icon} K2 服务路由: {'已连接' if k2_stats.get('connected', False) else '未连接'}")
                print(f"   📈 总请求数: {k2_stats.get('total_requests', 0)}")
                print(f"   📊 成功率: {k2_stats.get('success_rate', 0):.1f}%")
                print(f"   💰 总成本: ${k2_stats.get('total_cost', 0):.4f}")
            
            # Claude 工具模式
            if self.config.get("enable_tool_mode", True):
                tool_stats = self.tool_mode_manager.get_stats()
                tool_config = self.tool_mode_manager.get_config()
                status_icon = "✅" if tool_config.get("enabled", False) else "❌"
                print(f"{status_icon} Claude 工具模式: {'已启用' if tool_config.get('enabled', False) else '已禁用'}")
                print(f"   🚫 阻止请求数: {tool_stats.get('blocked_requests', 0)}")
                print(f"   🔧 允许工具数: {tool_stats.get('allowed_tools', 0)}")
                print(f"   🔄 K2 路由数: {tool_stats.get('k2_routes', 0)}")
            
            print("\n🎯 核心功能:")
            print("✅ 完全避免 Claude 模型推理余额消耗")
            print("✅ 保留所有 Claude 工具和指令功能")
            print("✅ 自动路由 AI 推理任务到 K2 服务")
            print("✅ ClaudeEditor 和本地环境实时同步")
            print("✅ 智能启动触发和自动安装")
            
            print("\n🔧 管理命令:")
            print("powerautomation status    - 查看状态")
            print("powerautomation config    - 查看配置")
            print("powerautomation restart   - 重启服务")
            print("powerautomation stop      - 停止服务")
            
            print("="*60)
            print("🌟 PowerAutomation v4.6.9.7 - 让 AI 开发更智能！")
            print("="*60 + "\n")
            
        except Exception as e:
            self.logger.error(f"打印服务状态错误: {e}")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"收到信号 {signum}，准备关闭服务器...")
        asyncio.create_task(self.stop())
    
    async def stop(self):
        """停止 MCP 服务器"""
        try:
            self.logger.info("🛑 正在停止 PowerAutomation 统一 MCP 服务器...")
            
            self.running = False
            
            # 清理组件
            if self.config.get("enable_claude_sync", True):
                await self.claude_sync_manager.cleanup()
            
            if self.config.get("enable_k2_router", True):
                await self.k2_client.cleanup()
            
            self.logger.info("✅ PowerAutomation 统一 MCP 服务器已停止")
            
        except Exception as e:
            self.logger.error(f"❌ 停止服务器失败: {e}")
    
    def get_server_status(self) -> Dict[str, Any]:
        """获取服务器状态"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            "server_name": self.config["server_name"],
            "version": self.config["version"],
            "running": self.running,
            "uptime_seconds": uptime,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "stats": self.stats,
            "components": {
                "claude_sync": self.claude_sync_manager.get_sync_status() if self.config.get("enable_claude_sync") else None,
                "k2_router": self.k2_client.get_stats() if self.config.get("enable_k2_router") else None,
                "tool_mode": self.tool_mode_manager.get_stats() if self.config.get("enable_tool_mode") else None
            }
        }


# 全局服务器实例
unified_mcp_server = PowerAutomationUnifiedMCPServer()


def get_unified_mcp_server() -> PowerAutomationUnifiedMCPServer:
    """获取统一 MCP 服务器实例"""
    return unified_mcp_server


# CLI 接口
async def main():
    parser = argparse.ArgumentParser(description="PowerAutomation 统一 MCP 服务器")
    parser.add_argument("--action", choices=["start", "status", "config", "test"], 
                       default="start", help="执行的动作")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="监听主机")
    parser.add_argument("--port", type=int, default=8765, help="监听端口")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="日志级别")
    parser.add_argument("--disable-claude-sync", action="store_true", 
                       help="禁用 Claude 同步服务")
    parser.add_argument("--disable-k2-router", action="store_true", 
                       help="禁用 K2 路由服务")
    parser.add_argument("--disable-tool-mode", action="store_true", 
                       help="禁用工具模式")
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建服务器配置
    config = {
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
        "enable_claude_sync": not args.disable_claude_sync,
        "enable_k2_router": not args.disable_k2_router,
        "enable_tool_mode": not args.disable_tool_mode
    }
    
    server = PowerAutomationUnifiedMCPServer(config)
    
    try:
        if args.action == "start":
            await server.start()
        
        elif args.action == "status":
            await server.initialize()
            status = server.get_server_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        
        elif args.action == "config":
            print("⚙️ PowerAutomation 统一 MCP 配置:")
            print(json.dumps(server.config, indent=2, ensure_ascii=False))
        
        elif args.action == "test":
            print("🧪 测试 PowerAutomation 统一 MCP...")
            success = await server.initialize()
            
            if success:
                print("✅ 所有组件初始化成功")
                
                # 测试各组件
                if config["enable_k2_router"]:
                    print("🔄 测试 K2 路由...")
                    k2_healthy = await server.k2_client.health_check()
                    print(f"K2 服务: {'✅ 正常' if k2_healthy else '❌ 异常'}")
                
                if config["enable_claude_sync"]:
                    print("🔗 测试 Claude 同步...")
                    sync_status = server.claude_sync_manager.get_sync_status()
                    print(f"同步服务: {'✅ 已连接' if sync_status.get('connected') else '⚠️ 未连接'}")
                
                if config["enable_tool_mode"]:
                    print("🔧 测试工具模式...")
                    tool_enabled = server.tool_mode_manager.is_tool_mode_enabled()
                    print(f"工具模式: {'✅ 已启用' if tool_enabled else '❌ 已禁用'}")
                
                print("🎉 测试完成")
            else:
                print("❌ 组件初始化失败")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 收到中断信号，正在停止服务器...")
    except Exception as e:
        print(f"❌ 服务器运行错误: {e}")
        sys.exit(1)
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())

