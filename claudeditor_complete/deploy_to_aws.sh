#!/bin/bash
# PowerAutomation + ClaudeEditor AWS EC2部署腳本
# 一鍵部署到Amazon EC2服務器

set -e

# 配置變數
EC2_HOST="ec2-44-206-225-192.compute-1.amazonaws.com"
EC2_USER="ubuntu"
SSH_KEY="alexchuang.pem"
DEPLOY_DIR="/opt/powerautomation"
SERVICE_NAME="powerautomation"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
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

# 檢查SSH密鑰
check_ssh_key() {
    if [ ! -f "$SSH_KEY" ]; then
        log_error "SSH密鑰文件不存在: $SSH_KEY"
        log_info "請確保SSH密鑰文件在當前目錄下"
        exit 1
    fi
    
    chmod 600 "$SSH_KEY"
    log_success "SSH密鑰檢查通過"
}

# 測試連接
test_connection() {
    log_info "測試EC2連接..."
    
    if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "echo 'Connection successful'"; then
        log_success "EC2連接測試成功"
    else
        log_error "無法連接到EC2實例"
        log_info "請檢查:"
        log_info "1. SSH密鑰是否正確"
        log_info "2. EC2實例是否運行"
        log_info "3. 安全組是否允許SSH(22)端口"
        exit 1
    fi
}

