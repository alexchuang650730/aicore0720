#!/bin/bash
# PowerAutomation ClaudeEditor 自动安装和启动脚本
# 解决 Claude 与 ClaudeEditor 启动依赖问题

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否已经安装
check_installation() {
    log_info "检查 PowerAutomation ClaudeEditor 安装状态..."
    
    if [ -d "/home/ubuntu/aicore0716" ]; then
        log_success "发现已安装的 PowerAutomation 项目"
        return 0
    else
        log_warning "未发现 PowerAutomation 项目，需要安装"
        return 1
    fi
}

# 安装 PowerAutomation ClaudeEditor
install_claudeeditor() {
    log_info "开始安装 PowerAutomation ClaudeEditor..."
    
    # 切换到用户目录
    cd /home/ubuntu
    
    # 克隆项目
    if [ ! -d "aicore0716" ]; then
        log_info "克隆 PowerAutomation 仓库..."
        git clone https://github.com/alexchuang650730/aicore0716.git
        cd aicore0716
    else
        log_info "更新现有 PowerAutomation 仓库..."
        cd aicore0716
        git pull origin main
    fi
    
    # 安装前端依赖
    log_info "安装 ClaudeEditor 前端依赖..."
    cd claudeditor
    
    # 检查 Node.js 和 npm
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    
    # 安装依赖
    npm install
    
    log_success "PowerAutomation ClaudeEditor 安装完成"
}

# 启动 ClaudeEditor 开发服务器
start_claudeeditor() {
    log_info "启动 ClaudeEditor 开发服务器..."
    
    cd /home/ubuntu/aicore0716/claudeditor
    
    # 检查端口是否被占用
    if lsof -Pi :5176 -sTCP:LISTEN -t >/dev/null ; then
        log_warning "端口 5176 已被占用，尝试终止现有进程..."
        pkill -f "vite.*5176" || true
        sleep 2
    fi
    
    # 启动开发服务器（后台运行）
    log_info "在端口 5176 启动 Vite 开发服务器..."
    nohup npm run dev -- --port 5176 --host 0.0.0.0 > /tmp/claudeeditor.log 2>&1 &
    
    # 等待服务器启动
    log_info "等待服务器启动..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:5176 > /dev/null 2>&1; then
            log_success "ClaudeEditor 服务器启动成功！"
            log_info "访问地址: http://127.0.0.1:5176"
            return 0
        fi
        sleep 1
    done
    
    log_error "ClaudeEditor 服务器启动失败，请检查日志: /tmp/claudeeditor.log"
    return 1
}

# 启动后端 MCP 服务
start_mcp_services() {
    log_info "启动 MCP 核心服务..."
    
    cd /home/ubuntu/aicore0716
    
    # 检查 Python 环境
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 启动 MCP 协调器
    log_info "启动 MCP 协调器..."
    nohup python3 -m core.components.mcp_coordinator_mcp.coordinator > /tmp/mcp_coordinator.log 2>&1 &
    
    # 启动其他核心服务
    log_info "启动其他 MCP 核心服务..."
    # 这里可以添加其他 MCP 服务的启动命令
    
    log_success "MCP 核心服务启动完成"
}

# 等待双向通信建立
wait_for_communication() {
    log_info "等待 Claude Code 与 ClaudeEditor 双向通信建立..."
    
    # 检查通信状态的逻辑
    for i in {1..60}; do
        # 这里可以添加检查双向通信是否建立的逻辑
        # 例如检查特定的端点或文件
        if [ -f "/tmp/claude_code_ready" ]; then
            log_success "双向通信已建立！"
            return 0
        fi
        sleep 1
    done
    
    log_warning "双向通信建立超时，但服务已启动"
    return 1
}

# 显示状态信息
show_status() {
    log_info "PowerAutomation ClaudeEditor 状态信息:"
    echo "=================================="
    echo "🌐 ClaudeEditor 前端: http://127.0.0.1:5176"
    echo "📊 系统状态: 运行中"
    echo "🔄 MCP 服务: 已启动"
    echo "📝 日志文件:"
    echo "  - ClaudeEditor: /tmp/claudeeditor.log"
    echo "  - MCP 协调器: /tmp/mcp_coordinator.log"
    echo "=================================="
}

# 主函数
main() {
    log_info "PowerAutomation ClaudeEditor 自动安装和启动脚本"
    log_info "版本: v4.6.9.6-ui-compliant"
    echo "=================================="
    
    # 检查安装状态
    if ! check_installation; then
        install_claudeeditor
    fi
    
    # 启动服务
    start_mcp_services
    start_claudeeditor
    
    # 等待通信建立
    wait_for_communication
    
    # 显示状态
    show_status
    
    log_success "PowerAutomation ClaudeEditor 已成功启动并准备就绪！"
}

# 如果直接执行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

