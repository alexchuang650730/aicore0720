#!/usr/bin/env python3
"""
PowerAutomation v4.6.97 - 最终版 Claude Code 代理
使用 Groq 和 Together AI 作为 K2 服务提供商
"""

import asyncio
import json
import logging
import re
import os
from aiohttp import web, ClientSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalClaudeProxy:
    def __init__(self):
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.original_claude_url = "https://api.anthropic.com"
        
        # 验证必需的环境变量
        if not self.hf_token:
            logger.warning("⚠️ 缺少 HF_TOKEN 环境变量")
        
        # K2 服务提供商配置 (基于性能测试结果)
        self.k2_providers = [
            {
                "name": "Groq",
                "provider": "groq",
                "model": "moonshotai/Kimi-K2-Instruct",
                "priority": 1,
                "description": "高性能推理服务 (0.36s 响应时间)"
            },
            {
                "name": "Together-AI", 
                "provider": "together",
                "model": "moonshotai/Kimi-K2-Instruct",
                "priority": 2,
                "description": "详细回答服务 (0.96s 响应时间)"
            }
        ]
        
        # 过滤有效的 provider
        self.active_providers = []
        if self.hf_token:
            self.active_providers = self.k2_providers
        
        logger.info(f"🔧 配置了 {len(self.active_providers)} 个 K2 服务提供商:")
        for provider in self.active_providers:
            logger.info(f"   - {provider['name']}: {provider['description']}")
        
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
        
    def is_simple_chat(self, data):
        """检查是否是简单对话"""
        if not isinstance(data, dict):
            return True
            
        # 如果是工具请求，则不是简单对话
        if self.is_tool_request(data):
            return False
            
        # 其他都当作对话处理
        return True
        
    async def handle_claude_request(self, request):
        try:
            if request.content_type == 'application/json':
                data = await request.json()
            else:
                data = {"messages": [{"role": "user", "content": "Hello"}]}
            
            logger.info(f"🔄 收到请求: {request.path}")
            
            # 优先检查工具请求
            if self.is_tool_request(data):
                logger.info("🔧 路由到 Claude API (工具请求)")
                return await self.forward_to_claude(request, data)
            
            # 其他都路由到 K2（包括对话和 shell 命令查询）
            else:
                logger.info("💬 路由到 K2 服务 (对话/命令查询)")
                return await self.route_to_k2(data)
                
        except Exception as e:
            logger.error(f"❌ 请求处理失败: {e}")
            return await self.create_error_response(str(e))
    
    async def forward_to_claude(self, request, data):
        """转发到原始 Claude API"""
        try:
            logger.info(f"📡 转发到 Claude API: {self.original_claude_url}")
            
            if not self.claude_api_key:
                logger.warning("⚠️ 缺少 Claude API 密钥，回退到 K2")
                return await self.route_to_k2(data)
            
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.claude_api_key}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                    "User-Agent": "PowerAutomation-Proxy/4.6.97"
                }
                
                async with session.post(
                    f"{self.original_claude_url}/v1/messages",
                    json=data,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info("✅ Claude API 响应成功")
                        return web.json_response(result)
                    else:
                        error_text = await response.text()
                        logger.warning(f"⚠️ Claude API 失败 ({response.status}): {error_text[:200]}...")
                        
                        if "credit" in error_text.lower() or "balance" in error_text.lower():
                            logger.info("💰 检测到余额问题，回退到 K2")
                            return await self.route_to_k2(data)
                        else:
                            return await self.create_error_response(f"Claude API error: {response.status}")
                        
        except Exception as e:
            logger.warning(f"⚠️ Claude API 连接失败: {e}，回退到 K2")
            return await self.route_to_k2(data)
    
    async def route_to_k2(self, data):
        """路由到 K2 服务"""
        if not self.active_providers:
            return await self.create_error_response("没有可用的 K2 服务提供商，请配置 HF_TOKEN")
        
        messages = data.get("messages", [])
        if not messages:
            messages = [{"role": "user", "content": "Hello"}]
        
        # 提取最后一条用户消息
        user_content = "Hello"
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    user_content = content
                elif isinstance(content, list) and content:
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            user_content = item.get("text", "Hello")
                            break
                break
        
        # 尝试每个 provider
        for i, provider in enumerate(self.active_providers, 1):
            try:
                logger.info(f"📡 尝试 K2 Provider {i}/{len(self.active_providers)}: {provider['name']}")
                
                # 使用 HuggingFace InferenceClient
                from huggingface_hub import InferenceClient
                
                client = InferenceClient(
                    provider=provider["provider"],
                    api_key=self.hf_token,
                )
                
                completion = client.chat.completions.create(
                    model=provider["model"],
                    messages=[{"role": "user", "content": user_content}],
                    max_tokens=500
                )
                
                # 转换为 Claude 格式响应
                response_content = completion.choices[0].message.content
                
                claude_response = {
                    "id": f"msg_01PowerAutomation{provider['name']}",
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "text", "text": response_content}],
                    "model": "claude-3-sonnet-20240229",
                    "stop_reason": "end_turn",
                    "stop_sequence": None,
                    "usage": {"input_tokens": len(user_content.split()), "output_tokens": len(response_content.split())}
                }
                
                logger.info(f"✅ {provider['name']} 响应成功")
                return web.json_response(claude_response)
                
            except Exception as e:
                logger.warning(f"⚠️ Provider {provider['name']} 失败: {str(e)[:200]}...")
                continue
        
        # 所有 provider 都失败
        logger.error("❌ 所有 K2 Provider 都失败")
        return await self.create_error_response("所有 K2 服务暂时不可用，但避免了 Claude 余额消耗！请检查网络连接或 API 密钥配置。")
    
    async def create_error_response(self, error_msg):
        """创建错误响应"""
        response = {
            "id": "msg_01PowerAutomationError",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": f"⏺ {error_msg}"}],
            "model": "claude-3-sonnet-20240229",
            "stop_reason": "end_turn"
        }
        return web.json_response(response)

