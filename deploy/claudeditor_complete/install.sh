#!/bin/bash
# PowerAutomation 一鍵安裝腳本
# 支援 curl+docker 部署 & 用戶狀態統計
# Website: powerauto.ai

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}"
    echo "██████╗  ██████╗ ██╗    ██╗███████╗██████╗  █████╗ ██╗   ██╗████████╗ ██████╗ "
    echo "██╔══██╗██╔═══██╗██║    ██║██╔════╝██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗"
    echo "██████╔╝██║   ██║██║ █╗ ██║█████╗  ██████╔╝███████║██║   ██║   ██║   ██║   ██║"
    echo "██╔═══╝ ██║   ██║██║███╗██║██╔══╝  ██╔══██╗██╔══██║██║   ██║   ██║   ██║   ██║"
    echo "██║     ╚██████╔╝╚███╔███╔╝███████╗██║  ██║██║  ██║╚██████╔╝   ██║   ╚██████╔╝"
    echo "╚═╝      ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ "
    echo ""
    echo "                    PowerAutomation v4.8.0 - AI工作流自動化平台"
    echo "                           https://powerauto.ai"
    echo -e "${NC}"
}

# 檢查系統環境
check_system() {
    print_info "檢查系統環境..."
    
    # 檢查操作系統
    OS=$(uname -s)
    if [[ "$OS" != "Linux" && "$OS" != "Darwin" ]]; then
        print_error "不支持的操作系統: $OS"
        exit 1
    fi
    
    # 檢查Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker未安裝，正在安裝Docker..."
        install_docker
    else
        print_success "Docker已安裝: $(docker --version)"
    fi
    
    # 檢查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose未安裝，正在安裝..."
        install_docker_compose
    else
        print_success "Docker Compose已安裝: $(docker-compose --version)"
    fi
    
    # 檢查curl
    if ! command -v curl &> /dev/null; then
        print_error "curl未安裝，請先安裝curl"
        exit 1
    fi
}

