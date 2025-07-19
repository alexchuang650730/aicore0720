#!/usr/bin/env python3
"""
PowerAutomation v4.6.97 - 增强版 Claude Code 代理
专门优化命令执行和工具请求的识别与路由
"""

import asyncio
import json
import logging
import re
from aiohttp import web, ClientSession
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedClaudeProxy:
    def __init__(self):
        self.k2_endpoint = "https://cloud.infini-ai.com/maas/v1"
        self.k2_api_key = "sk-infini-ai-k2-service-key"
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.original_claude_url = "https://api.anthropic.com"
        
        # Claude Code 内置指令
        self.claude_code_commands = [
            '/help',              # 显示帮助信息
            '/init',              # 初始化项目
            '/status',            # 显示状态
            '/permissions',       # 权限管理
            '/terminal-setup',    # 终端集成设置
            '/install-github-app', # GitHub 应用安装
            '/login',             # 登录
            '/logout',            # 登出
            '/settings',          # 设置
            '/clear',             # 清除历史
            '/reset',             # 重置
            '/version',           # 版本信息
            '/docs',              # 文档
            '/examples',          # 示例
            '/debug',             # 调试模式
            '/config',            # 配置
            '/workspace',         # 工作空间
            '/project',           # 项目管理
            '/files',             # 文件管理
            '/search',            # 搜索
            '/history',           # 历史记录
        ]
        
        # Shell 命令模式匹配
        self.shell_command_patterns = [
            r'^git\s+',           # git 命令
            r'^npm\s+',           # npm 命令  
            r'^pip\s+',           # pip 命令
            r'^python\s+',        # python 命令
            r'^node\s+',          # node 命令
            r'^ls\s*',            # ls 命令
            r'^cd\s+',            # cd 命令
            r'^mkdir\s+',         # mkdir 命令
            r'^rm\s+',            # rm 命令
            r'^cp\s+',            # cp 命令
            r'^mv\s+',            # mv 命令
            r'^cat\s+',           # cat 命令
            r'^echo\s+',          # echo 命令
            r'^curl\s+',          # curl 命令
            r'^wget\s+',          # wget 命令
            r'^chmod\s+',         # chmod 命令
            r'^sudo\s+',          # sudo 命令
            r'^which\s+',         # which 命令
            r'^whereis\s+',       # whereis 命令
            r'^find\s+',          # find 命令
            r'^grep\s+',          # grep 命令
            r'^awk\s+',           # awk 命令
            r'^sed\s+',           # sed 命令
            r'^tar\s+',           # tar 命令
            r'^zip\s+',           # zip 命令
            r'^unzip\s+',         # unzip 命令
            r'^\w+\s+--\w+',      # 带参数的命令
            r'^\w+\s+-\w+',       # 带选项的命令
        ]
        
    def is_command_request(self, content):
        """检查是否是命令执行请求"""
        if not isinstance(content, str):
            return False
            
        # 去除前后空格
        content = content.strip()
        
        # 检查是否是 Claude Code 内置指令
        for command in self.claude_code_commands:
            if content.startswith(command):
                logger.info(f"🔍 检测到 Claude Code 指令: {command}")
                return True
        
        # 转换为小写检查 shell 命令
        content_lower = content.lower()
        
        # 检查是否匹配 shell 命令模式
        for pattern in self.shell_command_patterns:
            if re.match(pattern, content_lower):
                logger.info(f"🔍 检测到 Shell 命令模式: {pattern} -> {content[:50]}...")
                return True
                
        # 检查是否包含典型的命令关键词
        command_keywords = [
            'git clone', 'git pull', 'git push', 'git commit', 'git status',
            'npm install', 'npm run', 'npm start', 'npm test', 'npm build',
            'pip install', 'pip list', 'pip show', 'pip freeze',
            'ls -la', 'ls -l', 'ls -al',
            'mkdir -p', 'rm -rf', 'rm -f',
            'chmod +x', 'chmod 755', 'chmod 644',
            'sudo ', 'sudo apt', 'sudo yum',
            'docker ', 'docker run', 'docker build',
            'kubectl ', 'helm ',
        ]
        
        for keyword in command_keywords:
            if keyword in content_lower:
                logger.info(f"🔍 检测到命令关键词: {keyword}")
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
                
                # 检查是否是命令执行请求
                if isinstance(content, str) and self.is_command_request(content):
                    logger.info("⚡ 检测到命令执行请求")
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
        """检查是否是简单对话（非工具、非命令）"""
        if not isinstance(data, dict):
            return True
            
        # 如果是工具请求，则不是简单对话
        if self.is_tool_request(data):
            return False
            
        messages = data.get("messages", [])
        if not messages:
            return True
            
        # 检查最后一条消息
        last_msg = messages[-1] if messages else {}
        content = last_msg.get("content", "")
        
        if isinstance(content, str):
            # 如果是命令，则不是简单对话
            if self.is_command_request(content):
                return False
                
            # 如果是简单的问候或对话，则是简单对话
            simple_patterns = [
                r'^hi$', r'^hello$', r'^hey$',
                r'^how are you', r'^what.*doing',
                r'^tell me about', r'^explain',
                r'^help me', r'^can you',
            ]
            
            content_lower = content.lower().strip()
            for pattern in simple_patterns:
                if re.match(pattern, content_lower):
                    logger.info(f"💬 检测到简单对话: {pattern}")
                    return True
                    
        return True
        
    async def handle_claude_request(self, request):
        try:
            if request.content_type == 'application/json':
                data = await request.json()
            else:
                data = {"messages": [{"role": "user", "content": "Hello"}]}
            
            logger.info(f"🔄 收到请求: {request.path}")
            
            # 优先检查工具请求（包括命令执行）
            if self.is_tool_request(data):
                logger.info("🔧 路由到 Claude API (工具/命令请求)")
                return await self.forward_to_claude(request, data)
            
            # 检查是否是简单对话
            elif self.is_simple_chat(data):
                logger.info("💬 路由到 K2 服务 (对话请求)")
                return await self.route_to_k2(data)
            
            # 默认转发到 Claude（保险起见）
            else:
                logger.info("🔄 默认路由到 Claude API")
                return await self.forward_to_claude(request, data)
                
        except Exception as e:
            logger.error(f"❌ 请求处理失败: {e}")
            return await self.create_error_response(str(e))
    
    async def forward_to_claude(self, request, data):
        """转发到原始 Claude API (端口 443)"""
        try:
            logger.info(f"📡 转发到 Claude API: {self.original_claude_url}")
            
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.claude_api_key}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                    "User-Agent": "PowerAutomation-Proxy/4.6.97"
                }
                
                # 如果没有 API 密钥，返回提示信息
                if not self.claude_api_key:
                    logger.warning("⚠️ 缺少 Claude API 密钥，回退到 K2")
                    return await self.route_to_k2(data)
                
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
                        
                        # 如果是余额不足，回退到 K2
                        if "credit" in error_text.lower() or "balance" in error_text.lower():
                            logger.info("💰 检测到余额问题，回退到 K2")
                            return await self.route_to_k2(data)
                        else:
                            return await self.create_error_response(f"Claude API error: {response.status}")
                        
        except Exception as e:
            logger.warning(f"⚠️ Claude API 连接失败: {e}，回退到 K2")
            return await self.route_to_k2(data)
    
    async def route_to_k2(self, data):
        """路由到 K2 服务 (端口 443)"""
        try:
            logger.info(f"📡 路由到 K2 服务: {self.k2_endpoint}")
            
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
            
            k2_data = {
                "model": "qwen-plus",
                "messages": [{"role": "user", "content": user_content}],
                "stream": False,
                "max_tokens": 4000
            }
            
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.k2_api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "PowerAutomation-Proxy/4.6.97"
                }
                
                async with session.post(
                    f"{self.k2_endpoint}/chat/completions",
                    json=k2_data,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        k2_response = await response.json()
                        content = k2_response.get("choices", [{}])[0].get("message", {}).get("content", "Hello from K2!")
                    else:
                        content = f"K2 服务暂时不可用 (状态: {response.status})，但避免了 Claude 余额消耗！"
            
            claude_response = {
                "id": "msg_01PowerAutomationK2",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": content}],
                "model": "claude-3-sonnet-20240229",
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 50}
            }
            
            logger.info("✅ K2 路由成功")
            return web.json_response(claude_response)
            
        except Exception as e:
            logger.error(f"❌ K2 路由失败: {e}")
            return await self.create_error_response(f"K2 service error: {str(e)}")
    
    async def create_error_response(self, error_msg):
        """创建错误响应"""
        response = {
            "id": "msg_01PowerAutomationError",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": f"PowerAutomation 代理错误: {error_msg}"}],
            "model": "claude-3-sonnet-20240229",
            "stop_reason": "end_turn"
        }
        return web.json_response(response)

async def create_app():
    proxy = EnhancedClaudeProxy()
    app = web.Application()
    app.router.add_route('*', '/{path:.*}', proxy.handle_claude_request)
    return app

async def main():
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    await site.start()
    
    print("🚀 增强版 Claude 代理服务器已启动")
    print("📍 监听地址: http://127.0.0.1:8080")
    print("🔧 工具/命令请求 → Claude API (api.anthropic.com:443)")
    print("💬 对话请求 → PowerAutomation K2 服务 (cloud.infini-ai.com:443)")
    print("")
    print("⚡ 支持的 Claude Code 内置指令:")
    print("   /help, /init, /status, /permissions, /terminal-setup")
    print("   /install-github-app, /login, /settings, /clear, /reset")
    print("   /version, /docs, /examples, /debug, /config, /workspace")
    print("")
    print("🔍 支持的 Shell 命令:")
    print("   git, npm, pip, python, node, ls, cd, mkdir, rm, cp, mv")
    print("   cat, echo, curl, wget, chmod, sudo, docker, kubectl 等")
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