# 準備部署文件
prepare_deployment() {
    log_info "準備部署文件..."
    
    # 創建臨時部署目錄
    TEMP_DIR=$(mktemp -d)
    cp -r . "$TEMP_DIR/powerautomation"
    
    # 創建部署配置文件
    cat > "$TEMP_DIR/powerautomation/deploy_config.json" << EOF
{
    "version": "4.8.0",
    "deployment_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "environment": "production",
    "services": {
        "web_server": {
            "port": 8080,
            "ssl": false
        },
        "websocket_server": {
            "port": 8765,
            "ssl": false
        },
        "member_api": {
            "port": 8081,
            "ssl": false
        }
    },
    "features": {
        "six_workflows": true,
        "dual_ai_mode": true,
        "memory_rag": true,
        "member_system": true,
        "cost_optimization": true
    }
}
EOF
    
    # 創建systemd服務文件
    cat > "$TEMP_DIR/powerautomation.service" << EOF
[Unit]
Description=PowerAutomation ClaudeEditor System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/bin/python3 start_powerautomation_driven.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=$DEPLOY_DIR

[Install]
WantedBy=multi-user.target
EOF

    # 創建nginx配置
    cat > "$TEMP_DIR/nginx_powerautomation.conf" << EOF
server {
    listen 80;
    server_name $EC2_HOST powerauto.ai www.powerauto.ai;
    
    # ClaudeEditor Web界面
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # PowerAutomation WebSocket
    location /powerautomation/driver {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 會員系統API
    location /api/ {
        proxy_pass http://localhost:8081;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 靜態文件緩存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    DEPLOYMENT_PACKAGE="$TEMP_DIR"
    log_success "部署文件準備完成"
}

# 安裝系統依賴
install_system_dependencies() {
    log_info "安裝系統依賴..."
    
    ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
        set -e
        
        # 更新包列表
        sudo apt update
        
        # 安裝基本依賴
        sudo apt install -y python3 python3-pip python3-venv nginx git curl wget
        
        # 安裝Node.js (用於某些工具)
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt install -y nodejs
        
        # 安裝系統監控工具
        sudo apt install -y htop tmux unzip
        
        echo "✅ 系統依賴安裝完成"
EOF
    
    log_success "系統依賴安裝完成"
}

# 部署應用代碼
deploy_application() {
    log_info "部署應用代碼..."
    
    # 創建部署目錄
    ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" "sudo mkdir -p $DEPLOY_DIR && sudo chown $EC2_USER:$EC2_USER $DEPLOY_DIR"
    
    # 上傳代碼
    scp -i "$SSH_KEY" -r "$DEPLOYMENT_PACKAGE/powerautomation/"* "$EC2_USER@$EC2_HOST:$DEPLOY_DIR/"
    
    # 安裝Python依賴
    ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << EOF
        set -e
        cd $DEPLOY_DIR
        
        # 創建虛擬環境
        python3 -m venv venv
        source venv/bin/activate
        
        # 升級pip
        pip install --upgrade pip
        
        # 安裝核心依賴
        pip install fastapi uvicorn websockets asyncio
        pip install bcrypt PyJWT pydantic[email]
        pip install sqlite3 numpy pandas
        pip install aiohttp aiofiles
        
        # 創建必要目錄
        mkdir -p logs data backups
        
        # 設置權限
        chmod +x start_powerautomation_driven.py
        chmod +x powerautomation_websocket_server.py
        chmod +x member_system.py
        
        echo "✅ 應用代碼部署完成"
EOF
    
    log_success "應用代碼部署完成"
}

# 配置系統服務
configure_services() {
    log_info "配置系統服務..."
    
    # 上傳服務文件
    scp -i "$SSH_KEY" "$DEPLOYMENT_PACKAGE/powerautomation.service" "$EC2_USER@$EC2_HOST:/tmp/"
    
    # 配置systemd服務
    ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << EOF
        set -e
        
        # 安裝systemd服務
        sudo cp /tmp/powerautomation.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        
        echo "✅ systemd服務配置完成"
EOF
    
    log_success "系統服務配置完成"
}

# 配置Nginx
configure_nginx() {
    log_info "配置Nginx..."
    
    # 上傳nginx配置
    scp -i "$SSH_KEY" "$DEPLOYMENT_PACKAGE/nginx_powerautomation.conf" "$EC2_USER@$EC2_HOST:/tmp/"
    
    ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << EOF
        set -e
        
        # 備份默認配置
        sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
        
        # 安裝新配置
        sudo cp /tmp/nginx_powerautomation.conf /etc/nginx/sites-available/powerautomation
        sudo ln -sf /etc/nginx/sites-available/powerautomation /etc/nginx/sites-enabled/
        
        # 移除默認站點
        sudo rm -f /etc/nginx/sites-enabled/default
        
        # 測試nginx配置
        sudo nginx -t
        
        echo "✅ Nginx配置完成"
EOF
    
    log_success "Nginx配置完成"
}

# 配置防火牆
configure_firewall() {
    log_info "配置防火牆..."
    
    ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
        set -e
        
        # 啟用ufw
        sudo ufw --force enable
        
        # 允許SSH
        sudo ufw allow ssh
        
        # 允許HTTP和HTTPS
        sudo ufw allow 80
        sudo ufw allow 443
        
        # 允許應用端口（僅本地訪問）
        sudo ufw allow from 127.0.0.1 to any port 8080
        sudo ufw allow from 127.0.0.1 to any port 8765
        sudo ufw allow from 127.0.0.1 to any port 8081
        
        # 顯示防火牆狀態
        sudo ufw status
        
        echo "✅ 防火牆配置完成"
EOF
    
    log_success "防火牆配置完成"
}

# 啟動服務
start_services() {
    log_info "啟動服務..."
    
    ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << EOF
        set -e
        
        # 啟動PowerAutomation服務
        sudo systemctl start $SERVICE_NAME
        
        # 重啟nginx
        sudo systemctl restart nginx
        
        # 檢查服務狀態
        sleep 5
        sudo systemctl status $SERVICE_NAME --no-pager
        sudo systemctl status nginx --no-pager
        
        echo "✅ 服務啟動完成"
EOF
    
    log_success "服務啟動完成"
}

# 驗證部署
verify_deployment() {
    log_info "驗證部署..."
    
    # 檢查服務端口
    ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
        echo "🔍 檢查服務端口..."
        netstat -tlnp | grep -E ':(80|8080|8765|8081)'
        
        echo "🔍 檢查進程..."
        ps aux | grep -E '(nginx|python.*powerautomation)'
        
        echo "🔍 檢查日誌..."
        sudo journalctl -u powerautomation --no-pager -n 10
EOF
    
    # 測試HTTP訪問
    log_info "測試HTTP訪問..."
    if curl -s -o /dev/null -w "%{http_code}" "http://$EC2_HOST" | grep -q "200"; then
        log_success "HTTP訪問測試成功"
    else
        log_warning "HTTP訪問測試失敗，請檢查服務狀態"
    fi
    
    log_success "部署驗證完成"
}

# 清理臨時文件
cleanup() {
    if [ -n "$DEPLOYMENT_PACKAGE" ] && [ -d "$DEPLOYMENT_PACKAGE" ]; then
        rm -rf "$DEPLOYMENT_PACKAGE"
        log_info "臨時文件已清理"
    fi
}

# 顯示部署信息
show_deployment_info() {
    log_success "🎉 PowerAutomation + ClaudeEditor 部署完成！"
    echo ""
    echo "📍 部署信息:"
    echo "   🌐 Web界面: http://$EC2_HOST"
    echo "   🔌 WebSocket: ws://$EC2_HOST/powerautomation/driver"
    echo "   🔧 API接口: http://$EC2_HOST/api/"
    echo "   📁 部署目錄: $DEPLOY_DIR"
    echo ""
    echo "🎯 功能特性:"
    echo "   ✅ PowerAutomation Core驅動ClaudeEditor"
    echo "   ✅ 六大工作流完整集成"
    echo "   ✅ Claude + K2雙AI模式"
    echo "   ✅ Memory RAG智能記憶"
    echo "   ✅ 會員積分系統"
    echo "   ✅ 2元→8元成本優化"
    echo ""
    echo "🔧 管理命令:"
    echo "   重啟服務: sudo systemctl restart $SERVICE_NAME"
    echo "   查看日誌: sudo journalctl -u $SERVICE_NAME -f"
    echo "   查看狀態: sudo systemctl status $SERVICE_NAME"
    echo ""
    echo "🔐 默認管理員賬號:"
    echo "   用戶名: admin@powerauto.ai"
    echo "   密碼: admin123"
    echo ""
    log_warning "請及時更改默認密碼並配置SSL證書！"
}

# 主執行流程
main() {
    echo "🚀 PowerAutomation + ClaudeEditor AWS EC2 部署腳本"
    echo "🎯 目標服務器: $EC2_USER@$EC2_HOST"
    echo "📁 部署目錄: $DEPLOY_DIR"
    echo "=" * 60
    
    # 設置錯誤處理
    trap cleanup EXIT
    
    # 執行部署步驟
    check_ssh_key
    test_connection
    prepare_deployment
    install_system_dependencies
    deploy_application
    configure_services
    configure_nginx
    configure_firewall
    start_services
    verify_deployment
    show_deployment_info
}

# 執行主函數
main "$@"