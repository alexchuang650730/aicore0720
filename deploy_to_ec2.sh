#!/bin/bash

# PowerAuto.ai EC2 完整部署腳本
echo "🚀 PowerAuto.ai EC2 自動化部署"
echo "=============================="

# 配置變量
EC2_HOST="ec2-13-222-125-83.compute-1.amazonaws.com"
EC2_USER="ec2-user"
KEY_PATH="/Users/alexchuang/alexchuang.pem"
LOCAL_APP_DIR="/Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.76/website/backend"
REMOTE_APP_DIR="/opt/powerauto"

# 檢查SSH密鑰
if [ ! -f "$KEY_PATH" ]; then
    echo "❌ SSH密鑰文件不存在: $KEY_PATH"
    exit 1
fi

# 設置密鑰權限
chmod 400 "$KEY_PATH"

echo "📡 測試EC2連接..."
if ! ssh -i "$KEY_PATH" -o ConnectTimeout=10 "$EC2_USER@$EC2_HOST" "echo 'EC2連接成功'" > /dev/null 2>&1; then
    echo "❌ 無法連接到EC2實例，請檢查："
    echo "   1. EC2實例是否運行"
    echo "   2. 安全組是否允許SSH(22端口)"
    echo "   3. SSH密鑰是否正確"
    exit 1
fi

echo "✅ EC2連接正常"

# 1. 準備EC2環境
echo "🔧 準備EC2環境..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" << 'EOF'
# 更新系統
sudo yum update -y

# 安裝Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 安裝Docker..."
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker ec2-user
fi

# 安裝Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "🔨 安裝Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 創建應用目錄
sudo mkdir -p /opt/powerauto
sudo chown ec2-user:ec2-user /opt/powerauto

echo "✅ EC2環境準備完成"
EOF

# 2. 上傳應用文件
echo "📦 上傳應用文件..."

# 上傳後端代碼
echo "📂 上傳後端代碼..."
scp -i "$KEY_PATH" -r "$LOCAL_APP_DIR"/* "$EC2_USER@$EC2_HOST:$REMOTE_APP_DIR/"

# 上傳Docker配置
echo "🐳 上傳Docker配置..."
scp -i "$KEY_PATH" /Users/alexchuang/alexchuangtest/aicore0720/Dockerfile "$EC2_USER@$EC2_HOST:$REMOTE_APP_DIR/"
scp -i "$KEY_PATH" /Users/alexchuang/alexchuangtest/aicore0720/docker-compose.yml "$EC2_USER@$EC2_HOST:$REMOTE_APP_DIR/"
scp -i "$KEY_PATH" /Users/alexchuang/alexchuangtest/aicore0720/nginx.conf "$EC2_USER@$EC2_HOST:$REMOTE_APP_DIR/"

# 3. 在EC2上構建和啟動服務
echo "🚀 構建和啟動服務..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" << EOF
cd $REMOTE_APP_DIR

# 創建requirements.txt
cat > requirements.txt << 'REQUIREMENTS_EOF'
flask==2.3.3
flask-sqlalchemy==3.0.5
flask-bcrypt==1.0.1
flask-cors==4.0.0
pyjwt==2.8.0
stripe==5.5.0
gunicorn==21.2.0
python-dotenv==1.0.0
REQUIREMENTS_EOF

# 創建生產環境配置
cat > .env << 'ENV_EOF'
SECRET_KEY=powerauto-ai-production-\$(openssl rand -hex 32)
DATABASE_URL=sqlite:///data/powerauto_production.db
STRIPE_SECRET_KEY=sk_test_dummy_key
STRIPE_WEBHOOK_SECRET=whsec_dummy_webhook_secret
FLASK_ENV=production
PORT=5000
ENV_EOF

# 創建必要目錄
mkdir -p data logs ssl

# 停止現有服務（如果存在）
docker-compose down 2>/dev/null || true

# 構建和啟動服務
echo "🔨 構建Docker映像..."
docker-compose build

echo "🚀 啟動服務..."
docker-compose up -d

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 30

# 檢查服務狀態
echo "🔍 檢查服務狀態..."
docker-compose ps

# 測試API
echo "🧪 測試API..."
if curl -f http://localhost:5000/api/subscription/plans >/dev/null 2>&1; then
    echo "✅ PowerAuto.ai API啟動成功"
else
    echo "❌ API測試失敗，檢查日誌："
    docker-compose logs --tail=20
fi

EOF

# 4. 獲取服務狀態
echo ""
echo "📊 獲取部署狀態..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" << 'EOF'
cd /opt/powerauto

echo "🐳 Docker容器狀態:"
docker-compose ps

echo ""
echo "📡 網路測試:"
echo "本地API: $(curl -s http://localhost:5000/api/subscription/plans > /dev/null && echo '✅ 正常' || echo '❌ 失敗')"

echo ""
echo "📋 最近日誌:"
docker-compose logs --tail=10 powerauto-web

EOF

echo ""
echo "🎉 PowerAuto.ai EC2部署完成！"
echo ""
echo "📍 服務訪問信息:"
echo "   🌐 公網地址: http://$EC2_HOST"
echo "   🔗 API測試: http://$EC2_HOST/api/subscription/plans"
echo ""
echo "🔧 管理命令:"
echo "   查看狀態: ssh -i \"$KEY_PATH\" $EC2_USER@$EC2_HOST 'cd /opt/powerauto && docker-compose ps'"
echo "   查看日誌: ssh -i \"$KEY_PATH\" $EC2_USER@$EC2_HOST 'cd /opt/powerauto && docker-compose logs'"
echo "   重啟服務: ssh -i \"$KEY_PATH\" $EC2_USER@$EC2_HOST 'cd /opt/powerauto && docker-compose restart'"
echo "   停止服務: ssh -i \"$KEY_PATH\" $EC2_USER@$EC2_HOST 'cd /opt/powerauto && docker-compose down'"
echo ""
echo "⚠️  注意事項:"
echo "   1. 確保EC2安全組開放80和443端口"
echo "   2. 配置域名DNS指向EC2公網IP"
echo "   3. 設置SSL證書(Let's Encrypt或自簽名)"
echo "   4. 更新Stripe密鑰為生產環境密鑰"