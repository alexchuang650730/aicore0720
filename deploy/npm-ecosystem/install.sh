#!/bin/bash
# PowerAutomation ClaudeEditor 一键安装脚本
# 支持 PC 和 Mobile 平台自动检测和安装

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 版本信息
VERSION="4.6.9.5"
REPO_URL="https://github.com/alexchuang650730/aicore0711"
NPM_PACKAGE="@powerautomation/claudeeditor"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    print_message $BLUE "🚀 PowerAutomation ClaudeEditor v${VERSION}"
    print_message $CYAN "   AI-Powered Code Editor with K2 Local Model"
    echo "=================================================================="
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -n "$ANDROID_HOME" ]] || [[ -n "$ANDROID_SDK_ROOT" ]]; then
            echo "android"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if [[ -n "$IOS_SIMULATOR" ]] || command -v xcrun &> /dev/null; then
            # 检查是否在 iOS 开发环境
            if [[ "$1" == "--ios" ]]; then
                echo "ios"
            else
                echo "macos"
            fi
        else
            echo "macos"
        fi
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# 检测架构
detect_arch() {
    local arch=$(uname -m)
    case $arch in
        x86_64|amd64)
            echo "x64"
            ;;
        arm64|aarch64)
            echo "arm64"
            ;;
        armv7l|armv6l)
            echo "arm"
            ;;
        *)
            echo "x64"  # 默认
            ;;
    esac
}

# 检查依赖
check_dependencies() {
    local os=$1
    
    print_message $CYAN "🔍 检查系统依赖..."
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_message $RED "❌ Node.js 未安装"
        print_message $YELLOW "请访问 https://nodejs.org 安装 Node.js (>= 16.0.0)"
        exit 1
    fi
    
    local node_version=$(node --version | sed 's/v//')
    print_message $GREEN "✅ Node.js: v${node_version}"
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        print_message $RED "❌ npm 未安装"
        exit 1
    fi
    
    local npm_version=$(npm --version)
    print_message $GREEN "✅ npm: v${npm_version}"
    
    # 平台特定检查
    case $os in
        "android")
            check_android_dependencies
            ;;
        "ios")
            check_ios_dependencies
            ;;
        "linux"|"macos"|"windows")
            check_desktop_dependencies
            ;;
    esac
}

# 检查 Android 依赖
check_android_dependencies() {
    print_message $CYAN "📱 检查 Android 开发环境..."
    
    if [[ -z "$ANDROID_HOME" ]] && [[ -z "$ANDROID_SDK_ROOT" ]]; then
        print_message $YELLOW "⚠️ Android SDK 未配置，将安装 Web 版本"
        return 1
    fi
    
    if ! command -v java &> /dev/null; then
        print_message $YELLOW "⚠️ Java 未安装，将安装 Web 版本"
        return 1
    fi
    
    print_message $GREEN "✅ Android 开发环境就绪"
    return 0
}

# 检查 iOS 依赖
check_ios_dependencies() {
    print_message $CYAN "📱 检查 iOS 开发环境..."
    
    if [[ "$(detect_os)" != "macos" ]]; then
        print_message $RED "❌ iOS 开发需要 macOS 系统"
        exit 1
    fi
    
    if ! command -v xcodebuild &> /dev/null; then
        print_message $YELLOW "⚠️ Xcode 未安装，将安装 Web 版本"
        return 1
    fi
    
    print_message $GREEN "✅ iOS 开发环境就绪"
    return 0
}

# 检查桌面依赖
check_desktop_dependencies() {
    print_message $CYAN "💻 检查桌面环境..."
    
    # 检查 Python (用于 K2 本地模型)
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        print_message $GREEN "✅ Python: v${python_version}"
    else
        print_message $YELLOW "⚠️ Python3 未安装，K2 本地模型将不可用"
    fi
    
    print_message $GREEN "✅ 桌面环境就绪"
    return 0
}

