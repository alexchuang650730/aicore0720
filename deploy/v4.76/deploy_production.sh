#!/bin/bash
# PowerAuto.ai v4.76 生產環境一鍵部署腳本

set -e

# 顏色輸出
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

# 檢查必要工具
check_requirements() {
    log_info "檢查部署必要工具..."
    
    # 檢查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安裝，請先安裝Docker"
        exit 1
    fi
    
    # 檢查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安裝，請先安裝Docker Compose"
        exit 1
    fi
    
    # 檢查curl
    if ! command -v curl &> /dev/null; then
        log_error "curl未安裝，請先安裝curl"
        exit 1
    fi
    
    log_success "所有必要工具已安裝"
}

# 環境變量檢查
check_environment() {
    log_info "檢查環境變量..."
    
    # 必要環境變量列表
    required_vars=(
        "SECRET_KEY"
        "CLAUDE_API_KEY"
        "STRIPE_SECRET_KEY"
        "DB_PASSWORD"
        "REDIS_PASSWORD"
    )
    
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "缺少以下環境變量："
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        echo ""
        log_info "請設置環境變量後重新運行部署"
        echo "示例："
        echo "export SECRET_KEY=your-secret-key"
        echo "export CLAUDE_API_KEY=your-claude-api-key"
        echo "export STRIPE_SECRET_KEY=your-stripe-secret-key"
        echo "export DB_PASSWORD=your-db-password"
        echo "export REDIS_PASSWORD=your-redis-password"
        exit 1
    fi
    
    log_success "環境變量檢查通過"
}

# 創建部署目錄
setup_directories() {
    log_info "創建部署目錄..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p ssl
    
    log_success "部署目錄創建完成"
}

# 生成配置文件
generate_configs() {
    log_info "生成配置文件..."
    
    # 生成.env文件
    cat > .env << EOF
# PowerAuto.ai v4.76 生產環境配置
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production

# 數據庫配置
DATABASE_URL=postgresql://powerauto:${DB_PASSWORD}@powerauto-db:5432/powerauto
DB_USER=powerauto
DB_PASSWORD=${DB_PASSWORD}

# Redis配置
REDIS_URL=redis://:${REDIS_PASSWORD}@powerauto-redis:6379/0
REDIS_PASSWORD=${REDIS_PASSWORD}

# AI API配置
CLAUDE_API_KEY=${CLAUDE_API_KEY}
K2_API_KEY=${K2_API_KEY:-}
K2_API_ENDPOINT=${K2_API_ENDPOINT:-https://api.k2.ai}

# 支付配置
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY:-}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET:-}

# 安全配置
ALLOWED_HOSTS=powerauto.ai,www.powerauto.ai,localhost,127.0.0.1
CORS_ORIGINS=https://powerauto.ai,https://www.powerauto.ai

# 監控配置
LOG_LEVEL=INFO
SENTRY_DSN=${SENTRY_DSN:-}
EOF

    # 生成docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  powerauto-web:
    build:
      context: ../../
      dockerfile: deploy/v4.76/Dockerfile.production
    image: powerauto:v4.76
    container_name: powerauto-web
    restart: unless-stopped
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - powerauto-network
    depends_on:
      powerauto-db:
        condition: service_healthy
      powerauto-redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  powerauto-db:
    image: postgres:15
    container_name: powerauto-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=powerauto
      - POSTGRES_USER=powerauto
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - powerauto-db-data:/var/lib/postgresql/data
    networks:
      - powerauto-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U powerauto"]
      interval: 10s
      timeout: 5s
      retries: 5

  powerauto-redis:
    image: redis:7-alpine
    container_name: powerauto-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - powerauto-redis-data:/data
    networks:
      - powerauto-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  powerauto-nginx:
    image: nginx:alpine
    container_name: powerauto-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - powerauto-network
    depends_on:
      - powerauto-web

volumes:
  powerauto-db-data:
  powerauto-redis-data:

networks:
  powerauto-network:
    driver: bridge
EOF

    # 生成Dockerfile
    cat > Dockerfile.production << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 創建非root用戶
RUN groupadd -r powerauto && useradd -r -g powerauto powerauto

# 複製requirements.txt
COPY requirements.txt .

# 安裝Python依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY deploy/v4.76/website/ .
COPY core/ ./core/

# 設置權限
RUN chown -R powerauto:powerauto /app
USER powerauto

# 設置環境變量
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 暴露端口
EXPOSE 5000

