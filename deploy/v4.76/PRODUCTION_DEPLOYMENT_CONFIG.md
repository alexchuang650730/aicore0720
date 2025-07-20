# PowerAuto.ai 生產環境部署配置

## 🚀 部署概覽

PowerAuto.ai v4.76 生產環境部署支持Docker容器化、Kubernetes集群、以及雲端服務部署，確保高可用性、可擴展性和安全性。

---

## 🐳 Docker 生產部署

### Dockerfile 配置
```dockerfile
# deploy/v4.76/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# 複製Python依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY deploy/v4.76/website/ .
COPY core/ ./core/

# 設置環境變量
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 暴露端口
EXPOSE 5000

# 啟動命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "backend.app:app"]
```

### docker-compose.yml 生產配置
```yaml
# deploy/v4.76/docker-compose.prod.yml
version: '3.8'

services:
  powerauto-web:
    build:
      context: ../../
      dockerfile: deploy/v4.76/Dockerfile
    image: powerauto:v4.76
    container_name: powerauto-web
    restart: unless-stopped
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - K2_API_KEY=${K2_API_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
    volumes:
      - powerauto-data:/app/data
      - powerauto-logs:/app/logs
    networks:
      - powerauto-network
    depends_on:
      - powerauto-db
      - powerauto-redis

  powerauto-db:
    image: postgres:15
    container_name: powerauto-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=powerauto
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - powerauto-db-data:/var/lib/postgresql/data
    networks:
      - powerauto-network

  powerauto-redis:
    image: redis:7-alpine
    container_name: powerauto-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - powerauto-redis-data:/data
    networks:
      - powerauto-network

  powerauto-nginx:
    image: nginx:alpine
    container_name: powerauto-nginx
    restart: unless-stopped
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    networks:
      - powerauto-network
    depends_on:
      - powerauto-web

volumes:
  powerauto-data:
  powerauto-logs:
  powerauto-db-data:
  powerauto-redis-data:

networks:
  powerauto-network:
    driver: bridge
```

### 環境變量配置
```env
# deploy/v4.76/.env.production
# 應用配置
SECRET_KEY=your-super-secret-production-key
FLASK_ENV=production

# 數據庫配置
DATABASE_URL=postgresql://powerauto:password@powerauto-db:5432/powerauto
DB_USER=powerauto
DB_PASSWORD=your-secure-db-password

# Redis配置
REDIS_URL=redis://:your-redis-password@powerauto-redis:6379/0
REDIS_PASSWORD=your-redis-password

# AI API配置
CLAUDE_API_KEY=your-claude-api-key
K2_API_KEY=your-k2-api-key
K2_API_ENDPOINT=https://your-k2-endpoint.com

# 支付配置
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# 安全配置
ALLOWED_HOSTS=powerauto.ai,www.powerauto.ai
CORS_ORIGINS=https://powerauto.ai,https://www.powerauto.ai

# 監控配置
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

---

## ☸️ Kubernetes 部署

### 命名空間配置
```yaml
# deploy/v4.76/k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: powerauto
  labels:
    name: powerauto
    version: v4.76
```

### 配置映射
```yaml
# deploy/v4.76/k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: powerauto-config
  namespace: powerauto
data:
  FLASK_ENV: "production"
  DATABASE_URL: "postgresql://powerauto:password@postgres-service:5432/powerauto"
  REDIS_URL: "redis://:password@redis-service:6379/0"
  LOG_LEVEL: "INFO"
  ALLOWED_HOSTS: "powerauto.ai,www.powerauto.ai"
```

### 密鑰配置
```yaml
# deploy/v4.76/k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: powerauto-secrets
  namespace: powerauto
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  CLAUDE_API_KEY: <base64-encoded-claude-key>
  K2_API_KEY: <base64-encoded-k2-key>
  STRIPE_SECRET_KEY: <base64-encoded-stripe-key>
  DB_PASSWORD: <base64-encoded-db-password>
```

### 應用部署
```yaml
# deploy/v4.76/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: powerauto-web
  namespace: powerauto
  labels:
    app: powerauto
    version: v4.76
spec:
  replicas: 3
  selector:
    matchLabels:
      app: powerauto
  template:
    metadata:
      labels:
        app: powerauto
        version: v4.76
    spec:
      containers:
      - name: powerauto
        image: powerauto:v4.76
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: powerauto-config
        - secretRef:
            name: powerauto-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 服務配置
```yaml
# deploy/v4.76/k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: powerauto-service
  namespace: powerauto
spec:
  selector:
    app: powerauto
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: ClusterIP
```

### Ingress 配置
```yaml
# deploy/v4.76/k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: powerauto-ingress
  namespace: powerauto
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - powerauto.ai
    - www.powerauto.ai
    secretName: powerauto-tls
  rules:
  - host: powerauto.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: powerauto-service
            port:
              number: 80
  - host: www.powerauto.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: powerauto-service
            port:
              number: 80
```

---

## 🌐 雲端服務部署

### AWS 部署 (ECS + RDS + ElastiCache)
```yaml
# deploy/v4.76/aws/ecs-task-definition.json
{
  "family": "powerauto-v476",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "powerauto-web",
      "image": "your-ecr-repo/powerauto:v4.76",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:powerauto/secrets"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/powerauto",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### Google Cloud Platform 部署 (Cloud Run)
```yaml
# deploy/v4.76/gcp/service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: powerauto-v476
  namespace: default
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/memory: "2Gi"
        run.googleapis.com/cpu: "2"
    spec:
      containerConcurrency: 100
      timeoutSeconds: 300
      containers:
      - image: gcr.io/your-project/powerauto:v4.76
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: production
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: powerauto-secrets
              key: DATABASE_URL
        resources:
          limits:
            memory: "2Gi"
            cpu: "2"
