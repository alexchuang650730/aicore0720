#!/bin/bash

# PowerAutomation 一鍵部署腳本
# 支持 macOS, Linux, Windows (WSL)
# 
# 使用方法：
# curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0718/main/deploy/one_click_install.sh | bash

set -e

# 定義變量
REPO_URL="https://github.com/alexchuang650730/aicore0718.git"
INSTALL_DIR="$HOME/powerautomation"
PYTHON_MIN_VERSION="3.8"
NODE_MIN_VERSION="16"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢測操作系統
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        log_error "不支持的操作系統: $OSTYPE"
        exit 1
    fi
    log_info "檢測到操作系統: $OS"
}

# 檢查依賴
check_dependencies() {
    log_info "檢查系統依賴..."
    
    # 檢查 Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ "$(printf '%s\n' "$PYTHON_MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" == "$PYTHON_MIN_VERSION" ]]; then
            log_success "Python $PYTHON_VERSION 可用"
        else
            log_error "Python 版本太舊，需要 $PYTHON_MIN_VERSION 或更高版本"
            install_python
        fi
    else
        log_error "Python 未安裝"
        install_python
    fi
    
    # 檢查 Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [[ $NODE_VERSION -ge $NODE_MIN_VERSION ]]; then
            log_success "Node.js v$NODE_VERSION 可用"
        else
            log_error "Node.js 版本太舊，需要 v$NODE_MIN_VERSION 或更高版本"
            install_nodejs
        fi
    else
        log_error "Node.js 未安裝"
        install_nodejs
    fi
    
    # 檢查 Git
    if ! command -v git &> /dev/null; then
        log_error "Git 未安裝"
        install_git
    else
        log_success "Git 可用"
    fi
}

# 安裝 Python
install_python() {
    log_info "安裝 Python..."
    case $OS in
        "macos")
            if command -v brew &> /dev/null; then
                brew install python@3.11
            else
                log_error "請先安裝 Homebrew 或手動安裝 Python 3.8+"
                exit 1
            fi
            ;;
        "linux")
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
            elif command -v yum &> /dev/null; then
                sudo yum install -y python3 python3-pip
            else
                log_error "請手動安裝 Python 3.8+"
                exit 1
            fi
            ;;
        "windows")
            log_error "請從 https://python.org 下載並安裝 Python 3.8+"
            exit 1
            ;;
    esac
}

# 安裝 Node.js
install_nodejs() {
    log_info "安裝 Node.js..."
    case $OS in
        "macos")
            if command -v brew &> /dev/null; then
                brew install node
            else
                log_error "請先安裝 Homebrew 或手動安裝 Node.js"
                exit 1
            fi
            ;;
        "linux")
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        "windows")
            log_error "請從 https://nodejs.org 下載並安裝 Node.js"
            exit 1
            ;;
    esac
}

# 安裝 Git
install_git() {
    log_info "安裝 Git..."
    case $OS in
        "macos")
            if command -v brew &> /dev/null; then
                brew install git
            else
                xcode-select --install
            fi
            ;;
        "linux")
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y git
            elif command -v yum &> /dev/null; then
                sudo yum install -y git
            fi
            ;;
        "windows")
            log_error "請從 https://git-scm.com 下載並安裝 Git"
            exit 1
            ;;
    esac
}

# 下載源代碼
download_source() {
    log_info "下載 PowerAutomation 源代碼..."
    
    # 如果目錄已存在，先備份
    if [[ -d "$INSTALL_DIR" ]]; then
        log_warn "目錄已存在，創建備份..."
        mv "$INSTALL_DIR" "$INSTALL_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    log_success "源代碼下載完成"
}

# 安裝依賴
install_dependencies() {
    log_info "安裝 Python 依賴..."
    
    # 創建虛擬環境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升級 pip
    pip install --upgrade pip
    
    # 安裝依賴
    pip install -r requirements.txt
    
    # 安裝額外依賴
    pip install gunicorn supervisor
    
    log_info "安裝 Node.js 依賴..."
    cd claudeditor
    npm install
    npm run build
    cd ..
    
    log_success "所有依賴安裝完成"
}