# 啟動命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "backend.app:app"]
EOF

    # 生成nginx配置
    cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream powerauto_backend {
        server powerauto-web:5000;
    }

    server {
        listen 80;
        server_name powerauto.ai www.powerauto.ai localhost;
        
        # 重定向到HTTPS（生產環境）
        # return 301 https://$server_name$request_uri;
        
        # 開發環境直接代理
        location / {
            proxy_pass http://powerauto_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超時設置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # 靜態文件緩存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            proxy_pass http://powerauto_backend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # HTTPS配置（需要SSL證書）
    # server {
    #     listen 443 ssl http2;
    #     server_name powerauto.ai www.powerauto.ai;
    #     
    #     ssl_certificate /etc/nginx/ssl/powerauto.ai.crt;
    #     ssl_certificate_key /etc/nginx/ssl/powerauto.ai.key;
    #     
    #     location / {
    #         proxy_pass http://powerauto_backend;
    #         proxy_set_header Host $host;
    #         proxy_set_header X-Real-IP $remote_addr;
    #         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #         proxy_set_header X-Forwarded-Proto $scheme;
    #     }
    # }
}
EOF

    log_success "配置文件生成完成"
}

# 構建和啟動服務
deploy_services() {
    log_info "構建Docker鏡像..."
    docker-compose build --no-cache

    log_info "啟動PowerAuto.ai服務..."
    docker-compose up -d

    log_info "等待服務啟動..."
    sleep 30
}

# 健康檢查
health_check() {
    log_info "執行健康檢查..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:5000/health > /dev/null 2>&1; then
            log_success "健康檢查通過！"
            return 0
        fi
        
        log_warning "健康檢查失敗，重試中... ($attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    log_error "健康檢查失敗，請檢查日誌"
    docker-compose logs powerauto-web
    return 1
}

# 顯示部署信息
show_deployment_info() {
    log_success "🎉 PowerAuto.ai v4.76 部署完成！"
    echo ""
    echo "📍 訪問地址:"
    echo "   🌐 Web界面: http://localhost"
    echo "   🔧 API文檔: http://localhost/api"
    echo "   💻 ClaudeEditor: http://localhost/claudeditor"
    echo ""
    echo "📊 服務狀態:"
    docker-compose ps
    echo ""
    echo "📋 常用命令:"
    echo "   查看日誌: docker-compose logs -f"
    echo "   重啟服務: docker-compose restart"
    echo "   停止服務: docker-compose down"
    echo "   更新服務: docker-compose pull && docker-compose up -d"
    echo ""
    echo "🔧 管理員帳號 (首次登錄):"
    echo "   用戶名: admin"
    echo "   密碼: admin123"
    echo "   ⚠️  請立即修改默認密碼"
}

# 清理函數
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "部署失敗，正在清理..."
        docker-compose down 2>/dev/null || true
    fi
}

# 主執行函數
main() {
    log_info "🚀 開始PowerAuto.ai v4.76生產環境部署..."
    
    # 設置錯誤處理
    trap cleanup EXIT
    
    # 執行部署步驟
    check_requirements
    check_environment
    setup_directories
    generate_configs
    deploy_services
    
    if health_check; then
        show_deployment_info
        log_success "✅ 部署成功完成！"
    else
        log_error "❌ 部署失敗"
        exit 1
    fi
}

# 命令行參數處理
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "PowerAuto.ai v4.76 生產環境部署腳本"
        echo ""
        echo "使用方法:"
        echo "  ./deploy_production.sh          # 執行完整部署"
        echo "  ./deploy_production.sh status   # 檢查服務狀態"
        echo "  ./deploy_production.sh logs     # 查看日誌"
        echo "  ./deploy_production.sh stop     # 停止服務"
        echo "  ./deploy_production.sh restart  # 重啟服務"
        echo ""
        echo "環境變量:"
        echo "  SECRET_KEY           # 應用密鑰（必須）"
        echo "  CLAUDE_API_KEY       # Claude API密鑰（必須）"
        echo "  STRIPE_SECRET_KEY    # Stripe密鑰（必須）"
        echo "  DB_PASSWORD          # 數據庫密碼（必須）"
        echo "  REDIS_PASSWORD       # Redis密碼（必須）"
        echo "  K2_API_KEY          # K2 API密鑰（可選）"
        echo "  SENTRY_DSN          # Sentry監控（可選）"
        ;;
    "status")
        docker-compose ps
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "stop")
        log_info "停止PowerAuto.ai服務..."
        docker-compose down
        log_success "服務已停止"
        ;;
    "restart")
        log_info "重啟PowerAuto.ai服務..."
        docker-compose restart
        log_success "服務已重啟"
        ;;
    *)
        main
        ;;
esac