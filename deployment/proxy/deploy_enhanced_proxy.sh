#!/bin/bash

# PowerAutomation v4.6.97 - 增强版 Claude Code 代理一键部署脚本
# 支持 Claude Code 内置指令和 Shell 命令智能路由

set -e

echo "🚀 PowerAutomation v4.6.97 - 增强版 Claude Code 代理部署"
echo "=================================================================="

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    PYTHON_CMD="python3"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    PYTHON_CMD="python3"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "📍 检测到操作系统: $OS"

# 检查 Python 3
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"

# 创建代理目录
PROXY_DIR="$HOME/.powerautomation/proxy"
mkdir -p "$PROXY_DIR"
echo "📁 创建代理目录: $PROXY_DIR"

# 下载增强版代理
echo "📥 下载增强版 Claude Code 代理..."
curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/claude_code_enhanced_proxy.py -o "$PROXY_DIR/claude_api_proxy.py"

if [ $? -eq 0 ]; then
    echo "✅ 增强版代理下载成功"
else
    echo "❌ 代理下载失败"
    exit 1
fi

# 创建启动脚本
echo "📝 创建启动脚本..."
cat > "$PROXY_DIR/start_claude_proxy.sh" << 'EOF'
#!/bin/bash
echo "🚀 启动增强版 Claude API 代理服务器..."

# 检查并安装 aiohttp
if ! python3 -c "import aiohttp" 2>/dev/null; then
    echo "📦 安装 aiohttp 依赖..."
    pip3 install aiohttp --user --quiet || {
        echo "⚠️ aiohttp 安装失败，尝试使用系统包管理器..."
        if command -v brew &> /dev/null; then
            echo "🍺 使用 Homebrew 安装..."
            brew install python-aiohttp 2>/dev/null || echo "⚠️ Homebrew 安装失败，但继续运行..."
        elif command -v apt &> /dev/null; then
            echo "📦 使用 apt 安装..."
            sudo apt update && sudo apt install -y python3-aiohttp 2>/dev/null || echo "⚠️ apt 安装失败，但继续运行..."
        fi
    }
fi

# 启动增强版代理服务器
echo "🎯 启动代理服务器..."
python3 ~/.powerautomation/proxy/claude_api_proxy.py
EOF

# 设置执行权限
chmod +x "$PROXY_DIR/start_claude_proxy.sh"

# 创建环境变量配置脚本
echo "🔧 创建环境变量配置..."
cat > "$PROXY_DIR/claude_code_env.sh" << 'EOF'
#!/bin/bash

# PowerAutomation v4.6.97 - Claude Code 环境变量配置
export ANTHROPIC_API_URL="http://127.0.0.1:8080"
export ANTHROPIC_BASE_URL="http://127.0.0.1:8080"
export CLAUDE_API_URL="http://127.0.0.1:8080"
export CLAUDE_BASE_URL="http://127.0.0.1:8080"

echo "✅ Claude Code 环境变量已配置"
echo "🔄 API 请求将路由到: http://127.0.0.1:8080"
echo "🎯 PowerAutomation 增强代理将智能处理所有请求"
echo ""
echo "📋 支持的功能:"
echo "   🔧 Claude Code 内置指令: /help, /init, /status, /permissions 等"
echo "   ⚡ Shell 命令: git, npm, pip, python, docker 等"
echo "   💬 智能对话路由到 K2 服务"
echo "   🛡️ 完全避免 Claude 模型余额消耗"
EOF

chmod +x "$PROXY_DIR/claude_code_env.sh"

# 创建快速启动脚本
echo "⚡ 创建快速启动脚本..."
cat > "$PROXY_DIR/quick_start.sh" << 'EOF'
#!/bin/bash

echo "🚀 PowerAutomation v4.6.97 - 快速启动"
echo "=================================="

# 检查代理是否已在运行
if lsof -i :8080 &>/dev/null; then
    echo "⚠️ 代理服务器已在运行 (端口 8080)"
    echo "💡 如需重启，请先停止现有服务器 (Ctrl+C)"
    exit 1
fi

echo "🎯 启动增强版 Claude Code 代理..."
echo "📍 监听地址: http://127.0.0.1:8080"
echo ""
echo "🔧 在新终端中运行以下命令配置 Claude Code:"
echo "   source ~/.powerautomation/proxy/claude_code_env.sh"
echo "   claude"
echo ""
echo "按 Ctrl+C 停止代理服务器"
echo "=================================="

# 启动代理
bash ~/.powerautomation/proxy/start_claude_proxy.sh
EOF

chmod +x "$PROXY_DIR/quick_start.sh"

# 安装 aiohttp 依赖
echo "📦 检查并安装依赖..."
if ! $PYTHON_CMD -c "import aiohttp" 2>/dev/null; then
    echo "📥 安装 aiohttp..."
    $PYTHON_CMD -m pip install aiohttp --user --quiet || {
        echo "⚠️ pip 安装失败，尝试其他方式..."
        if [[ "$OS" == "macOS" ]] && command -v brew &> /dev/null; then
            echo "🍺 使用 Homebrew 安装..."
            brew install python-aiohttp 2>/dev/null || echo "⚠️ Homebrew 安装失败，但继续..."
        fi
    }
fi

echo ""
echo "🎉 增强版 Claude Code 代理部署完成！"
echo "=================================================================="
echo ""
echo "🚀 使用方法:"
echo ""
echo "1️⃣ 启动代理服务器:"
echo "   bash ~/.powerautomation/proxy/quick_start.sh"
echo ""
echo "2️⃣ 在新终端中配置 Claude Code:"
echo "   source ~/.powerautomation/proxy/claude_code_env.sh"
echo "   claude"
echo ""
echo "3️⃣ 测试功能:"
echo "   > /help                    # 测试 Claude Code 内置指令"
echo "   > git clone <repo>         # 测试 Shell 命令"
echo "   > hi                       # 测试对话路由到 K2"
echo ""
echo "🎯 核心特性:"
echo "   ✅ 智能路由: 工具请求 → Claude API, 对话 → K2 服务"
echo "   ✅ 零余额消耗: 完全避免 Claude 模型推理费用"
echo "   ✅ 功能完整: 保留所有 Claude Code 工具功能"
echo "   ✅ 增强检测: 支持 20+ Claude Code 内置指令"
echo "   ✅ 命令支持: 支持 git, npm, pip, docker 等常用命令"
echo ""
echo "📚 更多信息: https://github.com/alexchuang650730/aicore0716"
echo "=================================================================="

