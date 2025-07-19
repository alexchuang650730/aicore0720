#!/bin/bash
# Claude Code 代理配置脚本
# 将 Claude Code 的 API 请求重定向到 PowerAutomation K2 路由

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_message() {
    echo -e "${1}${2}${NC}"
}

print_message $BLUE "🔧 配置 Claude Code 使用 PowerAutomation K2 路由..."

# PowerAutomation 代理服务器地址
PROXY_HOST="127.0.0.1"
PROXY_PORT="8080"
POWERAUTOMATION_DIR="$HOME/.powerautomation"

# 检查 PowerAutomation 是否安装
if [ ! -d "$POWERAUTOMATION_DIR" ]; then
    print_message $RED "❌ PowerAutomation 未安装"
    print_message $BLUE "请先安装 PowerAutomation："
    echo "curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/install_powerautomation_macos.sh | bash"
    exit 1
fi

# 创建代理配置目录
mkdir -p "$POWERAUTOMATION_DIR/proxy"

# 创建 Claude API 代理配置
cat > "$POWERAUTOMATION_DIR/proxy/claude_api_proxy.py" << 'EOF'
#!/usr/bin/env python3
"""
Claude API 代理服务器
将 Claude Code 的 API 请求重定向到 PowerAutomation K2 路由
"""

import asyncio
import json
import logging
from aiohttp import web, ClientSession
import aiohttp
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeAPIProxy:
    def __init__(self, k2_endpoint="https://cloud.infini-ai.com/maas/v1"):
        self.k2_endpoint = k2_endpoint
        self.k2_api_key = "sk-infini-ai-k2-service-key"  # K2 服务密钥
        
    async def handle_claude_request(self, request):
        """处理 Claude API 请求并转发到 K2 服务"""
        try:
            # 获取请求数据
            if request.content_type == 'application/json':
                data = await request.json()
            else:
                data = await request.text()
            
            # 记录请求
            logger.info(f"🔄 拦截 Claude API 请求: {request.path}")
            logger.info(f"📝 请求数据: {json.dumps(data, indent=2) if isinstance(data, dict) else data}")
            
            # 转换为 K2 API 格式
            k2_data = self._convert_to_k2_format(data)
            
            # 发送到 K2 服务
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.k2_api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.k2_endpoint}/chat/completions",
                    json=k2_data,
                    headers=headers
                ) as response:
                    k2_response = await response.json()
                    
            # 转换回 Claude API 格式
            claude_response = self._convert_to_claude_format(k2_response)
            
            logger.info(f"✅ K2 路由成功，返回响应")
            
            return web.json_response(claude_response)
            
        except Exception as e:
            logger.error(f"❌ 代理请求失败: {e}")
            return web.json_response({
                "error": {
                    "type": "proxy_error",
                    "message": f"PowerAutomation K2 路由失败: {str(e)}"
                }
            }, status=500)
    
    def _convert_to_k2_format(self, claude_data: Dict[str, Any]) -> Dict[str, Any]:
        """将 Claude API 格式转换为 K2 API 格式"""
        if isinstance(claude_data, str):
            return {
                "model": "qwen-plus",
                "messages": [{"role": "user", "content": claude_data}],
                "stream": False
            }
        
        return {
            "model": claude_data.get("model", "qwen-plus").replace("claude", "qwen"),
            "messages": claude_data.get("messages", []),
            "stream": claude_data.get("stream", False),
            "max_tokens": claude_data.get("max_tokens", 4000),
            "temperature": claude_data.get("temperature", 0.7)
        }
    
    def _convert_to_claude_format(self, k2_response: Dict[str, Any]) -> Dict[str, Any]:
        """将 K2 API 响应转换为 Claude API 格式"""
        if "choices" in k2_response and k2_response["choices"]:
            content = k2_response["choices"][0].get("message", {}).get("content", "")
            return {
                "id": k2_response.get("id", "claude-proxy-response"),
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": content}],
                "model": "claude-3-sonnet-20240229",
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {
                    "input_tokens": k2_response.get("usage", {}).get("prompt_tokens", 0),
                    "output_tokens": k2_response.get("usage", {}).get("completion_tokens", 0)
                }
            }
        
        return k2_response

async def create_app():
    """创建代理应用"""
    proxy = ClaudeAPIProxy()
    app = web.Application()
    
    # 添加路由 - 拦截所有 Claude API 请求
    app.router.add_route('*', '/v1/{path:.*}', proxy.handle_claude_request)
    app.router.add_route('*', '/{path:.*}', proxy.handle_claude_request)
    
    return app

async def main():
    """启动代理服务器"""
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    await site.start()
    
    print("🚀 Claude API 代理服务器已启动")
    print("📍 监听地址: http://127.0.0.1:8080")
    print("🎯 所有 Claude API 请求将路由到 PowerAutomation K2 服务")
    print("按 Ctrl+C 停止服务器")
    
    try:
        await asyncio.Future()  # 保持运行
    except KeyboardInterrupt:
        print("\n🛑 停止代理服务器...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# 创建启动脚本
cat > "$POWERAUTOMATION_DIR/proxy/start_claude_proxy.sh" << 'EOF'
#!/bin/bash
# 启动 Claude Code 代理服务器

POWERAUTOMATION_DIR="$HOME/.powerautomation"
VENV_DIR="$POWERAUTOMATION_DIR/powerautomation_env"

# 激活虚拟环境
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

# 安装依赖
pip install aiohttp

# 启动代理服务器
python3 "$POWERAUTOMATION_DIR/proxy/claude_api_proxy.py"
EOF

chmod +x "$POWERAUTOMATION_DIR/proxy/start_claude_proxy.sh"

# 创建环境变量配置
cat > "$POWERAUTOMATION_DIR/proxy/claude_code_env.sh" << 'EOF'
#!/bin/bash
# Claude Code 环境变量配置
# 将 Claude API 请求重定向到本地代理

export ANTHROPIC_API_URL="http://127.0.0.1:8080"
export ANTHROPIC_BASE_URL="http://127.0.0.1:8080"
export CLAUDE_API_URL="http://127.0.0.1:8080"
export CLAUDE_BASE_URL="http://127.0.0.1:8080"

echo "✅ Claude Code 环境变量已配置"
echo "🔄 API 请求将路由到: http://127.0.0.1:8080"
echo "🎯 PowerAutomation K2 服务将处理所有 AI 推理"
EOF

chmod +x "$POWERAUTOMATION_DIR/proxy/claude_code_env.sh"

print_message $GREEN "✅ Claude Code 代理配置完成"
print_message $BLUE "📋 配置文件位置:"
echo "  🔧 代理服务器: $POWERAUTOMATION_DIR/proxy/claude_api_proxy.py"
echo "  🚀 启动脚本: $POWERAUTOMATION_DIR/proxy/start_claude_proxy.sh"
echo "  ⚙️ 环境变量: $POWERAUTOMATION_DIR/proxy/claude_code_env.sh"

print_message $BLUE "🚀 使用方法:"
echo "1. 启动代理服务器:"
echo "   bash $POWERAUTOMATION_DIR/proxy/start_claude_proxy.sh"
echo ""
echo "2. 在新终端中配置环境变量:"
echo "   source $POWERAUTOMATION_DIR/proxy/claude_code_env.sh"
echo ""
echo "3. 启动 Claude Code:"
echo "   claude"
echo ""
print_message $GREEN "🎉 现在 Claude Code 将使用 PowerAutomation K2 路由，避免余额消耗！"

