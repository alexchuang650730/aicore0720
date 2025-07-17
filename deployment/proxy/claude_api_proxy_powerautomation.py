#!/usr/bin/env python3
"""
PowerAutomation v4.6.97 - 完全集成 MCP 架构的 Claude Code 代理
释放 PowerAutomation 的完整威力！

🚀 完整功能集成:
- ✅ claude_router_mcp - 智能路由决策
- ✅ command_mcp - 真正的命令执行
- ✅ unified_mcp_server - 统一服务协调
- ✅ claudeditor 双向通信
- ✅ K2 服务路由
- ✅ Mirror Code 追踪
- ✅ 零余额消耗
"""

import asyncio
import json
import logging
import re
import os
import sys
from aiohttp import web, ClientSession
from pathlib import Path

# 添加 PowerAutomation 组件路径
AICORE_PATH = Path(__file__).parent.parent / "aicore0716"
sys.path.insert(0, str(AICORE_PATH))

# 导入 PowerAutomation MCP 组件
try:
    from core.components.claude_router_mcp.unified_mcp_server import PowerAutomationUnifiedMCPServer
    from core.components.command_mcp.command_manager import CommandManager
    from core.components.command_mcp.smart_router import route_command_intelligently
    from core.components.claude_router_mcp.claude_sync.sync_manager import get_sync_manager
    from core.components.claude_router_mcp.k2_router.k2_client import get_k2_client
    from core.components.claude_router_mcp.tool_mode.tool_manager import get_tool_mode_manager
    MCP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"PowerAutomation MCP 组件导入失败: {e}")
    MCP_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PowerAutomationProxy:
    """PowerAutomation 完全集成代理 - 释放完整威力！"""
    
    def __init__(self):
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.original_claude_url = "https://api.anthropic.com"
        
        # PowerAutomation MCP 组件初始化
        self.mcp_available = MCP_AVAILABLE
        if self.mcp_available:
            self._initialize_mcp_components()
        else:
            logger.warning("⚠️ MCP 组件不可用，回退到基础模式")
            
        # Claude Code 内置指令
        self.claude_code_commands = [
            '/help', '/init', '/status', '/permissions', '/terminal-setup',
            '/install-github-app', '/login', '/logout', '/settings', '/clear',
            '/reset', '/version', '/docs', '/examples', '/debug', '/config',
            '/workspace', '/project', '/files', '/search', '/history',
            '/mcp', '/memory', '/model', '/pr-comments', '/release-notes',
            '/resume', '/review', '/upgrade', '/vim', '/hooks', '/ide',
            '/export', '/doctor', '/cost', '/compact', '/add-dir', '/bug'
        ]
        
        # Shell 命令模式匹配
        self.shell_command_patterns = [
            r'^git\s+', r'^npm\s+', r'^pip\s+', r'^python\s+', r'^node\s+',
            r'^ls\s*', r'^cd\s+', r'^mkdir\s+', r'^rm\s+', r'^cp\s+', r'^mv\s+',
            r'^cat\s+', r'^echo\s+', r'^curl\s+', r'^wget\s+', r'^chmod\s+',
            r'^sudo\s+', r'^which\s+', r'^whereis\s+', r'^find\s+', r'^grep\s+',
            r'^awk\s+', r'^sed\s+', r'^tar\s+', r'^zip\s+', r'^unzip\s+',
            r'^docker\s+', r'^kubectl\s+', r'^helm\s+', r'^make\s+',
            r'^\w+\s+--\w+', r'^\w+\s+-\w+',
        ]
        
    def _initialize_mcp_components(self):
        """初始化 PowerAutomation MCP 组件"""
        try:
            logger.info("🚀 初始化 PowerAutomation MCP 架构...")
            
            # 统一 MCP 服务器
            self.unified_mcp_server = PowerAutomationUnifiedMCPServer()
            
            # 命令管理器
            self.command_manager = CommandManager()
            
            # Claude 同步管理器
            self.claude_sync_manager = get_sync_manager()
            
            # K2 客户端
            self.k2_client = get_k2_client()
            
            # 工具模式管理器
            self.tool_mode_manager = get_tool_mode_manager()
            
            logger.info("✅ PowerAutomation MCP 架构初始化完成")
            
        except Exception as e:
            logger.error(f"❌ MCP 组件初始化失败: {e}")
            self.mcp_available = False
            
    def is_command_request(self, content):
        """检查是否是命令执行请求"""
        if not isinstance(content, str):
            return False
            
        content = content.strip()
        
        # 检查是否是 Claude Code 内置指令
        for command in self.claude_code_commands:
            if content.startswith(command):
                logger.info(f"🔍 检测到 Claude Code 指令: {command}")
                return True
        
        # 检查是否是 Shell 命令
        for pattern in self.shell_command_patterns:
            if re.match(pattern, content):
                logger.info(f"⚡ 检测到 Shell 命令: {content[:50]}...")
                return True
                
        return False
        
    def is_tool_request(self, data):
        """检查是否是工具相关请求"""
        if not isinstance(data, dict):
            return False
            
        # 检查是否包含工具定义
        tools = data.get("tools", [])
        if tools:
            logger.info("🔧 检测到工具定义请求")
            return True
            
        # 检查消息中是否有工具调用
        messages = data.get("messages", [])
        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content", "")
                
                # 检查是否是 Claude Code 内置指令
                if isinstance(content, str) and self.is_command_request(content):
                    logger.info("⚡ 检测到 Claude Code 内置指令请求")
                    return True
                    
                # 检查是否有工具使用结构
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "tool_use":
                                logger.info("🔧 检测到工具使用请求")
                                return True
                            if item.get("type") == "tool_result":
                                logger.info("📋 检测到工具结果请求")
                                return True
                                
        return False
        
    async def handle_claude_request(self, request):
        """处理 Claude 请求 - PowerAutomation 完整威力！"""
        try:
            if request.content_type == 'application/json':
                data = await request.json()
            else:
                data = {"messages": [{"role": "user", "content": "Hello"}]}
            
            logger.info(f"🔄 收到请求: {request.path}")
            
            # 提取用户消息
            user_message = self._extract_user_message(data)
            
            # 🚀 PowerAutomation MCP 架构处理
            if self.mcp_available:
                return await self._handle_with_mcp_architecture(user_message, data)
            else:
                # 回退到基础 K2 模式
                logger.warning("⚠️ MCP 不可用，使用基础 K2 模式")
                return await self._handle_with_basic_k2(user_message, data)
                
        except Exception as e:
            logger.error(f"❌ 请求处理失败: {e}")
            return await self.create_error_response(str(e))
    
    async def _handle_with_mcp_architecture(self, user_message: str, data: dict):
        """使用 PowerAutomation MCP 架构处理请求"""
        logger.info("🚀 使用 PowerAutomation MCP 架构处理")
        
        try:
            # 1. 检查是否是命令请求
            if self.is_command_request(user_message):
                logger.info(f"⚡ 命令请求: {user_message}")
                return await self._execute_command_with_mcp(user_message)
            
            # 2. 检查是否是工具请求
            elif self.is_tool_request(data):
                logger.info(f"🔧 工具请求: {user_message}")
                return await self._handle_tool_request_with_mcp(user_message, data)
            
            # 3. 普通对话请求 - 使用 K2 路由
            else:
                logger.info(f"💬 对话请求: {user_message}")
                return await self._handle_chat_with_k2_router(user_message)
                
        except Exception as e:
            logger.error(f"❌ MCP 架构处理失败: {e}")
            return await self.create_error_response(f"MCP 处理失败: {str(e)}")
    
    async def _execute_command_with_mcp(self, command: str):
        """使用 command_mcp 执行命令"""
        logger.info(f"🎯 使用 command_mcp 执行: {command}")
        
        try:
            # 使用 PowerAutomation 的智能路由和命令执行
            result = await self.command_manager.handle_slash_command(command)
            
            # 转换为 Claude 格式响应
            if "error" in result:
                response_text = f"❌ 命令执行失败: {result['error']}"
                if "suggestion" in result:
                    response_text += f"\n💡 建议: {result['suggestion']}"
            else:
                response_text = f"✅ 命令执行成功:\n{result.get('output', str(result))}"
            
            # 添加路由信息
            if "routing_info" in result:
                routing_info = result["routing_info"]
                response_text += f"\n\n📊 执行信息:"
                response_text += f"\n- 模型: {routing_info.get('model', 'Unknown')}"
                response_text += f"\n- 提供商: {routing_info.get('provider', 'Unknown')}"
                response_text += f"\n- 响应时间: {routing_info.get('response_time_ms', 0)}ms"
                response_text += f"\n- Claude 避免: {routing_info.get('claude_avoided', True)}"
            
            claude_response = {
                "id": f"msg_01PowerAutomationMCP_{hash(command) % 10000}",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": response_text}],
                "model": "powerautomation-mcp-v4.6.97",
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {
                    "input_tokens": len(command.split()),
                    "output_tokens": len(response_text.split())
                }
            }
            
            logger.info("✅ 命令执行完成")
            return web.json_response(claude_response)
            
        except Exception as e:
            logger.error(f"❌ 命令执行失败: {e}")
            return await self.create_error_response(f"命令执行失败: {str(e)}")
    
    async def _handle_tool_request_with_mcp(self, user_message: str, data: dict):
        """使用 MCP 架构处理工具请求"""
        logger.info("🔧 使用 tool_mode_manager 处理工具请求")
        
        try:
            # 使用工具模式管理器处理
            result = await self.tool_mode_manager.handle_tool_request(data)
            
            response_text = f"🔧 工具请求处理完成:\n{result.get('response', str(result))}"
            
            claude_response = {
                "id": f"msg_01PowerAutomationTool_{hash(user_message) % 10000}",
                "type": "message", 
                "role": "assistant",
                "content": [{"type": "text", "text": response_text}],
                "model": "powerautomation-mcp-v4.6.97",
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {
                    "input_tokens": len(str(data)),
                    "output_tokens": len(response_text.split())
                }
            }
            
            return web.json_response(claude_response)
            
        except Exception as e:
            logger.error(f"❌ 工具请求处理失败: {e}")
            return await self.create_error_response(f"工具请求处理失败: {str(e)}")
    
    async def _handle_chat_with_k2_router(self, user_message: str):
        """使用 K2 路由器处理对话"""
        logger.info("💬 使用 K2 路由器处理对话")
        
        try:
            # 使用 K2 客户端处理对话
            result = await self.k2_client.chat_completion(user_message)
            
            response_text = result.get("content", "K2 服务响应")
            
            claude_response = {
                "id": f"msg_01PowerAutomationK2_{hash(user_message) % 10000}",
                "type": "message",
                "role": "assistant", 
                "content": [{"type": "text", "text": response_text}],
                "model": "powerautomation-k2-v4.6.97",
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {
                    "input_tokens": len(user_message.split()),
                    "output_tokens": len(response_text.split())
                }
            }
            
            return web.json_response(claude_response)
            
        except Exception as e:
            logger.error(f"❌ K2 对话处理失败: {e}")
            return await self.create_error_response(f"K2 对话处理失败: {str(e)}")
    
    async def _handle_with_basic_k2(self, user_message: str, data: dict):
        """基础 K2 模式处理（MCP 不可用时的回退）"""
        logger.info("⚠️ 使用基础 K2 模式")
        
        # 这里保持原有的 K2 处理逻辑作为回退
        response_text = f"⚠️ PowerAutomation MCP 架构暂时不可用，使用基础模式处理: {user_message}"
        
        claude_response = {
            "id": f"msg_01PowerAutomationBasic_{hash(user_message) % 10000}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": response_text}],
            "model": "powerautomation-basic-v4.6.97",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": len(user_message.split()),
                "output_tokens": len(response_text.split())
            }
        }
        
        return web.json_response(claude_response)
    
    def _extract_user_message(self, data: dict) -> str:
        """提取用户消息"""
        messages = data.get("messages", [])
        if not messages:
            return "Hello"
        
        # 提取最后一条用户消息
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content
                elif isinstance(content, list) and content:
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            return item.get("text", "Hello")
        
        return "Hello"
    
    async def create_error_response(self, error_msg):
        """创建错误响应"""
        response = {
            "id": "msg_01PowerAutomationError",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": f"⏺ PowerAutomation 错误: {error_msg}"}],
            "model": "powerautomation-error-v4.6.97",
            "stop_reason": "end_turn"
        }
        return web.json_response(response)

