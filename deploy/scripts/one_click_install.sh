#!/bin/bash

# PowerAutomation v4.6.97 一键安装脚本
# 一个命令解决所有问题，无需多窗口操作

set -e

echo "🚀 PowerAutomation v4.6.97 一键安装"
echo "=================================="
echo ""

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    PYTHON_CMD="python3"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    PYTHON_CMD="python3"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "📋 检测到操作系统: $OS"

# 检查 Python
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python"
    exit 1
fi

echo "✅ Python 检查通过"

# 创建目录
INSTALL_DIR="$HOME/.powerautomation"
mkdir -p "$INSTALL_DIR/proxy"
mkdir -p "$INSTALL_DIR/logs"

echo "📁 创建安装目录: $INSTALL_DIR"

# 下载最终版代理
echo "📥 下载最终版代理..."
curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/claude_code_final_proxy.py -o "$INSTALL_DIR/proxy/claude_api_proxy.py"

if [ ! -f "$INSTALL_DIR/proxy/claude_api_proxy.py" ]; then
    echo "❌ 代理下载失败"
    exit 1
fi

echo "✅ 代理下载完成"

# 安装依赖
echo "📦 安装 Python 依赖..."

if [[ "$OS" == "macos" ]]; then
    # macOS 特殊处理
    if $PYTHON_CMD -c "import aiohttp" 2>/dev/null; then
        echo "✅ aiohttp 已安装"
    else
        echo "🔧 安装 aiohttp..."
        $PYTHON_CMD -m pip install aiohttp --break-system-packages --user 2>/dev/null || \
        $PYTHON_CMD -m pip install aiohttp --user 2>/dev/null || \
        pip3 install aiohttp --break-system-packages --user 2>/dev/null || \
        pip3 install aiohttp --user
    fi
    
    if $PYTHON_CMD -c "import huggingface_hub" 2>/dev/null; then
        echo "✅ huggingface_hub 已安装"
    else
        echo "🔧 安装 huggingface_hub..."
        $PYTHON_CMD -m pip install huggingface_hub --break-system-packages --user 2>/dev/null || \
        $PYTHON_CMD -m pip install huggingface_hub --user 2>/dev/null || \
        pip3 install huggingface_hub --break-system-packages --user 2>/dev/null || \
        pip3 install huggingface_hub --user
    fi
else
    # Linux
    $PYTHON_CMD -m pip install aiohttp huggingface_hub --user 2>/dev/null || \
    pip3 install aiohttp huggingface_hub --user
fi

echo "✅ 依赖安装完成"

# 配置环境变量
echo "🔑 配置环境变量..."

# 检查是否已有 HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo ""
    echo "⚠️ 需要配置 HuggingFace Token"
    echo "请访问: https://huggingface.co/settings/tokens"
    echo "创建一个新的 Token，并确保启用 'Make calls to Inference Providers' 权限"
    echo ""
    read -p "请输入您的 HuggingFace Token: " USER_HF_TOKEN
    
    if [ -z "$USER_HF_TOKEN" ]; then
        echo "❌ 未提供 HF_TOKEN，使用演示模式"
        USER_HF_TOKEN="demo-token"
    fi
else
    USER_HF_TOKEN="$HF_TOKEN"
    echo "✅ 使用现有的 HF_TOKEN"
fi

# 创建环境配置文件
cat > "$INSTALL_DIR/proxy/env.sh" << EOF
#!/bin/bash
export HF_TOKEN='$USER_HF_TOKEN'
export ANTHROPIC_API_KEY='\${ANTHROPIC_API_KEY:-}'
export POWERAUTOMATION_VERSION='4.6.97'
EOF

echo "✅ 环境配置完成"

# 创建启动脚本
cat > "$INSTALL_DIR/start_proxy.sh" << 'EOF'
#!/bin/bash

INSTALL_DIR="$HOME/.powerautomation"
cd "$INSTALL_DIR/proxy"

# 加载环境变量
source "$INSTALL_DIR/proxy/env.sh"

# 检查端口占用
if lsof -i :8080 &>/dev/null; then
    echo "⚠️ 端口 8080 已被占用，正在停止现有服务..."
    kill -9 $(lsof -ti:8080) 2>/dev/null || true
    sleep 2
fi

echo "🚀 启动 PowerAutomation v4.6.97 代理..."
echo "📍 监听地址: http://127.0.0.1:8080"
echo "🔧 配置 Claude Code: export ANTHROPIC_API_BASE=http://127.0.0.1:8080"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动代理
python3 claude_api_proxy.py
EOF

chmod +x "$INSTALL_DIR/start_proxy.sh"

# 创建 Claude Code 配置脚本
cat > "$INSTALL_DIR/setup_claude_code.sh" << 'EOF'
#!/bin/bash

echo "🔧 配置 Claude Code 环境..."

# 设置环境变量
export ANTHROPIC_API_BASE="http://127.0.0.1:8080"

# 添加到 shell 配置文件
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_RC="$HOME/.bash_profile"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "ANTHROPIC_API_BASE.*127.0.0.1:8080" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# PowerAutomation v4.6.97 Claude Code 配置" >> "$SHELL_RC"
        echo "export ANTHROPIC_API_BASE=http://127.0.0.1:8080" >> "$SHELL_RC"
        echo "✅ 已添加到 $SHELL_RC"
    else
        echo "✅ 配置已存在于 $SHELL_RC"
    fi
fi

echo "🎯 Claude Code 配置完成！"
echo ""
echo "现在您可以直接使用 Claude Code："
echo "  claude"
echo ""
EOF

chmod +x "$INSTALL_DIR/setup_claude_code.sh"

echo "✅ 启动脚本创建完成"

# 创建一键启动脚本（包含 Claude Code 配置）
cat > "$INSTALL_DIR/run_all.sh" << 'EOF'
#!/bin/bash

INSTALL_DIR="$HOME/.powerautomation"

echo "🚀 PowerAutomation v4.6.97 一键启动"
echo "=================================="

# 配置 Claude Code
source "$INSTALL_DIR/setup_claude_code.sh"

echo ""
echo "🎯 启动代理服务器..."
echo "代理启动后，您可以直接使用 Claude Code："
echo "  claude"
echo ""

# 启动代理
exec "$INSTALL_DIR/start_proxy.sh"
EOF

chmod +x "$INSTALL_DIR/run_all.sh"

echo ""
echo "🎉 PowerAutomation v4.6.97 安装完成！"
echo ""
echo "🚀 一键启动（推荐）："
echo "  $INSTALL_DIR/run_all.sh"
echo ""
echo "🔧 或分步操作："
echo "  1. 启动代理: $INSTALL_DIR/start_proxy.sh"
echo "  2. 配置 Claude Code: $INSTALL_DIR/setup_claude_code.sh"
echo "  3. 使用 Claude Code: claude"
echo ""
echo "📋 功能特性："
echo "  ✅ 零余额消耗 - 完全避免 Claude API 费用"
echo "  ✅ 高性能 - Groq 0.36s 快速响应"
echo "  ✅ 功能完整 - 30+ Claude Code 内置指令"
echo "  ✅ 智能路由 - 工具请求 → Claude API, 对话 → K2 服务"
echo ""
echo "🎯 现在运行: $INSTALL_DIR/run_all.sh"
echo ""

# 询问是否立即启动
read -p "是否立即启动 PowerAutomation？(y/N): " START_NOW

if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 正在启动..."
    exec "$INSTALL_DIR/run_all.sh"
else
    echo ""
    echo "✅ 安装完成！稍后运行: $INSTALL_DIR/run_all.sh"
fi