# 选择安装类型
select_install_type() {
    local os=$1
    local install_type=""
    
    print_message $CYAN "🎯 选择安装类型:"
    
    case $os in
        "android"|"ios")
            echo "1) 移动版 (Capacitor) - 推荐"
            echo "2) Web 版 (浏览器)"
            echo ""
            read -p "请选择 [1-2]: " choice
            
            case $choice in
                1)
                    install_type="mobile"
                    ;;
                2)
                    install_type="web"
                    ;;
                *)
                    install_type="mobile"  # 默认
                    ;;
            esac
            ;;
            
        "linux"|"macos"|"windows")
            echo "1) 桌面版 (Electron) - 推荐"
            echo "2) Web 版 (浏览器)"
            echo ""
            read -p "请选择 [1-2]: " choice
            
            case $choice in
                1)
                    install_type="desktop"
                    ;;
                2)
                    install_type="web"
                    ;;
                *)
                    install_type="desktop"  # 默认
                    ;;
            esac
            ;;
            
        *)
            install_type="web"  # 未知平台默认 Web 版
            ;;
    esac
    
    echo $install_type
}

# NPM 安装方式
install_via_npm() {
    local install_type=$1
    
    print_message $CYAN "📦 通过 npm 安装..."
    
    # 全局安装 PowerAutomation CLI
    npm install -g $NPM_PACKAGE
    
    # 创建项目
    local project_name="powerautomation-claudeeditor"
    print_message $CYAN "🏗️ 创建项目: $project_name"
    
    npx create-powerautomation-app $project_name --type=$install_type
    
    cd $project_name
    
    # 安装依赖
    npm install
    
    # 构建应用
    case $install_type in
        "desktop")
            npm run build:desktop
            ;;
        "mobile")
            npm run build:mobile
            ;;
        "web")
            npm run build
            ;;
    esac
    
    print_message $GREEN "✅ npm 安装完成"
}

# Git 克隆安装方式
install_via_git() {
    local install_type=$1
    
    print_message $CYAN "📥 通过 Git 克隆安装..."
    
    # 克隆仓库
    if [[ -d "aicore0711" ]]; then
        print_message $YELLOW "⚠️ 目录 aicore0711 已存在，正在更新..."
        cd aicore0711
        git pull origin main
    else
        git clone $REPO_URL aicore0711
        cd aicore0711
    fi
    
    # 安装依赖
    npm install
    
    # 运行平台特定安装
    node scripts/install.js --type=$install_type
    
    print_message $GREEN "✅ Git 安装完成"
}

# 快速安装方式
quick_install() {
    local install_type=$1
    local os=$2
    
    print_message $CYAN "⚡ 快速安装模式..."
    
    # 下载预构建包
    local download_url="https://github.com/alexchuang650730/aicore0711/releases/download/v${VERSION}/powerautomation-${install_type}-${os}.tar.gz"
    
    print_message $CYAN "📥 下载预构建包..."
    curl -L -o powerautomation.tar.gz $download_url
    
    # 解压
    tar -xzf powerautomation.tar.gz
    cd powerautomation-claudeeditor
    
    # 运行安装脚本
    chmod +x install.sh
    ./install.sh
    
    print_message $GREEN "✅ 快速安装完成"
}

# 配置环境
configure_environment() {
    local install_type=$1
    
    print_message $CYAN "⚙️ 配置环境..."
    
    # 创建配置文件
    cat > powerautomation.config.json << EOF
{
  "version": "${VERSION}",
  "installType": "${install_type}",
  "platform": "$(detect_os)",
  "architecture": "$(detect_arch)",
  "features": {
    "mirrorCode": true,
    "commandMCP": true,
    "k2Model": true,
    "claudeCode": true
  },
  "models": {
    "default": "k2_local",
    "available": ["k2_local", "k2_cloud", "claude_code"]
  }
}
EOF
    
    # 设置环境变量
    echo "export POWERAUTOMATION_HOME=$(pwd)" >> ~/.bashrc
    echo "export PATH=\$PATH:\$POWERAUTOMATION_HOME/bin" >> ~/.bashrc
    
    print_message $GREEN "✅ 环境配置完成"
}

