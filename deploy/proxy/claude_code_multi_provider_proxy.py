#!/usr/bin/env python3
"""
PowerAutomation v4.6.97 - 多 Provider Claude Code 代理
支持多个 K2 服务提供商的智能路由
"""

import asyncio
import json
import logging
import re
import os
from aiohttp import web, ClientSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiProviderClaudeProxy:
    def __init__(self):
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.original_claude_url = "https://api.anthropic.com"
        
        # 多个 K2 服务提供商配置
        self.k2_providers = [
            {
                "name": "Infini-AI",
                "endpoint": "https://cloud.infini-ai.com/maas/v1",
                "api_key": os.getenv("INFINI_AI_API_KEY", "sk-infini-ai-k2-service-key"),
                "model": "qwen-plus",
                "priority": 1
            },
            {
                "name": "HuggingFace",
                "endpoint": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                "api_key": os.getenv("HF_TOKEN", ""),
                "model": "microsoft/DialoGPT-medium",
                "priority": 2,
                "is_hf": True  # 特殊标记，因为 HF API 格式不同
            },
            {
                "name": "Novita-via-HF",
                "endpoint": "https://api-inference.huggingface.co/models/moonshotai/Kimi-K2-Instruct",
                "api_key": os.getenv("HF_TOKEN", ""),
                "model": "moonshotai/Kimi-K2-Instruct",
                "priority": 3,
                "is_hf_novita": True,  # 特殊标记，使用 HF Hub + Novita
                "provider": "novita"
            },
            {
                "name": "DeepSeek",
                "endpoint": "https://api.deepseek.com/v1",
                "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                "model": "deepseek-chat",
                "priority": 4
            },
            {
                "name": "Qwen",
                "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": os.getenv("QWEN_API_KEY", ""),
                "model": "qwen-turbo",
                "priority": 5
            },
            {
                "name": "Local-Ollama",
                "endpoint": "http://localhost:11434/v1",
                "api_key": "ollama",
                "model": "qwen2.5:7b",
                "priority": 6
            }
        ]
        
        # 过滤有效的 provider（有 API 密钥的）
        self.active_providers = [
            p for p in self.k2_providers 
            if p["api_key"] and p["api_key"] != ""
        ]
        
        if not self.active_providers:
            logger.warning("⚠️ 没有配置有效的 K2 服务提供商")
            # 添加默认的测试 provider
            self.active_providers = [{
                "name": "Test-Provider",
                "endpoint": "https://api.openai.com/v1",
                "api_key": "test-key",
                "model": "gpt-3.5-turbo",
                "priority": 999
            }]
        
        # 按优先级排序
        self.active_providers.sort(key=lambda x: x["priority"])
        
        logger.info(f"🔧 配置了 {len(self.active_providers)} 个 K2 服务提供商:")
        for provider in self.active_providers:
            logger.info(f"   - {provider['name']}: {provider['model']}")
        
        # Claude Code 内置指令
        self.claude_code_commands = [
            '/help', '/init', '/status', '/permissions', '/terminal-setup',
            '/install-github-app', '/login', '/logout', '/settings', '/clear',
            '/reset', '/version', '/docs', '/examples', '/debug', '/config',
            '/workspace', '/project', '/files', '/search', '/history',
        ]
        
        # Shell 命令模式匹配
        self.shell_command_patterns = [
            r'^git\s+', r'^npm\s+', r'^pip\s+', r'^python\s+', r'^node\s+',
            r'^ls\s*', r'^cd\s+', r'^mkdir\s+', r'^rm\s+', r'^cp\s+', r'^mv\s+',
            r'^cat\s+', r'^echo\s+', r'^curl\s+', r'^wget\s+', r'^chmod\s+',
            r'^sudo\s+', r'^which\s+', r'^whereis\s+', r'^find\s+', r'^grep\s+',
            r'^awk\s+', r'^sed\s+', r'^tar\s+', r'^zip\s+', r'^unzip\s+',
            r'^docker\s+', r'^kubectl\s+', r'^helm\s+',
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
        
        # 检查 shell 命令（但这些会被路由到 K2 进行智能分析）
        content_lower = content.lower()
        for pattern in self.shell_command_patterns:
            if re.match(pattern, content_lower):
                logger.info(f"🔍 检测到 Shell 命令（将路由到 K2 进行智能分析）: {content[:50]}...")
                return False  # 返回 False，让它们被当作对话处理
                
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
        """检查是否是简单对话（包括 shell 命令查询）"""
        if not isinstance(data, dict):
            return True
            
        # 如果是工具请求，则不是简单对话
        if self.is_tool_request(data):
            return False
            
        # 其他都当作对话处理（包括 shell 命令查询）
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
            
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.claude_api_key}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                    "User-Agent": "PowerAutomation-Proxy/4.6.97"
                }
                
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
                        
                        if "credit" in error_text.lower() or "balance" in error_text.lower():
                            logger.info("💰 检测到余额问题，回退到 K2")
                            return await self.route_to_k2(data)
                        else:
                            return await self.create_error_response(f"Claude API error: {response.status}")
                        
        except Exception as e:
            logger.warning(f"⚠️ Claude API 连接失败: {e}，回退到 K2")
            return await self.route_to_k2(data)
    
    async def route_to_k2(self, data):
        """路由到 K2 服务（支持多 provider）"""
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
        for i, provider in enumerate(self.active_providers):
            try:
                logger.info(f"📡 尝试 K2 Provider {i+1}/{len(self.active_providers)}: {provider['name']}")
                
                # 检查是否是 HuggingFace API
                if provider.get("is_hf", False) or provider.get("is_hf_novita", False):
                    # HuggingFace Inference API 格式
                    if provider.get("is_hf_novita", False):
                        # 使用 HuggingFace Hub + Novita provider 的格式
                        hf_data = {
                            "inputs": user_content,
                            "parameters": {
                                "max_new_tokens": 200,
                                "temperature": 0.7,
                                "return_full_text": False,
                                "provider": provider.get("provider", "novita")
                            }
                        }
                    else:
                        # 标准 HuggingFace Inference API
                        hf_data = {
                            "inputs": user_content,
                            "parameters": {
                                "max_new_tokens": 200,
                                "temperature": 0.7,
                                "return_full_text": False
                            }
                        }
                    
                    async with ClientSession() as session:
                        headers = {
                            "Authorization": f"Bearer {provider['api_key']}",
                            "Content-Type": "application/json",
                            "User-Agent": "PowerAutomation-Proxy/4.6.97"
                        }
                        
                        async with session.post(
                            provider['endpoint'],
                            json=hf_data,
                            headers=headers,
                            timeout=30
                        ) as response:
                            if response.status == 200:
                                hf_response = await response.json()
                                if isinstance(hf_response, list) and hf_response:
                                    content = hf_response[0].get("generated_text", f"Hello from {provider['name']}!")
                                elif isinstance(hf_response, dict):
                                    # 处理可能的不同响应格式
                                    content = hf_response.get("generated_text", 
                                             hf_response.get("text", 
                                             hf_response.get("content", f"Hello from {provider['name']}!")))
                                else:
                                    content = f"Hello from {provider['name']}!"
                                
                                claude_response = {
                                    "id": f"msg_01PowerAutomation{provider['name']}",
                                    "type": "message",
                                    "role": "assistant",
                                    "content": [{"type": "text", "text": content}],
                                    "model": "claude-3-sonnet-20240229",
                                    "stop_reason": "end_turn",
                                    "stop_sequence": None,
                                    "usage": {"input_tokens": 10, "output_tokens": 50}
                                }
                                
                                logger.info(f"✅ K2 Provider {provider['name']} 响应成功")
                                return web.json_response(claude_response)
                            else:
                                error_text = await response.text()
                                logger.warning(f"⚠️ Provider {provider['name']} 失败 ({response.status}): {error_text[:100]}...")
                                continue
                else:
                    # 标准 OpenAI 兼容 API 格式
                    k2_data = {
                        "model": provider["model"],
                        "messages": [{"role": "user", "content": user_content}],
                        "stream": False,
                        "max_tokens": 4000
                    }
                    
                    async with ClientSession() as session:
                        headers = {
                            "Authorization": f"Bearer {provider['api_key']}",
                            "Content-Type": "application/json",
                            "User-Agent": "PowerAutomation-Proxy/4.6.97"
                        }
                        
                        async with session.post(
                            f"{provider['endpoint']}/chat/completions",
                            json=k2_data,
                            headers=headers,
                            timeout=30
                        ) as response:
                            if response.status == 200:
                                k2_response = await response.json()
                                content = k2_response.get("choices", [{}])[0].get("message", {}).get("content", f"Hello from {provider['name']}!")
                                
                                claude_response = {
                                    "id": f"msg_01PowerAutomation{provider['name']}",
                                    "type": "message",
                                    "role": "assistant",
                                    "content": [{"type": "text", "text": content}],
                                    "model": "claude-3-sonnet-20240229",
                                    "stop_reason": "end_turn",
                                    "stop_sequence": None,
                                    "usage": {"input_tokens": 10, "output_tokens": 50}
                                }
                                
                                logger.info(f"✅ K2 Provider {provider['name']} 响应成功")
                                return web.json_response(claude_response)
                            else:
                                error_text = await response.text()
                                logger.warning(f"⚠️ Provider {provider['name']} 失败 ({response.status}): {error_text[:100]}...")
                                continue
                            
            except Exception as e:
                logger.warning(f"⚠️ Provider {provider['name']} 连接失败: {e}")
                continue
        
        # 所有 provider 都失败
        logger.error("❌ 所有 K2 Provider 都失败")
        content = "所有 K2 服务暂时不可用，但避免了 Claude 余额消耗！请检查网络连接或 API 密钥配置。"
        
        claude_response = {
            "id": "msg_01PowerAutomationFallback",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
            "model": "claude-3-sonnet-20240229",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 50}
        }
        
        return web.json_response(claude_response)
    
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
    proxy = MultiProviderClaudeProxy()
    app = web.Application()
    app.router.add_route('*', '/{path:.*}', proxy.handle_claude_request)
    return app

