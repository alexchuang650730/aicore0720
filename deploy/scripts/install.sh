#!/bin/bash

# PowerAutomation 安装脚本
# 适用于 macOS 和 Linux

set -e

echo "🚀 开始安装 PowerAutomation..."

# 检查系统要求
check_requirements() {
    echo "📋 检查系统要求..."
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3.8+ 未找到，请先安装 Python"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc) -eq 0 ]]; then
        echo "❌ Python 版本过低 ($PYTHON_VERSION)，需要 3.8+"
        exit 1
    fi
    
    # 检查Node.js版本
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未找到，请先安装 Node.js 16+"
        exit 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ $NODE_VERSION -lt 16 ]]; then
        echo "❌ Node.js 版本过低 ($NODE_VERSION)，需要 16+"
        exit 1
    fi
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        echo "❌ Git 未找到，请先安装 Git"
        exit 1
    fi
    
    echo "✅ 系统要求检查通过"
}

# 创建项目目录
create_directories() {
    echo "📁 创建项目目录..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p uploads
    mkdir -p downloads
    mkdir -p temp
    
    echo "✅ 项目目录创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    echo "🐍 安装Python依赖..."
    
    # 创建虚拟环境（可选）
    if [[ "$1" == "--venv" ]]; then
        echo "🔧 创建虚拟环境..."
        python3 -m venv venv
        source venv/bin/activate
        echo "✅ 虚拟环境已激活"
    fi
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    
    echo "✅ Python依赖安装完成"
}

# 安装Node.js依赖
install_node_dependencies() {
    echo "📦 安装Node.js依赖..."
    
    cd claudeditor
    npm install
    cd ..
    
    echo "✅ Node.js依赖安装完成"
}

# 配置环境变量
setup_environment() {
    echo "⚙️ 配置环境变量..."
    
    if [[ ! -f .env ]]; then
        cp .env.example .env
        echo "📝 已创建 .env 文件，请编辑其中的API密钥"
    else
        echo "📝 .env 文件已存在"
    fi
    
    echo "✅ 环境变量配置完成"
}

# 初始化数据库
initialize_database() {
    echo "🗄️ 初始化数据库..."
    
    python3 -c "
import sqlite3
import os

# 创建主数据库
conn = sqlite3.connect('powerautomation.db')
cursor = conn.cursor()

# 创建基础表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT,
        created_at REAL,
        updated_at REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS workflows (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        status TEXT,
        started_at REAL,
        completed_at REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        id TEXT PRIMARY KEY,
        command TEXT NOT NULL,
        result TEXT,
        executed_at REAL
    )
''')

conn.commit()
conn.close()

# 创建内存数据库
conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        memory_type TEXT,
        created_at REAL,
        importance REAL
    )
''')

conn.commit()
conn.close()

print('✅ 数据库初始化完成')
"
}

