#!/bin/bash
# Claude Code Tool 部署脚本

echo "🚀 部署 Claude Code Tool..."

# 设置环境变量
export CLAUDE_CODE_ROOT="/Users/alexchuang/alexchuangtest/aicore0720"
export MCP_SERVER_PORT=3001
export K2_MODEL_PATH="$CLAUDE_CODE_ROOT/models/k2-optimizer"

# 检查依赖
echo "📦 检查依赖..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 安装 MCP 服务器依赖
echo "📦 安装 MCP 服务器依赖..."
cd "$CLAUDE_CODE_ROOT/core/mcp_server"
npm install

# 启动 MCP 服务器
echo "🖥️ 启动 MCP 服务器..."
npm run start:daemon &
MCP_PID=$!
echo "MCP 服务器 PID: $MCP_PID"

# 配置工具注册
echo "🔧 配置工具注册..."
python3 "$CLAUDE_CODE_ROOT/core/tools/register_tools.py"

# 验证服务
echo "✅ 验证服务状态..."
sleep 3
curl -s http://localhost:$MCP_SERVER_PORT/health || {
    echo "❌ MCP 服务器启动失败"
    exit 1
}

echo "✅ Claude Code Tool 部署完成"
echo "📊 访问地址: http://localhost:$MCP_SERVER_PORT"