async def main():
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    await site.start()
    
    print("🚀 多 Provider Claude 代理服务器已启动")
    print("📍 监听地址: http://127.0.0.1:8080")
    print("🔧 工具请求 → Claude API (api.anthropic.com:443)")
    print("💬 对话/命令查询 → 多个 K2 服务提供商")
    print("")
    print("🌐 支持的 K2 服务提供商:")
    print("   1. Infini-AI (需要 INFINI_AI_API_KEY)")
    print("   2. HuggingFace (需要 HF_TOKEN)")
    print("   3. Novita via HuggingFace Hub (需要 HF_TOKEN)")
    print("   4. DeepSeek (需要 DEEPSEEK_API_KEY)")
    print("   5. Qwen (需要 QWEN_API_KEY)")
    print("   6. Local Ollama (本地服务)")
    print("")
    print("🔑 环境变量配置:")
    print("   export INFINI_AI_API_KEY='your-infini-ai-key'")
    print("   export HF_TOKEN='your-huggingface-token'  # 支持 HF + Novita")
    print("   export DEEPSEEK_API_KEY='your-deepseek-key'")
    print("   export QWEN_API_KEY='your-qwen-key'")
    print("   export ANTHROPIC_API_KEY='your-claude-key'")
    print("")
    print("按 Ctrl+C 停止服务器")
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        print("\n🛑 停止代理服务器...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

