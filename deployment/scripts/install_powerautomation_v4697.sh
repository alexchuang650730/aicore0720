#!/bin/bash
# PowerAutomation v4.6.9.7 一键安装脚本
# 包含 Claude Code Sync Service + K2 路由 + 工具模式

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 版本信息
VERSION="4.6.9.7"
INSTALL_DIR="$HOME/.powerautomation"
REPO_URL="https://github.com/alexchuang650730/aicore0716.git"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    echo "=================================================================="
    print_message $CYAN "🚀 PowerAutomation v${VERSION} 一键安装程序"
    echo "=================================================================="
    print_message $BLUE "📋 功能特性:"
    print_message $GREEN "  ✅ Claude Code 同步服务 - 与 ClaudeEditor 无缝同步"
    print_message $GREEN "  ✅ Claude 工具模式 - 完全避免模型推理余额消耗"
    print_message $GREEN "  ✅ K2 服务路由 - 自动路由 AI 推理任务到 K2"
    print_message $GREEN "  ✅ 统一 MCP 架构 - 一个组件解决所有问题"
    print_message $GREEN "  ✅ 一键安装配置 - npm/curl 开箱即用"
    echo "=================================================================="
    echo ""
}

check_dependencies() {
    print_message $BLUE "🔍 检查系统依赖..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_message $RED "❌ Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        print_message $RED "❌ pip3 未安装，请先安装 pip3"
        exit 1
    fi
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        print_message $RED "❌ git 未安装，请先安装 git"
        exit 1
    fi
    
    print_message $GREEN "✅ 系统依赖检查通过"
}

install_python_dependencies() {
    print_message $BLUE "📦 安装 Python 依赖包..."
    
    # 检测操作系统
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS 系统 - 使用虚拟环境
        print_message $BLUE "🍎 检测到 macOS 系统，创建虚拟环境..."
        
        # 创建虚拟环境
        if [ ! -d "$INSTALL_DIR/powerautomation_env" ]; then
            print_message $BLUE "🔧 创建 Python 虚拟环境..."
            python3 -m venv "$INSTALL_DIR/powerautomation_env" || {
                print_message $RED "❌ 虚拟环境创建失败"
                exit 1
            }
        fi
        
        # 激活虚拟环境
        source "$INSTALL_DIR/powerautomation_env/bin/activate"
        
        # 升级 pip
        python -m pip install --upgrade pip
        
        # 安装依赖
        python -m pip install httpx websockets aiofiles requests beautifulsoup4 lxml || {
            print_message $YELLOW "⚠️ 部分依赖包安装失败，但继续安装..."
        }
        
        # 创建激活脚本
        cat > "$INSTALL_DIR/activate_env.sh" << 'EOF'
#!/bin/bash
# PowerAutomation 虚拟环境激活脚本
source "$HOME/.powerautomation/powerautomation_env/bin/activate"
echo "✅ PowerAutomation 虚拟环境已激活"
EOF
        chmod +x "$INSTALL_DIR/activate_env.sh"
        
        print_message $GREEN "✅ macOS 虚拟环境配置完成"
        
    else
        # Linux 系统 - 尝试系统安装，失败则使用虚拟环境
        print_message $BLUE "🐧 检测到 Linux 系统..."
        
        # 尝试直接安装
        if pip3 install --user httpx websockets aiofiles requests beautifulsoup4 lxml 2>/dev/null; then
            print_message $GREEN "✅ 系统级安装成功"
        else
            # 回退到虚拟环境
            print_message $BLUE "🔧 系统级安装失败，使用虚拟环境..."
            python3 -m venv "$INSTALL_DIR/powerautomation_env"
            source "$INSTALL_DIR/powerautomation_env/bin/activate"
            python -m pip install --upgrade pip
            python -m pip install httpx websockets aiofiles requests beautifulsoup4 lxml
            
            # 创建激活脚本
            cat > "$INSTALL_DIR/activate_env.sh" << 'EOF'
#!/bin/bash
# PowerAutomation 虚拟环境激活脚本
source "$HOME/.powerautomation/powerautomation_env/bin/activate"
echo "✅ PowerAutomation 虚拟环境已激活"
EOF
            chmod +x "$INSTALL_DIR/activate_env.sh"
        fi
    fi
    
    print_message $GREEN "✅ Python 依赖包安装完成"
}

