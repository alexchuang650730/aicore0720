#!/bin/bash

echo "🚀 PowerAuto.ai EC2 部署脚本"
echo "============================="

# 系統更新
echo "📦 更新系統套件..."
sudo yum update -y

# 安裝必要套件
echo "🔧 安裝必要套件..."
sudo yum install -y python3 python3-pip git nginx

# 安裝Docker
echo "🐳 安裝Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# 安裝Docker Compose
echo "🔨 安裝Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 創建應用目錄
echo "📁 創建應用目錄..."
sudo mkdir -p /opt/powerauto
sudo chown ec2-user:ec2-user /opt/powerauto
cd /opt/powerauto

# 創建Python虛擬環境
echo "🐍 設置Python環境..."
python3 -m venv venv
source venv/bin/activate

# 創建requirements.txt
cat > requirements.txt << 'EOF'
flask==2.3.3
flask-sqlalchemy==3.0.5
flask-bcrypt==1.0.1
flask-cors==4.0.0
pyjwt==2.8.0
stripe==5.5.0
gunicorn==21.2.0
python-dotenv==1.0.0
EOF

# 安裝Python依賴
echo "📚 安裝Python依賴..."
pip install -r requirements.txt

# 創建環境變量文件
cat > .env << 'EOF'
SECRET_KEY=powerauto-ai-production-secret-key-$(openssl rand -hex 32)
DATABASE_URL=sqlite:///powerauto_production.db
STRIPE_SECRET_KEY=sk_live_your_stripe_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
FLASK_ENV=production
PORT=5000
EOF

echo "✅ EC2 環境準備完成"
echo ""
echo "📝 接下來需要："
echo "1. 上傳PowerAuto.ai應用代碼"
echo "2. 配置Nginx反向代理"
echo "3. 設置SSL證書"
echo "4. 啟動服務"
echo ""
echo "🔗 執行方式："
echo "scp -i alexchuang.pem -r /path/to/powerauto/backend ec2-user@ec2-13-222-125-83.compute-1.amazonaws.com:/opt/powerauto/"