# 显示完成信息
show_completion() {
    local install_type=$1
    local os=$2
    
    echo ""
    print_message $GREEN "🎉 PowerAutomation ClaudeEditor 安装完成！"
    echo "=================================================================="
    
    print_message $CYAN "📋 安装信息:"
    echo "   版本: v${VERSION}"
    echo "   类型: ${install_type}"
    echo "   平台: ${os}"
    echo "   路径: $(pwd)"
    
    echo ""
    print_message $CYAN "🚀 启动命令:"
    
    case $install_type in
        "desktop")
            echo "   ./powerautomation          # 启动桌面应用"
            echo "   npm start                  # 开发模式"
            echo "   npm run build              # 构建应用"
            ;;
        "mobile")
            echo "   npm run dev                # 开发模式"
            echo "   npx cap run ${os}          # 运行到设备"
            echo "   npm run build:mobile       # 构建移动应用"
            ;;
        "web")
            echo "   npm start                  # 启动开发服务器"
            echo "   npm run build              # 构建生产版本"
            echo "   访问: http://localhost:3000"
            ;;
    esac
    
    echo ""
    print_message $CYAN "🌟 核心特性:"
    echo "   🤖 默认 K2 本地模型 (免费)"
    echo "   🪞 Mirror Code 智能路由"
    echo "   📱 跨平台支持"
    echo "   🔄 实时任务同步"
    echo "   🎯 多智能体协作"
    
    echo ""
    print_message $CYAN "💡 使用提示:"
    echo "   - 使用 /help 查看所有指令"
    echo "   - 默认使用 K2 本地模型，无需 API 费用"
    echo "   - 使用 /switch-model claude 切换到 Claude Code"
    echo "   - 文档: https://powerautomation.ai/docs"
    
    echo ""
    print_message $YELLOW "🔄 重新加载环境变量:"
    echo "   source ~/.bashrc"
}

# 主安装流程
main() {
    print_header
    
    # 解析命令行参数
    local install_method="auto"
    local install_type=""
    local force_os=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --npm)
                install_method="npm"
                shift
                ;;
            --git)
                install_method="git"
                shift
                ;;
            --quick)
                install_method="quick"
                shift
                ;;
            --desktop)
                install_type="desktop"
                shift
                ;;
            --mobile)
                install_type="mobile"
                shift
                ;;
            --web)
                install_type="web"
                shift
                ;;
            --ios)
                force_os="ios"
                shift
                ;;
            --android)
                force_os="android"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_message $RED "❌ 未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检测平台
    local os=${force_os:-$(detect_os)}
    local arch=$(detect_arch)
    
    print_message $CYAN "🔍 检测到的平台:"
    echo "   操作系统: $os"
    echo "   架构: $arch"
    echo ""
    
    # 检查依赖
    check_dependencies $os
    
    # 选择安装类型
    if [[ -z "$install_type" ]]; then
        install_type=$(select_install_type $os)
    fi
    
    print_message $GREEN "✅ 安装类型: $install_type"
    echo ""
    
    # 执行安装
    case $install_method in
        "npm")
            install_via_npm $install_type
            ;;
        "git")
            install_via_git $install_type
            ;;
        "quick")
            quick_install $install_type $os
            ;;
        "auto")
            # 自动选择最佳安装方式
            if command -v npm &> /dev/null; then
                install_via_npm $install_type
            elif command -v git &> /dev/null; then
                install_via_git $install_type
            else
                quick_install $install_type $os
            fi
            ;;
    esac
    
    # 配置环境
    configure_environment $install_type
    
    # 显示完成信息
    show_completion $install_type $os
}

# 显示帮助
show_help() {
    echo "PowerAutomation ClaudeEditor 安装脚本"
    echo ""
    echo "用法:"
    echo "  curl -fsSL https://install.powerautomation.ai | bash"
    echo "  curl -fsSL https://install.powerautomation.ai | bash -s -- [选项]"
    echo ""
    echo "安装方式:"
    echo "  --npm          通过 npm 安装"
    echo "  --git          通过 Git 克隆安装"
    echo "  --quick        快速安装 (预构建包)"
    echo ""
    echo "安装类型:"
    echo "  --desktop      桌面版 (Electron)"
    echo "  --mobile       移动版 (Capacitor)"
    echo "  --web          Web 版 (浏览器)"
    echo ""
    echo "平台选项:"
    echo "  --ios          强制 iOS 平台"
    echo "  --android      强制 Android 平台"
    echo ""
    echo "示例:"
    echo "  # 自动检测并安装"
    echo "  curl -fsSL https://install.powerautomation.ai | bash"
    echo ""
    echo "  # 安装桌面版"
    echo "  curl -fsSL https://install.powerautomation.ai | bash -s -- --desktop"
    echo ""
    echo "  # 通过 npm 安装移动版"
    echo "  curl -fsSL https://install.powerautomation.ai | bash -s -- --npm --mobile"
}

# 执行主流程
main "$@"