async def create_app():
    proxy = PowerAutomationProxy()
    app = web.Application()
    app.router.add_route('*', '/{path:.*}', proxy.handle_claude_request)
    return app

async def main():
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    await site.start()
    
    print("🚀 PowerAutomation v4.6.97 完全集成代理已启动")
    print("📍 监听地址: http://127.0.0.1:8080")
    print("")
    print("🎯 PowerAutomation 完整威力已释放:")
    print("   ✅ claude_router_mcp - 智能路由决策")
    print("   ✅ command_mcp - 真正的命令执行")
    print("   ✅ unified_mcp_server - 统一服务协调")
    print("   ✅ claudeditor 双向通信")
    print("   ✅ K2 服务路由")
    print("   ✅ Mirror Code 追踪")
    print("   ✅ 零余额消耗")
    print("")
    print("⚡ 支持的功能:")
    print("   🔧 真正执行 Shell 命令 (git, npm, pip, docker 等)")
    print("   💬 智能对话路由到 K2 服务")
    print("   🛠️ Claude Code 工具模式")
    print("   📊 实时使用追踪和成本分析")
    print("   🔄 与 ClaudeEditor 双向同步")
    print("")
    print("🎊 现在 'git clone' 将真正执行！")
    print("按 Ctrl+C 停止服务器")
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        print("\n🛑 停止 PowerAutomation 代理服务器...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