# 配置系統
configure_system() {
    log_info "配置系統..."
    
    # 創建配置文件
    cat > .env << EOF
# PowerAutomation 配置
HOST=0.0.0.0
PORT=8000
WEBSOCKET_PORT=8001
MCP_SERVER_PORT=8765
LOG_LEVEL=INFO
DEBUG=false

# API 密鑰 (請替換為您的實際密鑰)
CLAUDE_API_KEY=your_claude_api_key_here
KIMI_API_KEY=your_kimi_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 數據庫配置
DATABASE_URL=sqlite:///powerautomation.db
MEMORY_DATABASE_URL=sqlite:///memory.db

# 會員系統配置
JWT_SECRET=your_jwt_secret_here
MEMBER_DATABASE_URL=sqlite:///members.db
REDIS_URL=redis://localhost:6379/0

# 外部服務集成
CLAUDE_CODE_CN_API=https://api.claude-code.cn
AICODEWITH_API=https://api.aicodewith.com
EOF
    
    # 創建日誌目錄
    mkdir -p logs data uploads downloads temp
    
    # 初始化數據庫
    python3 -c "
import sqlite3
import os

# 創建主數據庫
conn = sqlite3.connect('powerautomation.db')
cursor = conn.cursor()

# 創建表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        user_id TEXT,
        status TEXT DEFAULT 'active',
        created_at REAL,
        updated_at REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS workflows (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        user_id TEXT,
        status TEXT DEFAULT 'pending',
        started_at REAL,
        completed_at REAL,
        result TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        id TEXT PRIMARY KEY,
        command TEXT NOT NULL,
        user_id TEXT,
        result TEXT,
        executed_at REAL
    )
''')

conn.commit()
conn.close()

# 創建會員數據庫
conn = sqlite3.connect('members.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        points INTEGER DEFAULT 0,
        membership_tier TEXT DEFAULT 'free',
        created_at REAL,
        last_login REAL,
        is_active BOOLEAN DEFAULT 1
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS point_transactions (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        points INTEGER,
        transaction_type TEXT,
        description TEXT,
        created_at REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        token TEXT UNIQUE,
        expires_at REAL,
        created_at REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

conn.commit()
conn.close()

print('✅ 數據庫初始化完成')
"
    
    log_success "系統配置完成"
}

# 創建系統服務
create_services() {
    log_info "創建系統服務..."
    
    # 創建 systemd 服務文件 (Linux)
    if [[ "$OS" == "linux" ]]; then
        sudo tee /etc/systemd/system/powerautomation.service > /dev/null <<EOF
[Unit]
Description=PowerAutomation Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python3 -m gunicorn --bind 0.0.0.0:8000 --workers 4 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable powerautomation
        log_success "Systemd 服務創建完成"
    fi
    
    # 創建 launchd 服務文件 (macOS)
    if [[ "$OS" == "macos" ]]; then
        mkdir -p ~/Library/LaunchAgents
        cat > ~/Library/LaunchAgents/com.powerautomation.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.powerautomation</string>
    <key>ProgramArguments</key>
    <array>
        <string>$INSTALL_DIR/venv/bin/python3</string>
        <string>-m</string>
        <string>gunicorn</string>
        <string>--bind</string>
        <string>0.0.0.0:8000</string>
        <string>--workers</string>
        <string>4</string>
        <string>app:app</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$INSTALL_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>$INSTALL_DIR/logs/error.log</string>
    <key>StandardOutPath</key>
    <string>$INSTALL_DIR/logs/output.log</string>
</dict>
</plist>
EOF
        
        launchctl load ~/Library/LaunchAgents/com.powerautomation.plist
        log_success "LaunchD 服務創建完成"
    fi
}

# 創建管理腳本
create_management_scripts() {
    log_info "創建管理腳本..."
    
    # 啟動腳本
    cat > start.sh <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "🚀 啟動 PowerAutomation..."

# 啟動 MCP 服務器
python3 mcp_server/main.py --port 8765 &
MCP_PID=$!
echo "✅ MCP 服務器啟動完成 (PID: $MCP_PID)"

# 啟動主應用
python3 -m gunicorn --bind 0.0.0.0:8000 --workers 4 app:app &
APP_PID=$!
echo "✅ 主應用啟動完成 (PID: $APP_PID)"

# 啟動前端 (如果需要)
if [[ -f "claudeditor/package.json" ]]; then
    cd claudeditor
    npm run serve &
    FRONTEND_PID=$!
    cd ..
    echo "✅ 前端服務啟動完成 (PID: $FRONTEND_PID)"
fi

echo "🎉 PowerAutomation 啟動完成!"
echo "🌐 訪問 http://localhost:8000"
echo "🛑 使用 ./stop.sh 停止服務"

# 保存 PID
echo "$MCP_PID" > mcp.pid
echo "$APP_PID" > app.pid
[[ -n "$FRONTEND_PID" ]] && echo "$FRONTEND_PID" > frontend.pid

wait
EOF
    
    # 停止腳本
    cat > stop.sh <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🛑 停止 PowerAutomation..."

# 停止服務
[[ -f mcp.pid ]] && kill $(cat mcp.pid) 2>/dev/null && rm mcp.pid
[[ -f app.pid ]] && kill $(cat app.pid) 2>/dev/null && rm app.pid
[[ -f frontend.pid ]] && kill $(cat frontend.pid) 2>/dev/null && rm frontend.pid

# 強制停止
pkill -f "powerautomation"
pkill -f "mcp_server"
pkill -f "gunicorn"

echo "✅ PowerAutomation 已停止"
EOF
    
    # 狀態檢查腳本
    cat > status.sh <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "📊 PowerAutomation 狀態檢查"
echo "========================="

# 檢查服務狀態
if [[ -f mcp.pid ]] && kill -0 $(cat mcp.pid) 2>/dev/null; then
    echo "✅ MCP 服務器: 運行中"
else
    echo "❌ MCP 服務器: 未運行"
fi

if [[ -f app.pid ]] && kill -0 $(cat app.pid) 2>/dev/null; then
    echo "✅ 主應用: 運行中"
else
    echo "❌ 主應用: 未運行"
fi

if [[ -f frontend.pid ]] && kill -0 $(cat frontend.pid) 2>/dev/null; then
    echo "✅ 前端服務: 運行中"
else
    echo "❌ 前端服務: 未運行"
fi

echo ""
echo "📱 訪問地址:"
echo "🌐 主服務: http://localhost:8000"
echo "🎯 ClaudeEditor: http://localhost:5173"
echo "🔌 MCP 服務: http://localhost:8765"
EOF
    
    # 更新腳本
    cat > update.sh <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🔄 更新 PowerAutomation..."

# 停止服務
./stop.sh

# 備份配置
cp .env .env.backup

# 更新代碼
git pull origin main

# 更新依賴
source venv/bin/activate
pip install -r requirements.txt

# 更新前端
cd claudeditor
npm install
npm run build
cd ..

# 恢復配置
cp .env.backup .env

echo "✅ PowerAutomation 更新完成"
echo "🚀 使用 ./start.sh 重新啟動服務"
EOF
    
    # 給腳本執行權限
    chmod +x start.sh stop.sh status.sh update.sh
    
    log_success "管理腳本創建完成"
}

# 主安裝函數
main() {
    echo "🎯 PowerAutomation 一鍵安裝腳本"
    echo "=============================="
    
    detect_os
    check_dependencies
    download_source
    install_dependencies
    configure_system
    create_services
    create_management_scripts
    
    log_success "🎉 PowerAutomation 安裝完成!"
    echo ""
    echo "📋 接下來的步驟:"
    echo "1. 編輯 $INSTALL_DIR/.env 文件，配置您的 API 密鑰"
    echo "2. 運行 cd $INSTALL_DIR && ./start.sh 啟動服務"
    echo "3. 訪問 http://localhost:8000 使用 PowerAutomation"
    echo ""
    echo "🔧 管理命令:"
    echo "啟動服務: ./start.sh"
    echo "停止服務: ./stop.sh"
    echo "檢查狀態: ./status.sh"
    echo "更新系統: ./update.sh"
    echo ""
    echo "📚 文檔: https://github.com/alexchuang650730/aicore0718"
    echo "🎯 PowerAutomation - 讓開發永不偏離目標!"
}

# 運行主函數
main "$@"