# 安裝Docker
install_docker() {
    if [[ "$OS" == "Linux" ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            usermod -aG docker $USER
        # CentOS/RHEL
        elif command -v yum &> /dev/null; then
            yum install -y docker
            systemctl start docker
            systemctl enable docker
            usermod -aG docker $USER
        fi
    elif [[ "$OS" == "Darwin" ]]; then
        print_warning "請手動安裝Docker Desktop for Mac: https://docs.docker.com/docker-for-mac/install/"
        exit 1
    fi
}

# 安裝Docker Compose
install_docker_compose() {
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
}

# 創建安裝目錄
create_directories() {
    print_info "創建安裝目錄..."
    
    INSTALL_DIR="$HOME/powerautomation"
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # 創建必要的目錄結構
    mkdir -p {data,logs,config,backups,ssl}
    
    print_success "安裝目錄創建完成: $INSTALL_DIR"
}

# 下載配置文件
download_configs() {
    print_info "下載PowerAutomation配置文件..."
    
    # 創建docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PowerAutomation 核心服務
  powerautomation-core:
    image: powerauto/core:latest
    container_name: powerautomation-core
    restart: unless-stopped
    ports:
      - "8080:8080"  # 主服務端口
      - "8081:8081"  # 會員系統端口
      - "8082:8082"  # WebSocket端口
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://powerauto:powerauto123@postgres:5432/powerautomation
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET:-powerauto-secret-key}
      - MOONSHOT_API_KEY=${MOONSHOT_API_KEY}
      - INFINIFLOW_API_KEY=${INFINIFLOW_API_KEY}
      - ALIPAY_APP_ID=${ALIPAY_APP_ID}
      - WECHAT_APP_ID=${WECHAT_APP_ID}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - postgres
      - redis
    networks:
      - powerautomation

  # ClaudeEditor Web界面
  claudeditor-web:
    image: powerauto/claudeditor:latest
    container_name: claudeditor-web
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8080
      - REACT_APP_WS_URL=ws://localhost:8082
    volumes:
      - ./config/claudeditor:/app/config
    networks:
      - powerautomation

  # PostgreSQL 數據庫
  postgres:
    image: postgres:15-alpine
    container_name: powerautomation-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=powerautomation
      - POSTGRES_USER=powerauto
      - POSTGRES_PASSWORD=powerauto123
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - powerautomation

  # Redis 緩存
  redis:
    image: redis:7-alpine
    container_name: powerautomation-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - powerautomation

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: powerautomation-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs
      - ./logs:/var/log/nginx
    depends_on:
      - powerautomation-core
      - claudeditor-web
    networks:
      - powerautomation

  # 用戶狀態統計服務
  user-analytics:
    image: powerauto/analytics:latest
    container_name: powerautomation-analytics
    restart: unless-stopped
    ports:
      - "8083:8083"
    environment:
      - DATABASE_URL=postgresql://powerauto:powerauto123@postgres:5432/powerautomation
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data/analytics:/app/data
      - ./logs/analytics:/app/logs
    depends_on:
      - postgres
      - redis
    networks:
      - powerautomation

volumes:
  postgres_data:
  redis_data:

networks:
  powerautomation:
    driver: bridge
EOF

    # 創建Nginx配置
    cat > config/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream powerautomation_backend {
        server powerautomation-core:8080;
    }
    
    upstream claudeditor_frontend {
        server claudeditor-web:3000;
    }
    
    upstream analytics_service {
        server user-analytics:8083;
    }

    server {
        listen 80;
        server_name powerauto.ai www.powerauto.ai;
        
        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name powerauto.ai www.powerauto.ai;
        
        # SSL配置
        ssl_certificate /etc/ssl/certs/powerauto.ai.crt;
        ssl_certificate_key /etc/ssl/certs/powerauto.ai.key;
        
        # 主頁 - ClaudeEditor
        location / {
            proxy_pass http://claudeditor_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # API路由
        location /api/ {
            proxy_pass http://powerautomation_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket支持
        location /ws {
            proxy_pass http://powerautomation_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
        
        # 用戶分析端點
        location /analytics/ {
            proxy_pass http://analytics_service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
EOF

    print_success "配置文件下載完成"
}

# 創建環境變量文件
create_env_file() {
    print_info "創建環境配置文件..."
    
    cat > .env << 'EOF'
# PowerAutomation 環境配置
JWT_SECRET=powerauto-jwt-secret-$(openssl rand -base64 32)

# K2 AI Provider API Keys
MOONSHOT_API_KEY=your-moonshot-api-key
INFINIFLOW_API_KEY=your-infiniflow-api-key

# 支付配置
ALIPAY_APP_ID=your-alipay-app-id
WECHAT_APP_ID=your-wechat-app-id  
STRIPE_SECRET_KEY=your-stripe-secret-key

# 數據庫配置
POSTGRES_PASSWORD=powerauto123
POSTGRES_USER=powerauto
POSTGRES_DB=powerautomation

# 域名配置
DOMAIN_NAME=powerauto.ai
EOF

    print_warning "請編輯 .env 文件，配置您的API密鑰和支付信息"
}

# 創建用戶狀態統計腳本
create_user_analytics() {
    print_info "創建用戶狀態統計系統..."
    
    mkdir -p scripts
    
    cat > scripts/user_analytics.py << 'EOF'
#!/usr/bin/env python3
"""
PowerAutomation 用戶狀態統計系統
實時監控用戶上線狀態、使用情況和系統性能
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserAnalyticsSystem:
    """用戶狀態統計系統"""
    
    def __init__(self):
        self.db_pool = None
        self.redis = None
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions = {}
        
    async def initialize(self):
        """初始化統計系統"""
        try:
            # 連接PostgreSQL
            self.db_pool = await asyncpg.create_pool(
                "postgresql://powerauto:powerauto123@postgres:5432/powerautomation",
                min_size=5,
                max_size=20
            )
            
            # 連接Redis
            self.redis = redis.from_url("redis://redis:6379")
            
            # 創建統計表
            await self._create_analytics_tables()
            
            logger.info("✅ 用戶分析系統初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 用戶分析系統初始化失敗: {e}")
            raise
    
    async def _create_analytics_tables(self):
        """創建分析統計表"""
        async with self.db_pool.acquire() as conn:
            # 用戶在線狀態表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_online_status (
                    user_id TEXT PRIMARY KEY,
                    is_online BOOLEAN DEFAULT FALSE,
                    last_seen TIMESTAMP DEFAULT NOW(),
                    session_start TIMESTAMP DEFAULT NOW(),
                    ip_address TEXT,
                    user_agent TEXT,
                    platform TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # 用戶活動記錄表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_activity_logs (
                    log_id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,  -- login, logout, api_call, chat, etc.
                    details JSONB,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # 系統統計表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    stat_id SERIAL PRIMARY KEY,
                    date DATE DEFAULT CURRENT_DATE,
                    total_users INTEGER DEFAULT 0,
                    active_users INTEGER DEFAULT 0,
                    new_registrations INTEGER DEFAULT 0,
                    total_api_calls INTEGER DEFAULT 0,
                    total_revenue DECIMAL(10,2) DEFAULT 0,
                    avg_session_duration INTERVAL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # 實時統計視圖
            await conn.execute('''
                CREATE OR REPLACE VIEW realtime_stats AS
                SELECT 
                    COUNT(*) FILTER (WHERE is_online = TRUE) as online_users,
                    COUNT(*) as total_registered_users,
                    AVG(EXTRACT(EPOCH FROM (last_seen - session_start))) as avg_session_duration_seconds,
                    COUNT(*) FILTER (WHERE last_seen > NOW() - INTERVAL '1 hour') as active_last_hour,
                    COUNT(*) FILTER (WHERE created_at > CURRENT_DATE) as new_today
                FROM user_online_status
            ''')
    
    async def track_user_online(self, user_id: str, ip_address: str = None, user_agent: str = None):
        """追蹤用戶上線"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO user_online_status 
                    (user_id, is_online, session_start, ip_address, user_agent, updated_at)
                    VALUES ($1, TRUE, NOW(), $2, $3, NOW())
                    ON CONFLICT (user_id) 
                    DO UPDATE SET 
                        is_online = TRUE,
                        session_start = NOW(),
                        ip_address = $2,
                        user_agent = $3,
                        updated_at = NOW()
                ''', user_id, ip_address, user_agent)
                
                # 記錄活動日誌
                await self._log_user_activity(user_id, "login", {"ip": ip_address})
                
                # 更新Redis緩存
                await self.redis.hset("online_users", user_id, json.dumps({
                    "timestamp": time.time(),
                    "ip": ip_address
                }))
                
                logger.info(f"👤 用戶上線: {user_id}")
                
        except Exception as e:
            logger.error(f"❌ 追蹤用戶上線失敗: {e}")
    
    async def track_user_offline(self, user_id: str):
        """追蹤用戶下線"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute('''
                    UPDATE user_online_status 
                    SET is_online = FALSE, last_seen = NOW(), updated_at = NOW()
                    WHERE user_id = $1
                ''', user_id)
                
                # 記錄活動日誌
                await self._log_user_activity(user_id, "logout")
                
                # 從Redis緩存移除
                await self.redis.hdel("online_users", user_id)
                
                logger.info(f"👤 用戶下線: {user_id}")
                
        except Exception as e:
            logger.error(f"❌ 追蹤用戶下線失敗: {e}")
    
    async def _log_user_activity(self, user_id: str, activity_type: str, details: Dict = None):
        """記錄用戶活動"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO user_activity_logs (user_id, activity_type, details)
                    VALUES ($1, $2, $3)
                ''', user_id, activity_type, json.dumps(details) if details else None)
                
        except Exception as e:
            logger.error(f"❌ 記錄用戶活動失敗: {e}")
    
    async def get_realtime_stats(self) -> Dict[str, Any]:
        """獲取實時統計數據"""
        try:
            async with self.db_pool.acquire() as conn:
                # 基本統計
                stats = await conn.fetchrow('SELECT * FROM realtime_stats')
                
                # Redis中的實時數據
                online_users_data = await self.redis.hgetall("online_users")
                current_online = len(online_users_data)
                
                # 今日新註冊用戶
                today_registrations = await conn.fetchval('''
                    SELECT COUNT(*) FROM users 
                    WHERE created_at::date = CURRENT_DATE
                ''')
                
                # 今日API調用量
                today_api_calls = await conn.fetchval('''
                    SELECT COUNT(*) FROM user_activity_logs 
                    WHERE activity_type = 'api_call' 
                    AND created_at::date = CURRENT_DATE
                ''')
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "online_users": current_online,
                    "total_users": stats["total_registered_users"] or 0,
                    "active_last_hour": stats["active_last_hour"] or 0,
                    "new_today": today_registrations or 0,
                    "api_calls_today": today_api_calls or 0,
                    "avg_session_duration": stats["avg_session_duration_seconds"] or 0,
                    "server_status": "healthy"
                }
                
        except Exception as e:
            logger.error(f"❌ 獲取實時統計失敗: {e}")
            return {"error": str(e)}
    
    async def get_user_analytics_dashboard(self) -> Dict[str, Any]:
        """獲取用戶分析儀表板數據"""
        try:
            async with self.db_pool.acquire() as conn:
                # 7天用戶活躍度
                weekly_activity = await conn.fetch('''
                    SELECT 
                        date_trunc('day', created_at) as date,
                        COUNT(DISTINCT user_id) as active_users
                    FROM user_activity_logs 
                    WHERE created_at > NOW() - INTERVAL '7 days'
                    GROUP BY date_trunc('day', created_at)
                    ORDER BY date
                ''')
                
                # 用戶註冊趨勢
                registration_trend = await conn.fetch('''
                    SELECT 
                        date_trunc('day', created_at) as date,
                        COUNT(*) as registrations
                    FROM users 
                    WHERE created_at > NOW() - INTERVAL '30 days'
                    GROUP BY date_trunc('day', created_at)
                    ORDER BY date
                ''')
                
                # 熱門功能使用
                feature_usage = await conn.fetch('''
                    SELECT 
                        activity_type,
                        COUNT(*) as usage_count
                    FROM user_activity_logs 
                    WHERE created_at > NOW() - INTERVAL '7 days'
                    GROUP BY activity_type
                    ORDER BY usage_count DESC
                    LIMIT 10
                ''')
                
                return {
                    "weekly_activity": [dict(row) for row in weekly_activity],
                    "registration_trend": [dict(row) for row in registration_trend],
                    "feature_usage": [dict(row) for row in feature_usage]
                }
                
        except Exception as e:
            logger.error(f"❌ 獲取分析儀表板數據失敗: {e}")
            return {"error": str(e)}

# FastAPI應用
def create_analytics_app():
    app = FastAPI(title="PowerAutomation 用戶分析系統")
    analytics = UserAnalyticsSystem()
    
    @app.on_event("startup")
    async def startup():
        await analytics.initialize()
    
    @app.get("/analytics/realtime")
    async def get_realtime_stats():
        return await analytics.get_realtime_stats()
    
    @app.get("/analytics/dashboard")
    async def get_dashboard():
        return await analytics.get_user_analytics_dashboard()
    
    @app.post("/analytics/track/online/{user_id}")
    async def track_online(user_id: str, ip: str = None):
        await analytics.track_user_online(user_id, ip)
        return {"status": "tracked"}
    
    @app.post("/analytics/track/offline/{user_id}")
    async def track_offline(user_id: str):
        await analytics.track_user_offline(user_id)
        return {"status": "tracked"}
    
    return app

if __name__ == "__main__":
    app = create_analytics_app()
    uvicorn.run(app, host="0.0.0.0", port=8083)
EOF

    chmod +x scripts/user_analytics.py
    print_success "用戶狀態統計系統創建完成"
}

# 啟動服務
start_services() {
    print_info "啟動PowerAutomation服務..."
    
    # 拉取最新鏡像
    print_info "拉取Docker鏡像..."
    docker-compose pull
    
    # 啟動服務
    print_info "啟動所有服務..."
    docker-compose up -d
    
    # 等待服務啟動
    print_info "等待服務啟動..."
    sleep 10
    
    # 檢查服務狀態
    if docker-compose ps | grep -q "Up"; then
        print_success "PowerAutomation服務啟動成功！"
    else
        print_error "服務啟動失敗，請檢查日誌"
        docker-compose logs
        exit 1
    fi
}

# 顯示訪問信息
show_access_info() {
    print_success "🎉 PowerAutomation安裝完成！"
    echo ""
    echo -e "${CYAN}訪問信息:${NC}"
    echo -e "  🌐 ClaudeEditor Web界面: ${GREEN}http://localhost:3000${NC}"
    echo -e "  🔧 API服務端點: ${GREEN}http://localhost:8080${NC}"
    echo -e "  👥 會員系統: ${GREEN}http://localhost:8081${NC}"
    echo -e "  📊 用戶分析儀表板: ${GREEN}http://localhost:8083/analytics/dashboard${NC}"
    echo ""
    echo -e "${CYAN}管理命令:${NC}"
    echo -e "  查看服務狀態: ${YELLOW}docker-compose ps${NC}"
    echo -e "  查看日誌: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  停止服務: ${YELLOW}docker-compose down${NC}"
    echo -e "  重啟服務: ${YELLOW}docker-compose restart${NC}"
    echo ""
    echo -e "${CYAN}配置提醒:${NC}"
    echo -e "  1. 請編輯 ${YELLOW}.env${NC} 文件配置API密鑰"
    echo -e "  2. 如需HTTPS，請將SSL證書放到 ${YELLOW}ssl/${NC} 目錄"
    echo -e "  3. 數據備份位於 ${YELLOW}backups/${NC} 目錄"
    echo ""
    echo -e "${GREEN}享受使用PowerAutomation！🚀${NC}"
}

# 主函數
main() {
    print_header
    
    # 檢查是否為root用戶
    if [[ $EUID -eq 0 ]]; then
        print_warning "建議不要使用root用戶運行此腳本"
    fi
    
    check_system
    create_directories
    download_configs
    create_env_file
    create_user_analytics
    start_services
    show_access_info
}

# 運行主函數
main "$@"