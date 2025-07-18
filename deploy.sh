#!/bin/bash

# PowerAutomation 一鍵部署到 EC2
# 生產環境部署腳本

set -e

echo "🚀 PowerAutomation 生產環境部署開始..."
echo "=========================================="

# 配置變數
EC2_HOST="ec2-13-222-125-83.compute-1.amazonaws.com"
EC2_USER="ec2-user"
DOMAIN="powerauto.ai"
PROJECT_DIR="/home/ec2-user/powerautomation"

# 檢查必要文件
if [[ ! -f ".env.production" ]]; then
    echo "❌ 缺少 .env.production 文件"
    exit 1
fi

if [[ ! -f "alexchuang.pem" ]]; then
    echo "❌ 缺少 SSH 密鑰文件"
    exit 1
fi

echo "✅ 預檢查通過"

# 設置 SSH 密鑰權限
chmod 600 alexchuang.pem

# 創建部署包
echo "📦 創建部署包..."
tar -czf powerautomation-deploy.tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='logs' \
    --exclude='data' \
    .

echo "✅ 部署包創建完成"

# 上傳到服務器
echo "⬆️ 上傳代碼到服務器..."
scp -i alexchuang.pem powerautomation-deploy.tar.gz ${EC2_USER}@${EC2_HOST}:/tmp/

# 第一步：準備服務器環境
echo "🔧 步驟1: 準備服務器環境..."
ssh -i alexchuang.pem ${EC2_USER}@${EC2_HOST} << 'EOF'
    # 安裝 Docker (如果未安裝)
    if ! command -v docker &> /dev/null; then
        echo "🐳 安裝 Docker..."
        sudo yum update -y
        sudo yum install docker -y
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -a -G docker ec2-user
    fi
    
    # 安裝 Docker Compose (如果未安裝)
    if ! command -v docker-compose &> /dev/null; then
        echo "🐙 安裝 Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    # 停止現有服務
    echo "⏹️ 停止現有服務..."
    cd /home/ec2-user/powerautomation 2>/dev/null && docker-compose -f docker-compose.production.yml down || true
    
    echo "✅ 服務器環境準備完成"
EOF

# 第二步：創建項目目錄和解壓代碼
echo "📂 步驟2: 部署代碼..."
ssh -i alexchuang.pem ${EC2_USER}@${EC2_HOST} << 'EOF'
    # 創建項目目錄
    sudo mkdir -p /home/ec2-user/powerautomation
    cd /home/ec2-user/powerautomation
    
    # 備份現有配置(如果存在)
    if [[ -f ".env" ]]; then
        cp .env .env.backup.$(date +%Y%m%d-%H%M%S)
    fi
    
    # 解壓新代碼
    echo "📂 解壓新代碼..."
    tar -xzf /tmp/powerautomation-deploy.tar.gz
    
    # 創建必要目錄
    mkdir -p data logs nginx/ssl nginx/logs uploads temp exports
    
    # 設置權限
    sudo chown -R ec2-user:ec2-user /home/ec2-user/powerautomation
    
    echo "✅ 代碼部署完成"
EOF

# 第三步：上傳配置文件
echo "🔐 步驟3: 上傳配置文件..."

# 上傳環境配置
echo "🔧 上傳生產環境配置..."
scp -i alexchuang.pem .env.production ${EC2_USER}@${EC2_HOST}:${PROJECT_DIR}/.env

# 創建 Nginx 配置
echo "🌐 創建 Nginx 配置..."
cat > nginx.conf << 'NGINX_EOF'
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server powerautomation-frontend:3000;
    }
    
    upstream membership_api {
        server membership-api:8082;
    }
    
    upstream core_api {
        server powerautomation-core:8080;
    }
    
    server {
        listen 80;
        server_name powerauto.ai www.powerauto.ai;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name powerauto.ai www.powerauto.ai;
        
        ssl_certificate /etc/nginx/ssl/powerauto.ai.crt;
        ssl_certificate_key /etc/nginx/ssl/powerauto.ai.key;
        
        # 主頁面
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # 會員 API
        location /api/ {
            proxy_pass http://membership_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Core API
        location /core/ {
            proxy_pass http://core_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket 支持
        location /ws/ {
            proxy_pass http://core_api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
NGINX_EOF

echo "🌐 上傳 Nginx 配置..."
scp -i alexchuang.pem nginx.conf ${EC2_USER}@${EC2_HOST}:${PROJECT_DIR}/nginx/
echo "✅ 配置文件上傳完成"

# 第四步：構建和啟動服務
echo "🚀 步驟4: 構建和啟動 PowerAutomation 服務..."
ssh -i alexchuang.pem ${EC2_USER}@${EC2_HOST} << 'EOF'
    cd /home/ec2-user/powerautomation
    
    # 確保 .env 文件存在
    if [[ ! -f ".env" ]]; then
        echo "❌ .env 文件不存在，部署終止"
        exit 1
    fi
    
    # 拉取最新基礎鏡像
    echo "⬇️ 拉取基礎鏡像..."
    docker pull node:18-alpine
    docker pull python:3.9-slim
    docker pull nginx:alpine
    
    # 構建並啟動服務
    echo "🔨 構建服務鏡像..."
    docker-compose -f docker-compose.production.yml build --no-cache
    
    echo "🚀 啟動所有服務..."
    docker-compose -f docker-compose.production.yml up -d
    
    echo "✅ 服務啟動命令執行完成"
EOF

# 第五步：健康檢查和驗證
echo "🔍 步驟5: 服務健康檢查..."

# 等待服務啟動
echo "⏳ 等待服務啟動 (60秒)..."
sleep 60

# 連接服務器檢查狀態
ssh -i alexchuang.pem ${EC2_USER}@${EC2_HOST} << 'EOF'
    cd /home/ec2-user/powerautomation
    
    echo "📊 檢查容器狀態..."
    docker-compose -f docker-compose.production.yml ps
    
    echo "📝 檢查服務日志..."
    echo "=== Frontend 日志 ==="
    docker-compose -f docker-compose.production.yml logs --tail=10 powerautomation-frontend
    
    echo "=== Membership API 日志 ==="
    docker-compose -f docker-compose.production.yml logs --tail=10 membership-api
    
    echo "=== Core API 日志 ==="
    docker-compose -f docker-compose.production.yml logs --tail=10 powerautomation-core
    
    echo "=== Nginx 日志 ==="
    docker-compose -f docker-compose.production.yml logs --tail=10 nginx
    
    # 測試內部連接
    echo "🔗 測試內部服務連接..."
    docker exec powerauto-membership curl -f http://localhost:8082/api/health || echo "❌ Membership API 不健康"
    docker exec powerauto-core curl -f http://localhost:8080/health || echo "❌ Core API 不健康"
EOF

# 清理本地文件
rm -f powerautomation-deploy.tar.gz nginx.conf

echo ""
echo "🎉 PowerAutomation 部署完成！"
echo "=========================================="
echo "🌐 網站地址: https://powerauto.ai"
echo "📊 系統狀態: https://powerauto.ai/api/health"
echo "🔧 管理面板: https://powerauto.ai/admin"
echo ""
echo "📝 下一步："
echo "1. 檢查網站是否正常運行"
echo "2. 測試會員註冊和登錄功能"
echo "3. 驗證 K2 模型路由功能"
echo "4. 監控服務器狀態"
echo ""
echo "👨‍💻 技術支持: Alex Chuang"
echo "📅 部署時間: $(date)"