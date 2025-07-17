#!/bin/bash

# PowerAutomation v4.6.97 - macOS 依赖修复脚本
# 解决 macOS externally-managed-environment 问题

set -e

echo "🍎 PowerAutomation v4.6.97 - macOS 依赖修复"
echo "=============================================="

# 检测操作系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 此脚本仅适用于 macOS"
    exit 1
fi

echo "📍 检测到 macOS 系统"

# 检查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python 3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"

# 检查是否已安装 aiohttp
if python3 -c "import aiohttp" 2>/dev/null; then
    echo "✅ aiohttp 已安装，无需修复"
    exit 0
fi

echo "🔧 开始修复 aiohttp 依赖..."

# 方案 1: 使用 --break-system-packages
echo "📦 尝试方案 1: 使用 --break-system-packages 安装..."
if pip3 install aiohttp --break-system-packages --user --quiet 2>/dev/null; then
    echo "✅ 方案 1 成功: aiohttp 已通过 pip 安装"
    
    # 验证安装
    if python3 -c "import aiohttp" 2>/dev/null; then
        echo "🎉 aiohttp 安装验证成功！"
        echo ""
        echo "🚀 现在可以启动代理了:"
        echo "   bash ~/.powerautomation/proxy/quick_start.sh"
        exit 0
    fi
fi

echo "⚠️ 方案 1 失败，尝试方案 2..."

# 方案 2: 使用 Homebrew 安装 pipx
echo "📦 尝试方案 2: 使用 Homebrew 和 pipx..."

# 检查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未找到 Homebrew，请先安装 Homebrew:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# 安装 pipx
if ! command -v pipx &> /dev/null; then
    echo "📥 安装 pipx..."
    if brew install pipx --quiet 2>/dev/null; then
        echo "✅ pipx 安装成功"
    else
        echo "⚠️ pipx 安装失败，继续尝试其他方案..."
    fi
fi

# 使用 pipx 安装 aiohttp（在独立环境中）
if command -v pipx &> /dev/null; then
    echo "📦 使用 pipx 创建独立环境..."
    
    # 创建专用的 PowerAutomation 环境
    VENV_PATH="$HOME/.powerautomation/venv"
    mkdir -p "$HOME/.powerautomation"
    
    if python3 -m venv "$VENV_PATH" 2>/dev/null; then
        echo "✅ 虚拟环境创建成功: $VENV_PATH"
        
        # 在虚拟环境中安装 aiohttp
        if "$VENV_PATH/bin/pip" install aiohttp --quiet 2>/dev/null; then
            echo "✅ aiohttp 已安装到虚拟环境"
            
            # 更新启动脚本使用虚拟环境
            echo "🔧 更新启动脚本..."
            
            cat > "$HOME/.powerautomation/proxy/start_claude_proxy.sh" << 'EOF'
#!/bin/bash
echo "🚀 启动增强版 Claude API 代理服务器..."

# 激活虚拟环境
VENV_PATH="$HOME/.powerautomation/venv"
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    echo "✅ 已激活虚拟环境"
else
    echo "⚠️ 虚拟环境未找到，使用系统 Python"
fi

# 检查 aiohttp
if python3 -c "import aiohttp" 2>/dev/null; then
    echo "✅ aiohttp 可用"
else
    echo "❌ aiohttp 不可用"
    exit 1
fi

# 启动增强版代理服务器
echo "🎯 启动代理服务器..."
python3 ~/.powerautomation/proxy/claude_api_proxy.py
EOF
            
            chmod +x "$HOME/.powerautomation/proxy/start_claude_proxy.sh"
            
            echo "🎉 macOS 依赖修复完成！"
            echo ""
            echo "🚀 现在可以启动代理了:"
            echo "   bash ~/.powerautomation/proxy/quick_start.sh"
            exit 0
        fi
    fi
fi

echo "⚠️ 方案 2 失败，尝试方案 3..."

# 方案 3: 使用 conda（如果可用）
if command -v conda &> /dev/null; then
    echo "📦 尝试方案 3: 使用 conda..."
    if conda install -c conda-forge aiohttp -y --quiet 2>/dev/null; then
        echo "✅ 方案 3 成功: aiohttp 已通过 conda 安装"
        
        if python3 -c "import aiohttp" 2>/dev/null; then
            echo "🎉 aiohttp 安装验证成功！"
            echo ""
            echo "🚀 现在可以启动代理了:"
            echo "   bash ~/.powerautomation/proxy/quick_start.sh"
            exit 0
        fi
    fi
fi

# 方案 4: 最后的尝试 - 强制安装
echo "⚠️ 前面的方案都失败了，尝试最后的方案..."
echo "📦 尝试方案 4: 强制安装到用户目录..."

# 创建用户 Python 包目录
USER_SITE=$(python3 -m site --user-site)
mkdir -p "$USER_SITE"

# 尝试直接下载和安装 aiohttp
if pip3 install aiohttp --user --force-reinstall --no-deps --quiet 2>/dev/null; then
    echo "✅ 强制安装成功"
    
    if python3 -c "import aiohttp" 2>/dev/null; then
        echo "🎉 aiohttp 安装验证成功！"
        echo ""
        echo "🚀 现在可以启动代理了:"
        echo "   bash ~/.powerautomation/proxy/quick_start.sh"
        exit 0
    fi
fi

# 所有方案都失败
echo ""
echo "❌ 所有自动修复方案都失败了"
echo ""
echo "🔧 手动解决方案:"
echo "1. 安装 Homebrew (如果还没有):"
echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
echo ""
echo "2. 使用 Homebrew 安装 Python:"
echo "   brew install python"
echo ""
echo "3. 使用 Homebrew Python 安装 aiohttp:"
echo "   /opt/homebrew/bin/pip3 install aiohttp"
echo ""
echo "4. 或者创建虚拟环境:"
echo "   python3 -m venv ~/.powerautomation/venv"
echo "   source ~/.powerautomation/venv/bin/activate"
echo "   pip install aiohttp"
echo ""
echo "📚 更多信息: https://github.com/alexchuang650730/aicore0716"

exit 1

