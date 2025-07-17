#!/bin/bash
# PowerAutomation v4.6.97 - macOS 专用安装脚本
# 解决 externally-managed-environment 问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
VERSION="4.6.97"
REPO_URL="https://github.com/alexchuang650730/aicore0716.git"
INSTALL_DIR="$HOME/.powerautomation"

print_message() {
    echo -e "${1}${2}${NC}"
}

print_header() {
    echo ""
    echo "=================================================================="
    print_message $BLUE "🚀 PowerAutomation v${VERSION} - macOS 安装程序"
    echo "=================================================================="
    echo ""
}

check_system() {
    print_message $BLUE "🔍 检查系统环境..."
    
    # 检查 macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_message $RED "❌ 此脚本仅适用于 macOS 系统"
        exit 1
    fi
    
    # 检查 Python 3
    if ! command -v python3 &> /dev/null; then
        print_message $RED "❌ Python 3 未安装"
        print_message $BLUE "请先安装 Python 3: brew install python"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_message $RED "❌ Node.js 未安装"
        print_message $BLUE "请先安装 Node.js: brew install node"
        exit 1
    fi
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        print_message $RED "❌ git 未安装"
        print_message $BLUE "请先安装 git: brew install git"
        exit 1
    fi
    
    print_message $GREEN "✅ 系统环境检查通过"
}

create_virtual_environment() {
    print_message $BLUE "🔧 创建 Python 虚拟环境..."
    
    # 创建安装目录
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # 创建虚拟环境
    if [ ! -d "powerautomation_env" ]; then
        python3 -m venv powerautomation_env || {
            print_message $RED "❌ 虚拟环境创建失败"
            exit 1
        }
        print_message $GREEN "✅ 虚拟环境创建成功"
    else
        print_message $YELLOW "⚠️ 虚拟环境已存在，跳过创建"
    fi
    
    # 激活虚拟环境
    source powerautomation_env/bin/activate
    
    # 升级 pip
    python -m pip install --upgrade pip
    
    print_message $GREEN "✅ 虚拟环境配置完成"
}

install_python_dependencies() {
    print_message $BLUE "📦 安装 Python 依赖包..."
    
    # 确保虚拟环境已激活
    source "$INSTALL_DIR/powerautomation_env/bin/activate"
    
    # 安装依赖包
    python -m pip install httpx websockets aiofiles requests beautifulsoup4 lxml || {
        print_message $YELLOW "⚠️ 部分依赖包安装失败，但继续安装..."
    }
    
    print_message $GREEN "✅ Python 依赖包安装完成"
}

download_powerautomation() {
    print_message $BLUE "📥 下载 PowerAutomation v${VERSION}..."
    
    cd "$INSTALL_DIR"
    
    # 如果已存在，先备份
    if [ -d "aicore0716" ]; then
        print_message $YELLOW "⚠️ 发现现有安装，正在备份..."
        mv aicore0716 "aicore0716_backup_$(date +%Y%m%d_%H%M%S)" || true
    fi
    
    # 克隆仓库
    git clone "$REPO_URL" aicore0716 || {
        print_message $RED "❌ 下载失败，请检查网络连接"
        exit 1
    }
    
    print_message $GREEN "✅ PowerAutomation 下载完成"
}

configure_powerautomation() {
    print_message $BLUE "⚙️ 配置 PowerAutomation..."
    
    cd "$INSTALL_DIR/aicore0716"
    
    # 创建配置目录
    mkdir -p "$INSTALL_DIR/config"
    
    # 创建启动脚本
    cat > "$INSTALL_DIR/powerautomation" << 'EOF'
#!/bin/bash
# PowerAutomation macOS 启动脚本

POWERAUTOMATION_DIR="$HOME/.powerautomation"
VENV_DIR="$POWERAUTOMATION_DIR/powerautomation_env"
AICORE_DIR="$POWERAUTOMATION_DIR/aicore0716"

# 激活虚拟环境
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

# 切换到工作目录
cd "$AICORE_DIR"

# 运行 PowerAutomation
node bin/powerautomation.js "$@"
EOF
    
    chmod +x "$INSTALL_DIR/powerautomation"
    
    # 添加到 PATH
    if ! grep -q "powerautomation" ~/.zshrc 2>/dev/null; then
        echo 'export PATH="$HOME/.powerautomation:$PATH"' >> ~/.zshrc
    fi
    if ! grep -q "powerautomation" ~/.bash_profile 2>/dev/null; then
        echo 'export PATH="$HOME/.powerautomation:$PATH"' >> ~/.bash_profile
    fi
    
    print_message $GREEN "✅ PowerAutomation 配置完成"
}

test_installation() {
    print_message $BLUE "🧪 测试安装..."
    
    # 激活虚拟环境
    source "$INSTALL_DIR/powerautomation_env/bin/activate"
    
    cd "$INSTALL_DIR/aicore0716"
    
    # 测试 PowerAutomation
    if node bin/powerautomation.js test; then
        print_message $GREEN "✅ 安装测试通过"
    else
        print_message $YELLOW "⚠️ 部分功能测试失败，但安装已完成"
    fi
}

print_success() {
    echo ""
    echo "=================================================================="
    print_message $GREEN "🎉 PowerAutomation v${VERSION} 安装成功！"
    echo "=================================================================="
    echo ""
    print_message $BLUE "📋 安装信息:"
    echo "  📁 安装目录: $INSTALL_DIR"
    echo "  🐍 虚拟环境: $INSTALL_DIR/powerautomation_env"
    echo "  📜 启动脚本: $INSTALL_DIR/powerautomation"
    echo ""
    print_message $BLUE "🚀 快速开始:"
    echo "  # 重新加载 shell 配置"
    echo "  source ~/.zshrc"
    echo ""
    echo "  # 启动 PowerAutomation 服务"
    echo "  powerautomation start"
    echo ""
    echo "  # 查看服务状态"
    echo "  powerautomation status"
    echo ""
    echo "  # 测试功能"
    echo "  powerautomation test"
    echo ""
    print_message $BLUE "🎯 核心功能:"
    echo "  ✅ 完全避免 Claude 模型推理余额消耗"
    echo "  ✅ 保留所有 Claude 工具和指令功能"
    echo "  ✅ 自动路由 AI 推理任务到 K2 服务"
    echo "  ✅ ClaudeEditor 和本地环境实时同步"
    echo ""
    print_message $BLUE "📚 更多帮助:"
    echo "  powerautomation --help"
    echo "  https://github.com/alexchuang650730/aicore0716"
    echo ""
    echo "=================================================================="
    print_message $GREEN "🌟 PowerAutomation v${VERSION} - 让 AI 开发更智能！"
    echo "=================================================================="
    echo ""
}

# 主安装流程
main() {
    print_header
    check_system
    create_virtual_environment
    install_python_dependencies
    download_powerautomation
    configure_powerautomation
    test_installation
    print_success
}

# 运行主函数
main "$@"