async def create_app():
    proxy = FinalClaudeProxy()
    app = web.Application()
    app.router.add_route('*', '/{path:.*}', proxy.handle_claude_request)
    return app

async def main():
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    await site.start()
    
    print("🚀 PowerAutomation v4.6.97 最终版代理已启动")
    print("📍 监听地址: http://127.0.0.1:8080")
    print("🔧 工具/命令请求 → Claude API (api.anthropic.com:443)")
    print("💬 对话请求 → K2 服务提供商")
    print("")
    print("🌐 K2 服务提供商 (基于性能测试):")
    print("   1. Groq via HuggingFace Hub (主要 - 0.36s 响应)")
    print("   2. Together AI via HuggingFace Hub (备用 - 详细回答)")
    print("")
    print("⚡ 支持的 Claude Code 内置指令:")
    print("   /help, /init, /status, /permissions, /terminal-setup")
    print("   /install-github-app, /login, /settings, /clear, /reset")
    print("   /version, /docs, /examples, /debug, /config, /workspace")
    print("   /mcp, /memory, /model, /review, /upgrade, /vim 等")
    print("")
    print("🔍 支持的 Shell 命令:")
    print("   git, npm, pip, python, node, ls, cd, mkdir, rm, cp, mv")
    print("   cat, echo, curl, wget, chmod, sudo, docker, kubectl 等")
    print("")
    print("🔑 环境变量:")
    print("   export HF_TOKEN='your-huggingface-token'  # 必需")
    print("   export ANTHROPIC_API_KEY='your-claude-key'  # 可选，启用工具功能")
    print("")
    print("🎯 智能路由：自动识别请求类型并选择最佳服务")
    print("按 Ctrl+C 停止服务器")
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        print("\n🛑 停止代理服务器...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