download_powerautomation() {
    print_message $BLUE "📥 下载 PowerAutomation v${VERSION}..."
    
    # 创建安装目录
    mkdir -p "$INSTALL_DIR"
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
    
    cd aicore0716
    
    print_message $GREEN "✅ PowerAutomation 下载完成"
}

setup_powerautomation() {
    print_message $BLUE "⚙️ 配置 PowerAutomation..."
    
    cd "$INSTALL_DIR/aicore0716"
    
    # 设置 Python 路径
    export PYTHONPATH="$INSTALL_DIR/aicore0716:$PYTHONPATH"
    
    # 创建配置目录
    mkdir -p "$HOME/.powerautomation"
    
    # 创建启动脚本
    cat > "$HOME/.powerautomation/powerautomation" << 'EOF'
#!/bin/bash
# PowerAutomation 启动脚本

INSTALL_DIR="$HOME/.powerautomation/aicore0716"
export PYTHONPATH="$INSTALL_DIR:$PYTHONPATH"

case "$1" in
    start)
        echo "🚀 启动 PowerAutomation 统一 MCP 服务器..."
        cd "$INSTALL_DIR"
        python3 -m core.components.claude_router_mcp.unified_mcp_server --action start
        ;;
    stop)
        echo "🛑 停止 PowerAutomation 服务..."
        pkill -f "claude_router_mcp"
        ;;
    restart)
        echo "🔄 重启 PowerAutomation 服务..."
        pkill -f "claude_router_mcp" || true
        sleep 2
        cd "$INSTALL_DIR"
        python3 -m core.components.claude_router_mcp.unified_mcp_server --action start
        ;;
    status)
        echo "📊 PowerAutomation 服务状态:"
        cd "$INSTALL_DIR"
        python3 -m core.components.claude_router_mcp.unified_mcp_server --action status
        ;;
    config)
        echo "⚙️ PowerAutomation 配置:"
        cd "$INSTALL_DIR"
        python3 -m core.components.claude_router_mcp.unified_mcp_server --action config
        ;;
    test)
        echo "🧪 测试 PowerAutomation 功能:"
        cd "$INSTALL_DIR"
        python3 -m core.components.claude_router_mcp.unified_mcp_server --action test
        ;;
    claude-sync)
        echo "🔗 测试 Claude Code 同步:"
        cd "$INSTALL_DIR"
        python3 -m core.components.claude_router_mcp.claude_sync.sync_manager --action test
        ;;
    k2-test)
        echo "🔄 测试 K2 服务路由:"
        cd "$INSTALL_DIR"
        python3 -m core.components.claude_router_mcp.k2_router.k2_client --action test
        ;;
    tool-mode)
        echo "🔧 管理工具模式:"
        cd "$INSTALL_DIR"
        python3 -m core.components.claude_router_mcp.tool_mode.tool_manager "$@"
        ;;
    *)
        echo "PowerAutomation v4.6.9.7 - 统一 MCP 解决方案"
        echo ""
        echo "使用方法: powerautomation <命令>"
        echo ""
        echo "可用命令:"
        echo "  start        启动 PowerAutomation 服务"
        echo "  stop         停止 PowerAutomation 服务"
        echo "  restart      重启 PowerAutomation 服务"
        echo "  status       查看服务状态"
        echo "  config       查看配置信息"
        echo "  test         测试所有功能"
        echo "  claude-sync  测试 Claude Code 同步"
        echo "  k2-test      测试 K2 服务路由"
        echo "  tool-mode    管理工具模式"
        echo ""
        echo "示例:"
        echo "  powerautomation start"
    # 创建启动脚本
    cat > "$INSTALL_DIR/powerautomation" << 'EOF'
#!/bin/bash
# PowerAutomation 启动脚本

# PowerAutomation 安装目录
POWERAUTOMATION_DIR="$HOME/.powerautomation"
VENV_DIR="$POWERAUTOMATION_DIR/powerautomation_env"
AICORE_DIR="$POWERAUTOMATION_DIR/aicore0716"

