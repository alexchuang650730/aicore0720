#!/bin/bash
# PowerAutomation macOS 启动脚本
# 自动处理虚拟环境激活

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印彩色消息
print_message() {
    echo -e "${1}${2}${NC}"
}

# PowerAutomation 安装目录
POWERAUTOMATION_DIR="$HOME/.powerautomation"
VENV_DIR="$POWERAUTOMATION_DIR/powerautomation_env"
AICORE_DIR="$POWERAUTOMATION_DIR/aicore0716"

# 检查安装
check_installation() {
    if [ ! -d "$POWERAUTOMATION_DIR" ]; then
        print_message $RED "❌ PowerAutomation 未安装"
        print_message $BLUE "请先运行安装脚本："
        echo "curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/install_powerautomation_v4697.sh | bash"
        exit 1
    fi
    
    if [ ! -d "$AICORE_DIR" ]; then
        print_message $RED "❌ PowerAutomation 核心文件缺失"
        exit 1
    fi
}

# 激活虚拟环境
activate_venv() {
    if [ -d "$VENV_DIR" ]; then
        print_message $BLUE "🔧 激活 PowerAutomation 虚拟环境..."
        source "$VENV_DIR/bin/activate"
        print_message $GREEN "✅ 虚拟环境已激活"
    else
        print_message $YELLOW "⚠️ 未找到虚拟环境，使用系统 Python"
    fi
}

# 运行 PowerAutomation
run_powerautomation() {
    cd "$AICORE_DIR"
    
    case "$1" in
        "start")
            print_message $BLUE "🚀 启动 PowerAutomation 统一 MCP 服务器..."
            python3 -m core.components.claude_router_mcp.unified_mcp_server --action start
            ;;
        "stop")
            print_message $BLUE "🛑 停止 PowerAutomation 服务..."
            python3 -m core.components.claude_router_mcp.unified_mcp_server --action stop
            ;;
        "status")
            print_message $BLUE "📊 PowerAutomation 服务状态:"
            python3 -m core.components.claude_router_mcp.unified_mcp_server --action status
            ;;
        "test")
            print_message $BLUE "🧪 测试 PowerAutomation 功能:"
            python3 -m core.components.claude_router_mcp.unified_mcp_server --action test
            ;;
        "config")
            print_message $BLUE "⚙️ PowerAutomation 配置:"
            python3 -m core.components.claude_router_mcp.unified_mcp_server --action config
            ;;
        "--version")
            print_message $BLUE "📋 PowerAutomation 版本信息:"
            python3 -m core.components.claude_router_mcp.unified_mcp_server --action version
            ;;
        "--help"|"help"|"")
            show_help
            ;;
        *)
            print_message $RED "❌ 未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 显示帮助信息
show_help() {
    echo "PowerAutomation v4.6.97 - macOS 版本"
    echo ""
    echo "用法: powerautomation [命令]"
    echo ""
    echo "命令:"
    echo "  start      启动 PowerAutomation 服务"
    echo "  stop       停止 PowerAutomation 服务"
    echo "  status     查看服务状态"
    echo "  test       测试功能"
    echo "  config     查看配置"
    echo "  --version  显示版本信息"
    echo "  --help     显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  powerautomation start"
    echo "  powerautomation test"
    echo "  powerautomation status"
    echo ""
    echo "🎯 核心功能:"
    echo "  ✅ 完全避免 Claude 模型推理余额消耗"
    echo "  ✅ 保留所有 Claude 工具和指令功能"
    echo "  ✅ 自动路由 AI 推理任务到 K2 服务"
    echo "  ✅ ClaudeEditor 和本地环境实时同步"
    echo ""
    echo "📚 更多帮助: https://github.com/alexchuang650730/aicore0716"
}

# 主函数
main() {
    check_installation
    activate_venv
    run_powerautomation "$1"
}

# 运行主函数
main "$@"

