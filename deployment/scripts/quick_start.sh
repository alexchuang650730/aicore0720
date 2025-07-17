#!/bin/bash
# PowerAutomation 快速启动脚本
# 适用于 macOS，无需安装即可使用

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_message() {
    echo -e "${1}${2}${NC}"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AICORE_DIR="$SCRIPT_DIR"

print_message $BLUE "🚀 PowerAutomation 快速启动..."
print_message $BLUE "📁 工作目录: $AICORE_DIR"

# 检查必要文件
if [ ! -f "$AICORE_DIR/bin/powerautomation.js" ]; then
    print_message $RED "❌ PowerAutomation 文件未找到"
    print_message $BLUE "请确保在正确的 aicore0716 目录中运行此脚本"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    print_message $RED "❌ Node.js 未安装"
    print_message $BLUE "请先安装 Node.js: brew install node"
    exit 1
fi

# 检查 Python 3
if ! command -v python3 &> /dev/null; then
    print_message $RED "❌ Python 3 未安装"
    print_message $BLUE "请先安装 Python 3: brew install python"
    exit 1
fi

# 创建临时虚拟环境（如果需要）
TEMP_VENV="$AICORE_DIR/.temp_venv"
if [ ! -d "$TEMP_VENV" ]; then
    print_message $BLUE "🔧 创建临时 Python 环境..."
    python3 -m venv "$TEMP_VENV" 2>/dev/null || {
        print_message $YELLOW "⚠️ 虚拟环境创建失败，使用系统 Python"
    }
fi

# 激活虚拟环境（如果存在）
if [ -d "$TEMP_VENV" ]; then
    source "$TEMP_VENV/bin/activate"
    print_message $GREEN "✅ 临时 Python 环境已激活"
    
    # 安装必要依赖
    pip install --quiet httpx websockets aiofiles 2>/dev/null || {
        print_message $YELLOW "⚠️ 部分 Python 依赖安装失败，但继续运行..."
    }
fi

# 切换到工作目录
cd "$AICORE_DIR"

# 根据参数运行不同命令
case "${1:-start}" in
    "start")
        print_message $BLUE "🚀 启动 PowerAutomation 服务..."
        node bin/powerautomation.js start
        ;;
    "stop")
        print_message $BLUE "🛑 停止 PowerAutomation 服务..."
        node bin/powerautomation.js stop
        ;;
    "status")
        print_message $BLUE "📊 PowerAutomation 服务状态:"
        node bin/powerautomation.js status
        ;;
    "test")
        print_message $BLUE "🧪 测试 PowerAutomation 功能:"
        node bin/powerautomation.js test
        ;;
    "proxy")
        print_message $BLUE "🔧 配置 Claude Code 代理..."
        bash claude_code_proxy_config.sh
        ;;
    "claude-setup")
        print_message $BLUE "📋 显示 Claude Code 配置指南..."
        if [ -f "claude_code_setup_guide.md" ]; then
            cat claude_code_setup_guide.md
        else
            print_message $RED "❌ 配置指南文件未找到"
        fi
        ;;
    "--version")
        print_message $BLUE "📋 PowerAutomation 版本信息:"
        node bin/powerautomation.js --version
        ;;
    "--help"|"help")
        show_help
        ;;
    *)
        print_message $RED "❌ 未知命令: $1"
        show_help
        exit 1
        ;;
esac

show_help() {
    echo ""
    echo "PowerAutomation v4.6.97 - 快速启动脚本"
    echo ""
    echo "用法: bash quick_start.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start         启动 PowerAutomation 服务"
    echo "  stop          停止 PowerAutomation 服务"
    echo "  status        查看服务状态"
    echo "  test          测试功能"
    echo "  proxy         配置 Claude Code 代理"
    echo "  claude-setup  显示 Claude Code 配置指南"
    echo "  --version     显示版本信息"
    echo "  --help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  bash quick_start.sh start"
    echo "  bash quick_start.sh test"
    echo "  bash quick_start.sh proxy"
    echo ""
    echo "🎯 核心功能:"
    echo "  ✅ 完全避免 Claude 模型推理余额消耗"
    echo "  ✅ 保留所有 Claude 工具和指令功能"
    echo "  ✅ 自动路由 AI 推理任务到 K2 服务"
    echo "  ✅ ClaudeEditor 和本地环境实时同步"
    echo ""
}

# 清理函数
cleanup() {
    if [ -d "$TEMP_VENV" ]; then
        deactivate 2>/dev/null || true
    fi
}

# 设置退出时清理
trap cleanup EXIT