# 验证安装
verify_installation() {
    echo "🔍 验证安装..."
    
    # 检查Python模块
    python3 -c "
import sys
import importlib

modules = [
    'fastapi', 'uvicorn', 'pydantic', 'websockets', 
    'httpx', 'aiofiles', 'numpy', 'sqlite3'
]

for module in modules:
    try:
        importlib.import_module(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
        sys.exit(1)
"
    
    # 检查Node.js模块
    if [[ -f claudeditor/package.json ]]; then
        echo "✅ Node.js模块检查通过"
    else
        echo "❌ Node.js模块检查失败"
        exit 1
    fi
    
    echo "✅ 安装验证完成"
}

# 生成启动脚本
generate_startup_scripts() {
    echo "📝 生成启动脚本..."
    
    # 创建启动脚本
    cat > start_powerautomation.sh << 'EOF'
#!/bin/bash

# PowerAutomation 启动脚本

echo "🚀 启动 PowerAutomation 系统..."

# 检查环境变量
if [[ ! -f .env ]]; then
    echo "❌ .env 文件不存在，请先配置环境变量"
    exit 1
fi

# 加载环境变量
source .env

# 创建日志目录
mkdir -p logs

# 启动服务（使用screen或tmux保持后台运行）
echo "🔧 启动 PowerAutomation Core 驱动器..."
python3 core/powerautomation_core_driver.py &
CORE_PID=$!

echo "🎨 启动 ClaudeEditor..."
python3 claude_code_integration/claudeditor_enhanced.py &
EDITOR_PID=$!

echo "🔌 启动 MCP 服务器..."
python3 mcp_server/main.py &
MCP_PID=$!

# 等待服务启动
sleep 5

# 检查服务状态
if ps -p $CORE_PID > /dev/null; then
    echo "✅ PowerAutomation Core 驱动器运行中 (PID: $CORE_PID)"
else
    echo "❌ PowerAutomation Core 驱动器启动失败"
fi

if ps -p $EDITOR_PID > /dev/null; then
    echo "✅ ClaudeEditor 运行中 (PID: $EDITOR_PID)"
else
    echo "❌ ClaudeEditor 启动失败"
fi

if ps -p $MCP_PID > /dev/null; then
    echo "✅ MCP 服务器运行中 (PID: $MCP_PID)"
else
    echo "❌ MCP 服务器启动失败"
fi

echo "🎯 PowerAutomation 系统启动完成！"
echo "📱 访问 ClaudeEditor: http://localhost:8000"
echo "🔌 访问 MCP 服务器: http://localhost:8765"
echo "📊 API 文档: http://localhost:8000/docs"

# 保存PID文件
echo $CORE_PID > logs/core.pid
echo $EDITOR_PID > logs/editor.pid
echo $MCP_PID > logs/mcp.pid

echo "🔧 使用 ./stop_powerautomation.sh 停止服务"
EOF

    # 创建停止脚本
    cat > stop_powerautomation.sh << 'EOF'
#!/bin/bash

# PowerAutomation 停止脚本

echo "🔄 停止 PowerAutomation 系统..."

# 读取PID文件并停止服务
if [[ -f logs/core.pid ]]; then
    CORE_PID=$(cat logs/core.pid)
    if ps -p $CORE_PID > /dev/null; then
        kill $CORE_PID
        echo "✅ PowerAutomation Core 驱动器已停止"
    fi
    rm logs/core.pid
fi

if [[ -f logs/editor.pid ]]; then
    EDITOR_PID=$(cat logs/editor.pid)
    if ps -p $EDITOR_PID > /dev/null; then
        kill $EDITOR_PID
        echo "✅ ClaudeEditor 已停止"
    fi
    rm logs/editor.pid
fi

if [[ -f logs/mcp.pid ]]; then
    MCP_PID=$(cat logs/mcp.pid)
    if ps -p $MCP_PID > /dev/null; then
        kill $MCP_PID
        echo "✅ MCP 服务器已停止"
    fi
    rm logs/mcp.pid
fi

echo "🎯 PowerAutomation 系统已停止"
EOF

    # 设置执行权限
    chmod +x start_powerautomation.sh
    chmod +x stop_powerautomation.sh
    
    echo "✅ 启动脚本生成完成"
}

# 主安装函数
main() {
    echo "🎯 PowerAutomation 安装程序"
    echo "================================"
    
    check_requirements
    create_directories
    install_python_dependencies "$1"
    install_node_dependencies
    setup_environment
    initialize_database
    verify_installation
    generate_startup_scripts
    
    echo ""
    echo "🎉 PowerAutomation 安装完成！"
    echo ""
    echo "📋 下一步操作："
    echo "1. 编辑 .env 文件，配置API密钥"
    echo "2. 运行 ./start_powerautomation.sh 启动系统"
    echo "3. 访问 http://localhost:8000 使用ClaudeEditor"
    echo ""
    echo "📚 更多信息请查看 README.md"
}

# 检查参数
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "PowerAutomation 安装脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --venv    创建Python虚拟环境"
    echo "  --help    显示帮助信息"
    echo ""
    exit 0
fi

# 运行主函数
main "$1"