# 激活虚拟环境（如果存在）
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
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! grep -q "powerautomation" ~/.zshrc 2>/dev/null; then
            echo 'export PATH="$HOME/.powerautomation:$PATH"' >> ~/.zshrc
        fi
        if ! grep -q "powerautomation" ~/.bash_profile 2>/dev/null; then
            echo 'export PATH="$HOME/.powerautomation:$PATH"' >> ~/.bash_profile
        fi
    else
        # Linux
        if ! grep -q "powerautomation" ~/.bashrc 2>/dev/null; then
            echo 'export PATH="$HOME/.powerautomation:$PATH"' >> ~/.bashrc
        fi
    fi
    
    print_message $GREEN "✅ 已添加 powerautomation 到 PATH"
    
    # 为当前会话设置 PATH
    export PATH="$HOME/.powerautomation:$PATH"
    
    print_message $GREEN "✅ PowerAutomation 配置完成"
}

configure_claude_tool_mode() {
    print_message $BLUE "🔧 配置 Claude 工具模式..."
    
    cd "$INSTALL_DIR/aicore0716"
    
    # 启用工具模式
    python3 -m core.components.claude_router_mcp.tool_mode.tool_manager --action enable || {
        print_message $YELLOW "⚠️ 工具模式配置可能需要手动调整"
    }
    
    print_message $GREEN "✅ Claude 工具模式配置完成"
}

test_installation() {
    print_message $BLUE "🧪 测试安装..."
    
    cd "$INSTALL_DIR/aicore0716"
    
    # 测试统一 MCP 服务器
    python3 -m core.components.claude_router_mcp.unified_mcp_server --action test || {
        print_message $YELLOW "⚠️ 部分功能测试失败，但安装已完成"
        return
    }
    
    print_message $GREEN "✅ 安装测试通过"
}

print_success_message() {
    echo ""
    echo "=================================================================="
    print_message $GREEN "🎉 PowerAutomation v${VERSION} 安装成功！"
    echo "=================================================================="
    echo ""
    print_message $CYAN "📋 安装信息:"
    print_message $BLUE "  📁 安装目录: $INSTALL_DIR"
    print_message $BLUE "  🔧 配置目录: $HOME/.powerautomation"
    print_message $BLUE "  📜 启动脚本: $HOME/.powerautomation/powerautomation"
    echo ""
    print_message $CYAN "🚀 快速开始:"
    print_message $GREEN "  # 重新加载 shell 配置"
    print_message $YELLOW "  source ~/.bashrc"
    echo ""
    print_message $GREEN "  # 启动 PowerAutomation 服务"
    print_message $YELLOW "  powerautomation start"
    echo ""
    print_message $GREEN "  # 查看服务状态"
    print_message $YELLOW "  powerautomation status"
    echo ""
    print_message $GREEN "  # 测试功能"
    print_message $YELLOW "  powerautomation test"
    echo ""
    print_message $CYAN "🎯 核心功能:"
    print_message $GREEN "  ✅ 完全避免 Claude 模型推理余额消耗"
    print_message $GREEN "  ✅ 保留所有 Claude 工具和指令功能"
    print_message $GREEN "  ✅ 自动路由 AI 推理任务到 K2 服务"
    print_message $GREEN "  ✅ ClaudeEditor 和本地环境实时同步"
    echo ""
    print_message $CYAN "📚 更多帮助:"
    print_message $BLUE "  powerautomation --help"
    print_message $BLUE "  https://github.com/alexchuang650730/aicore0716"
    echo ""
    echo "=================================================================="
    print_message $PURPLE "🌟 PowerAutomation v${VERSION} - 让 AI 开发更智能！"
    echo "=================================================================="
    echo ""
}

# 主安装流程
main() {
    print_header
    
    # 检查是否为 root 用户
    if [ "$EUID" -eq 0 ]; then
        print_message $RED "❌ 请不要使用 root 用户运行此脚本"
        exit 1
    fi
    
    # 安装步骤
    check_dependencies
    install_python_dependencies
    download_powerautomation
    setup_powerautomation
    configure_claude_tool_mode
    test_installation
    print_success_message
}

# 错误处理
trap 'print_message $RED "❌ 安装过程中发生错误，请检查上面的错误信息"; exit 1' ERR

# 运行主函数
main "$@"