```

---

## 🔧 部署腳本

### 自動化部署腳本
```bash
#!/bin/bash
# deploy/v4.76/scripts/deploy_production.sh

set -e

echo "🚀 開始PowerAuto.ai v4.76生產環境部署..."

# 檢查環境變量
if [ -z "$SECRET_KEY" ] || [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ 缺少必要的環境變量"
    exit 1
fi

# 構建Docker鏡像
echo "📦 構建Docker鏡像..."
docker build -t powerauto:v4.76 -f deploy/v4.76/Dockerfile .

# 推送到鏡像倉庫（如果使用）
if [ -n "$DOCKER_REGISTRY" ]; then
    echo "📤 推送到鏡像倉庫..."
    docker tag powerauto:v4.76 $DOCKER_REGISTRY/powerauto:v4.76
    docker push $DOCKER_REGISTRY/powerauto:v4.76
fi

# 部署方式選擇
case "$DEPLOYMENT_TYPE" in
    "docker-compose")
        echo "🐳 使用Docker Compose部署..."
        docker-compose -f deploy/v4.76/docker-compose.prod.yml up -d
        ;;
    "kubernetes")
        echo "☸️ 使用Kubernetes部署..."
        kubectl apply -f deploy/v4.76/k8s/
        ;;
    "aws")
        echo "☁️ 部署到AWS ECS..."
        aws ecs register-task-definition --cli-input-json file://deploy/v4.76/aws/ecs-task-definition.json
        aws ecs update-service --cluster powerauto --service powerauto-service --task-definition powerauto-v476
        ;;
    *)
        echo "❓ 未知的部署類型: $DEPLOYMENT_TYPE"
        exit 1
        ;;
esac

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 30

# 健康檢查
echo "🔍 執行健康檢查..."
if curl -f http://localhost/health; then
    echo "✅ 部署成功！"
else
    echo "❌ 健康檢查失敗"
    exit 1
fi

# 運行部署後測試
echo "🧪 運行部署後測試..."
python deploy/v4.76/tests/production_smoke_test.py

echo "🎉 PowerAuto.ai v4.76部署完成！"
echo "🌐 訪問: https://powerauto.ai"
```

### 資料庫遷移腳本
```python
# deploy/v4.76/scripts/migrate_database.py
#!/usr/bin/env python3
"""
數據庫遷移腳本
從開發環境遷移到生產環境
"""

import os
import sys
from sqlalchemy import create_engine
from flask import Flask
from backend.app import db, User, APIUsage, Payment

def migrate_database():
    """執行數據庫遷移"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        print("🔧 創建數據庫表...")
        db.create_all()
        
        # 創建預設管理員用戶
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("👨‍💼 創建管理員用戶...")
            admin = User(
                username='admin',
                email='admin@powerauto.ai',
                password_hash='$2b$12$hashed_password_here',
                role='admin',
                subscription='enterprise',
                api_calls_limit=100000
            )
            db.session.add(admin)
            db.session.commit()
        
        print("✅ 數據庫遷移完成")

if __name__ == '__main__':
    migrate_database()
```

---

## 🔒 安全配置

### SSL/TLS 配置
```nginx
# deploy/v4.76/nginx.conf
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
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # 安全標頭
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    location / {
        proxy_pass http://powerauto-web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 防火牆配置
```bash
# deploy/v4.76/scripts/setup_firewall.sh
#!/bin/bash

# 更新防火牆規則
echo "🔥 配置防火牆..."

# 允許SSH、HTTP、HTTPS
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp

# 拒絕其他入站連接
ufw --force enable

echo "✅ 防火牆配置完成"
```

---

## 📊 監控和日誌

### Prometheus 監控配置
```yaml
# deploy/v4.76/monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'powerauto'
    static_configs:
      - targets: ['powerauto-web:5000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### 日誌收集配置
```yaml
# deploy/v4.76/logging/fluentd.conf
<source>
  @type tail
  path /app/logs/*.log
  pos_file /app/logs/fluentd.log.pos
  tag powerauto.*
  <parse>
    @type json
  </parse>
</source>

<match powerauto.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name powerauto-logs
</match>
```

---

## 🚀 部署執行命令

### 快速部署
```bash
# 設置環境變量
export DEPLOYMENT_TYPE=docker-compose
export SECRET_KEY=your-production-secret
export CLAUDE_API_KEY=your-claude-key
export K2_API_KEY=your-k2-key

# 執行部署
bash deploy/v4.76/scripts/deploy_production.sh
```

### Kubernetes部署
```bash
# 創建命名空間
kubectl apply -f deploy/v4.76/k8s/namespace.yaml

# 部署配置和密鑰
kubectl apply -f deploy/v4.76/k8s/configmap.yaml
kubectl apply -f deploy/v4.76/k8s/secrets.yaml

# 部署應用
kubectl apply -f deploy/v4.76/k8s/

# 檢查狀態
kubectl get pods -n powerauto
kubectl get services -n powerauto
```

---

## 📞 技術支持

### 部署問題排除
- **健康檢查失敗**: 檢查環境變量和依賴服務
- **數據庫連接問題**: 驗證數據庫URL和認證信息
- **SSL證書問題**: 確認域名解析和證書有效性

### 聯繫方式
- **GitHub Issues**: https://github.com/alexchuang650730/aicore0720/issues
- **技術支持**: chuang.hsiaoyen@gmail.com
- **部署諮詢**: https://powerauto.ai/support

---

**PowerAuto.ai v4.76 生產環境部署配置**  
*最後更新: 2025-07-20*  
*🚀 高可用 | 可擴展 | 安全部署*